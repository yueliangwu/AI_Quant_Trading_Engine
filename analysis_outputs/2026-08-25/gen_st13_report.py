# -*- coding: utf-8 -*-
"""读取实时行情JSON + 四维打分, 输出全13只ST优先级排序HTML报告(仅写Temp, 不碰项目目录)"""
import json

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st13_data.json", encoding="utf-8") as fp:
    quotes = {d["code"]: d for d in json.load(fp)}

# 四维评分(1-5): 退市风险(30%)+重组预期(30%)+基本面改善(25%)+市场关注度(15%)
# 退市风险分越高=风险越低(越安全)
W = {"退市风险":0.30, "重组预期":0.30, "基本面改善":0.25, "市场关注度":0.15}

scores = {
"600079": {"退市风险":5.0, "重组预期":4.0, "基本面改善":5.0, "市场关注度":3.5,
    "risk":"低(规范类ST/信披违规,非财务退市,麻醉龙头主业正常)",
    "rationale":"招商局央企入主+定增全额认购(36月锁定期),历史违规已整改完毕;麻醉镇痛龙头市占率前列,业绩企稳回升,是13只中唯一正PE(15.32);摘帽条件2026.12期满后可申,预计2027.1摘帽。基本面与风险可控性双优,综合第一。",
    "catalyst":"央企赋能+归核聚焦(剥离乐福思10.56亿)+创新药临床获批+摘帽预期",
    "risk_note":"定增折价短期摊薄EPS;FDA警示整改未完;摘帽需等2026.12期满,时间窗较远"},
"002726": {"退市风险":4.5, "重组预期":4.5, "基本面改善":3.5, "市场关注度":5.0,
    "risk":"低(ST非*ST,屠宰硬资产+知名渠道)",
    "rationale":"1250万头/年屠宰产能+海底捞/肯德基渠道是硬资产;27家投资人报名+莱阳国资代偿转债,重整预期最热;当日涨停(+10.07%)换手10.36%全市最高,资金关注度第一。风险在仍亏损(PE-6.56)、重整方案未落定。",
    "catalyst":"预重整投资人遴选+国资代偿转股+重整草案",
    "risk_note":"重整进度不及预期;消费复苏弱拖累屠宰利润;ST涨跌幅5%前波动大"},
"000711": {"退市风险":4.5, "重组预期":3.5, "基本面改善":4.0, "市场关注度":4.5,
    "risk":"低(ST非*ST,重整已于2023.12执行完毕)",
    "rationale":"中报营收4.45亿(+98%)、归母7420万扭亏(+213%),铟资源化主业放量;拟更名'铟靶新材'并申请摘帽,市场热度高(换手4.49%)。但扣非仅570万、靠处置重整股票收益7600万(不可持续),经营现金流-1.45亿,资产注入(鑫联科技)逾期未完成。改善信号明确但质量偏弱。",
    "catalyst":"中报扭亏+申请摘帽+铟价上行+更名",
    "risk_note":"盈利依赖一次性收益;现金流为负;资产注入存疑;股价已脱离业绩(公司自提示)"},
"000838": {"退市风险":3.5, "重组预期":4.5, "基本面改善":3.0, "市场关注度":4.0,
    "risk":"高(*ST,但重整协议已签确定性最高)",
    "rationale":"重整投资协议已签、景行新能入主确定性高,程序最先进;但*ST且净资产-2亿,股本稀释大。重组确定性拉高排序,退市风险仍高于纯ST。",
    "catalyst":"重整投资人入主+资产注入+摘星",
    "risk_note":"净资产为负;稀释比例大;重整后整合不及预期"},
"600337": {"退市风险":4.5, "重组预期":4.0, "基本面改善":3.0, "市场关注度":3.0,
    "risk":"低(ST非*ST,产投协议已签)",
    "rationale":"产投协议已签,万德溙AI算力铜缆跨界概念强;但跨界协同与业绩亏损(PE-1.85)压制,换手仅1.41%关注度中等。",
    "catalyst":"产投落地+AI算力/铜缆概念+摘帽",
    "risk_note":"跨界协同不确定;主业仍亏;概念炒作退潮"},
"002168": {"退市风险":4.5, "重组预期":4.0, "基本面改善":3.0, "市场关注度":2.5,
    "risk":"低(ST非*ST,二债会已过)",
    "rationale":"二债会通过重整计划草案,程序推进快但尚未获法院受理;换手0.51%偏低,关注度弱于前列。",
    "catalyst":"法院受理重整+草案执行",
    "risk_note":"法院受理时点不确定;受理前仍处风险期"},
"600381": {"退市风险":3.5, "重组预期":4.0, "基本面改善":3.0, "市场关注度":4.0,
    "risk":"高(*ST,但营收踩线达标摘帽在即)",
    "rationale":"营收踩线达标,摘星摘帽申请已进入交易所终审,当日涨停(+9.35%);但上半年仍亏损+问询函风险。摘帽确定性推高排序。",
    "catalyst":"摘星摘帽裁定+听花酒营收修复",
    "risk_note":"仍亏损;问询函/监管风险;消费场景修复不及预期"},
"300147": {"退市风险":3.0, "重组预期":3.5, "基本面改善":3.0, "市场关注度":3.0,
    "risk":"高(*ST,广药中选但协议未签)",
    "rationale":"广药资本中选,产业协同想象空间大;但协议未签+预重整四次延期逾期,确定性低于已签协议组。",
    "catalyst":"广药资本协议签署+T细胞治疗进展",
    "risk_note":"协议久拖不签;预重整逾期;未盈利"},
"002542": {"退市风险":2.5, "重组预期":3.0, "基本面改善":2.5, "市场关注度":3.0,
    "risk":"高(*ST,仅拟申请预重整,净资产为负)",
    "rationale":"成都国资背景+低空概念,但仅是'拟申请'预重整,净资产为负,程序最早期。",
    "catalyst":"预重整受理+国资入主",
    "risk_note":"仅预期无实质;净资产为负保壳难"},
"300027": {"退市风险":3.5, "重组预期":2.5, "基本面改善":2.0, "市场关注度":2.5,
    "risk":"中(ST非*ST,但七年累亏82亿)",
    "rationale":"影视IP知名,但七年累亏82亿、重整投资人未定、造血极差,基本面改善最弱之一。",
    "catalyst":"重整投资人落地+内容回暖",
    "risk_note":"持续大额亏损;重整投资人未定;行业承压"},
"300020": {"退市风险":3.0, "重组预期":2.5, "基本面改善":2.5, "市场关注度":2.5,
    "risk":"中(ST非*ST,三重ST叠加)",
    "rationale":"智慧城市主业还在,但三重ST叠加、违规担保2.36亿未解、扭亏困难。",
    "catalyst":"内控整改完成+摘帽+担保解除",
    "risk_note":"违规担保未解;扭亏困难;多风险叠加"},
"600340": {"退市风险":1.5, "重组预期":2.5, "基本面改善":1.5, "市场关注度":2.0,
    "risk":"极高(*ST,净资产缺口-177亿)",
    "rationale":"债务重组规模大但协议未签,净资产缺口-177亿,保壳极难;1元股情绪化。",
    "catalyst":"债务重组协议+战投",
    "risk_note":"保壳失败直接退市;净资产巨额缺口"},
"600370": {"退市风险":1.5, "重组预期":2.5, "基本面改善":1.5, "市场关注度":1.5,
    "risk":"极高(*ST,非标审计+内控否定+股权拍卖+近面值)",
    "rationale":"江阴国资入主预期,但非标审计+内控否定+股权拍卖+近面值,退市风险最高;换手0.34%极低。",
    "catalyst":"国资入主+保壳",
    "risk_note":"非标审计;内控否定;股权拍卖;面值退市边缘"},
}

order = ["600079","002726","000711","000838","600337","002168","600381","300147","002542","300027","300020","600340","600370"]

rows=[]
for code in order:
    s=scores[code]; q=quotes[code]
    total=sum(s[k]*W[k] for k in W)
    rows.append((code, s, q, total))

# ---- HTML ----
def bar(v):  # v in 1..5
    pct=int(v/5*100)
    return f'<div style="background:#2a2f3a;border-radius:4px;height:12px;width:120px;display:inline-block;vertical-align:middle"><div style="background:#4aa3ff;height:12px;border-radius:4px;width:{pct}%"></div></div>'

html=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<style>
body{{background:#0e1116;color:#e6e6e6;font-family:-apple-system,'Segoe UI',Roboto,'Microsoft YaHei',sans-serif;margin:0;padding:24px}}
h1{{color:#fff;font-size:22px;border-left:4px solid #4aa3ff;padding-left:12px}}
h2{{color:#ffd166;font-size:17px;margin-top:28px}}
.sub{{color:#9aa4b2;font-size:13px}}
table{{border-collapse:collapse;width:100%;margin-top:12px;font-size:13px}}
th,td{{border:1px solid #2a2f3a;padding:8px 10px;text-align:center}}
th{{background:#1a2030;color:#cdd6e4}}
tr:nth-child(even){{background:#161b24}}
.rank{{color:#ffd166;font-weight:bold;font-size:15px}}
.card{{background:#161b24;border:1px solid #2a2f3a;border-radius:10px;padding:16px;margin-top:14px}}
.tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;margin-right:6px}}
.t-new{{background:#1b4d2e;color:#7CFC9B}}
.t-st{{background:#3a2f12;color:#ffd166}}
.t-xst{{background:#4d1b1b;color:#ff8a8a}}
.dim{{color:#9aa4b2;font-size:12px}}
.note{{color:#ff9b9b;font-size:12px}}
.ok{{color:#7CFC9B;font-size:12px}}
</style></head><body>
<h1>ST/*ST 反转预期 · 全13只统一优先级排序（工作流分析）</h1>
<p class="sub">数据基准：2026-08-20 收盘实时行情（腾讯 qt.gtimg.cn 逐只核验）｜评分模型：退市风险30% ＋ 重组预期30% ＋ 基本面改善25% ＋ 市场关注度15%｜新增标的：ST京蓝(000711)、ST人福(600079)</p>

<h2>一、最终排序总表</h2>
<table>
<tr><th>优先级</th><th>标的</th><th>状态</th><th>现价</th><th>涨跌幅</th><th>总市值(亿)</th><th>换手%</th><th>四维综合分</th></tr>
'''
for i,(code,s,q,t) in enumerate(rows,1):
    tag = "t-xst" if q["status"]=="*ST" else "t-st"
    html+=f'''<tr><td class="rank">{i}</td><td style="text-align:left"><b>{q["name"]}</b> {code}</td>
<td><span class="tag {tag}">{q["status"]}</span></td><td>{q["price"]:.2f}</td><td>{q["chg_pct"]:+.2f}%</td>
<td>{q["total_cap_yi"]:.1f}</td><td>{q["turnover"]:.2f}</td><td><b>{t:.3f}</b></td></tr>'''

html+='''</table>
<p class="sub">注：退市风险分越高=风险越低(越安全)；综合分=四维加权。标 <span class="tag t-xst">*ST</span> 为退市风险警示，保壳失败可归零。</p>

<h2>二、新增标的速览（本次加入）</h2>
<div class="card">
<span class="tag t-new">NEW</span><b>ST人福 600079</b> — 综合第1。规范类ST(信披违规,非财务退市)，招商局央企入主、违规整改完，麻醉龙头主业正常，唯一正PE(15.32)，摘帽预计2027.1。风险可控性全场最佳。
</div>
<div class="card">
<span class="tag t-new">NEW</span><b>ST京蓝 000711</b> — 综合第3。重整已于2023.12执行完毕(ST非*ST)，中报营收+98%、归母扭亏，拟更名"铟靶新材"申请摘帽，热度高。但扣非仅570万、盈利靠一次性收益、现金流为负、资产注入逾期。
</div>

<h2>三、逐只明细（按优先级）</h2>
'''
for i,(code,s,q,t) in enumerate(rows,1):
    tag = "t-xst" if q["status"]=="*ST" else "t-st"
    isnew = "t-new" if code in ("600079","000711") else ""
    newbadge = '<span class="tag t-new">NEW</span>' if code in ("600079","000711") else ""
    html+=f'''
<div class="card">
<div style="font-size:15px"><span class="rank">P{i}</span> {newbadge}<b>{q["name"]}</b> <span class="tag {tag}">{q["status"]}</span> <span class="dim">{code}｜现价{q["price"]:.2f}｜{q["chg_pct"]:+.2f}%｜市值{q["total_cap_yi"]:.1f}亿｜换手{q["turnover"]:.2f}%</span></div>
<div style="margin-top:8px">
<span class="dim">退市风险</span> {bar(s["退市风险"])} {s["退市风险"]:.1f}　
<span class="dim">重组预期</span> {bar(s["重组预期"])} {s["重组预期"]:.1f}　
<span class="dim">基本面改善</span> {bar(s["基本面改善"])} {s["基本面改善"]:.1f}　
<span class="dim">市场关注度</span> {bar(s["市场关注度"])} {s["市场关注度"]:.1f}
</div>
<div style="margin-top:8px"><b>风险等级：</b><span class="note">{s["risk"]}</span></div>
<div style="margin-top:6px"><b>排序理由：</b>{s["rationale"]}</div>
<div style="margin-top:6px"><b>核心催化：</b><span class="ok">{s["catalyst"]}</span></div>
<div style="margin-top:6px"><b>主要风险：</b><span class="note">{s["risk_note"]}</span></div>
</div>'''

html+='''
<h2>四、关键结论</h2>
<div class="card">
<b>1. 两只新股均进入前三：</b>ST人福(第1)、ST京蓝(第3)——二者均为<b>ST（其他风险警示/规范类）</b>，非*ST，退市风险显著低于榜单后半段的*ST群体，且具备明确的基本面改善信号（人福业绩回升、京蓝中报扭亏），故排序靠前。<br><br>
<b>2. 风险分层清晰：</b>前7名以ST（低退市风险）为主+少数程序最先进的*ST（发展/春天）；后6名均为*ST，保壳失败可归零，建议回避或极轻仓。<br><br>
<b>3. 催化确定性排序：</b>协议/草案已签（龙大、发展、美克、惠程）> 审核/摘帽在途（人福、京蓝、春天、香雪）> 仅预期（中岩、华幸、三房、华谊、银江）。
</div>
<p class="note" style="margin-top:20px">⚠️ 免责声明：本报告为研究性排序与框架讨论，<b>不构成任何投资建议</b>，不代客下单。ST/*ST 退市与变脸风险极高，*ST 类保壳失败可能本金归零。请独立决策、严控仓位。</p>
</body></html>'''

out=r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST13_final_priority_20260820.html"
with open(out,"w",encoding="utf-8") as fp:
    fp.write(html)
print("报告已生成:", out)
print("\n最终排序:")
for i,(code,s,q,t) in enumerate(rows,1):
    print(f" P{i}. {q['name']}({code}) [{q['status']}] 综合={t:.3f}")
