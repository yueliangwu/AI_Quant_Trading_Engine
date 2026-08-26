# -*- coding: utf-8 -*-
import json, urllib.request, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get(url, timeout=15, retries=2):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://finance.qq.com/"
            })
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            last = e
            time.sleep(1)
    return None

def fetch_kline(code, market="sz", n=80):
    # qfq daily kline
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},day,,,{n},qfq"
    txt = get(url)
    if not txt: return None
    try:
        d = json.loads(txt)
        node = d["data"][market+code]
        key = "qfqday" if "qfqday" in node else ("day" if "day" in node else None)
        if not key: return None
        rows = node[key]
        out = []
        for r in rows:
            # [date, open, close, high, low, volume, ...]
            out.append({
                "date": r[0], "open": float(r[1]), "close": float(r[2]),
                "high": float(r[3]), "low": float(r[4]), "vol": float(r[5])
            })
        return out
    except Exception as e:
        return {"error": str(e), "raw": txt[:300]}

def fetch_snapshot(codes):
    # codes like sz002726
    q = "/".join(codes)
    url = f"https://qt.gtimg.cn/q={q}"
    txt = get(url)
    if not txt: return None
    res = {}
    for line in txt.split(";"):
        line = line.strip()
        if not line or "=" not in line: continue
        name, val = line.split("=", 1)
        val = val.strip().strip('"')
        parts = val.split("~")
        code = name.replace("v_", "").strip()
        if len(parts) < 50:
            res[code] = {"raw": val[:200]}
            continue
        try:
            res[code] = {
                "name": parts[1], "code": parts[2],
                "price": float(parts[3]), "prev_close": float(parts[4]),
                "open": float(parts[5]),
                "volume_hand": float(parts[6]),  # 手
                "out": float(parts[7]), "in": float(parts[8]),
                "bid1": float(parts[9]), "bid1v": float(parts[10]),
                "time": parts[30], "chg": float(parts[31]), "pct": float(parts[32]),
                "high": float(parts[33]), "low": float(parts[34]),
                "amp_pct": float(parts[37]), "turnover": float(parts[38]),
                "pe": parts[39], "circ_mv": float(parts[44]), "total_mv": float(parts[45]),
                "pb": parts[46], "wb": parts[47],  # 委比/量比some
                "avg": float(parts[49]) if parts[49] else None,
            }
        except Exception as e:
            res[code] = {"parse_error": str(e), "raw": val[:200]}
    return res

def fetch_em_fflow_day(secid, n=30):
    # EastMoney daily capital flow
    url = (f"https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
           f"?lmt={n}&klt=101&secid={secid}"
           f"&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65")
    txt = get(url, timeout=15)
    if not txt: return {"error": "no_response"}
    try:
        d = json.loads(txt)
        if d.get("data") and d["data"].get("klines"):
            return [x.split(",") for x in d["data"]["klines"]]
        return {"error": "empty", "json": txt[:200]}
    except Exception as e:
        return {"error": str(e), "raw": txt[:200]}

def fetch_em_fflow_min(secid, klt=1, n=240):
    url = (f"https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
           f"?lmt={n}&klt={klt}&secid={secid}"
           f"&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65")
    txt = get(url, timeout=15)
    if not txt: return {"error": "no_response"}
    try:
        d = json.loads(txt)
        if d.get("data") and d["data"].get("klines"):
            return [x.split(",") for x in d["data"]["klines"]]
        return {"error": "empty", "json": txt[:200]}
    except Exception as e:
        return {"error": str(e), "raw": txt[:200]}

def fetch_tx_minute(code, market="sz"):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={market}{code}"
    txt = get(url)
    if not txt: return {"error": "no_response"}
    try:
        d = json.loads(txt)
        qt = d["data"][market+code]["data"]
        # qt has "data" list of [price, volume(手), time?] and "date"]
        return qt
    except Exception as e:
        return {"error": str(e), "raw": txt[:200]}

STOCKS = {
    "longda": {"code": "002726", "market": "sz", "secid": "0.002726"},
    "jinglan": {"code": "000711", "market": "sz", "secid": "0.000711"},
}

out = {"fetch_time": time.strftime("%Y-%m-%d %H:%M:%S")}
for key, s in STOCKS.items():
    c, m, sid = s["code"], s["market"], s["secid"]
    print(f"=== {key} {c} ===")
    kline = fetch_kline(c, m, 90)
    snap = fetch_snapshot([m+c])
    em_day = fetch_em_fflow_day(sid, 30)
    em_min = fetch_em_fflow_min(sid, 1, 240)
    tx_min = fetch_tx_minute(c, m)
    out[key] = {
        "kline": kline if not isinstance(kline, dict) else kline,
        "snapshot": snap.get(m+c) if snap else None,
        "em_fflow_day": em_day,
        "em_fflow_min": em_min,
        "tx_minute": tx_min,
    }
    # quick status
    if isinstance(kline, list):
        print(f"  kline: {len(kline)} bars, last={kline[-1]['date']} close={kline[-1]['close']}")
    else:
        print(f"  kline: FAILED {kline}")
    print(f"  snap: {snap.get(m+c,{}).get('name') if snap else 'NONE'} price={snap.get(m+c,{}).get('price') if snap else 'NONE'}")
    emd = "OK" if isinstance(em_day, list) else f"FAIL {em_day}"
    emm = "OK" if isinstance(em_min, list) else f"FAIL {em_min}"
    print(f"  em_fflow_day: {emd}  em_fflow_min: {emm}")

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_data_20260825.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("SAVED tech_data_20260825.json")
