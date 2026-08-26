# -*- coding: utf-8 -*-
import urllib.request, json

def get(url, enc="gbk"):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://stockapp.finance.qq.com/"})
    return urllib.request.urlopen(req, timeout=15).read().decode(enc, errors="ignore")

# 1) 实时快照
q = get("https://qt.gtimg.cn/q=sz002726")
for line in q.strip().split(";\n"):
    if "=" not in line: continue
    f = line.split("=",1)[1].strip().strip('"').split("~")
    if len(f) < 46: continue
    name, code, price, chg = f[1], f[2], f[3], f[32]
    turn, pe = f[38], f[39]
    total, circ = f[45], f[44]
    print(f"实时: {name} {code} 现价={price} 涨跌={chg}% 换手={turn}% PE={pe} 总市值={total}亿 流通={circ}亿")

# 2) 近期日K(前复权), 取最近40根
k = get("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz002726,day,,,40,qfq", enc="utf-8")
try:
    data = json.loads(k)
    kl = data["data"]["sz002726"]["qfqday"]
    # kl: [date, open, close, high, low, volume]
    closes = [float(x[2]) for x in kl]
    first, last = closes[0], closes[-1]
    # 找区间最低/最高
    low = min(closes); high = max(closes)
    low_i = closes.index(low); high_i = closes.index(high)
    print(f"\n近{len(kl)}交易日: 首={kl[0][0]}收{first:.2f} → 末={kl[-1][0]}收{last:.2f}")
    print(f"区间最低={low:.2f}({kl[low_i][0]}) 区间最高={high:.2f}({kl[high_i][0]})")
    print(f"从区间最低到当前涨幅 = {(last/low-1)*100:.1f}%")
    print(f"从区间首日到当前涨幅 = {(last/first-1)*100:.1f}%")
    print("\n最近10日(日期 收 涨):")
    for x in kl[-10:]:
        c = float(x[2])
        op = float(x[1])
        pct = (c/op-1)*100
        print(f"  {x[0]} 收{c:.2f} 开{op:.2f} 日内{pct:+.1f}%")
except Exception as e:
    print("K线解析失败:", e)
    print(k[:300])
