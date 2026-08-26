# -*- coding: utf-8 -*-
"""重验13只ST/*ST实时行情与状态（基于2026.7.6新规口径）"""
import urllib.request, json, time

# 原11只 + ST京蓝000711 + ST人福600079
stocks = [
    ("000838","*ST发展"),("002726","ST龙大"),("002168","ST惠程"),("002542","*ST中岩"),
    ("300027","ST华谊"),("300147","*ST香雪"),("600337","ST美克"),("600340","*ST华幸"),
    ("600370","*ST三房"),("300020","ST银江"),("600381","*ST春天"),
    ("000711","ST京蓝"),("600079","ST人福"),
]

# 板块前缀：深交所 0/3 -> sz, 上交所 6 -> sh
def prefix(code):
    return "sh" if code.startswith("6") else "sz"

codes = ",".join(f"{prefix(c)}{c}" for c,_ in stocks)
url = f"https://qt.gtimg.cn/q={codes}"

def fetch():
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://gu.qq.com/"})
    return urllib.request.urlopen(req, timeout=15).read().decode("gbk", "ignore")

raw = fetch()
# 板块涨跌幅档位：主板(沪600/605, 深000/001/002/003) ST/*ST=10%; 创业板(300) ST/*ST=20%
def limit_band(code, name):
    if code.startswith("30") or code.startswith("688"):
        return "20% (创业板/科创板ST)"
    return "10% (主板ST)"

result = []
for line in raw.strip().split(";"):
    if not line.strip(): continue
    try:
        head, body = line.split("=",1)
    except ValueError:
        continue
    body = body.strip().strip('"')
    if not body: continue
    f = body.split("~")
    code = head.replace("v_","").replace("sh","").replace("sz","")
    name = f[1]
    price = float(f[3]) if f[3] else 0.0
    prev_close = float(f[4]) if f[4] else 0.0
    pct = float(f[32]) if len(f)>32 and f[32] else 0.0
    turnover = float(f[38]) if len(f)>38 and f[38] else 0.0
    # 市值字段 f[44]=流通(亿) f[45]=总市值(亿) 已是"亿"单位
    float_cap = float(f[44]) if len(f)>44 and f[44] else 0.0
    total_cap = float(f[45]) if len(f)>45 and f[45] else 0.0
    band = limit_band(code, name)
    result.append({
        "code": code, "name": name, "price": price, "prev_close": prev_close,
        "pct": pct, "turnover": turnover, "float_cap": float_cap,
        "total_cap": total_cap, "band": band,
        "is_st": ("ST" in name),
    })

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st13_v2.json","w",encoding="utf-8") as fp:
    json.dump(result, fp, ensure_ascii=False, indent=2)

for r in result:
    print(f"{r['code']} {r['name']:8s} 现价={r['price']:.2f} 涨跌幅={r['pct']:+.2f}% "
          f"换手={r['turnover']:.2f}% 总市值={r['total_cap']:.2f}亿 档位={r['band']} ST={r['is_st']}")
