# -*- coding: utf-8 -*-
import json, math

D=json.load(open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/doji_data_20260825.json",encoding="utf-8"))
RED="#e23b3b"; GREEN="#1aa251"; UP=RED; DOWN=GREEN; GREY="#888"; HL="#e8943b"

def ma(v,n):
    return sum(v[-n:])/n if len(v)>=n else None

def build(kl, hl_date, w=920, h=340, vol_h=110):
    kl=kl[-25:]
    opens=[b["open"] for b in kl]; closes=[b["close"] for b in kl]
    highs=[b["high"] for b in kl]; lows=[b["low"] for b in kl]; vols=[b["vol"] for b in kl]
    dates=[b["date"][5:] for b in kl]
    pmin=min(lows); pmax=max(highs); pad=(pmax-pmin)*0.1 or 0.1
    pmin-=pad; pmax+=pad; vmax=max(vols)
    L=46; R=w-10; T=14; B=h-vol_h-10; pw=R-L; ph=B-T; n=len(kl); cw=pw/n; bw=max(3,cw*0.6)
    def X(i): return L+cw*i+cw/2
    def Y(p): return T+(pmax-p)/(pmax-pmin)*ph
    def YV(v): return B+vol_h-(v/vmax)*(vol_h-14)
    parts=[f'<svg viewBox="0 0 {w} {h+vol_h+18}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Microsoft YaHei,sans-serif" font-size="10">']
    for g in range(5):
        yy=T+ph*g/4; pv=pmax-(pmax-pmin)*g/4
        parts.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{R}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{L-4}" y="{yy+3:.1f}" fill="{GREY}" text-anchor="end">{pv:.2f}</text>')
    ma5=[ma(closes[:i+1],5) for i in range(n)]; ma10=[ma(closes[:i+1],10) for i in range(n)]
    def mp(arr,col):
        pts=[f"{X(i):.1f},{Y(arr[i]):.1f}" for i in range(n) if arr[i] is not None]
        if pts: parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="1.1" opacity="0.85"/>')
    mp(ma5,"#f5a623"); mp(ma10,"#3b82f6")
    for i in range(n):
        up=closes[i]>=opens[i]; col=UP if up else DOWN
        x=X(i); yt=Y(highs[i]); yb=Y(lows[i]); y1=Y(opens[i]); y2=Y(closes[i])
        bt=min(y1,y2); bb=max(y1,y2)
        parts.append(f'<line x1="{x:.1f}" y1="{yt:.1f}" x2="{x:.1f}" y2="{yb:.1f}" stroke="{col}" stroke-width="1"/>')
        parts.append(f'<rect x="{x-bw/2:.1f}" y="{bt:.1f}" width="{bw:.1f}" height="{max(1,bb-bt):.1f}" fill="{col}"/>')
        parts.append(f'<rect x="{x-bw/2:.1f}" y="{YV(vols[i]):.1f}" width="{bw:.1f}" height="{B+vol_h-YV(vols[i]):.1f}" fill="{col}" opacity="0.5"/>')
        if kl[i]["date"]==hl_date:
            # highlight doji: diamond above high + label
            dy=Y(highs[i])-10
            parts.append(f'<path d="M{x:.1f},{dy-7:.1f} L{x+7:.1f},{dy:.1f} L{x:.1f},{dy+7:.1f} L{x-7:.1f},{dy:.1f} Z" fill="{HL}" stroke="#fff" stroke-width="0.8"/>')
            parts.append(f'<text x="{x:.1f}" y="{dy-10:.1f}" fill="{HL}" text-anchor="middle" font-weight="bold">十字星</text>')
    for i in range(0,n,5):
        parts.append(f'<text x="{X(i):.1f}" y="{h+vol_h+14:.1f}" fill="{GREY}" text-anchor="middle">{dates[i]}</text>')
    parts.append(f'<text x="{R}" y="{T+2:.1f}" fill="{HL}" text-anchor="end">橙=MA5 蓝=MA10 ◆=十字星</text>')
    parts.append('</svg>')
    return "".join(parts)

def info(kl):
    # recent closes for context
    c=[b["close"] for b in kl]
    return {"last":kl[-1],"ma5":ma(c,5),"ma10":ma(c,10),"ma20":ma(c,20),
            "start":kl[-12]["close"],"peak":max(b["high"] for b in kl[-12:]),
            "trough":min(b["low"] for b in kl[-12:])}

rep={}
for k in ["changyuan","ningke"]:
    kl=D[k]["kline"]; last=kl[-1]
    rep[k]={"svg":build(kl,"2026-08-24"),"info":info(kl),
            "snap":D[k]["snap"],
            "vol_last":last["vol"],"vol_prev":[b["vol"] for b in kl[-6:-1]],
            "vol_ma5":ma([b["vol"] for b in kl],5)}

def card(name,code,sub,pos,vol,bull,signal):
    return f"""
<section>
 <h2>{name}（{code}） <span class="badge">{sub}</span></h2>
 <div class="chart">{rep['changyuan' if code=='600525' else 'ningke']['svg']}</div>
 <div class="block"><b>① 所处位置：</b>{pos}</div>
 <div class="block"><b>② 成交量特征：</b>{vol}</div>
 <div class="block"><b>③ 多空博弈含义：</b>{bull}</div>
 <div class="block"><b>④ 对短期走势的信号（转折 or 延续）：</b>{signal}</div>
</section>"""

cy = card("ST长园","600525","摘帽前夜·最后交易日8-24",
 "8-24十字星处于<b>上升趋势末端 / 阶段高位</b>。该股自8-07的5.09一路推升至8-24收盘5.78（约+13.5%），当日最高5.94创阶段新高，收盘价稳于MA5(≈5.63)上方，均线多头排列未破。但连续的8-17(巨量46万手长上影)、8-21(中阳5.77)拉升后，8-24在相对高位走出实体为0的十字星，属于<b>“高位十字星”</b>位置——即一波上涨后的滞涨僵持区，而非下跌途中或低位盘整。",
 "8-24成交<b>25.1万手</b>，较前几日(8-18~8-21约17-18万手)温和放大，但明显低于8-17摘帽申请首日的46.3万手天量。量能属<b>“高位温和放量”</b>：不是极致天量出货，但也非地量惜售，说明多空在摘帽前夜交换筹码、分歧升温，部分获利盘借利好预期逢高派发。",
 "十字星实体为0（开=收=5.78），且<b>上影0.16 &gt; 下影0.10</b>：盘中多头一度推高至5.94(+2.8%)，却被砸回开盘价，显示<b>上方5.9+抛压沉重、上攻乏力</b>；下影0.10表明5.68一线尚有承接。<b>多空在摘帽前夜陷入僵持</b>——多头想借摘帽预期继续推，空头借阶段高位兑现，最终平收。这是典型的“上档有压、下档有托”的均衡态，但长上影更偏向卖方占优。",
 "纯K线语言：高位长上影十字星是<b>“黄昏十字星”雏形（变盘/见顶预警）</b>，单独偏<b>转折（向下）</b>信号，需次日阴线确认。<b>但关键变量是8-26摘帽复牌事件</b>：①若复牌市场认可摘帽（基本面改善、风险警示消除），可能高开放量、十字星后<b>延续</b>升势，目标看5.94上方；②若“利好兑现”+高位获利盘涌出，则十字星确认为阶段性顶部，复牌高开低走。<b>最可靠的确认信号是8-26复牌首日的量价</b>：放量站稳5.94=延续，缩量/跌破5.68=转折回调。")

nk = card("ST宁科","600165","摘帽前夜·最后交易日8-24",
 "8-24十字星同样处于<b>上升趋势末端 / 暴涨后高位</b>。该股8-07仅2.42，经8-17、8-18两个一字涨停板（地量）跳升至2.94，8-19开板巨量长阴，随后8-20~8-21两连阳至3.31，8-24盘中最高冲3.44（较8-07低点<b>+42%</b>）后回落收3.27。收盘价3.27仍高于MA5(≈3.16)，多头排列未破，但已处<b>急涨后的高位滞涨区</b>。",
 "8-24成交<b>21.4万手</b>，属<b>温和缩量</b>：对比开板日8-19的50.3万手、8-20的40.9万手天量分歧，之后逐日缩至21万手。说明8-19开板释放的集中抛压已部分消化，8-24多空转为<b>观望僵持</b>——在摘帽前夜，激进资金已撤退、剩筹码惜售与试探性博弈并存。",
 "十字星实体仅0.01（开3.28/收3.27），<b>上影0.16 远超下影0.07</b>：盘中多头三次上攻（8-19、8-20、8-24）均试图站稳3.4+，8-24更冲至3.44（近涨停）却被砸回3.27，<b>3.4-3.44一线抛压极重、多头屡攻不克</b>；下影0.07偏弱，说明低位3.20承接一般。<b>这是暴涨后的典型“高位长上影十字星”——多空分歧极大、上攻动能衰竭</b>，卖方在高位兑现意愿强于买方的追高意愿。",
 "纯技术面：高位长上影十字星+暴涨乖离，是<b>强转折（见顶/回调）预警</b>，偏向下。但同样本股，<b>8-26摘帽复牌是决定性事件</b>：①若摘帽催化未被充分price-in（从2.42涨至3.27虽+35%，但摘帽后估值重构空间仍在），复牌放量突破3.44则<b>延续</b>升势；②若已price-in，则十字星成顶，复牌易“利好兑现”回落。<b>确认信号：8-26复牌首日量价</b>——放量站上3.44=延续，缩量/失守3.20=转折回踩。")

html=f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>长园 & 宁科 8-24 十字星形态分析</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:"Segoe UI","Microsoft YaHei",sans-serif;margin:0;background:#f5f6f8;color:#222;line-height:1.65}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}}
h1{{font-size:21px;margin:0 0 4px}}
.sub{{color:#666;font-size:13px;margin-bottom:12px}}
h2{{font-size:17px;margin:24px 0 10px;border-left:4px solid #e8943b;padding-left:8px}}
.badge{{font-size:12px;background:#fff5e8;color:#e8943b;border:1px solid #f3d9b0;padding:1px 8px;border-radius:10px;vertical-align:middle}}
.chart{{background:#fff;border:1px solid #f0f0f0;border-radius:8px;padding:6px;overflow-x:auto;margin:8px 0}}
.chart svg{{width:100%;height:auto;display:block}}
.block{{background:#fafbfc;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:14px}}
.foot{{font-size:12px;color:#999;margin-top:18px;border-top:1px solid #eee;padding-top:10px}}
.legend{{font-size:12px;color:#888;margin:2px 0 6px}}
</style></head><body><div class="wrap">
<h1>长园集团（600525）& 宁科生物（600165）<br>8-24 十字星 K线形态分析</h1>
<div class="sub">数据：腾讯日K线(近25交易日)＋快照 ｜ 末交易日 2026-08-24（8-25停牌，8-26摘帽复牌）｜ 注：文中“长园/宁科”为摘帽后名称，当前仍处ST停牌</div>
<div class="legend">配色：红=涨 绿=跌（A股惯例）；◆=本分析标记的十字星。</div>
{cy}
{nk}
<div class="block"><b>两星对比与综合研判：</b>
<ul>
<li><b>共性位置</b>：两者十字星均出现在<b>“上升趋势末端 / 阶段高位”</b>（长园+13.5%、宁科+42%后的相对顶部），且都是<b>摘帽复牌前夜的最后一个交易日</b>——这是理解两星的关键事件背景。</li>
<li><b>共性量价</b>：均为<b>长上影 &gt; 下影</b>的高位十字星，上攻被拒、抛压浮现；量能长园温和放大(25万手)、宁科温和缩量(21万手)，都不算极端天量。</li>
<li><b>纯技术信号</b>：两星都偏<b>“转折/见顶预警”</b>（黄昏十字星雏形），即若无事件干扰，短期应回调。</li>
<li><b>事件改写信号</b>：因8-26摘帽复牌，十字星的“转折”含义被事件对冲——<b>复牌首日量价是终极确认</b>：放量突破各自前高(长园5.94 / 宁科3.44)则<b>延续</b>升势；缩量或高开低走失守支撑(长园5.68 / 宁科3.20)则十字星确认顶部、短期<b>转折</b>回落。</li>
<li><b>差异</b>：宁科涨幅更大(+42%)、筹码更松动(曾一字板+开板巨量)，高位滞涨与转折风险相对长园更突出；长园走势更连贯温和，但8-17巨量长上影已埋下分歧伏笔。</li>
</ul></div>
<div class="foot">
数据来源：腾讯财经日K线接口与行情快照（2026-08-25 收盘后抓取，末交易日2026-08-24）。<br>
重要说明：十字星本身为多空均衡信号，方向需结合位置与后续确认K线/事件判定；“摘帽复牌”属重大事件催化，可能覆盖纯技术面的转折含义，须以复牌首日实际量价为准。<br>
<b>免责声明：</b>本文仅为基于公开行情的K线形态客观描述，不构成投资建议。ST/*ST及摘帽股波动剧烈、存在复牌后大幅波动与退市风险，请独立判断、自负盈亏。
</div>
</div></body></html>"""

open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/长园_宁科_十字星分析_20260825.html","w",encoding="utf-8").write(html)
print("HTML written, size=",len(html))
