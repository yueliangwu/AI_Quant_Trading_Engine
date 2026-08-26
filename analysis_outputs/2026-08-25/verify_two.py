import urllib.request, json

codes = ["sz002726", "sz000711"]
url = "https://qt.gtimg.cn/q=" + ",".join(codes)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req, timeout=15).read().decode("gbk")

for line in raw.strip().split(";"):
    if not line.strip():
        continue
    name, rest = line.split("=", 1)
    rest = rest.strip().rstrip('"').lstrip('"')
    f = rest.split("~")
    print("=" * 60)
    print("代码:", f[2], "名称:", f[1])
    print("今日开盘:", f[5], "昨收:", f[4], "现价:", f[3])
    print("今日最高:", f[33], "今日最低:", f[34])
    print("涨跌幅%:", f[32], "涨跌额:", f[31])
    print("成交量(手):", f[36], "成交额(元):", f[37], "换手%:", f[38])
    print("总市值(亿):", f[45], "流通市值(亿):", f[44])
    print("市盈率TTM:", f[39], "市净率:", f[46])
