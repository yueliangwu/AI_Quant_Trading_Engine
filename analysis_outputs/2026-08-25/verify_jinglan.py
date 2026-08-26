import urllib.request, json, time

codes = ["sz000711", "sz301217", "sz002340", "sh600961", "sh600459", "sh600392"]
url = "https://qt.gtimg.cn/q=" + ",".join(codes)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req, timeout=15).read().decode("gbk", "ignore")
print("code | name | price | chg% | 换手% | 总市值(亿) | 市盈(TTM)")
for line in raw.strip().split(";"):
    if not line.strip():
        continue
    try:
        key, payload = line.split("=", 1)
        payload = payload.strip().strip('"')
        f = payload.split("~")
        code = f[2]; name = f[1]; price = f[3]; chg = f[32]; turn = f[38]
        mcap = f[45]; pe = f[39]
        print(f"{code} | {name} | {price} | {chg} | {turn} | {mcap} | {pe}")
    except Exception as e:
        print("parse err:", e)
