#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ST京蓝(000711)/哈药股份(600664) 技术面：腾讯日K + 腾讯实时快照。仅存 Temp。资金流分项由检索补充。"""
import os, json, time, requests
import pandas as pd, numpy as np
OUT = r"C:\Users\EDY\AppData\Local\Temp\wb_analysis"
os.makedirs(OUT, exist_ok=True)
H = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36","Referer":"https://gu.qq.com/","Accept":"*/*"}

def get_json(url, tag="", retries=4):
    for i in range(retries):
        try:
            r=requests.get(url,headers=H,timeout=25)
            if r.status_code!=200: print(f"[{tag}] HTTP {r.status_code}"); time.sleep(2); continue
            return r.json()
        except Exception as e:
            print(f"[ERR]{tag}{e}"); time.sleep(3)
    return None

def get_text(url, tag="", retries=4):
    for i in range(retries):
        try:
            r=requests.get(url,headers=H,timeout=25)
            if r.status_code!=200: time.sleep(2); continue
            return r.text
        except Exception as e:
            print(f"[ERR]{tag}{e}"); time.sleep(3)
    return None

def kline(tc):
    j=get_json(f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tc},day,,,400,qfq","kline")
    if not j or "data" not in j: return None
    d=j["data"][tc]; key="qfqday" if "qfqday" in d else "day"
    return d[key]

def snap(tc):
    t=get_text(f"https://qt.gtimg.cn/q={tc}","snap")
    if not t: return {}
    seg=t.split('"')[1].split("~")
    def f(i,cast=float,default=None):
        try: return cast(seg[i])
        except: return default
    return {"name":seg[1],"code":seg[2],"price":f(3),"prev":f(4),"open":f(5),
            "volume_hand":f(6),"amount_wan":f(37),"turnover":f(38),"high":f(33),"low":f(34)}

def analyze(tc):
    tk=kline(tc); time.sleep(1.5); sp=snap(tc)
    rows=[]
    for it in tk:
        rows.append({"日期":it[0],"开盘":float(it[1]),"收盘":float(it[2]),"最高":float(it[3]),"最低":float(it[4]),"成交量(手)":float(it[5])})
    df=pd.DataFrame(rows)
    df["涨跌幅%"]=(df["收盘"].pct_change()*100).fillna(0)
    for w in (5,10,20,60): df[f"MA{w}"]=df["收盘"].rolling(w).mean()
    ma20=df["收盘"].rolling(20).mean(); sd20=df["收盘"].rolling(20).std()
    df["BOLL_UP"]=ma20+2*sd20; df["BOLL_LOW"]=ma20-2*sd20
    df["VOL_MA5"]=df["成交量(手)"].rolling(5).mean(); df["VOL_MA10"]=df["成交量(手)"].rolling(10).mean()
    last=df.iloc[-1]; prev=df.iloc[-2]
    if sp:
        o=sp.get("open",last["开盘"]); c=sp.get("price",last["收盘"]); h=sp.get("high",last["最高"]); l=sp.get("low",last["最低"])
        prevc=sp.get("prev",prev["收盘"]); chg=(c-prevc)/prevc*100
        amount_yi=(sp.get("amount_wan",0) or 0)/10000; turnover=sp.get("turnover"); vol=sp.get("volume_hand",last["成交量(手)"])
    else:
        o,c,h,l=last["开盘"],last["收盘"],last["最高"],last["最低"]; prevc=prev["收盘"]; chg=last["涨跌幅%"]; amount_yi=0; turnover=None; vol=last["成交量(手)"]
    y20=df["收盘"].tail(20).values; x=np.arange(len(y20)); slope=float(np.polyfit(x,y20,1)[0])
    hi60=df["最高"].tail(60).max(); lo60=df["最低"].tail(60).min(); hi20=df["最高"].tail(20).max(); lo20=df["最低"].tail(20).min()
    k10=[{"d":r["日期"],"c":round(r["收盘"],2),"pct":round(r["涨跌幅%"],2)} for _,r in df.tail(10).iterrows()]
    return {"code":tc[2:],"tc":tc,"date":str(last["日期"]),"name":sp.get("name",""),
      "open":round(o,2),"close":round(c,2),"high":round(h,2),"low":round(l,2),
      "volume_hand":int(vol),"amount_yi":round(amount_yi,2),"turnover":(round(turnover,2) if turnover else None),
      "chg":round(chg,2),"prev_close":round(prevc,2),"body":round(c-o,3),"upper":round(h-max(o,c),3),
      "lower":round(min(o,c)-l,3),"is_yang":bool(c>o),"vol_ratio_5":round(vol/df["VOL_MA5"].iloc[-1],2),
      "vol_ratio_10":round(vol/df["VOL_MA10"].iloc[-1],2),
      "ma":{w:round(df[f"MA{w}"].iloc[-1],3) for w in (5,10,20,60)},
      "boll":{"mid":round(ma20.iloc[-1],3),"up":round(df["BOLL_UP"].iloc[-1],3),"low":round(df["BOLL_LOW"].iloc[-1],3)},
      "trend":{"slope20":round(slope,4)},"range60":{"hi":round(hi60,2),"lo":round(lo60,2),"hi20":round(hi20,2),"lo20":round(lo20,2)},"k10":k10}

stocks=["sz000711","sh600664"]
out={}
for tc in stocks:
    print(f"\n===== {tc} =====")
    try:
        r=analyze(tc); out[tc[2:]]=r
        print(json.dumps(r,ensure_ascii=False,indent=1))
    except Exception as e:
        print("FAIL",tc,repr(e))
with open(os.path.join(OUT,"st_analysis.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("\nsaved ->",os.path.join(OUT,"st_analysis.json"))
