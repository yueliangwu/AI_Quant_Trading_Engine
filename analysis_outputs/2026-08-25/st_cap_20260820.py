import urllib.request, json

codes = {
    "1.600165":"ST宁科","1.600525":"ST长园","0.002822":"ST中装","0.300311":"ST任子行",
    "1.603268":"松发股份","0.002759":"ST天际","0.000639":"ST西王","0.002082":"ST万邦",
    "0.000711":"ST京蓝","1.603822":"ST嘉澳","0.000793":"ST华闻","1.603595":"ST东尼",
    "1.600889":"*ST京化","0.000908":"石药景峰","0.002713":"东易日盛","0.002289":"宇顺电子",
    "0.002305":"*ST南置","1.600568":"ST中珠","1.600358":"国旅联合","1.603007":"顺景科技",
}

hdr = {"User-Agent":"Mozilla/5.0","Referer":"https://quote.eastmoney.com/"}
url = "https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f43,f84,f85,f116,f117,f162&invt=2&fltt=2"

def yi(v):
    try: return round(float(v)/1e8,2)
    except: return None

rows=[]
for s in codes:
    u=url.format(secid=s)
    try:
        req=urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=10) as r:
            d=json.loads(r.read().decode("utf-8"))
        dd=d.get("data") or {}
        ts=dd.get("f84"); ts_yi=round(float(ts)/1e8,2) if ts else None
        rows.append({"name":dd.get("f58"),"code":dd.get("f57"),"price":dd.get("f43"),
                     "total_cap":yi(dd.get("f116")),"float_cap":yi(dd.get("f117")),
                     "total_shares":ts_yi,"pb":dd.get("f162")})
    except Exception as e:
        rows.append({"secid":s,"name":codes[s],"error":str(e)[:60]})

print(f"{'名称':<10}{'代码':<9}{'现价':>8}{'总市值(亿)':>12}{'流通市值(亿)':>13}{'总股本(亿股)':>12}{'PB':>7}")
for r in rows:
    if "error" in r:
        print(f"{r['name']:<10}{r.get('code',''):<9}{'--':>8}  ERR {r['error']}"); continue
    print(f"{r['name']:<10}{r['code']:<9}{str(r['price']):>8}{str(r['total_cap']):>12}{str(r['float_cap']):>13}{str(r['total_shares']):>12}{str(r['pb']):>7}")

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_cap_20260820.json","w",encoding="utf-8") as fp:
    json.dump(rows,fp,ensure_ascii=False,indent=2)
print("\n保存 caps -> st_cap_20260820.json")
