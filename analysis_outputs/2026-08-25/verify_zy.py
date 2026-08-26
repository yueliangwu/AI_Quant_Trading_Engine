import urllib.request, re, json

codes = ["sz002542"]
url = "https://qt.gtimg.cn/q=" + ",".join(codes)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
try:
    raw = urllib.request.urlopen(req, timeout=10).read().decode("gbk", "ignore")
    print(raw)
except Exception as e:
    print("ERR", e)
