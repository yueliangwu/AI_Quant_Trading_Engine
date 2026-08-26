# -*- coding: utf-8 -*-
import json

M=json.load(open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_metrics_20260825.json",encoding="utf-8"))
S=json.load(open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_svgs_20260825.json",encoding="utf-8"))
RAW=json.load(open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_data_20260825.json",encoding="utf-8"))

def c2c(kl, n=8):
    kl=kl[-n:]; out=[]
    for i in range(1,len(kl)):
        pc=kl[i-1]["close"]; c=kl[i]["close"]
        out.append((kl[i]["date"], c, (c-pc)/pc-1))
    return out

def fmt_pct(x): return f"{x*100:+.2f}%"

cards_tpl = """
<div class="cards">
  <div class="card"><div class="k">收盘价</div><div class="v {cls}">{price}</div><div class="s">{chg}</div></div>
  <div class="card"><div class="k">开盘 / 昨收</div><div class="v">{open} / {prev}</div><div class="s">高 {high} · 低 {low}</div></div>
  <div class="card"><div class="k">换手率 / 量比</div><div class="v">{turn}% / {wb}</div><div class="s">流通市值 {mv}亿</div></div>
  <div class="card"><div class="k">主力净流入(当日)</div><div class="v {mcls}">{mw}万</div><div class="s">上午 {mn} · 下午 {an}</div></div>
</div>"""

ma_tpl = """<div class="ma"><span>MA5 {m5:.3f}</span><span>MA10 {m10:.3f}</span><span>MA20 {m20:.3f}</span><span>MA60 {m60:.3f}</span></div>"""

def section(key, name, code, sub, verdict, shape_txt, flow_txt, judge, sup, resis, short_p, mid_p, risk):
    m=M[key]
    cls = "up" if m["chg"]>=0 else "down"
    mcls = "down" if (m["main_last_w"] or 0)<0 else "up"
    cards = cards_tpl.format(
        price=m["price"], chg=fmt_pct(m["chg"]/100), cls=cls,
        open=m["open"], prev=m["prev"], high=m["high"], low=m["low"],
        turn=m["turn"], wb=m["wb"], mv=m["mv"],
        mw=f"{m['main_last_w']:.0f}", mcls=mcls,
        mn=f"{m['morn_net_w']:+.0f}万", an=f"{m['aft_net_w']:+.0f}万")
    ma = ma_tpl.format(m5=m["m5"],m10=m["m10"],m20=m["m20"],m60=m["m60"])
    # recent table
    rows=""
    for d,c,p in c2c(RAW[key]["kline"],8):
        pc="up" if p>=0 else "down"
        rows+=f"<tr><td>{d}</td><td>{c:.2f}</td><td class='{pc}'>{fmt_pct(p)}</td></tr>"
    candle=S[key]; flow=S["flow_"+key]
    return f"""
<section>
  <h2>{name}（{code}） <span class="badge">{sub}</span></h2>
  <div class="verdict">{verdict}</div>
  {cards}
  {ma}
  <h3>日K线 · 成交量（近45交易日，橙=MA5 蓝=MA10 紫=MA20）</h3>
  <div class="chart">{candle}</div>
  <h3>分时主力资金净流入（当日累计，东财口径）</h3>
  <div class="chart">{flow}</div>
  <h3>近8日收盘环比</h3>
  <table class="mini"><tr><th>日期</th><th>收盘</th><th>环比</th></tr>{rows}</table>
  <div class="block"><b>① K线形态：</b>{shape_txt}</div>
  <div class="block"><b>② 资金流向：</b>{flow_txt}</div>
  <div class="block"><b>③ 主力意图研判：</b>{judge}</div>
  <div class="grid2">
    <div class="box"><b>支撑位</b><br>{sup}</div>
    <div class="box"><b>压力位</b><br>{resis}</div>
  </div>
  <div class="block"><b>④ 走势预测：</b><br><b>短期：</b>{short_p}<br><b>中期：</b>{mid_p}</div>
  <div class="risk"><b>⚠ 风险提示：</b>{risk}</div>
</section>"""

ld = section("longda","ST龙大美食","002726","*ST · 预重整概念",
    "【综合研判】高位放量长上影十字星 + 主力净流出，短线偏震荡洗盘/派发，中期多头趋势未破。",
    "今日收2.85，开=收=2.85形成<b>十字星</b>，上影0.24（最高冲至3.09、逼近涨停）、下影仅0.06，呈典型<b>“冲高回落、上档抛压重”</b>形态。此前8-20放量涨停至2.95、8-21即巨量长阴(-6.1%、155万手)已现派发雏形，近三日2.77→2.90→2.85高位滞涨。均线呈多头排列（价>MA5>MA10>MA20>MA60），但今日量比3.19放出近阶段天量，高位巨量滞涨需警惕。",
    "东财主力净流入累计 <b>-4222万（净流出）</b>，且呈<b>午后加速</b>特征：上午净流出-777万、下午扩大至-3473万。即早盘尚有抵抗、午后资金集中离场。5档拆分显示超大单+大单合计+4222万、中单-2315万、小单-1907万（注：东财对ST标的五档字段存在口径争议，结论以‘主力净流入’累计值为准，该值与价格走势自洽）。",
    "放量长上影 + 主力全天净流出（尤其午后），更偏向<b>“拉高派发 / 高位换手洗盘”</b>。由于股价仍稳于MA5(2.83)上方、且预重整（7-9启动、27家意向投资人）属中期利好未兑现，暂不能判定为彻底出货，更像是<b>边拉边洗、消化2.0→2.95获利盘</b>。若后续跌破MA10且主力持续流出，则派发确认。",
    "① 即时支撑 <b>2.83（MA5/今收）</b>；② 强支撑 <b>2.55–2.57</b>（8-18/8-24低点区+MA10）；③ 谷底支撑 <b>2.35（MA20）</b>。跌破2.35则短期转弱。",
    "① 短线压力 <b>3.00–3.09</b>（今日高点+ST涨停价区，8-20/8-21/8-25三触3.0附近均回落）；② 突破需放量站稳3.10上方方打开空间。",
    "1–2周大概率在 <b>2.55–3.09 箱体震荡洗盘</b>，关注2.55防线；若守住则蓄势再攻3.09，若失守2.35则回踩2.16。",
    "中期多头趋势未破（价较MA60高+54%），若预重整正式受理/投资人落定的实质进展落地，洗盘后有望再挑战3.09乃至更高；但ST股波动极大，须防利好兑现反杀。",
    "*ST仍未摘帽，预重整仅启动、尚未法院正式受理，27家意向投资人未定最终，若重整失败有退市风险；今日高位天量滞涨，追高易被套。")

jl = section("jinglan","ST京蓝科技","000711","ST · 摘帽申请已提交(8-24)",
    "【综合研判】摘帽申请利好兑现，高开低走放量大阴 + 主力全天净流出1.73亿，短线偏空考验6.00，中期看9月初过审窗口。",
    "今日收6.20，开6.54（高开于昨收6.60下方）、最高6.67、最低6.18，收<b>中阴线</b>，上影0.47、下影仅0.02（收盘贴近最低），呈<b>“高开低走、空头主导”</b>。8-24摘帽申请落地当日冲高至6.60，今日即放量大跌-6.06%，典型的<b>“利好出尽”</b>走势。均线仍多头（价>MA10>MA20>MA60），但已跌破MA5(6.30)，短线转弱。",
    "东财主力净流入累计 <b>-1.73亿（大幅净流出）</b>，且<b>开盘即砸</b>：09:31首分钟已-749万，全天持续扩大至-1.73亿（上午-8847万、下午-7733万）。资金出逃坚决、贯穿全天，与价格大跌完全对应。5档拆分超大单+大单合计+1.73亿、中单-7884万、小单-9444万（口径争议同上，以‘主力净流入’累计值为准）。",
    "高开低走 + 开盘即主力净流出 + 全天扩大至1.73亿，强烈指向<b>“利好兑现、主力出货”</b>。摘帽申请(8-24)这个最大预期已落地，短线资金选择兑现。当前并非建仓/洗盘信号，而是<b>派发</b>。需等待缩量企稳、资金回流，方为再介入时机。",
    "① 心理整数关 <b>6.00</b>（今日低点6.18，逼近）；② 强支撑 <b>5.64（MA20）</b>；③ 前低 <b>5.85（8-17）</b>。6.00失守将考验MA20。",
    "① 即时反压 <b>6.30（MA5）</b>；② 强压力 <b>6.60–6.67</b>（8-24/今日高点，摘帽预期密集套牢区）。",
    "1–2周考验 <b>6.00 整数关</b>，若失守下看5.64(MA20)；反弹需收复6.30(MA5)方可缓和。过审前(9月初)以震荡寻底为主。",
    "摘帽审核预计 <b>9-02（受理次日起6交易日）至9-15（法定上限）</b>出结果。若过审，参照宁科/长圆摘帽后走势有望打开上行空间；若失守6.00则先完成探底。中期方向取决于过审结果+资金是否回流。",
    "刚提交摘帽申请、审核结果未出；H1虽扭亏(归母7420万)但基数薄，若深交所认为整改/信披不达标可驳回；且今日主力大幅净流出，利好兑现后短期下杀风险高，切勿盲目抄底。")

html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>龙大美食 & 京蓝科技 技术资金面分析（2026-08-25收盘）</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:"Segoe UI","Microsoft YaHei",sans-serif;margin:0;background:#f5f6f8;color:#222;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:#666;font-size:13px;margin-bottom:14px}}
h2{{font-size:18px;margin:26px 0 10px;border-left:4px solid #e23b3b;padding-left:8px}}
h3{{font-size:14px;color:#333;margin:18px 0 6px}}
section{{background:#fff;border-radius:10px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.badge{{font-size:12px;background:#fff0f0;color:#e23b3b;border:1px solid #f3c2c2;padding:1px 8px;border-radius:10px;vertical-align:middle}}
.verdict{{background:#fff8e6;border-left:4px solid #f5a623;padding:8px 12px;border-radius:6px;font-size:14px;margin:6px 0 12px}}
.cards{{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}}
.card{{flex:1 1 160px;background:#fafbfc;border:1px solid #eee;border-radius:8px;padding:10px 12px}}
.card .k{{font-size:12px;color:#888}}
.card .v{{font-size:18px;font-weight:700;margin:2px 0}}
.card .s{{font-size:12px;color:#999}}
.up{{color:#e23b3b}}.down{{color:#1aa251}}
.ma{{display:flex;gap:14px;font-size:13px;color:#555;margin:4px 0 8px;flex-wrap:wrap}}
.chart{{background:#fff;border:1px solid #f0f0f0;border-radius:8px;padding:6px;overflow-x:auto}}
.chart svg{{width:100%;height:auto;display:block}}
.mini{{width:100%;border-collapse:collapse;font-size:13px;margin-top:4px}}
.mini th,.mini td{{border:1px solid #eee;padding:5px 8px;text-align:center}}
.mini th{{background:#fafbfc;color:#888;font-weight:600}}
.block{{background:#fafbfc;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:14px}}
.grid2{{display:flex;gap:12px;margin:10px 0}}
.box{{flex:1;background:#f0f7ff;border:1px solid #d6e8ff;border-radius:8px;padding:10px 12px;font-size:14px}}
.risk{{background:#fff0f0;border:1px solid #f3c2c2;border-radius:8px;padding:10px 12px;font-size:13px;color:#a33;margin-top:10px}}
.foot{{font-size:12px;color:#999;margin-top:20px;border-top:1px solid #eee;padding-top:10px}}
.legend{{font-size:12px;color:#888;margin:2px 0 8px}}
</style></head><body><div class="wrap">
<h1>ST龙大美食（002726） & ST京蓝科技（000711）<br>技术形态与资金流向分析</h1>
<div class="sub">数据时点：2026-08-25 收盘 ｜ 行情：腾讯快照+K线 ｜ 资金流：东方财富（当日累计+分时）｜ 涨跌停新规 ±10%</div>
<div class="legend">配色说明：价格/蜡烛 <span class="up">红=涨</span> <span class="down">绿=跌</span>（A股惯例）；资金流 红=净流入 绿=净流出。</div>
{ld}
{jl}
<div class="block"><b>两股对比小结：</b>龙大处于“强势拉升后的高位换手”，均线仍多头、洗盘特征更浓，关键看2.55防线；京蓝则是“利好兑现后的坚决派发”，主力开盘即出逃1.73亿、短线考验6.00，关键看摘帽过审窗口(9月初)能否扭转资金面。两者均为ST/*ST高波动品种，资金面当下均偏空，操作上宜等企稳信号而非追高。</div>
<div class="foot">
数据来源：腾讯财经行情快照与日K线接口、东方财富资金流向接口（当日+分时）。<br>
重要说明：① 东方财富日线资金流接口仅返回当日数据，历史主力流向以量价K线辅助研判；② 东财对风险警示(ST/*ST)标的的“主力”字段与“超大单+大单”合计存在口径/符号争议，本文以“主力净流入累计值+分时轨迹”为准，该口径与两股当日价格走势自洽；③ 均线为收盘价简单移动平均。<br>
<b>免责声明：</b>本文仅为基于公开行情数据的技术形态与资金面客观描述，不构成任何投资建议或买卖邀约。ST/*ST股票波动剧烈、存在退市风险，请独立判断、自负盈亏。
</div>
</div></body></html>"""

open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/ST龙大_京蓝_技术资金分析_20260825.html","w",encoding="utf-8").write(html)
print("HTML written. size=",len(html))
