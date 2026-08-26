# -*- coding: utf-8 -*-
import json, math

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_data_20260825.json", encoding="utf-8") as f:
    D = json.load(f)

RED="#e23b3b"; GREEN="#1aa251"; GREY="#888"; UP=RED; DOWN=GREEN

def ma(vals,n):
    return sum(vals[-n:])/n if len(vals)>=n else None

def parse_min(rows):
    out=[]
    for r in rows:
        try:
            out.append({"t":r[0],"main":float(r[1]),"xl":float(r[2]),"lg":float(r[3]),"mid":float(r[4]),"sm":float(r[5])})
        except: pass
    return out

def build_candle_svg(kl, n=45, w=920, h=380, vol_h=120):
    kl=kl[-n:]
    dates=[b["date"][5:] for b in kl]
    opens=[b["open"] for b in kl]; closes=[b["close"] for b in kl]
    highs=[b["high"] for b in kl]; lows=[b["low"] for b in kl]; vols=[b["vol"] for b in kl]
    allc=closes[:]
    ma5=[ma(closes[:i+1],5) for i in range(len(closes))]
    ma10=[ma(closes[:i+1],10) for i in range(len(closes))]
    ma20=[ma(closes[:i+1],20) for i in range(len(closes))]
    pmin=min(lows); pmax=max(highs)
    pad=(pmax-pmin)*0.08 or 0.1
    pmin-=pad; pmax+=pad
    vmax=max(vols)
    # layout
    L=46; R=w-10; T=14; B=h-vol_h-10; BW=h
    plotw=R-L; ploth=B-T
    n=len(kl); cw=plotw/n; bodyw=max(3,cw*0.62)
    def X(i): return L+cw*i+cw/2
    def Y(p): return T+(pmax-p)/(pmax-pmin)*ploth
    def YV(v): return B+vol_h-(v/vmax)*(vol_h-14)
    parts=[]
    parts.append(f'<svg viewBox="0 0 {w} {h+vol_h+20}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Microsoft YaHei,sans-serif" font-size="10">')
    # grid + y labels
    for g in range(5):
        yy=T+ploth*g/4; pv=pmax-(pmax-pmin)*g/4
        parts.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{R}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{L-4}" y="{yy+3:.1f}" fill="{GREY}" text-anchor="end">{pv:.2f}</text>')
    # ma lines
    def ma_path(ma_arr,color):
        pts=[]
        for i in range(n):
            if ma_arr[i] is None: continue
            pts.append(f"{X(i):.1f},{Y(ma_arr[i]):.1f}")
        if pts:
            parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.1" opacity="0.85"/>')
    ma_path(ma5,"#f5a623"); ma_path(ma10,"#3b82f6"); ma_path(ma20,"#9b59b6")
    # candles + volume
    for i in range(n):
        up = closes[i]>=opens[i]
        col=UP if up else DOWN
        x=X(i); yb1=Y(opens[i]); yb2=Y(closes[i])
        ytop=Y(highs[i]); ybot=Y(lows[i])
        body_top=min(yb1,yb2); body_bot=max(yb1,yb2)
        parts.append(f'<line x1="{x:.1f}" y1="{ytop:.1f}" x2="{x:.1f}" y2="{ybot:.1f}" stroke="{col}" stroke-width="1"/>')
        parts.append(f'<rect x="{x-bodyw/2:.1f}" y="{body_top:.1f}" width="{bodyw:.1f}" height="{max(1,body_bot-body_top):.1f}" fill="{col}"/>')
        # volume bar
        vy=YV(vols[i]); vx=X(i); vw=bodyw
        parts.append(f'<rect x="{vx-vw/2:.1f}" y="{vy:.1f}" width="{vw:.1f}" height="{B+vol_h-vy:.1f}" fill="{col}" opacity="0.55"/>')
    # volume baseline label
    parts.append(f'<text x="{L}" y="{B+vol_h+12:.1f}" fill="{GREY}">成交量(万手) 量比见正文</text>')
    # legend
    parts.append(f'<text x="{R}" y="{T+2:.1f}" fill="{UP}" text-anchor="end">MA5橙 MA10蓝 MA20紫</text>')
    # x labels (every 5)
    for i in range(0,n,5):
        parts.append(f'<text x="{X(i):.1f}" y="{h+vol_h+16:.1f}" fill="{GREY}" text-anchor="middle">{dates[i]}</text>')
    parts.append('</svg>')
    return "".join(parts)

def build_flow_svg(minrows, w=920, h=240):
    if not minrows: return "<p>分时资金流数据缺失</p>"
    xs=[r["t"][11:16] for r in minrows]
    ys=[r["main"]/1e4 for r in minrows]  # 万
    ymin=min(ys); ymax=max(ys); rng=max(abs(ymin),abs(ymax)) or 1
    L=54; R=w-12; T=14; B=h-28; pw=R-L; ph=B-T
    def X(i): return L+pw*i/(len(xs)-1)
    def Y(v): return T+(rng-v)/(2*rng)*ph
    parts=[f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Microsoft YaHei,sans-serif" font-size="10">']
    # zero line
    zy=Y(0)
    parts.append(f'<line x1="{L}" y1="{zy:.1f}" x2="{R}" y2="{zy:.1f}" stroke="#bbb" stroke-dasharray="3,3"/>')
    parts.append(f'<text x="{L-4}" y="{zy+3:.1f}" fill="{GREY}" text-anchor="end">0</text>')
    # y labels
    parts.append(f'<text x="{L-4}" y="{Y(rng)+3:.1f}" fill="{GREY}" text-anchor="end">{rng:.0f}万</text>')
    parts.append(f'<text x="{L-4}" y="{Y(-rng)+3:.1f}" fill="{GREY}" text-anchor="end">{-rng:.0f}万</text>')
    # area + line
    col = DOWN if ys[-1]<0 else UP
    pts=[f"{X(i):.1f},{Y(v):.1f}" for i,v in enumerate(ys)]
    parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="1.4"/>')
    # mark morning/afternoon boundary 11:30 / 13:00
    for idx,r in enumerate(minrows):
        if r["t"][11:16] in ("11:30","13:01"):
            parts.append(f'<line x1="{X(idx):.1f}" y1="{T}" x2="{X(idx):.1f}" y2="{B}" stroke="#ddd"/>')
    # x labels
    for i in range(0,len(xs),30):
        parts.append(f'<text x="{X(i):.1f}" y="{h-10:.1f}" fill="{GREY}" text-anchor="middle">{xs[i]}</text>')
    parts.append(f'<text x="{R}" y="{T+2:.1f}" fill="{col}" text-anchor="end">主力净流入累计(万, 东财)</text>')
    parts.append('</svg>')
    return "".join(parts)

reports={}
for key in ["longda","jinglan"]:
    s=D[key]; kl=s["kline"]; snap=s["snapshot"]; minr=parse_min(s["em_fflow_min"] if isinstance(s["em_fflow_min"],list) else [])
    closes=[b["close"] for b in kl]; vols=[b["vol"] for b in kl]
    m5=ma(closes,5); m10=ma(closes,10); m20=ma(closes,20); m60=ma(closes,60)
    v5=ma(vols,5); v10=ma(vols,10)
    price=snap["price"]; prevc=snap["prev_close"]; op=snap["open"]; hi=snap["high"]; lo=snap["low"]
    chg=snap["pct"]; turn=snap["turnover"]; wb=snap["wb"]
    mv=snap["circ_mv"]
    # capital flow today
    main_last = minr[-1]["main"] if minr else None
    # morning/afternoon split
    morn=[r for r in minr if r["t"][11:13] in ("09","10","11")]
    aft=[r for r in minr if r["t"][11:13] in ("13","14","15")]
    morn_net = (morn[-1]["main"]-minr[0]["main"])/1e4 if morn else 0
    aft_net = (minr[-1]["main"]-morn[-1]["main"])/1e4 if (morn and minr) else 0
    # brackets from last bar
    lb=minr[-1]
    rep={
        "name":snap["name"],"code":snap["code"],"price":price,"chg":chg,"open":op,"prev":prevc,
        "high":hi,"low":lo,"turn":turn,"wb":wb,"mv":mv,
        "m5":m5,"m10":m10,"m20":m20,"m60":m60,
        "v5":v5,"v10":v10,"vol_today":vols[-1],
        "main_last_w":(main_last/1e4) if main_last else None,
        "morn_net_w":morn_net,"aft_net_w":aft_net,
        "xl":lb["xl"]/1e4,"lg":lb["lg"]/1e4,"mid":lb["mid"]/1e4,"sm":lb["sm"]/1e4,
    }
    reports[key]=rep
    # print metrics
    print("="*60, key, snap["name"])
    print(f" 收={price} 涨={chg}% 开={op}(昨收{prevc}) 高={hi} 低={lo} 换手={turn}% 量比={wb}")
    print(f" MA5={m5:.3f} MA10={m10:.3f} MA20={m20:.3f} MA60={m60:.3f}")
    print(f" 价 vs MA: 5={price/m5-1:+.1%} 10={price/m10-1:+.1%} 20={price/m20-1:+.1%} 60={price/m60-1:+.1%}")
    print(f" 今日量={vols[-1]/1e4:.1f}万手 vs MA5量={v5/1e4:.1f}万手 (倍率{vols[-1]/v5:.2f}) vs MA10量={v10/1e4:.1f}万手")
    print(f" 主力净流入累计={rep['main_last_w']:.1f}万  上午净={morn_net:.1f}万 下午净={aft_net:.1f}万")
    print(f" 5类(万): 超大={lb['xl']/1e4:.1f} 大={lb['lg']/1e4:.1f} 中={lb['mid']/1e4:.1f} 小={lb['sm']/1e4:.1f}")
    # recent 8 bars
    print(" 近8日: 日期 收 涨 量(万手)")
    for b in kl[-8:]:
        c=b["close"]; pct=(c-b["open"])/b["open"]-1
        print(f"   {b['date']} {c:.2f} {pct:+.1%} {b['vol']/1e4:.1f}")
    # candle shape today
    up = price>=op
    us=hi-price; ls=price-lo; bs=abs(price-op)
    print(f" 今日K线: {'阳' if up else '阴'}线 实体={bs:.2f} 上影={us:.2f} 下影={ls:.2f} 上影/实体={us/bs if bs else 0:.1f}")

# save metrics
with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_metrics_20260825.json","w",encoding="utf-8") as f:
    json.dump(reports,f,ensure_ascii=False,indent=2)

# build SVGs
svg_longda=build_candle_svg(D["longda"]["kline"])
svg_jinglan=build_candle_svg(D["jinglan"]["kline"])
flow_longda=build_flow_svg(parse_min(D["longda"]["em_fflow_min"]))
flow_jinglan=build_flow_svg(parse_min(D["jinglan"]["em_fflow_min"]))

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_svgs_20260825.json","w",encoding="utf-8") as f:
    json.dump({"longda":svg_longda,"jinglan":svg_jinglan,"flow_longda":flow_longda,"flow_jinglan":flow_jinglan},f,ensure_ascii=False)
print("SVGs built.")
