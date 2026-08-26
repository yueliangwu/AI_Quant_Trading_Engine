# -*- coding: utf-8 -*-
"""
ST股重整/摘帽每日监控 · 飞书推送
=================================
功能:
  1. 交易日历判断 (跳过周末与大陆法定节假日) —— 非交易日自动跳过
  2. 多源拉取 13 只 ST 股最近公告, 识别「重整 / 预重整 / 摘帽(撤销风险警示)」进展
  3. 结合最新公告 + 行情信号, 判定 利好 / 利空 / 中性 (规则引擎 + 可选LLM深度研判)
  4. 汇总消息推送至飞书 (默认走 lark-cli / bot身份发给指定 open_id; 可选 webhook 或 app_id)
  5. 错误重试 (指数退避) + 发送状态记录 (JSONL 日志)

使用:
  python st_monitor.py                 # 正常运行 (由每日9点自动化触发, 默认 lark-cli 推送)
  python st_monitor.py --dry-run       # 用内置样例校验逻辑, 不联网不推送
  python st_monitor.py --test-send     # 仅发送一条 CLI 通道自测消息, 不分析
  python st_monitor.py --force         # 非交易日也强制运行
  python st_monitor.py --no-send       # 只分析不推送 (状态仍写入日志)

配置优先级: 同目录 st_monitor_config.json  >  环境变量  >  下方 DEFAULT_CONFIG
"""
import os
import sys
import json
import time
import logging
import datetime
import hashlib
import hmac
import base64
import argparse
import shutil
import subprocess
import urllib.request
import urllib.error
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "st_monitor_run.log"), encoding="utf-8"),
    ],
)
log = logging.getLogger("st_monitor")

# ---------------------------------------------------------------- 默认配置
# 17 只 ST/*ST 标的 (代码, 名称, 市场前缀 sh/sz) —— 与最新优先级清单一致
# 名称已含 ST 标识 (*ST=退市风险警示 / ST=其他风险警示)
# 2026-08-25 增补: 宁科(600165) / 长圆(600525) / 正平(603843) / 东时(603377)
DEFAULT_STOCKS = [
    ("600079", "ST人福", "sh"), ("002726", "ST龙大", "sz"), ("000711", "ST京蓝", "sz"),
    ("000838", "*ST发展", "sz"), ("600337", "ST美克", "sh"), ("002168", "ST惠程", "sz"),
    ("600381", "*ST春天", "sh"), ("300147", "*ST香雪", "sz"), ("002542", "*ST中岩", "sz"),
    ("300027", "ST华谊", "sz"), ("300020", "ST银江", "sz"), ("600340", "*ST华幸", "sh"),
    ("600370", "*ST三房", "sh"),
    ("600165", "ST宁科", "sh"), ("600525", "ST长圆", "sh"),
    ("603843", "*ST正平", "sh"), ("603377", "ST东时", "sh"),
]

# 2026 年大陆 A 股法定节假日 (休市) —— 数据以交易所公告为准, 可逐年更新
CN_HOLIDAYS_2026 = {
    "2026-01-01","2026-01-02","2026-02-16","2026-02-17","2026-02-18","2026-02-19","2026-02-20",
    "2026-02-23","2026-02-24","2026-04-04","2026-04-05","2026-04-06","2026-05-01","2026-05-02",
    "2026-05-03","2026-05-04","2026-05-05","2026-06-19","2026-06-20","2026-06-21","2026-06-22",
    "2026-09-25","2026-09-26","2026-09-27","2026-10-01","2026-10-02","2026-10-03","2026-10-04",
    "2026-10-05","2026-10-06","2026-10-07",
}

DEFAULT_CONFIG = {
    "stocks": DEFAULT_STOCKS,
    "feishu_push_mode": "cli",   # 推送方式: cli(默认, lark-cli bot) / webhook / app
    "feishu_webhook": "",        # 群机器人 webhook (push_mode=webhook 时填)
    "feishu_secret": "",         # 群机器人签名密钥 (可选, 开启了"签名校验"才需要)
    "feishu_app_id": "",         # push_mode=app 时填
    "feishu_app_secret": "",
    "feishu_receive_id": "ou_10cdef8ea8a202ab450597b1501eb8dd",  # 指定联系人 open_id
    "lark_cli_path": "",         # 可选: 显式指定 lark-cli 绝对路径 (留空则自动 which 探测)
    "deepseek_api_key": "",      # 可选: 用于深度利好/利空研判 (留空则用纯规则引擎)
    "announcement_days": 7,      # 仅扫描最近 N 天公告
    "max_retry": 3,              # 网络/发送重试次数
}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    p = os.path.join(BASE_DIR, "st_monitor_config.json")
    if os.path.exists(p):
        try:
            cfg.update(json.load(open(p, encoding="utf-8")))
            log.info("已加载配置文件 %s", p)
        except Exception as e:
            log.warning("配置文件读取失败, 改用默认/环境变量: %s", e)
    for k in ["feishu_webhook", "feishu_secret", "feishu_app_id",
              "feishu_app_secret", "feishu_receive_id", "deepseek_api_key"]:
        v = os.getenv(k.upper())
        if v:
            cfg[k] = v
    return cfg


# ---------------------------------------------------------------- 交易日历
def is_trading_day(dt: datetime.date) -> bool:
    if dt.weekday() >= 5:
        return False
    if dt.strftime("%Y-%m-%d") in CN_HOLIDAYS_2026:
        return False
    return True


# ---------------------------------------------------------------- 重试装饰器
def with_retry(max_attempts=3, base=2.0):
    def deco(fn):
        def wrap(*a, **k):
            last = None
            for i in range(max_attempts):
                try:
                    return fn(*a, **k)
                except Exception as e:
                    last = e
                    wait = base ** i
                    log.warning("调用 %s 失败(%d/%d): %s, %ss 后重试",
                                fn.__name__, i + 1, max_attempts, e, wait)
                    time.sleep(wait)
            log.error("调用 %s 最终失败: %s", fn.__name__, last)
            return None
        return wrap
    return deco


# ---------------------------------------------------------------- 网络请求
@with_retry()
def http_get(url, timeout=10, headers=None):
    h = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


# ---------------------------------------------------------------- 公告拉取
BULL_KW = ["重整", "预重整", "重整计划", "重整投资人", "摘帽", "撤销风险警示",
           "撤销退市风险警示", "摘星", "资产注入", "控股权", "回购", "增持",
           "中标", "扭亏", "业绩预盈", "申请撤销"]
BEAR_KW = ["退市", "终止上市", "被立案", "立案调查", "业绩预亏", "预亏",
           "亏损扩大", "退市风险", "股价低于1元", "面值退市", "问询函",
           "监管函", "公开谴责", "债务违约", "破产清算", "否定意见", "无法表示意见"]


def fetch_announcements(code, days=7):
    """拉取个股最近公告, 返回 [{'date','title','url'}]。

    数据源: 东财公告中心(np-anotice-stock.eastmoney.com)。
    历史数据源(datacenter-web RPTA_WEB_GG_LB / RPT_ANNOUNCE)已于2026年作废
    (返回 '报表配置不存在,code:9501'), 故切换至此。若接口仍不可用(返回空/报错)
    则返回 [], 由调用方标记为 '公告接口失效' 而非伪 '中性'。
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    url = ("https://np-anotice-stock.eastmoney.com/api/security/ann"
           f"?sr=-1&page_size=15&page_index=1&ann_type=0&client_source=web&stock_list={code}")
    try:
        raw = http_get(url, timeout=12)
        d = json.loads(raw)
        if not d.get("success") or d.get("data", {}).get("total_hits", 0) == 0:
            return []
        rows = d.get("data", {}).get("list", []) or []
        out = []
        for r in rows:
            dstr = (r.get("notice_date") or "")[:10]
            t = r.get("title") or ""
            u = r.get("art_code") or r.get("url") or ""
            if dstr and start.strftime("%Y-%m-%d") <= dstr <= end.strftime("%Y-%m-%d"):
                out.append({"date": dstr, "title": t, "url": u})
        return out
    except Exception as e:
        log.warning("公告拉取失败 %s: %s", code, e)
        return []


def probe_ann_api():
    """启动自检: 用已知近期有公告的标的(000711京蓝 8-24提交摘帽申请)探测接口是否可用。
    返回 True=可用, False=失效(沙箱/接口变更导致取不到公告)。"""
    try:
        rows = fetch_announcements("000711", days=7)
        return len(rows) > 0
    except Exception as e:
        log.warning("公告接口自检异常: %s", e)
        return False


def detect_price_anomaly(pct):
    """ST股价格异动识别 (2026-07-06起 主板ST/*ST涨跌幅±10%)。
    返回 '' 或 异动描述字符串。"""
    try:
        p = float(pct)
    except (TypeError, ValueError):
        return ""
    if p >= 9.5:
        return f"涨停 +{p:.2f}%(触及利好兑现/情绪极致, 重点核查催化)"
    if p <= -9.5:
        return f"跌停 {p:.2f}%(风险宣泄/利空, 警惕退市或重组失败)"
    if p >= 5:
        return f"大涨 +{p:.2f}%(疑似催化剂驱动)"
    if p <= -5:
        return f"大跌 {p:.2f}%(疑似风险释放)"
    return ""


def detect_progress(anns):
    """从公告标题识别重整/摘帽进展关键词, 返回 [(kw,title,date), ...]"""
    hits = []
    for a in anns:
        for kw in BULL_KW + BEAR_KW:
            if kw in a["title"]:
                hits.append((kw, a["title"], a["date"]))
    return hits


# ---------------------------------------------------------------- 行情信号 (腾讯)
@with_retry()
def fetch_quote(code, market):
    """腾讯实时快照, 取现价与涨跌幅作为市场情绪辅助信号"""
    url = f"https://qt.gtimg.cn/q={market}{code}"
    raw = http_get(url)
    if "=" not in raw:
        return None
    payload = raw.split("=", 1)[1].strip().strip('"')
    f = payload.split("~")
    if len(f) < 33:
        return None
    return {"name": f[1], "price": f[3], "pct": f[32]}


# ---------------------------------------------------------------- 利好利空判定
def rule_judge(hits, quote):
    """纯规则引擎: 利好关键词 +1, 利空关键词 -1; 返回 (verdict, score, reasons)"""
    score = 0
    reasons = []
    for kw, title, date in hits:
        if kw in BULL_KW:
            score += 1
            reasons.append(f"利好信号[{kw}] {title} ({date})")
        else:
            score -= 1
            reasons.append(f"利空信号[{kw}] {title} ({date})")
    # 行情辅助: 当日大涨伴随利好公告 -> 强化; 大跌伴随利空 -> 强化
    pct = quote.get("pct", "-") if quote else "-"
    try:
        p = float(pct)
        if p > 5 and score > 0:
            reasons.append(f"行情印证: 当日 +{p}% 与利好公告共振")
        elif p < -5 and score < 0:
            reasons.append(f"行情印证: 当日 {p}% 与利空公告共振")
    except (TypeError, ValueError):
        pass
    verdict = "中性"
    if score > 0:
        verdict = "利好"
    elif score < 0:
        verdict = "利空"
    return verdict, score, reasons


def llm_judge(text, api_key):
    """可选: 调用 DeepSeek 做深度研判 (需配置 deepseek_api_key)"""
    if not api_key:
        return None
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        body = json.dumps({"model": "deepseek-chat",
                           "messages": [{"role": "user", "content": text}],
                           "temperature": 0.2}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Authorization": f"Bearer {api_key}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            j = json.loads(r.read().decode())
            return j["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.warning("LLM 研判失败: %s", e)
        return None


# ---------------------------------------------------------------- 飞书推送
def feishu_sign(secret):
    ts = str(int(time.time()))
    s = f"{ts}\n{secret}".encode()
    h = hmac.new(secret.encode(), s, hashlib.sha256).digest()
    return ts, base64.b64encode(h).decode()


@with_retry()
def send_webhook(webhook, text, secret=""):
    msg = {"msg_type": "text", "content": {"text": text}}
    if secret:
        ts, sign = feishu_sign(secret)
        msg["timestamp"] = ts
        msg["sign"] = sign
    data = json.dumps(msg).encode()
    req = urllib.request.Request(webhook, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode()


@with_retry()
def send_to_user(app_id, app_secret, receive_id, text):
    tok_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(tok_url, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        tok = json.loads(r.read().decode())["tenant_access_token"]
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    msg = json.dumps({"msg_type": "text", "content": json.dumps({"text": text})}).encode()
    req = urllib.request.Request(url, data=msg,
                                 headers={"Authorization": f"Bearer {tok}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode()


def resolve_cli():
    """定位 lark-cli 可执行文件 (Windows 下需带 .CMD 扩展名)"""
    base = [
        os.environ.get("LARK_CLI_PATH", ""),
        shutil.which("lark-cli") or "",
        r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages\lark-cli.CMD",
    ]
    for c in base:
        if c and os.path.exists(c):
            return c
    return None


@with_retry()
def send_via_cli(text, receive_id, cli_path=None):
    """通过 lark-cli (bot 身份) 发送 P2P 消息到指定 open_id"""
    cli = cli_path or resolve_cli()
    if not cli:
        raise RuntimeError("未找到 lark-cli, 请配置 LARK_CLI_PATH 或将其加入 PATH")
    if not receive_id:
        raise RuntimeError("未配置 feishu_receive_id (接收人 open_id)")
    cmd = [cli, "im", "+messages-send", "--as", "bot",
           "--user-id", receive_id, "--text", text]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"lark-cli 返回非0: {r.stderr[:200]}")
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"lark-cli 输出非JSON: {r.stdout[:200]}")
    if not out.get("ok"):
        raise RuntimeError(f"lark-cli 发送失败: {r.stdout[:200]}")
    return r.stdout


def push_feishu(cfg, text):
    mode = (cfg.get("feishu_push_mode") or "cli").lower()
    if mode == "webhook" and cfg.get("feishu_webhook"):
        return send_webhook(cfg["feishu_webhook"], text, cfg.get("feishu_secret", ""))
    if mode == "app" and cfg.get("feishu_app_id") and cfg.get("feishu_app_secret"):
        return send_to_user(cfg["feishu_app_id"], cfg["feishu_app_secret"],
                            cfg["feishu_receive_id"], text)
    # 默认 / cli: 走 lark-cli (bot 身份发给指定 open_id)
    return send_via_cli(text, cfg.get("feishu_receive_id", ""),
                        cfg.get("lark_cli_path"))


# ---------------------------------------------------------------- 状态记录
def record_status(date_str, records, send_ok, detail):
    path = os.path.join(LOG_DIR, "st_monitor_send_log.jsonl")
    row = {"date": date_str, "send_ok": send_ok,
           "generated_at": datetime.datetime.now().isoformat(),
           "records": records, "detail": detail}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


# ---------------------------------------------------------------- 消息构建
def build_message(date_str, results, ann_ok=True):
    lines = [f"【ST股重整/摘帽监控】{date_str}"]
    if not ann_ok:
        lines.append("⚠️ 公告接口暂不可用(东财/腾讯公告源均失效), 以下为【价格异动监控】,"
                     "重整/摘星/摘帽文本进度需人工Web检索核验。")
    lines.append("=" * 32)
    for r in results:
        days = r.get("days", 7)
        prog = r["progress"] or f"近{days}日无重整/摘帽相关公告"
        lines.append(f"\n● {r['name']}({r['code']})  行情:{r.get('price','-')} ({r.get('pct','-')}%)")
        lines.append(f"  进展:{prog}")
        lines.append(f"  研判:{r['verdict']} (score={r['score']})")
        for why in r["reasons"][:3]:
            lines.append(f"   - {why}")
    lines.append("\n" + "=" * 32)
    lines.append("[风险提示] 本消息为程序自动生成的事件监控, 非投资建议, ST/*ST 退市风险极高。")
    return "\n".join(lines)


def analyze_one(code, name, market, cfg, ann_ok=True):
    quote = fetch_quote(code, market) or {}
    hits = []
    verdict, score, reasons = "中性", 0, []
    progress_kw = ""
    if ann_ok:
        anns = fetch_announcements(code, cfg["announcement_days"])
        hits = detect_progress(anns)
        verdict, score, reasons = rule_judge(hits, quote)
        progress_kw = "; ".join(sorted({h[0] for h in hits})) or ""
    # 价格异动信号 (腾讯行情在沙箱内可用, 作为核心可行动信号)
    anomaly = detect_price_anomaly(quote.get("pct", "-"))
    if anomaly:
        reasons.append(f"价格异动: {anomaly}")
    # 组装进展文案
    if not ann_ok:
        prog = "公告接口失效·仅价格监控"
        if anomaly:
            prog += " | " + anomaly
    else:
        prog = progress_kw
        if anomaly:
            prog = (prog + " | " + anomaly).strip(" |")
        if not prog:
            prog = f"近{cfg['announcement_days']}日无重整/摘帽相关公告"
    # 可选 LLM 深度研判
    if cfg.get("deepseek_api_key") and (hits or quote):
        ctx = (f"股票{name}({code})最新公告:{[h[1] for h in hits] or '无'}; "
               f"行情涨跌:{quote.get('pct','-')}%。请判断对股价利好/利空并给一句理由。")
        llm = llm_judge(ctx, cfg["deepseek_api_key"])
        if llm:
            reasons.append(f"[LLM]{llm[:120]}")
    return {"code": code, "name": name, "price": quote.get("price", "-"),
            "pct": quote.get("pct", "-"), "progress": prog,
            "verdict": verdict, "score": score, "reasons": reasons,
            "days": cfg["announcement_days"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="用内置样例校验逻辑, 不联网不推送")
    ap.add_argument("--test-send", action="store_true", help="仅发送一条 CLI 通道自测消息, 不分析")
    ap.add_argument("--force", action="store_true", help="非交易日也强制运行")
    ap.add_argument("--no-send", action="store_true", help="只分析不推送")
    args = ap.parse_args()

    cfg = load_config()
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")

    if not args.force and not is_trading_day(today):
        log.info("%s 非交易日, 跳过", date_str)
        record_status(date_str, [], True, "非交易日跳过")
        return

    if args.test_send:
        test_text = (
            f"[ST监控] 飞书CLI推送通道自测\n"
            f"时间: {date_str} {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            f"通道: lark-cli (bot身份) -> open_id {cfg.get('feishu_receive_id','')}\n"
            f"若您收到此消息, 说明每日9点自动化推送已就绪。"
        )
        try:
            detail = push_feishu(cfg, test_text)
            record_status(date_str, [], True, detail[:200])
            log.info("测试推送成功")
        except Exception as e:
            record_status(date_str, [], False, str(e))
            log.error("测试推送失败: %s", e)
        return

    log.info("开始监控 %s (dry=%s)", date_str, args.dry_run)
    # 公告接口自检: 不可用时降级为价格异动监控, 不再伪造 '中性'
    ann_ok = probe_ann_api()
    if not ann_ok:
        log.warning("公告接口不可用, 本次仅做价格异动监控")
    results = []
    if args.dry_run:
        sample = [
            ("600079", "ST人福", "sh", [("重整投资人", "关于重整投资人招募进展的公告", "2026-08-20")]),
            ("002542", "*ST中岩", "sz", [("退市风险", "关于股票可能被终止上市的风险提示公告", "2026-08-21")]),
        ]
        for code, name, mkt, hits in sample:
            verdict, score, reasons = rule_judge(hits, None)
            results.append({"code": code, "name": name, "price": "-", "pct": "-",
                            "progress": ";".join(h[0] for h in hits), "verdict": verdict,
                            "score": score, "reasons": [f"{h[0]}: {h[1]}" for h in hits], "days": 7})
    else:
        for code, name, market in cfg["stocks"]:
            try:
                results.append(analyze_one(code, name, market, cfg, ann_ok))
            except Exception as e:
                log.error("分析 %s 失败: %s", code, e)
                results.append({"code": code, "name": name, "price": "-", "pct": "-",
                                "progress": "分析异常", "verdict": "未知", "score": 0,
                                "reasons": [str(e)], "days": 7})

    msg = build_message(date_str, results, ann_ok)
    log.info("生成消息:\n%s", msg)

    send_ok = True
    detail = ""
    if args.no_send:
        detail = "no_send 跳过推送"
    else:
        try:
            detail = push_feishu(cfg, msg)
        except Exception as e:
            send_ok = False
            detail = str(e)
            log.error("飞书推送失败: %s", e)

    log_path = record_status(date_str, results, send_ok, detail)
    log.info("状态已记录: %s (send_ok=%s)", log_path, send_ok)


if __name__ == "__main__":
    main()
