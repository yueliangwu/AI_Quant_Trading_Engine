import requests, time
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
   "Referer":"https://gu.qq.com/","Accept":"*/*"}
# 1) 腾讯日K（单独）
r=requests.get("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz000711,day,,,5,qfq",headers=H,timeout=20)
print("TXK", r.status_code, len(r.text), r.text[:200])
time.sleep(3)
# 2) 东方财富历史域名 资金流 kline
r2=requests.get("https://push2his.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=101&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&secid=0.000711",headers=H,timeout=20)
print("EMH_FLOW", r2.status_code, len(r2.text), r2.text[:160])
