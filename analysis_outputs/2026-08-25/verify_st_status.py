import urllib.request, re

# 重新核验全部候选的实时显示名（带不带 ST/*ST 前缀即当前是否被实施风险警示）
codes = [
    ("sh600165","ST宁科"),("sh600525","ST长园"),("sz002822","ST中装"),
    ("sz300311","ST任子行"),("sz002759","ST天际"),("sz000639","ST西王"),
    ("sz002082","ST万邦"),("sz000711","ST京蓝"),("sh603822","ST嘉澳"),
    ("sz000793","ST华闻"),("sh603595","ST东尼"),("sh600889","*ST京化"),
    ("sz002305","*ST南置"),("sh600568","ST中珠"),
    # 参照组
    ("sh603268","松发"),("sz000908","景峰"),("sz002713","东易"),
    ("sz002289","宇顺"),("sh600358","国旅"),("sh603007","顺景"),
]

url = "http://qt.gtimg.cn/q=" + ",".join(c[0] for c in codes)
with urllib.request.urlopen(url, timeout=15) as r:
    raw = r.read().decode("gbk", errors="ignore")

print(f"{'代码':<10}{'实时显示名':<12}{'当前ST状态'}")
for c in codes:
    m = re.search(r'%s="([^"]+)"' % c[0], raw)
    if not m:
        print(c[0], "无数据"); continue
    f = m.group(1).split("~")
    name = f[1]
    is_st = ("ST" in name.upper()) or ("*ST" in name)
    status = "❌已摘帽/非ST" if not is_st else ("*ST(退市风险)" if name.startswith("*") else "ST(其他风险)")
    print(f"{c[0][2:]:<10}{name:<12}{status}")
