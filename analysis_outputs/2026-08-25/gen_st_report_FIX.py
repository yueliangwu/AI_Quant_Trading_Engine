# -*- coding: utf-8 -*-
import json, datetime

W = {"fund":0.25, "liq":0.15, "restruct":0.25, "turn":0.20, "risk":0.15}

# 已剔除 ST任子行(300311)：实时名「任子行」无ST前缀，已摘帽，不属"潜力"标的
data = [
 ("ST宁科","600165",3.23,5.90,3.36,40.87,False,"已申请撤销其他风险警示(8/14)",
   (5,4,5,4,3.5),
   "①8/14已提交撤销ST申请，交易所15个交易日内裁定；②重整计划执行完毕、行政处罚满12个月、追溯重述完成；③国资背景，持续经营不确定性消除。",
   "①上交所审核存在被驳回/延期可能；②曾因信披被处罚，历史合规瑕疵；③若审核不通过仍为ST。"),
 ("ST长园","600525",5.57,2.20,5.64,16.97,False,"已申请撤销其他风险警示(8/14)",
   (5,4,5,4,4),
   "①8/14董事会审议通过申请撤销ST，依据内控否定意见情形已消除；②智能电网设备主业稳健，中报预盈3500-5200万；③审核进度明确。",
   "①撤销ST尚需上交所审核，结果存不确定性；②历史内控问题需持续观察整改实效。"),
 ("ST华闻","000793",2.15,0.47,2.16,9.30,False,"重整计划执行完毕(2026/6/30)",
   (5,3,5,4,3.5),
   "①2026/6/30重整计划执行完毕，海南国资入主；②中报预盈4700-6000万(含约1亿重整收益)；③摘帽路径清晰。",
   "①曾为*ST、信披违规遗留风险；②盈利含非经常性重整收益，主业持续性待验；③股价低、波动大。"),
 ("*ST京化","600889",13.40,0.75,13.63,2.03,True,"重大资产重组完成，市值字段异常待复核",
   (5,3,5,4,3.5),
   "①重大资产重组完成，置入高端装备制造资产；②中报预盈4000-4800万，同比扭亏；③主营彻底转型，基本面根本改善。",
   "①仍为*ST，退市风险警示未完全解除；②转型后整合与订单兑现需跟踪；③市值数据异常需复核。"),
 ("ST中装","002822",3.19,1.59,3.19,6.58,False,"破产重整全部完成，已提交摘帽申请",
   (5,3,5,4,3),
   "①破产重整全部完成并已提交摘帽申请；②转型环保物业主业，营收规模充足；③困境反转逻辑明确。",
   "①曾因年报财务造假被处罚、主要账户曾被冻结；②仍背负其他风险警示，摘帽审核存变数；③低市值、流动性一般。"),
 ("ST天际","002759",17.62,0.46,17.85,18.93,False,"中报预盈2.2-2.6亿(六氟磷酸锂回暖)",
   (4,5,3,5,4.5),
   "①中报预盈2.2-2.6亿，居ST板块预盈榜首；②核心产品六氟磷酸锂盈利能力回升；③流动性好(换手17.85%)。",
   "①锂电周期波动大，盈利随产品价格起伏；②若锂价回落预盈或不及预期；③摘帽需满足净资产/营收等硬条件。"),
 ("ST万邦","002082",9.97,2.26,10.15,9.19,False,"中报预盈6500-9000万，同比+380%~568%",
   (4,4,3,5,4),
   "①中报预盈6500-9000万，同比增长超380%；②创新药合作驱动；③主业改善+流动性尚可。",
   "①高增长部分来自合作/非经常性因素，可持续性待验；②小市值、股价弹性与回撤均大。"),
 ("ST东尼","603595",26.00,-0.69,26.80,1.87,True,"摘帽预期，市值字段异常待复核",
   (4,3,3,4,4),
   "①摘帽条件充分(净利润/净资产转正)；②消费电子景气修复；③高换手显示资金关注度高。",
   "①市值字段异常需复核，或低流通盘、滑点风险；②摘帽申请或被驳回/延期；③消费电子需求波动。"),
 ("ST西王","000639",1.87,6.25,1.94,112.17,False,"中报预盈2.0-2.5亿(处置Iovate资产)",
   (4,3,3,4,3.5),
   "①中报预盈2.0-2.5亿；②处置Iovate资产获约3.5亿投资收益；③低价股、市值大。",
   "①盈利主要靠资产处置非经常性收益，主业改善有限；②此前债务危机遗留；③大市值、弹性偏低。"),
 ("ST京蓝","000711",6.11,-0.33,6.18,105.82,False,"中报预盈6800-8300万，转型铟/ITO靶材",
   (4,3,3,4,3.5),
   "①中报预盈6800-8300万(含子公司处置股票7600万非经常性收益)；②更名铟靶新材，切入稀缺新材料赛道；③三季度摘帽潜力。",
   "①盈利含非经常性收益；②历史问题待彻底出清；③转型新业务兑现存不确定性。"),
 ("ST嘉澳","603822",57.76,3.79,59.32,0.65,True,"中报预盈6000-9000万(生物航煤)，市值异常待复核",
   (4,3,3,4,3.5),
   "①中报预盈6000-9000万，生物航煤行情向好、订单充足；②扭亏确定性高；③超高换手显示强资金博弈。",
   "①市值字段异常(显示<1亿)需复核，或极低流通盘、滑点/操纵风险极高；②过高换手蕴含剧烈波动；③ST标签未除。"),
 ("ST中珠","600568",2.21,0.45,2.22,7.15,False,"债务重组落地，2025年业绩盈利",
   (3,3,4,3,3.5),
   "①2025年度业绩盈利，债务重组落地，财务隐患基本化解；②摘帽条件基本满足；③新规催化估值修复预期。",
   "①改善更多来自债务/资产端，主业内生增长待验；②低换手、流动性一般；③仍需持续观察。"),
 ("*ST南置","002305",2.11,2.43,2.11,17.70,False,"控股股东启动重大资产剥离(避免退市)",
   (3,3,4,3,3),
   "①控股股东中国电建地产启动重大资产重组，拟剥离地产相关资产及负债；②交易完成后净资产有望转正、避免退市；③重组处实质推进阶段。",
   "①仍为*ST，退市风险未解除；②资产剥离交易尚需审批，存在终止可能；③地产资产估值与接盘方不确定；④低换手。"),
]

def st_tag(name):
    if name.startswith("*ST"): return "*ST·退市风险警示"
    if "ST" in name: return "ST·其他风险警示"
    return "已摘帽"

rows=[]
for (name,code,price,chg,turn,cap,anom,status,scores,cat,risk) in data:
    fund,liq,restruct,turn_s,risk_s = scores
    total = fund*W["fund"]+liq*W["liq"]+restruct*W["restruct"]+turn_s*W["turn"]+risk_s*W["risk"]
    rows.append(dict(name=name,code=code,price=price,chg=chg,turn=turn,cap=cap,anom=anom,
                     status=status,tag=st_tag(name),fund=fund,liq=liq,restruct=restruct,
                     turn_s=turn_s,risk=risk_s,total=round(total,3),cat=cat,risk_txt=risk))
rows.sort(key=lambda r:-r["total"])

# 已摘帽/更名（已剔除出潜力榜，仅作参照）
done = [
 ("任子行","300311",6.11,"摘帽完成(实时名已无ST前缀)，反转已兑现——原P1已移除"),
 ("松发股份","603268",176.21,"恒力重工100%股权置入，已申请摘帽"),
 ("石药景峰","000908",7.00,"石药控股入主，重整完成，转型创新药平台"),
 ("东易日盛","002713",9.45,"重整完成，北京华著科技入主，注入算力订单"),
 ("宇顺电子","002289",41.50,"现金收购数据中心资产，转型算力"),
 ("国旅联合","600358",5.07,"润田实业100%股权注入，恢复审核"),
 ("顺景科技","603007",4.59,"原ST花王重整完成，转型新能源/半导体"),
]

P=lambda r:("up" if r["chg"]>=0 else "down")
S=lambda r:("+" if r["chg"]>=0 else "")
C=lambda r:(f'{r["cap"]}亿<span class="anom">*</span>' if r["anom"] else f'{r["cap"]}亿')

H=[]
H.append(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ST/*ST反转预期优先级清单(2026-08-20 修正)</title>
<style>
:root{{--bg:#0f1419;--card:#1a2330;--line:#2a3645;--txt:#e6edf3;--mut:#9fb0c0;--acc:#4ea1ff;--up:#ff5b5b;--down:#26c281;--gold:#ffcf5c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--txt);font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;line-height:1.6}}
.wrap{{max-width:1100px;margin:0 auto;padding:28px 20px 60px}}h1{{font-size:24px;margin:0 0 4px}}
.sub{{color:var(--mut);font-size:13px;margin-bottom:18px}}
.disc{{background:#2a1f1f;border:1px solid #5a3a3a;color:#ffd9d9;padding:10px 14px;border-radius:8px;font-size:12.5px;margin-bottom:22px}}
.fix{{background:#16301f;border:1px solid #2f6b45;color:#bff5cf;padding:10px 14px;border-radius:8px;font-size:12.5px;margin-bottom:22px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:26px}}
th,td{{border:1px solid var(--line);padding:8px 10px;text-align:center}}th{{background:#16202c;color:var(--mut);font-weight:600}}
td.l,th.l{{text-align:left}}.rank{{color:var(--gold);font-weight:700;font-size:15px}}.up{{color:var(--up)}}.down{{color:var(--down)}}
.tier{{margin:22px 0 10px;font-size:16px;font-weight:700;color:var(--acc);border-left:4px solid var(--acc);padding-left:10px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:14px}}
.card h3{{margin:0 0 6px;font-size:16px}}.code{{color:var(--mut);font-size:12px;font-weight:400;margin-left:8px}}
.scores{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}.sc{{background:#0e1620;border:1px solid var(--line);border-radius:6px;padding:3px 9px;font-size:11.5px;color:var(--mut)}}.sc b{{color:var(--txt)}}
.cat,.rk{{margin:6px 0;font-size:13.5px}}.cat b{{color:var(--gold)}}.rk b{{color:#ff9b9b}}
.anom{{color:#ffcf5c;font-size:11.5px}}.foot{{color:var(--mut);font-size:12px;margin-top:30px;border-top:1px solid var(--line);padding-top:14px}}
.st{{display:inline-block;border-radius:5px;padding:1px 7px;font-size:11px;margin-left:6px}}
.stst{{background:#3a2a10;border:1px solid #8a6a20;color:#ffcf5c}}
.stx{{background:#3a1010;border:1px solid #8a2020;color:#ff8b8b}}
</style></head><body><div class="wrap">
<h1>ST / *ST 反转预期 · 投资价值优先级清单（修正版）</h1>
<div class="sub">数据基准：2026-08-20 收盘（腾讯实时行情核验）｜评分模型：五维加权｜修正时间：{datetime.date.today().isoformat()}</div>
<div class="disc">⚠️ 免责声明：本清单仅基于公开财报、公告与行情数据的<strong>研究性排序与情景讨论</strong>，不构成任何投资建议或要约。ST/*ST 属高风险警示板块，存在退市、业绩变脸、监管处罚等风险，务必严控仓位、独立决策。</div>
<div class="fix">✅ <b>本次修正：</b>已剔除「ST任子行(300311)」——实时行情名已无 ST 前缀（摘帽完成），不属于"潜力"标的。下表 13 只均为 <b>2026-08-20 实时核验仍带 ST/*ST 前缀</b>的标的；另附已摘帽参照（已移出潜力榜）。</div>
""")

H.append("""<table><tr><th>优先级</th><th class="l">标的</th><th>当前状态</th><th>现价</th><th>涨跌幅</th><th>换手%</th><th>总市值</th><th>基本面</th><th>市值流动</th><th>重组进度</th><th>扭亏概率</th><th>风险可控</th><th>综合</th></tr>""")
for i,r in enumerate(rows,1):
    stcls="stx" if r["tag"].startswith("*") else "stst"
    H.append(f"""<tr><td class="rank">{i}</td><td class="l"><b>{r['name']}</b><span class="code">{r['code']}</span></td>
<td><span class="st {stcls}">{r['tag']}</span></td>
<td>{r['price']}</td><td class="{P(r)}">{S(r)}{r['chg']}%</td><td>{r['turn']}</td><td>{C(r)}</td>
<td>{r['fund']}</td><td>{r['liq']}</td><td>{r['restruct']}</td><td>{r['turn_s']}</td><td>{r['risk']}</td><td class="rank">{r['total']}</td></tr>""")
H.append("</table>")
H.append('<div class="anom">* 市值字段在行情源显示异常（流通&gt;总或显著偏离板块常态），已标注待复核，评分中流动性维度按审慎处理。</div>')

def tier(title, items):
    out=[f'<div class="tier">{title}</div>']
    for r in items:
        stcls="stx" if r["tag"].startswith("*") else "stst"
        out.append(f"""<div class="card"><h3>{r['name']}<span class="code">{r['code']}｜现价 {r['price']}（{S(r)}{r['chg']}%）｜总市值 {C(r)}｜换手 {r['turn']}%</span><span class="st {stcls}">{r['tag']}</span></h3>
<div class="scores"><span class="sc">基本面 <b>{r['fund']}</b></span><span class="sc">市值流动 <b>{r['liq']}</b></span><span class="sc">重组进度 <b>{r['restruct']}</b></span><span class="sc">扭亏概率 <b>{r['turn_s']}</b></span><span class="sc">风险可控 <b>{r['risk']}</b></span><span class="sc">综合 <b>{r['total']}</b></span></div>
<div style="color:var(--mut);font-size:12px;margin:2px 0 8px">状态：{r['status']}</div>
<div class="cat"><b>核心催化逻辑：</b>{r['cat']}</div><div class="rk"><b>主要风险：</b>{r['risk_txt']}</div></div>""")
    return "\n".join(out)

p1=[r for r in rows if r["total"]>=4.2]
p2=[r for r in rows if 3.8<=r["total"]<4.2]
p3=[r for r in rows if 3.3<=r["total"]<3.8]
p4=[r for r in rows if r["total"]<3.3]
H.append(tier("【P1 高确定性 · 近期催化（摘帽申请/重整执行完毕）】", p1))
H.append(tier("【P2 中高确定性 · 基本面反转/扭亏兑现】", p2))
H.append(tier("【P3 中报扭亏 · 主业改善，待摘帽条件验证】", p3))
H.append(tier("【P4 进展中 · 需持续跟踪】", p4))

H.append('<div class="tier">【已摘帽 / 更名 · 反转已兑现（已移出潜力榜，仅作参照）】</div>')
H.append('<table><tr><th class="l">标的</th><th>现价</th><th class="l">说明</th></tr>')
for n,c,p,desc in done:
    H.append(f'<tr><td class="l"><b>{n}</b><span class="code">{c}</span></td><td>{p}</td><td class="l">{desc}</td></tr>')
H.append('</table>')

H.append(f"""<div class="foot"><b>方法论：</b>五维加权评分（各维度1-5分）：基本面改善确定性(25%)＋市值与流动性(15%)＋重组进度(25%)＋业绩预告扭亏概率(20%)＋风险可控性(15%)。
<b>ST状态核验：</b>以腾讯 qt.gtimg.cn 实时显示名为准（带 ST/*ST 前缀即当前仍被实施风险警示），核验时间 2026-08-20。
<b>数据来源：</b>行情/市值来自腾讯；催化与风险依据证券时报·数据宝、东方财富、同花顺、雪球公开公告梳理。
<b>重要提示：</b>摘帽审核结果、重组审批、市值异常项均存在不确定性，请以交易所与上市公司最新公告为准。</div></div></body></html>""")

out="\n".join(H)
with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_reversal_priority_FIX_20260820.html","w",encoding="utf-8") as f: f.write(out)
with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_reversal_scores_FIX_20260820.json","w",encoding="utf-8") as f: json.dump(rows,f,ensure_ascii=False,indent=2)
print("OK 修正版已生成。排名:", " > ".join(f"{i+1}.{r['name']}({r['total']})" for i,r in enumerate(rows)))
print("已剔除: ST任子行(300311) 实时名=任子行 已摘帽")
