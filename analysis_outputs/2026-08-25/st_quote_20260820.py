import urllib.request, re, json

codes = [
    ("sh600165","ST宁科"),("sh600525","ST长园"),("sz002822","ST中装"),
    ("sz300311","ST任子行"),("sh603268","ST松发"),("sz002759","ST天际"),
    ("sz000639","ST西王"),("sz002082","ST万邦"),("sz000711","ST京蓝"),
    ("sh603822","ST嘉澳"),("sz000793","ST华闻"),("sh603595","ST东尼"),
    ("sh600889","*ST京化"),("sz000908","ST景峰"),("sz002713","ST东易"),
    ("sz002289","ST宇顺"),("sz002305","ST南置"),("sh600568","ST中珠"),
    ("sh600358","ST联合"),("sh603007","ST花王"),
]

url = "http://qt.gtimg.cn/q=" + ",".join(c[0] for c in codes)
with urllib.request.urlopen(url, timeout=15) as r:
    raw = r.read().decode("gbk", errors="ignore")

rows = []
for line in raw.split(";"):
    line = line.strip()
    if not line or "=" not in line:
        continue
    m = re.search(r'="(.+)"', line)
    if not m:
        continue
    f = m.group(1).split("~")
    if len(f) < 45:
        continue
    name = f[1]; code = f[2]; price = f[3]; prev = f[4]
    chg = f[31]; chgpct = f[32]; turnover = f[33]
    float_cap = f[36]; total_cap = f[37]; pb = f[38]
    t = f[30]
    rows.append({
        "name": name, "code": code, "price": price, "prev": prev,
        "chgpct": chgpct, "turnover": turnover,
        "float_cap": float_cap, "total_cap": total_cap, "pb": pb, "time": t
    })

# 市值单位换算：原值单位为万元
def to_yi(v):
    try:
        return round(float(v)/10000, 2)
    except:
        return v

print(f"{'名称':<10}{'代码':<10}{'现价':>8}{'涨跌幅%':>9}{'换手%':>8}{'流通市值(亿)':>14}{'总市值(亿)':>12}{'PB':>7}{'时间'}")
for r in rows:
    print(f"{r['name']:<10}{r['code']:<10}{r['price']:>8}{r['chgpct']:>9}{r['turnover']:>8}{to_yi(r['float_cap']):>14}{to_yi(r['total_cap']):>12}{r['pb']:>7}{r['time']}")

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_quote_20260820.json","w",encoding="utf-8") as fp:
    json.dump(rows, fp, ensure_ascii=False, indent=2)
print("\n已保存 quotes -> st_quote_20260820.json")
