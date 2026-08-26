# -*- coding: utf-8 -*-
"""
st_lowprice_scanner.py
------------------------------------------------------------
A股低位 ST/*ST 重整/摘星/摘帽预期 实时监控扫描器

功能:
  1. 行情(腾讯快照) + K线(腾讯日K) 判断"低位"(低价/小市值/超跌)
  2. 公告多源聚合(东财/巨潮/深交所/上交所) 识别"重整/摘星/摘帽预期"
  3. 按"低位 + ST状态(天然隐含撤销预期) + 近期实质进展"分级预警
  4. 输出: 代码/名称/现价/总市值/风险状态/触发原因/最近信号公告

数据源(均公开合规, 多源容错):
  - 行情: https://qt.gtimg.cn/q={market}{code}      (腾讯实时快照)
  - K线: https://web.ifzq.gtimg.cn/.../fqkline/get   (腾讯日K)
  - 公告: 东财 datacenter-web / 巨潮 hisAnnouncement / 深交所 annQuery / 上交所 getAnnInfoByCode
          (逐个尝试, 全失败则降级为"仅行情预警", 并标注需人工回巨潮核验)

免责声明:
  本脚本仅做公开信息的程序化归集与条件筛选, 不构成任何投资建议或要约。
  ST/*ST 股票退市风险极高, 请独立判断、自担风险。凡涉及"摘星/摘帽/重整"结论,
  须回交易所指定信披媒体(巨潮/交易所官网)核验后方可采信。

用法:
  python st_lowprice_scanner.py                  # 用内置13只池扫描
  python st_lowprice_scanner.py --pool pool.json # 自定义股票池
  python st_lowprice_scanner.py --price 3 --mktcap 50 --drop 25 --days 30
  python st_lowprice_scanner.py --html            # 额外生成 HTML 报告
  python st_lowprice_scanner.py --out D:/out       # 指定输出目录
"""

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("st_scanner")

# 17 只 ST/*ST 标的 (代码, 名称, 市场前缀 sh/sz); 名称已含 ST 标识
# 2026-08-25 增补: 宁科(600165) / 长圆(600525) / 正平(603843) / 东时(603377)
DEFAULT_POOL = [
    ("600079", "ST人福", "sh"), ("002726", "ST龙大", "sz"), ("000711", "ST京蓝", "sz"),
    ("000838", "*ST发展", "sz"), ("600337", "ST美克", "sh"), ("002168", "ST惠程", "sz"),
    ("600381", "*ST春天", "sh"), ("300147", "*ST香雪", "sz"), ("002542", "*ST中岩", "sz"),
    ("300027", "ST华谊", "sz"), ("300020", "ST银江", "sz"), ("600340", "*ST华幸", "sh"),
    ("600370", "*ST三房", "sh"),
    ("600165", "ST宁科", "sh"), ("600525", "ST长圆", "sh"),
    ("603843", "*ST正平", "sh"), ("603377", "ST东时", "sh"),
]

# 公告关键词: 核心=高置信直接命中; 辅助=配合风险状态
CORE_KW = ["重整", "预重整", "破产重整", "撤销退市风险警示", "撤销其他风险警示",
           "申请撤销风险警示", "撤销风险警示", "摘星", "摘帽"]
AUX_KW = ["资本公积转增", "重整投资人", "重整计划", "债务豁免", "重组", "保壳", "重大资产"]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
COOKIE_JAR = urllib.request.HTTPCookieProcessor()


# ---------------------------------------------------------------------------
def infer_market(code: str) -> str:
    c = code.strip()
    if c[:1] in ("6", "9") or c[:2] in ("68", "90"):
        return "sh"
    if c[:1] in ("4", "8"):
        return "bj"
    return "sz"


# ---------------------------------------------------------------------------
# 行情: 腾讯快照  (f[3]价 f[4]昨收 f[44]/f[45]市值(亿, 勿再除1e8))
# ---------------------------------------------------------------------------
def fetch_quote(code: str, market: str) -> dict:
    try:
        raw = urllib.request.urlopen(f"https://qt.gtimg.cn/q={market}{code}",
                                     timeout=10).read().decode("gbk", "ignore")
        f = raw.split('="', 1)[1].rstrip('";\n').split("~")
        price = float(f[3])
        prev = float(f[4]) if f[4] else price
        pct = round((price - prev) / prev * 100, 2) if prev else 0.0
        circ = float(f[44]) if len(f) > 44 and f[44] else None
        total = float(f[45]) if len(f) > 45 and f[45] else None
        return {"name": f[1], "code": code, "price": price, "prev": prev,
                "pct": pct, "circ_mv": circ, "total_mv": total}
    except Exception as e:
        log.warning("行情失败 %s%s: %s", market, code, e)
        return {}


# ---------------------------------------------------------------------------
# K线: 腾讯日K  (近 N 日高点回撤)
# ---------------------------------------------------------------------------
def fetch_drawdown(code: str, market: str, n: int = 30):
    url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?param={market}{code},day,,,{n},qfq")
    try:
        j = json.loads(urllib.request.urlopen(url, timeout=10).read().decode("utf-8", "ignore"))
        node = j["data"].get(f"{market}{code}") or j["data"].get(code, {})
        days = node.get("day") or node.get("qfqday") or []
        if not days:
            return None, None
        highs = [float(r[3]) for r in days if len(r) > 3]
        last = float(days[-1][2])
        mh = max(highs) if highs else last
        return mh, round((mh - last) / mh * 100, 2) if mh else 0.0
    except Exception as e:
        log.warning("K线失败 %s%s: %s", market, code, e)
        return None, None


# ---------------------------------------------------------------------------
# 公告源 1: 东方财富 datacenter-web
# ---------------------------------------------------------------------------
def _anns_eastmoney(code: str, start: str, end: str):
    url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_WEB_GG_LB"
           "&columns=ALL&pageSize=30&sortColumns=NOTICE_DATE&sortTypes=-1&source=WEB"
           f"&filter=(SECURITY_CODE%3D%22{code}%22)")
    try:
        j = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=12).read().decode("utf-8", "ignore"))
        if not j.get("success"):
            return None
        res = j.get("result")
        rows = (res.get("data") if isinstance(res, dict) else res) or []
        out = []
        for r in rows:
            d = (r.get("NOTICE_DATE") or "")[:10]
            if start <= d <= end:
                out.append((r.get("TITLE") or "", d))
        return out
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 公告源 2: 巨潮 hisAnnouncement  (需 cookie + 按 secCode 客户端过滤)
# ---------------------------------------------------------------------------
def _anns_cninfo(code: str, name: str, market: str, start: str, end: str):
    plate = {"sh": "sse", "sz": "szse", "bj": "bjse"}.get(market, "szse")
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = urllib.parse.urlencode({
        "stock_code": code, "stock_name": name, "plateId": plate, "date_range": "",
        "start_date": start, "end_date": end, "page_size": "30", "page_index": "0",
        "ann_type": "", "is_cx": ""}).encode()
    hdr = {"User-Agent": UA,
           "Referer": f"https://www.cninfo.com.cn/new/disclosure/stock?stockCode={code}",
           "X-Requested-With": "XMLHttpRequest",
           "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    try:
        opener = urllib.request.build_opener(COOKIE_JAR)
        raw = opener.open(urllib.request.Request(url, data=data, headers=hdr), timeout=12).read().decode("utf-8", "ignore")
        j = json.loads(raw)
        anns = j.get("announcements") or []
        if not isinstance(anns, list):
            return None
        out = []
        for a in anns:
            if a.get("secCode") != code:
                continue  # 巨潮接口不过滤时, 仅保留本股
            ts = a.get("announcementTime")
            if isinstance(ts, int):
                d = dt.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            else:
                d = (ts or "")[:10]
            if start <= d <= end:
                out.append((a.get("announcementTitle") or "", d))
        return out if out else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 公告源 3/4: 深交所 / 上交所 官方 (可用性随网络环境)
# ---------------------------------------------------------------------------
def _anns_szse(code: str, start: str, end: str):
    try:
        url = "https://www.szse.cn/api/disc/announcement/annQuery"
        data = urllib.parse.urlencode({"secode": code, "secName": "", "stockType": "",
                                        "channelCode": "", "bigCategory": "", "smallCategory": "",
                                        "pageSize": "30", "pageNum": "1", "random": "0.1"}).encode()
        hdr = {"User-Agent": UA, "Referer": "https://www.szse.cn/",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        j = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, data=data, headers=hdr), timeout=12).read().decode("utf-8", "ignore"))
        rows = j.get("data") or []
        return [(r.get("announcementTitle") or "", (r.get("announcementTime") or "")[:10]) for r in rows]
    except Exception:
        return None


def _anns_sse(code: str, start: str, end: str):
    try:
        url = (f"https://query.sse.com.cn/api/disc/info/getAnnInfoByCode?stockCode={code}"
               f"&fromDate={start}&toDate={end}&pageSize=30&pageNum=1&isPagination=true")
        j = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.sse.com.cn/"}),
            timeout=12).read().decode("utf-8", "ignore"))
        rows = (j.get("data") or [])
        return [(r.get("title") or r.get("announcementTitle") or "", (r.get("date") or r.get("noticeDate") or "")[:10]) for r in rows]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 多源聚合: 返回 (ann_list[(title,date)], source_name)
# ---------------------------------------------------------------------------
def fetch_announcements(code: str, name: str, market: str, days: int):
    end = dt.date.today()
    start = (end - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")
    for fn, src in [(_anns_eastmoney, "东财"), (_anns_cninfo, "巨潮"),
                    (_anns_szse, "深交所"), (_anns_sse, "上交所")]:
        try:
            if fn is _anns_eastmoney:
                res = fn(code, start, end_s)
            elif fn is _anns_cninfo:
                res = fn(code, name, market, start, end_s)
            elif fn is _anns_szse:
                res = fn(code, start, end_s) if market in ("sz", "bj") else None
            else:
                res = fn(code, start, end_s) if market == "sh" else None
            if res:
                return res, src
        except Exception:
            continue
    return [], "源不可用"


# ---------------------------------------------------------------------------
def risk_status(name: str):
    if "*ST" in name:
        return "退市风险警示(*ST)"
    if "ST" in name:
        return "其他风险警示(ST)"
    return "正常"


def is_st(name: str):
    return "ST" in name


# ---------------------------------------------------------------------------
def scan_one(code, name, market, args):
    q = fetch_quote(code, market)
    if not q:
        return {"code": code, "name": name, "alert": False, "watch": False,
                "reason": "行情获取失败", "ann_source": "-", "latest_sig": "-", "latest_sig_date": "-"}
    name = q.get("name") or name
    price, total_mv, pct = q.get("price"), q.get("total_mv"), q.get("pct")
    status = risk_status(name)

    low = []
    if price is not None and price <= args["price"]:
        low.append(f"低价(现价{price}≤{args['price']})")
    if total_mv is not None and total_mv <= args["mktcap"]:
        low.append(f"小市值(总市值{total_mv}亿≤{args['mktcap']}亿)")
    if args["kline"]:
        _, dd = fetch_drawdown(code, market, 30)
        if dd is not None and dd >= args["drop"]:
            low.append(f"超跌(近30日回撤{dd}%≥{args['drop']}%)")

    anns, src = fetch_announcements(code, name, market, args["days"])
    hit_core = [(d, t) for t, d in anns if any(k in t for k in CORE_KW)]
    hit_aux = [(d, t) for t, d in anns if any(k in t for k in AUX_KW)]

    has_progress = bool(hit_core) or (bool(hit_aux) and is_st(name))
    is_low = bool(low)

    if is_st(name) and is_low and hit_core:
        latest = hit_core[0]
        reason = "【强预警】" + " + ".join(low) + f" + 重整/摘星/摘帽公告:{latest[1]}({latest[0]})"
        alert, watch = True, False
    elif is_st(name) and is_low and hit_aux:
        latest = hit_aux[0]
        reason = "【强预警】" + " + ".join(low) + f" + 重组/保壳动作:{latest[1]}({latest[0]})"
        alert, watch = True, False
    elif is_st(name) and is_low:
        reason = ("【观察】" + " + ".join(low) +
                  " + ST状态隐含摘星/摘帽预期" +
                  (f" (公告源:{src}, 未命中重整词, 需人工回巨潮核验)" if src != "源不可用"
                   else " (公告源暂不可用, 需人工回巨潮核验)"))
        alert, watch = False, True
    else:
        reason = "未触发(非低位 或 非ST)"
        alert, watch = False, False

    latest_sig = (hit_core[0] if hit_core else (hit_aux[0] if hit_aux else None))
    return {"code": code, "name": name, "price": price, "pct": pct, "total_mv": total_mv,
            "status": status, "low": low, "alert": alert, "watch": watch, "reason": reason,
            "ann_source": src, "latest_sig": latest_sig[1] if latest_sig else "-",
            "latest_sig_date": latest_sig[0] if latest_sig else "-"}


# ---------------------------------------------------------------------------
def load_pool(path):
    if not path:
        return [(c, n, m) for c, n, m in DEFAULT_POOL]
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    pool = []
    for item in data:
        if isinstance(item, str):
            pool.append((item, "", infer_market(item)))
        elif isinstance(item, list):
            pool.append((item[0], item[1] if len(item) > 1 else "",
                         item[2] if len(item) > 2 else infer_market(item[0])))
        elif isinstance(item, dict):
            c = item.get("code") or item.get("symbol")
            pool.append((c, item.get("name") or "", item.get("market") or infer_market(c)))
    log.info("已加载股票池: %d 只", len(pool))
    return pool


# ---------------------------------------------------------------------------
def render(results, args, out_dir):
    alerts = [r for r in results if r.get("alert")]
    watches = [r for r in results if r.get("watch")]
    print("\n" + "=" * 80)
    print(f"  A股低位 ST/*ST 重整/摘星/摘帽预期 扫描  ({dt.date.today()})")
    print(f"  低位阈值: 价≤{args['price']}元 / 总市值≤{args['mktcap']}亿 / 近30日回撤≥{args['drop']}%")
    print(f"  公告回溯: {args['days']}天   扫描: {len(results)}只")
    print("=" * 80)

    def show(rows, tag):
        if not rows:
            print(f"\n[{tag}] 无")
            return
        print(f"\n[{tag}] {len(rows)} 只")
        for r in rows:
            print(f"  ● {r['name']}({r['code']})  现价:{r['price']}  涨跌:{r['pct']}%  "
                  f"总市值:{r['total_mv']}亿  状态:{r['status']}  [公告源:{r.get('ann_source')}]")
            print(f"      原因: {r['reason']}")
            if r.get("latest_sig") != "-":
                print(f"      信号公告: {r['latest_sig_date']} {r['latest_sig']}")

    show(alerts, "强预警 ALERT")
    show(watches, "观察 WATCH(低位+ST隐含预期)")
    print("\n" + "=" * 80)
    print("  免责: 程序化筛选非投资建议; ST/*ST 退市风险极高, 结论须回巨潮/交易所核验。")
    print("=" * 80)

    csv_path = os.path.join(out_dir, f"st_lowprice_alerts_{dt.date.today():%Y%m%d}.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["代码", "名称", "现价", "涨跌幅%", "总市值(亿)", "风险状态", "是否预警",
                    "触发原因", "最近信号公告", "公告日期", "公告源"])
        for r in results:
            w.writerow([r["code"], r["name"], r.get("price", "-"), r.get("pct", "-"),
                        r.get("total_mv", "-"), r.get("status", "-"),
                        "强预警" if r.get("alert") else ("观察" if r.get("watch") else "否"),
                        r.get("reason", "-"), r.get("latest_sig", "-"),
                        r.get("latest_sig_date", "-"), r.get("ann_source", "-")])
    log.info("CSV: %s", csv_path)
    return csv_path, alerts, watches


def render_html(results, args, out_dir):
    alerts = [r for r in results if r.get("alert")]
    rows = "".join(
        f"<tr><td>{r['code']}</td><td>{r['name']}</td><td>{r.get('price','-')}</td>"
        f"<td>{r.get('pct','-')}%</td><td>{r.get('total_mv','-')}</td><td>{r.get('status','-')}</td>"
        f"<td>{r.get('reason','-')}</td></tr>" for r in alerts) or "<tr><td colspan='7'>无</td></tr>"
    html = (f"""<html><head><meta charset="utf-8"><title>ST低位扫描</title><style>
body{{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#fff;color:#222;padding:24px}}
h1{{font-size:18px}}table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#f5f5f5}}
.box{{border:1px solid #e5b3b3;background:#fdf3f3;border-radius:10px;padding:16px;margin:12px 0}}
.warn{{color:#a32d2d;font-weight:600}}</style></head><body>
<h1>A股低位 ST/*ST 重整/摘星/摘帽预期 扫描 ({dt.date.today()})</h1>
<div class="box">低位阈值: 价≤{args['price']}元 / 总市值≤{args['mktcap']}亿 / 近30日回撤≥{args['drop']}%　公告回溯 {args['days']}天</div>
<p class="warn">强预警 {len(alerts)} 只。本页仅为公开信息程序化筛选, 非投资建议; ST/*ST 退市风险极高。</p>
<table><tr><th>代码</th><th>名称</th><th>现价</th><th>涨跌幅</th><th>总市值(亿)</th><th>风险状态</th><th>触发原因</th></tr>{rows}</table></body></html>""")
    path = os.path.join(out_dir, f"st_lowprice_alerts_{dt.date.today():%Y%m%d}.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    log.info("HTML: %s", path)
    return path


def main():
    ap = argparse.ArgumentParser(description="A股低位 ST/*ST 重整/摘星/摘帽预期扫描器")
    ap.add_argument("--pool", default="", help="股票池JSON")
    ap.add_argument("--price", type=float, default=3.0)
    ap.add_argument("--mktcap", type=float, default=50.0, help="设很大可关闭小市值筛选")
    ap.add_argument("--drop", type=float, default=25.0, help="近30日回撤阈值%")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--kline", action="store_true", default=True)
    ap.add_argument("--no-kline", dest="kline", action="store_false")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--html", action="store_true")
    ns = ap.parse_args()
    args = {"price": ns.price, "mktcap": ns.mktcap, "drop": ns.drop,
            "days": ns.days, "kline": ns.kline}
    os.makedirs(ns.out, exist_ok=True)

    pool = load_pool(ns.pool)
    results = []
    for code, name, market in pool:
        try:
            r = scan_one(code, name, market, args)
            results.append(r)
            log.info("扫描 %s %s -> %s [源:%s]", code, name or r.get("name", ""),
                     "强预警" if r.get("alert") else ("观察" if r.get("watch") else "否"),
                     r.get("ann_source"))
        except Exception as e:
            log.error("扫描 %s 异常: %s", code, e)
            results.append({"code": code, "name": name, "alert": False, "watch": False,
                            "reason": f"异常:{e}", "ann_source": "-", "latest_sig": "-", "latest_sig_date": "-"})
        time.sleep(0.3)
    csv_path, alerts, watches = render(results, args, ns.out)
    if ns.html:
        render_html(results, args, ns.out)
    log.info("完成: 强预警 %d / 观察 %d / 总计 %d", len(alerts), len(watches), len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
