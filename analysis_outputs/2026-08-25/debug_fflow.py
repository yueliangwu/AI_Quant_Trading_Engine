# -*- coding: utf-8 -*-
import json, urllib.request, ssl, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://quote.eastmoney.com/"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode("utf-8","ignore")

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_data_20260825.json", encoding="utf-8") as f:
    D = json.load(f)

# raw day fflow
for key in ["longda","jinglan"]:
    sid = "0.002726" if key=="longda" else "0.000711"
    print("="*60, key)
    # re-fetch day with lmt=0
    url = (f"https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid={sid}"
           f"&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65")
    try:
        d = json.loads(get(url))
        kls = d.get("data",{}).get("klines",[])
        print(f"  day klines count={len(kls)}")
        for x in kls[:5]:
            print("   ", x)
        print("   ...")
        for x in kls[-3:]:
            print("   ", x)
    except Exception as e:
        print("  ERR", e)
    # raw minute: print first 3 and last 3
    m = D[key]["em_fflow_min"]
    if isinstance(m, list):
        print(f"  min count={len(m)}")
        for x in m[:3]: print("   M", x)
        for x in m[-3:]: print("   M", x)
    else:
        print("  min FAIL", m)
