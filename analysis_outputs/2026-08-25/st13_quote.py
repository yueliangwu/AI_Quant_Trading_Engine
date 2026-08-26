# -*- coding: utf-8 -*-
"""批量拉取全部13只ST/*ST实时行情快照 -> 输出JSON(仅写Temp,不碰项目目录)"""
import urllib.request, json

# 原11只(截图) + ST京蓝(000711) + ST人福(600079)
names = {
    "sz000838": "ST发展", "sz002726": "ST龙大", "sz002168": "ST惠程",
    "sz002542": "ST中岩", "sz300027": "ST华谊", "sz300147": "ST香雪",
    "sh600337": "ST美克", "sh600340": "ST华幸", "sh600370": "ST三房",
    "sz300020": "ST银江", "sh600381": "ST春天", "sz000711": "ST京蓝",
    "sh600079": "ST人福",
}
# 重组/重整驱动(来自之前检索+本次新股检索)
driver = {
    "sz000838": "重整投资协议已签,景行新能入主(确定性高)",
    "sz002726": "27家投资人报名+莱阳国资代偿转债,重整预期最热",
    "sz002168": "二债会通过重整计划草案,程序推进快",
    "sz002542": "成都国资背景+低空概念,仅拟申请预重整",
    "sz300027": "影视IP知名,七年累亏82亿,重整投资人未定",
    "sz300147": "广药资本中选,预重整四次延期逾期",
    "sh600337": "产投协议已签,万德溙AI算力铜缆跨界",
    "sh600340": "债务重组规模大,净资产缺口-177亿",
    "sh600370": "江阴国资入主预期,非标审计+股权拍卖",
    "sz300020": "智慧城市主业还在,三重ST,违规担保未解",
    "sh600381": "营收踩线达标,摘星摘帽申请进入交易所终审",
    "sz000711": "中报扭亏(铟资源化),拟更名铟靶新材申请摘帽",
    "sh600079": "招商局入主,违规整改完,2026.12期满可申摘帽",
}
url = "https://qt.gtimg.cn/q=" + ",".join(names.keys())
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://stockapp.finance.qq.com/"})
raw = urllib.request.urlopen(req, timeout=15).read().decode("gbk", errors="ignore")

out = []
for line in raw.strip().split(";\n"):
    line=line.strip()
    if "=" not in line: continue
    k,v=line.split("=",1); v=v.strip().strip('"')
    if not v: continue
    f=v.split("~")
    if len(f) < 46: continue
    code=f[2]; name=f[1]
    try: price=float(f[3])
    except: price=None
    try: chg=float(f[32])
    except: chg=None
    try: turn=float(f[38])
    except: turn=None
    try: pe=float(f[39])
    except: pe=None
    try: circ_cap=float(f[44])   # 流通市值(亿)
    except: circ_cap=None
    try: total_cap=float(f[45])  # 总市值(亿)
    except: total_cap=None
    # ST状态判定
    status = "ST" if name.startswith("ST") else ("*ST" if name.startswith("*ST") else "正常")
    out.append({
        "code": code, "name": name, "status": status,
        "price": price, "chg_pct": chg, "turnover": turn,
        "pe_ttm": pe, "total_cap_yi": total_cap, "circ_cap_yi": circ_cap,
        "driver": driver.get(k, ""),
    })

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st13_data.json","w",encoding="utf-8") as fp:
    json.dump(out, fp, ensure_ascii=False, indent=2)

print(f"{'实时名':<10}{'代码':<9}{'状态':<5}{'现价':>8}{'涨跌%':>8}{'换手%':>8}{'总市值亿':>11}{'流通亿':>10}{'PE':>9}")
print("-"*78)
for r in out:
    print(f"{r['name']:<10}{r['code']:<9}{r['status']:<5}{r['price']:>8.2f}{r['chg_pct']:>8.2f}{r['turnover']:>8.2f}{r['total_cap_yi']:>11.2f}{r['circ_cap_yi']:>10.2f}{str(r['pe_ttm']):>9}")
print("\nJSON已写出: st13_data.json, 共", len(out), "只")
