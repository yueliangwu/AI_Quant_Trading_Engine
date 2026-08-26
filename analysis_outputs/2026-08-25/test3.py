import requests, time
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36","Referer":"https://finance.sina.com.cn/","Accept":"*/*"}
# 腾讯K线结构确认
r=requests.get("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz000711,day,,,5,qfq",headers={"User-Agent":"Mozilla/5.0","Referer":"https://gu.qq.com/"},timeout=20)
print("TXK",r.status_code,len(r.text))
try:
    d=r.json()["data"]["sz000711"]; key="qfqday" if "qfqday" in d else "day"
    print("KEY",key,"sample",d[key][-2:])
except Exception as e:
    print("TXK parse err",repr(e), r.text[:200])
time.sleep(2)
# 新浪资金流（当日）
r2=requests.get("https://money.finance.sina.com.cn/q/api/json_v2.php/CN_MarketData.getMoneyFlow?symbol=sz000711",headers=H,timeout=20)
print("SINA_FLOW",r2.status_code,len(r2.text),r2.text[:400])
