import urllib.request, re, json, time

# 非创业板、重整进行中(S2-S5)且不在原13只清单的主板候选
codes = {
    "sh600491": "ST龙元",
    "sz002634": "*ST棒杰",
    "sz000669": "ST金鸿",
    "sz002360": "ST同德",
    "sz002528": "*ST英飞",
    "sh603843": "*ST正平",
    "sh600537": "*ST亿晶",
    "sz002620": "*ST瑞和",
    "sh603377": "ST东时",
    "sz000826": "*ST启环",
}

def get(url, enc="gbk"):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://gu.qq.com/"})
    return urllib.request.urlopen(req, timeout=15).read().decode(enc, "ignore")

results = {}
# 1) 快照
q = "https://qt.gtimg.cn/q=" + ",".join(codes.keys())
raw = get(q)
snap = {}
for line in raw.split(";"):
    line = line.strip()
    if not line.startswith("v_"):
        continue
    code = line[2:line.index("=")]
    body = line[line.index('"')+1:line.rindex('"')]
    f = body.split("~")
    snap[code] = f

# 2) 近60日K线算阶段高低
for code in codes:
    time.sleep(0.2)
    kurl = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,70,qfq"
    try:
        kd = json.loads(get(kurl, "utf-8"))
        node = kd["data"][code]
        kline = node.get("qfqday") or node.get("day") or []
        closes = [float(r[2]) for r in kline]
        lows = [float(r[4]) for r in kline]
        highs = [float(r[3]) for r in kline]
        min_low = min(lows)
        max_high = max(highs)
        min_close = min(closes)
        results[code] = {
            "name": snap[code][1],
            "price": float(snap[code][3]),
            "chg_pct": float(snap[code][32]) if len(snap[code])>32 and snap[code][32] else 0.0,
            "mktcap_yi": float(snap[code][45]) if snap[code][45] else 0.0,
            "k60_minlow": round(min_low,3),
            "k60_maxhigh": round(max_high,3),
            "k60_minclose": round(min_close,3),
            "up_from_minclose_pct": round((float(snap[code][3])/min_close-1)*100,1),
            "drawdown_from_maxhigh_pct": round((float(snap[code][3])/max_high-1)*100,1),
            "kcount": len(kline),
        }
    except Exception as e:
        results[code] = {"name": snap[code][1] if code in snap else "?", "error": str(e)}

print(json.dumps(results, ensure_ascii=False, indent=2))
with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_restructure_low.json","w",encoding="utf-8") as fp:
    json.dump(results, fp, ensure_ascii=False, indent=2)
