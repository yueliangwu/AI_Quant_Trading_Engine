import requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
   "Referer":"https://gu.qq.com/"}
# 腾讯日K (sz000711)
r=requests.get("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz000711,day,,,80,qfq",headers=H,timeout=20)
print("TX_KLINE", r.status_code, len(r.text), r.text[:160])
# 东财资金流 push2
r2=requests.get("https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=101&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&secid=0.000711",headers=H,timeout=20)
print("EM_FLOW", r2.status_code, len(r2.text), r2.text[:160])
# 东财实时快照
r3=requests.get("https://push2.eastmoney.com/api/qt/stock/get?secid=0.000711&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f59,f60,f168,f169,f170",headers=H,timeout=20)
print("EM_SNAP", r3.status_code, len(r3.text), r3.text[:160])
