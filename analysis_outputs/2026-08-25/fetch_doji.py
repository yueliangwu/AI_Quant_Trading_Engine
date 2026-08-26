# -*- coding: utf-8 -*-
import json, urllib.request, ssl, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def get(url, timeout=15, retries=2):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://finance.qq.com/"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read().decode("utf-8","ignore")
        except Exception as e:
            last=e; time.sleep(1)
    return None

def fetch_kline(code, market="sh", n=45):
    url=f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},day,,,{n},qfq"
    t=get(url)
    if not t: return None
    try:
        d=json.loads(t); node=d["data"][market+code]
        key="qfqday" if "qfqday" in node else ("day" if "day" in node else None)
        if not key: return None
        return [{"date":r[0],"open":float(r[1]),"close":float(r[2]),"high":float(r[3]),"low":float(r[4]),"vol":float(r[5])} for r in node[key]]
    except Exception as e:
        return {"err":str(e)}

def fetch_snapshot(code, market="sh"):
    t=get(f"https://qt.gtimg.cn/q={market}{code}")
    if not t: return None
    for line in t.split(";"):
        if "=" in line:
            parts=line.split("=",1)[1].strip().strip('"').split("~")
            if len(parts)>=35:
                return {"name":parts[1],"price":float(parts[3]),"prev":float(parts[4]),"open":float(parts[5]),
                        "high":float(parts[33]),"low":float(parts[34]),"pct":float(parts[32]),
                        "turn":parts[38],"status":parts[0]}
    return None

stocks={"changyuan":"600525","ningke":"600165"}
out={}
for k,c in stocks.items():
    print("="*60,k,c)
    kl=fetch_kline(c,"sh",45)
    snap=fetch_snapshot(c,"sh")
    out[k]={"kline":kl,"snap":snap}
    if snap: print(f"  快照: {snap['name']} 现价={snap['price']} 涨={snap['pct']}% 状态字段={snap['status']} 换手={snap['turn']}")
    else: print("  快照获取失败")
    if isinstance(kl,list):
        print(f"  K线 {len(kl)} 根, 末日={kl[-1]['date']}")
        for b in kl[-12:]:
            o,bc,h,l,v=b["open"],b["close"],b["high"],b["low"],b["vol"]
            body=abs(bc-o); rng=h-l
            doji = body<=0.005 or (rng>0 and body/rng<0.18)
            up = bc>=o
            us=h-max(o,bc); ls=min(o,bc)-l
            shape = "十字星" if doji else ("阳" if up else "阴")
            print(f"   {b['date']} 开{o:.2f} 收{bc:.2f} 高{h:.2f} 低{l:.2f} 量{v/1e4:.1f}万手 实体{body:.2f} 上影{us:.2f} 下影{ls:.2f} -> {shape}{' [长上影]' if us>body*2.5 and not doji else ''}{' [长下影]' if ls>body*2.5 and not doji else ''}")
    else:
        print("  K线失败", kl)

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/doji_data_20260825.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("SAVED")
