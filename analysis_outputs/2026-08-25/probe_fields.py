# -*- coding: utf-8 -*-
import urllib.request
url = "https://qt.gtimg.cn/q=sh600079,sz000711,sz002726"
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://stockapp.finance.qq.com/"})
raw = urllib.request.urlopen(req, timeout=15).read().decode("gbk", errors="ignore")
for line in raw.strip().split(";\n"):
    line=line.strip()
    if "=" not in line: continue
    k,v=line.split("=",1)
    v=v.strip().strip('"')
    f=v.split("~")
    print("KEY",k,"N=",len(f))
    print("  [38-57]:", f[38:58])
    print("  name/code/price/chg/turn/pe:", f[1], f[2], f[3], f[32], f[38], f[39])
