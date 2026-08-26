import urllib.request, json
url = "https://web.ifzq.gtimg.cn/appstock/app/stockinfo/get?_var=stockinfo&code=sh600165"
with urllib.request.urlopen(url, timeout=10) as r:
    txt = r.read().decode("utf-8")
print("RAW head:", txt[:120])
if txt.startswith("stockinfo="):
    txt = txt[len("stockinfo="):]
d = json.loads(txt)
print("top keys:", list(d.keys()))
print("data type:", type(d["data"]), "data keys:", list(d["data"].keys()) if isinstance(d["data"],dict) else d["data"][:200])
