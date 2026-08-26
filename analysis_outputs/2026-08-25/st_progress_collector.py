# -*- coding: utf-8 -*-
# ============================================================================
# ST股 摘星摘帽进度 每日自动收集与推送程序  (st_progress_collector.py)
# ----------------------------------------------------------------------------
# 用途：每个交易日早晨自动收集 17 只 ST/*ST 股票的
#       (1) 实时行情与成交量异动  (2) 主力资金流向  (3) 摘星摘帽/重整文本进度
#       并汇总成 HTML+文本报告，经飞书(lark-cli)推送给老板。
#
# 仅依赖 Python 标准库，可在任意 python3 环境跑，便于迁移与定时调度。
#
# ============================ 一、任务调度配置 ============================
#   触发方式 : WorkBuddy 自动化 automation-1787294825559 (每日 09:00, Asia/Shanghai)
#   调度规则 : FREQ=DAILY;BYHOUR=9;BYMINUTE=0  (开盘前推送，便于盘中决策)
#   非交易日 : 内置 is_trading_day() 判断(周末/法定节假日跳过)，无需人工干预
#   文本进度 : 自动化在触发时会先 WebSearch 刷新 progress_db.json，本程序读取渲染
#   失败处理 : 推送失败重试1次；仍失败写错误日志并回报，不影响报告落盘
#
# ============================ 二、信息收集字段定义 ============================
#   行情字段 (腾讯 qt.gtimg.cn)  : 代码/名称/现价/涨跌幅/振幅/换手率/量比/
#                                   开盘/最高/最低/昨收/成交量(手)/成交额(亿)/总市值(亿)
#   资金字段 (东财 push2.eastmoney) : 当日主力净流入(亿)/主力净流入占比(%)/
#                                   上午主力净流入/下午主力净流入/大单净流向
#   进度字段 (progress_db.json)   : st_type(ST/*ST)/stage(阶段)/
#                                   last_event_date/last_event(最新进展)/
#                                   catalyst_window(催化窗口)/risks(风险)/updated(更新日)
#   派生字段                      : 异动标记(涨跌停/放量)/进度新鲜度(距更新天数)/
#                                   判定(利好/利空/需关注/中性)
#
# ============================ 三、通知方式说明 ============================
#   默认通道 : lark-cli (bot 身份 P2P 发给老板 open_id)
#   接收人   : feishu_receive_id = ou_10cdef8ea8a202ab450597b1501eb8dd
#   命令原型 : lark-cli im +messages-send --as bot --user-id <open_id> --text <内容>
#   备选通道 : webhook 群机器人 / app(tenant_access_token) — 见 CONFIG.feishu_push_mode
#   输出物   : 同时落盘 HTML 报告 + JSONL 发送日志，便于回溯
# ============================================================================

import os
import sys
import json
import subprocess
import datetime as dt
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 配置区
# ---------------------------------------------------------------------------
CONFIG = {
    "schedule": {
        "trigger": "WorkBuddy automation-1787294825559",
        "rrule": "FREQ=DAILY;BYHOUR=9;BYMINUTE=0",
        "timezone": "Asia/Shanghai",
        "note": "每日09:00开盘前触发；非交易日(周末/法定节假日)自动跳过",
    },
    "feishu_push_mode": "cli",          # cli(默认) / webhook / app
    "feishu_receive_id": "ou_10cdef8ea8a202ab450597b1501eb8dd",  # 老板 open_id
    "feishu_webhook": "",
    "feishu_secret": "",
    "feishu_app_id": "",
    "feishu_app_secret": "",
    "lark_cli_path": r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages\lark-cli.cmd",  # 已探明绝对路径, 不依赖环境PATH
    "progress_db": os.path.join(BASE_DIR, "progress_db.json"),
    "ann_stale_days": 3,                  # 进度距更新>该天数则标"需关注核实"
    "anomaly_vol_ratio": 3.0,             # 量比阈值→放量
    "anomaly_pct_limit": 9.5,             # 涨跌幅阈值→涨跌停(主板ST ±10%)
    "anomaly_pct_move": 4.9,              # 涨跌幅阈值→大幅异动
}

# ---------------------------------------------------------------------------
# 股票清单 (17只 ST/*ST)
#   market: sh=上交所(secid 1.x), sz=深交所(secid 0.x, 含创业板3开头)
# ---------------------------------------------------------------------------
STOCKS = [
    {"code": "600079", "name": "ST人福",   "market": "sh", "secid": "1.600079"},
    {"code": "002726", "name": "ST龙大",   "market": "sz", "secid": "0.002726"},
    {"code": "000711", "name": "ST京蓝",   "market": "sz", "secid": "0.000711"},
    {"code": "000838", "name": "*ST发展",  "market": "sz", "secid": "0.000838"},
    {"code": "600337", "name": "ST美克",   "market": "sh", "secid": "1.600337"},
    {"code": "002168", "name": "ST惠程",   "market": "sz", "secid": "0.002168"},
    {"code": "600381", "name": "*ST春天",  "market": "sh", "secid": "1.600381"},
    {"code": "300147", "name": "*ST香雪",  "market": "sz", "secid": "0.300147"},
    {"code": "002542", "name": "*ST中岩",  "market": "sz", "secid": "0.002542"},
    {"code": "300027", "name": "ST华谊",   "market": "sz", "secid": "0.300027"},
    {"code": "300020", "name": "ST银江",   "market": "sz", "secid": "0.300020"},
    {"code": "600340", "name": "*ST华幸",  "market": "sh", "secid": "1.600340"},
    {"code": "600370", "name": "*ST三房",  "market": "sh", "secid": "1.600370"},
    {"code": "600165", "name": "ST宁科",   "market": "sh", "secid": "1.600165"},
    {"code": "600525", "name": "ST长圆",   "market": "sh", "secid": "1.600525"},
    {"code": "603843", "name": "*ST正平",  "market": "sh", "secid": "1.603843"},
    {"code": "603377", "name": "ST东时",   "market": "sh", "secid": "1.603377"},
]

# 法定节假日(2026, 简单维护；is_trading_day 也会排除周末)
HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-02", "2026-02-16", "2026-02-17", "2026-02-18",
    "2026-02-19", "2026-02-20", "2026-04-03", "2026-04-04", "2026-04-05",
    "2026-05-01", "2026-05-02", "2026-05-03", "2026-06-19", "2026-09-25",
    "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05",
    "2026-10-06", "2026-10-07",
}


# ---------------------------------------------------------------------------
# 通用：HTTP GET (带 UA，超时)
# ---------------------------------------------------------------------------
def http_get(url, timeout=15, encoding=None, retries=2):
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            enc = encoding or ("gb2312" if "qt.gtimg.cn" in url else "utf-8")
            return raw.decode(enc, errors="ignore")
        except Exception as e:
            last_err = e
            if attempt < retries:
                import time
                time.sleep(1.2 * (attempt + 1))
    raise last_err


# ---------------------------------------------------------------------------
# 交易日判断
# ---------------------------------------------------------------------------
def is_trading_day(d=None):
    d = d or dt.date.today()
    if d.weekday() >= 5:               # 周六/周日
        return False
    if d.strftime("%Y-%m-%d") in HOLIDAYS_2026:
        return False
    return True


# ---------------------------------------------------------------------------
# 采集1：腾讯实时快照
# ---------------------------------------------------------------------------
def collect_snapshot(stock):
    url = f"https://qt.gtimg.cn/q={stock['market']}{stock['code']}"
    try:
        txt = http_get(url)
    except Exception as e:
        return {"ok": False, "err": str(e)[:120]}
    # 形如 v_sh600079="1~名称~代码~今开~昨收~现价~最高~最低~...~涨跌幅~振幅~换手~量比~...~成交量~成交额~...~总市值~流通市值~..."
    s = txt.split("=", 1)[1].strip().strip('"')
    f = s.split("~")
    def g(i, cast=float, default=""):
        try:
            return cast(f[i])
        except (IndexError, ValueError):
            return default
    return {
        "ok": True,
        "name": g(1, str, stock["name"]),
        "open": g(3), "prev_close": g(4), "price": g(5),
        "high": g(6), "low": g(7),
        "time": g(30, str, ""),
        "pct": g(32), "amplitude": g(33), "turnover": g(34), "vol_ratio": g(35),
        "volume": g(37),                       # 手
        "amount": g(38),                       # 元
        "total_mv": g(44),                     # 亿 (腾讯 f[44] 已是亿单位, 见项目记忆)
        "float_mv": g(45),                      # 亿
    }


# ---------------------------------------------------------------------------
# 采集2：东财主力资金流 (当日累计 + 分时)
# ---------------------------------------------------------------------------
def collect_fflow(stock, n_day=1, n_min=240):
    secid = stock["secid"]
    out = {"ok": False, "main_net": None, "main_net_pct": None,
           "am_main": None, "pm_main": None}
    # 当日累计 (daykline, lmt=1 取最近1交易日)
    try:
        day_url = (f"https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
                   f"?lmt={n_day}&klt=101&secid={secid}")
        dj = json.loads(http_get(day_url))
        klines = (dj.get("data") or {}).get("klines") or []
        if klines:
            last = klines[-1].split(",")
            # [日期, 主力净流入额(元), 主力净流入占比%, 小单, 中单, 大单, 特大单, 收盘价, ...]
            out["main_net"] = float(last[1]) / 1e8 if last[1] not in ("", "-") else None
            out["main_net_pct"] = float(last[2]) if len(last) > 2 and last[2] not in ("", "-") else None
            out["ok"] = True
    except Exception:
        pass
    # 分时 (分钟 kline, lmt=240) → 拆上午/下午主力净流入
    try:
        min_url = (f"https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
                   f"?lmt={n_min}&klt=1&secid={secid}")
        mj = json.loads(http_get(min_url))
        mk = (mj.get("data") or {}).get("klines") or []
        am, pm = 0.0, 0.0
        for line in mk:
            parts = line.split(",")
            ts = parts[0][-8:] if len(parts) > 0 else ""   # HH:MM:SS
            try:
                val = float(parts[1]) / 1e8
            except (ValueError, IndexError):
                val = 0.0
            if "09:" <= ts < "11:30":
                am += val
            elif "13:00" <= ts <= "15:00":
                pm += val
        out["am_main"] = round(am, 4)
        out["pm_main"] = round(pm, 4)
        if not out["ok"]:
            out["ok"] = True
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------
# 读取进度缓存库
# ---------------------------------------------------------------------------
def load_progress_db():
    try:
        with open(CONFIG["progress_db"], encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        return {"meta": {"updated": "?", "source": "读取失败:" + str(e)[:80]},
                "stocks": {}}


# ---------------------------------------------------------------------------
# 异常 + 判定 派生
# ---------------------------------------------------------------------------
def derive_flags(snap, fflow, prog, today):
    flags = []
    verdict = "中性"
    pct = snap.get("pct") or 0.0
    vr = snap.get("vol_ratio") or 0.0
    if vr >= CONFIG["anomaly_vol_ratio"]:
        flags.append(f"放量(量比{vr:.2f})")
    if pct >= CONFIG["anomaly_pct_limit"]:
        flags.append(f"涨停+{pct:.2f}%")
    elif pct <= -CONFIG["anomaly_pct_limit"]:
        flags.append(f"跌停{pct:.2f}%")
    elif pct >= CONFIG["anomaly_pct_move"]:
        flags.append(f"大涨+{pct:.2f}%")
    elif pct <= -CONFIG["anomaly_pct_move"]:
        flags.append(f"大跌{pct:.2f}%")

    mn = fflow.get("main_net")
    if mn is not None:
        if mn >= 0.3:
            flags.append(f"主力净流入{mn:.2f}亿")
        elif mn <= -0.3:
            flags.append(f"主力净流出{mn:.2f}亿")

    # 进度新鲜度
    fresh_days = None
    if prog and prog.get("updated"):
        try:
            ud = dt.datetime.strptime(prog["updated"], "%Y-%m-%d").date()
            fresh_days = (today - ud).days
        except Exception:
            fresh_days = None

    # 判定逻辑
    stage = (prog or {}).get("stage", "")
    if stage == "已摘帽":
        verdict = "利好(已摘帽)"
    elif "涨停" in " ".join(flags) or (mn is not None and mn >= 0.3 and pct > 0):
        verdict = "利好"
    elif "跌停" in " ".join(flags) or (mn is not None and mn <= -0.3 and pct < 0):
        verdict = "利空"
    if fresh_days is not None and fresh_days > CONFIG["ann_stale_days"]:
        flags.append(f"进度{prog.get('updated')}未更新,{fresh_days}天前")
        if verdict == "中性":
            verdict = "需关注核实"
    if (vr >= CONFIG["anomaly_vol_ratio"] or abs(pct) >= CONFIG["anomaly_pct_move"]) and verdict == "中性":
        verdict = "需关注(异动)"
    return flags, verdict, fresh_days


# ---------------------------------------------------------------------------
# 组装单只记录
# ---------------------------------------------------------------------------
def analyze_one(stock, db, today):
    snap = collect_snapshot(stock)
    fflow = collect_fflow(stock)
    prog = (db.get("stocks") or {}).get(stock["code"], {})
    flags, verdict, fresh_days = derive_flags(snap, fflow, prog, today)
    return {
        "code": stock["code"], "name": stock["name"],
        "market": stock["market"], "secid": stock["secid"],
        "snap": snap, "fflow": fflow, "prog": prog,
        "flags": flags, "verdict": verdict, "fresh_days": fresh_days,
    }


# ---------------------------------------------------------------------------
# 生成文本(飞书)报告
# ---------------------------------------------------------------------------
def build_text(recs, today, ann_ok=True):
    lines = []
    lines.append(f"【ST摘星摘帽每日进度】{today:%Y-%m-%d} 共{len(recs)}只")
    if not ann_ok:
        lines.append("⚠️ 行情/资金源部分异常，以下以可得数据为准")
    lines.append("-" * 32)
    for r in recs:
        s = r["snap"]
        f = r["fflow"]
        p = r["prog"]
        price = s.get("price", "-") if s.get("ok") else "行情异常"
        pct = s.get("pct", 0) if s.get("ok") else 0
        mn = f.get("main_net")
        mn_s = f"{mn:+.2f}亿" if mn is not None else "—"
        stage = p.get("stage", "—")
        last = p.get("last_event", "—")[:40]
        flag_s = ("；".join(r["flags"])) if r["flags"] else "无"
        lines.append(f"{r['name']}({r['code']}) [{p.get('st_type','ST')}]")
        lines.append(f"  价 {price} {pct:+.2f}% | 主力 {mn_s} | 阶段:{stage}")
        lines.append(f"  进展:{last}")
        lines.append(f"  异动:{flag_s} → 判定:{r['verdict']}")
        lines.append("")
    lines.append("⚠️ 纯事件/量价监控，非投资建议。ST/*ST退市风险极高，自负盈亏。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 生成 HTML 报告
# ---------------------------------------------------------------------------
def build_html(recs, today, meta):
    stage_color = {
        "已摘帽": "#1a7f37", "申请待审": "#0969da", "投资人已签": "#8250df",
        "预重整中": "#bf8700", "等待摘帽门槛": "#0a7ea4", "滞后": "#9a6700",
    }
    rows = []
    for r in recs:
        s = r["snap"]; f = r["fflow"]; p = r["prog"]
        price = f"{s['price']:.2f}" if s.get("ok") else "—"
        pct = s.get("pct", 0) if s.get("ok") else 0
        pct_col = "#cf222e" if pct >= 0 else "#1a7f37"   # A股:涨红跌绿
        if s.get("ok") and pct < 0:
            pct_col = "#1a7f37"
        elif s.get("ok"):
            pct_col = "#cf222e"
        mn = f.get("main_net")
        mn_s = f"{mn:+.2f}亿" if mn is not None else "—"
        mn_col = "#cf222e" if (mn or 0) >= 0 else "#1a7f37"
        vr = s.get("vol_ratio") or 0
        sc = stage_color.get(p.get("stage", ""), "#57606a")
        flag_s = "；".join(r["flags"]) if r["flags"] else "无"
        vcolor = {"利好": "#1a7f37", "利好(已摘帽)": "#1a7f37",
                  "利空": "#cf222e"}.get(r["verdict"], "#9a6700")
        rows.append(f"""
        <tr>
          <td><b>{r['name']}</b><br><span class="code">{r['code']}</span></td>
          <td>{p.get('st_type','ST')}</td>
          <td class="num">{price}</td>
          <td class="num" style="color:{pct_col}">{pct:+.2f}%</td>
          <td class="num">{vr:.2f}</td>
          <td class="num" style="color:{mn_col}">{mn_s}</td>
          <td><span class="badge" style="background:{sc}">{p.get('stage','—')}</span></td>
          <td class="prog">{p.get('last_event','—')[:60]}</td>
          <td class="prog">{p.get('catalyst_window','—')}</td>
          <td class="flag">{flag_s}</td>
          <td style="color:{vcolor}"><b>{r['verdict']}</b></td>
        </tr>""")
    html = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ST摘星摘帽每日进度 {today:%Y-%m-%d}</title>
<style>
 body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f6f8fa;color:#1f2328;margin:0;padding:18px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#57606a;font-size:12px;margin-bottom:14px}}
 table{{border-collapse:collapse;width:100%;background:#fff;font-size:12px;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
 th,td{{border:1px solid #e1e4e8;padding:7px 8px;vertical-align:top;text-align:left}}
 th{{background:#f0f3f6;font-weight:600}} .num{{text-align:right;font-variant-numeric:tabular-nums}}
 .code{{color:#57606a;font-size:11px}} .badge{{color:#fff;padding:1px 6px;border-radius:10px;font-size:11px;white-space:nowrap}}
 .prog{{max-width:260px}} .flag{{max-width:150px;color:#9a6700}}
 .legend{{margin-top:12px;font-size:11px;color:#57606a;line-height:1.7}}
</style></head><body>
<h1>ST/*ST 摘星摘帽进度日报</h1>
<div class="sub">日期 {today:%Y-%m-%d} ｜ 标的 {len(recs)} 只 ｜ 数据源：腾讯行情+东财资金流+progress_db缓存(每日WebSearch刷新) ｜ 非投资建议</div>
<table>
<tr><th>名称/代码</th><th>类型</th><th>现价</th><th>涨跌幅</th><th>量比</th><th>主力净流入</th><th>阶段</th><th>最新进展</th><th>催化窗口</th><th>异动/信号</th><th>判定</th></tr>
{''.join(rows)}
</table>
<div class="legend">
阶段色：<span class="badge" style="background:#1a7f37">已摘帽</span>
<span class="badge" style="background:#0969da">申请待审</span>
<span class="badge" style="background:#8250df">投资人已签</span>
<span class="badge" style="background:#bf8700">预重整中</span>
<span class="badge" style="background:#0a7ea4">等待摘帽门槛</span>
<span class="badge" style="background:#9a6700">滞后</span><br>
进度库更新日：{meta.get('updated','?')} ｜ 来源：{meta.get('source','?')}<br>
⚠️ 沙箱内公告接口全废，文本进度由每日自动化WebSearch刷新progress_db.json；行情异动(量比&gt;3/涨跌停)自动标红。ST/*ST退市风险极高，本日报仅为事件监控，不构成投资建议。
</div></body></html>"""
    return html


# ---------------------------------------------------------------------------
# 飞书推送
# ---------------------------------------------------------------------------
def resolve_cli():
    import shutil
    candidates = [
        CONFIG.get("lark_cli_path"),
        shutil.which("lark-cli"),
        shutil.which("lark-cli.CMD"),
        shutil.which("lark-cli.cmd"),
        r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages\lark-cli.cmd",
        r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages\lark-cli.CMD",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    # 最后兜底: 即便文件探测不到, 仍返回已知路径交由 subprocess 尝试
    return candidates[0] or r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages\lark-cli.cmd"


def push_feishu(text):
    mode = (CONFIG.get("feishu_push_mode") or "cli").lower()
    if mode == "cli":
        rid = CONFIG.get("feishu_receive_id")
        if not rid:
            raise RuntimeError("未配置 feishu_receive_id")
        # 飞书文本消息需 JSON 编码的 content: {"text":"..."}
        import json as _json
        content = _json.dumps({"text": text}, ensure_ascii=False)
        # 直接用受管 node 执行 lark-cli 的 run.js, 绕开 lark-cli.cmd
        # (其内部 node 依赖 PATH, 后台/自动化 shell 缺失 node 会导致"不是内部或外部命令")
        node = r"C:\Users\EDY\.workbuddy\binaries\node\versions\22.22.2\node.exe"
        runjs = (r"C:\Users\EDY\.workbuddy\binaries\node\cli-connector-packages"
                 r"\node_modules\@larksuite\cli\scripts\run.js")
        if not (os.path.exists(node) and os.path.exists(runjs)):
            raise RuntimeError("lark-cli 运行环境缺失(node/run.js)")
        cmd = [node, runjs, "im", "+messages-send", "--as", "bot",
               "--user-id", rid, "--msg-type", "text", "--content", content]
        r = subprocess.run(cmd, capture_output=True, timeout=30)  # 字节模式, 避免GBK解码崩溃
        out_raw = (r.stdout or b"").decode("utf-8", "ignore")
        err_raw = (r.stderr or b"").decode("utf-8", "ignore")
        if r.returncode != 0:
            raise RuntimeError(f"lark-cli非0:{err_raw[:200]}")
        try:
            out = _json.loads(out_raw)
        except _json.JSONDecodeError:
            raise RuntimeError(f"lark-cli非JSON:{out_raw[:120]}")
        if not isinstance(out, dict) or not out.get("ok"):
            raise RuntimeError(f"lark-cli发送失败:{out_raw[:200]}")
        return out_raw
    else:
        raise RuntimeError(f"未实现的推送模式:{mode}")


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
def record_log(today, recs, send_ok, detail):
    path = os.path.join(LOG_DIR, "st_collector_send_log.jsonl")
    entry = {
        "date": today.strftime("%Y-%m-%d"),
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "send_ok": send_ok,
        "detail": detail,
        "records": [
            {"code": r["code"], "name": r["name"],
             "price": r["snap"].get("price", "-"),
             "pct": r["snap"].get("pct", "-"),
             "stage": r["prog"].get("stage", ""),
             "verdict": r["verdict"], "flags": r["flags"]}
            for r in recs
        ],
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    today = dt.date.today()
    args = sys.argv[1:]
    test_send = "--test-send" in args
    no_send = "--no-send" in args

    print(f"[*] {today:%Y-%m-%d} ST进度收集启动 (标的{len(STOCKS)}只)")

    if not is_trading_day(today):
        msg = f"{today:%Y-%m-%d} 非交易日，跳过。(周末/法定节假日)"
        print(f"[!] {msg}")
        record_log(today, [], True, msg)
        return

    if test_send:
        ok, detail = _try_send(
            "【通道自测】ST进度收集程序飞书推送通道正常 ✅ " + today.strftime("%Y-%m-%d"))
        print(f"[+] 通道自测推送:{'成功' if ok else '失败'} | {str(detail)[:80]}")
        record_log(today, [], ok, detail)
        return

    db = load_progress_db()
    recs = [analyze_one(s, db, today) for s in STOCKS]
    ann_ok = all(r["snap"].get("ok", False) for r in recs)

    # 落盘 HTML
    html = build_html(recs, today, db.get("meta", {}))
    html_path = os.path.join(BASE_DIR, f"st_progress_daily_{today:%Y%m%d}.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"[+] HTML报告: {html_path}")

    text = build_text(recs, today, ann_ok)

    if test_send:
        send_ok, detail = _try_send("【通道自测】ST进度收集程序飞书推送正常 ✅ " + today.strftime("%Y-%m-%d"))
    elif no_send:
        send_ok, detail = True, "no_send 跳过推送"
        print("[*] --no-send 仅分析不推送")
    else:
        send_ok, detail = _try_send(text)

    record_log(today, recs, send_ok, detail)
    # 控制台摘要
    print(f"[+] 推送:{'成功' if send_ok else '失败'} | 标的{len(recs)} | 详情:{str(detail)[:80]}")
    for r in recs:
        print(f"    {r['name']}({r['code']}) {r['verdict']} | " +
              ("；".join(r['flags']) if r['flags'] else "无信号"))


def _try_send(text):
    for attempt in (1, 2):
        try:
            out = push_feishu(text)
            return True, out
        except Exception as e:
            if attempt == 1:
                print(f"[!] 推送失败, 重试: {e}")
            else:
                return False, f"推送失败:{e}"


if __name__ == "__main__":
    main()
