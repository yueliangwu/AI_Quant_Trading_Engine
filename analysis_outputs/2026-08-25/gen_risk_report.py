# -*- coding: utf-8 -*-
"""生成 ST/*ST 反转预期风险与近5年摘帽成功率统计报告（纯内联，无外部依赖）"""
import os

OUT = r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_reversal_risk_report_20260820.html"

# ---- 数据（来自东方财富/同花顺/证券时报/财经 多源交叉，2026-08-20 复核）----
# 摘帽后行情成功率（口径B：已成功摘帽样本）
quote_win = [
    ("摘帽前1个月(埋伏期)", 87, 20.0, "资金提前抢跑，确定性最高"),
    ("摘帽首日",            80, 7.7, "多数高开，涨停率超60%"),
    ("摘帽后5日",           63, 11.8, "分化开始"),
    ("摘帽后1个月",         56, 5.4, "已接近五五开"),
    ("摘帽后3个月",         49, 0.0, "完全看基本面，赌性退潮"),
]

# 逐年摘帽数 / 上涨数
year_stat = [
    ("2021", 88, 71, 80.7),
    ("2024", 30, None, None),
    ("2025", 50, None, None),  # 同花顺：50家脱帽，平均涨幅75%
]

# 逐年退市数（口径A分母背景）
delist_year = [("2022",46),("2023",45),("2024",52),("2025",31)]

# 在榜 vs 摘帽（2025年末）
onboard_st = 81
onboard_ast = 96
delist_2025 = 50

# 13只清单风险分级（来自上一轮修正版）
stocks = [
    ("ST长园","600525","ST","5.57",1),
    ("ST宁科","600165","ST","3.23",2),
    ("ST华闻","000793","ST","2.15",3),
    ("*ST京化","600889","*ST","13.40",3),
    ("ST中装","002822","ST","3.19",5),
    ("ST天际","002759","ST","17.62",6),
    ("ST万邦","002082","ST","9.97",7),
    ("ST东尼","603595","ST","26.00",8),
    ("ST西王","000639","ST","1.87",9),
    ("ST京蓝","000711","ST","6.11",9),
    ("ST嘉澳","603822","ST","57.76",9),
    ("ST中珠","600568","ST","2.21",12),
    ("*ST南置","002305","*ST","2.11",13),
]

def bar_row(label, pct, color, note=""):
    return f"""
    <div class="row">
      <div class="rlabel">{label}</div>
      <div class="track"><div class="fill" style="width:{pct}%;background:{color}"></div><span class="pct">{pct}%</span></div>
      <div class="note">{note}</div>
    </div>"""

quote_bars = "".join(bar_row(r[0], r[1], "#e0483e" if r[1]>=60 else ("#f5a623" if r[1]>=50 else "#888"), r[3]) for r in quote_win)

# 风险清单
risks = [
    ("1. 退市归零（最致命）", "*ST 若保壳失败直接退市，本金可能归零。退市后转三板，日均成交<10万元，几乎无法退出。2024年52家退市创新高，面值退市占73%。", "高危"),
    ("2. 利好出尽 / 见光死", "摘帽前1月平均已涨20%，前期涨幅>50%的标的摘帽后下跌概率升至40%+。你买在高位，正好接盘。", "高危"),
    ("3. 报表式保壳 ≠ 实质重生", "大量公司靠突击增收、1元剥离亏损资产、债务豁免保壳，非实质性改善，后续会重新ST。科新发展7次保壳、文投控股7次、中毅达6次。", "中"),
    ("4. 摘帽不=风险出清", "存在『摘星不摘帽』：如ST宁科、ST中装、ST云网，财务达标但其他风险警示未消，仍带ST。撤销警示只是阶段性改善。", "中"),
    ("5. 游资操纵 / 接力收割", "*ST东易9-11月涨124%（23%→99%→14%），11月20日见顶后跌45.86%。典型游资快进快出，散户接最后一棒。", "高危"),
    ("6. 审计非标黑天鹅", "*ST创兴营收突击到3.21亿，仍因年报『无法表示意见』直接退市；*ST国化收入预告3.3亿、审计仅2.94亿跌破红线。", "高危"),
    ("7. 5%涨跌停限制的双刃剑", "ST每日±5%限制，单边下跌时难逃顶、流动性受限；暴涨时也很难上车，波动被锁死在窄幅。", "中"),
    ("8. 信息不对称", "重整进展、摘帽时点、监管问询均属非公开节奏，散户天然滞后，容易被『预期』反复割。", "中"),
]

risk_cards = "".join(f"""
<div class="risk risk-{r[2]}">
  <div class="risk-head"><span class="tag tag-{r[2]}">{r[2]}</span><b>{r[0]}</b></div>
  <div class="risk-body">{r[1]}</div>
</div>""" for r in risks)

stock_rows = "".join(f"""
<tr class="{'row-ast' if s[2]=='*ST' else ''}">
  <td>{s[0]}</td><td>{s[1]}</td>
  <td><span class="badge {'badge-ast' if s[2]=='*ST' else 'badge-st'}">{s[2]}</span></td>
  <td>{s[3]}</td><td>优先级 {s[4]}</td>
</tr>""" for s in stocks)

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ST/*ST反转预期：风险与近5年摘帽成功率统计</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f1115;color:#e6e6e6;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.6;padding:28px}}
.wrap{{max-width:960px;margin:0 auto}}
h1{{font-size:24px;color:#fff;margin-bottom:4px}}
h2{{font-size:18px;color:#ffd24a;margin:28px 0 12px;border-left:4px solid #ffd24a;padding-left:10px}}
.sub{{color:#9aa0a6;font-size:13px;margin-bottom:8px}}
.card{{background:#1a1d24;border:1px solid #2a2e37;border-radius:10px;padding:18px;margin:14px 0}}
.disclaimer{{background:#2a1f1a;border:1px solid #5a3a2a;color:#ffb38a;padding:12px 16px;border-radius:8px;font-size:13px}}
.row{{display:grid;grid-template-columns:140px 1fr;gap:10px;align-items:center;margin:10px 0}}
.rlabel{{font-size:13px;color:#cfd3d8}}
.track{{position:relative;background:#262a33;border-radius:6px;height:26px;overflow:hidden}}
.fill{{height:100%;border-radius:6px;transition:width .4s}}
.pct{{position:absolute;right:8px;top:3px;font-size:12px;color:#fff;font-weight:700}}
.note{{grid-column:1/3;font-size:12px;color:#8b9098;margin-top:-4px}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}}
th,td{{padding:8px 10px;border-bottom:1px solid #2a2e37;text-align:left}}
th{{color:#ffd24a;font-weight:600}}
.row-ast{{background:rgba(224,72,62,.08)}}
.badge{{padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700}}
.badge-st{{background:#3a5a3a;color:#9be29b}}
.badge-ast{{background:#5a2a2a;color:#ff9b9b}}
.risk{{border-radius:8px;padding:12px 14px;margin:10px 0;border:1px solid #2a2e37;background:#161a20}}
.risk-高危{{border-left:4px solid #e0483e}}
.risk-中{{border-left:4px solid #f5a623}}
.risk-head{{margin-bottom:6px}}
.risk-head b{{color:#fff;font-size:14px}}
.tag{{font-size:11px;padding:1px 7px;border-radius:4px;margin-right:8px;font-weight:700}}
.tag-高危{{background:#5a2a2a;color:#ff9b9b}}
.tag-中{{background:#4a3a1a;color:#ffd24a}}
.risk-body{{font-size:13px;color:#c2c7ce}}
.kpi{{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}}
.kpi div{{flex:1;min-width:150px;background:#161a20;border:1px solid #2a2e37;border-radius:8px;padding:12px;text-align:center}}
.kpi .n{{font-size:26px;font-weight:800;color:#ffd24a}}
.kpi .l{{font-size:12px;color:#9aa0a6;margin-top:4px}}
footer{{margin-top:30px;color:#666;font-size:12px;text-align:center}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:680px){{.grid2{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="wrap">

<h1>ST/*ST 反转预期：风险全景 & 近5年摘帽成功率统计</h1>
<div class="sub">数据来源：东方财富 / 同花顺 / 证券时报 / 财经 多源交叉 · 复核日期 2026-08-20 · 行情口径为已成功摘帽样本统计</div>

<div class="disclaimer">⚠️ 本研究为信息整理与统计，<b>不构成任何投资建议，不代客下单</b>。ST/*ST 属高风险品种，*ST 可能直接退市致本金归零，请独立决策、严控仓位。</div>

<h2>一、你能不能买？先分清两级风险</h2>
<div class="card">
<p style="margin-bottom:10px">ST（其他风险警示）：经营/内控异常，<b>暂无直接退市威胁</b>，但可能长期横盘或重新戴帽。</p>
<p style="margin-bottom:10px">*ST（退市风险警示）：已触及财务/面值等<b>退市红线</b>，保壳失败即退市，本金可能归零——<b>这是最高危的一档</b>。</p>
<p>我们上一轮清单里，<b>*ST京化(600889)、*ST南置(002305) 是 *ST</b>，风险等级远高于清单里其余 11 只纯 ST，切勿混为一谈。</p>
</div>

<h2>二、近5年摘帽「行情成功率」（已摘帽样本）</h2>
<div class="card">
<div class="kpi">
  <div><div class="n">87%</div><div class="l">摘帽前1月上涨概率<br>（埋伏期，资金抢跑）</div></div>
  <div><div class="n">56%</div><div class="l">摘帽后1月上涨概率<br>（已接近五五开）</div></div>
  <div><div class="n">49%</div><div class="l">摘帽后3月上涨概率<br>（完全看基本面）</div></div>
</div>
{quote_bars}
<p style="font-size:12px;color:#8b9098;margin-top:10px">注：上述为「已知会摘帽」的事后样本统计。事前押注反转的真实胜率远低于此，因大量 ST 根本摘不了帽、直接退市（见第三节）。</p>
</div>

<h2>三、更残酷的「摘帽成功率」（戴帽后能否毕业）</h2>
<div class="grid2">
<div class="card">
<b style="color:#ffd24a">2025年末在榜 vs 当年摘帽</b>
<div class="kpi" style="margin-top:8px">
  <div><div class="n">177</div><div class="l">在榜 ST+*ST<br>(81+96)</div></div>
  <div><div class="n">50</div><div class="l">当年成功脱帽</div></div>
</div>
<p style="font-size:13px;color:#c2c7ce">→ 单年「毕业率」约 <b style="color:#ffd24a">28%</b>，即约 3/4 的 ST 当年仍带帽。</p>
</div>
<div class="card">
<b style="color:#ffd24a">财务类 *ST 终局（2025年报后）</b>
<p style="font-size:13px;color:#c2c7ce;margin-top:6px">沪主板首批 25 家：仅 <b style="color:#9be29b">4 家完全摘帽</b>，8 家已锁定退市。<br>深主板 31 家：6 家保壳成功，4 家明确退市。</p>
<p style="font-size:13px;color:#ff9b9b;margin-top:6px">→ 约 <b>1/3 财务类 *ST 最终退市</b>。</p>
</div>
</div>

<h2>四、逐年退市数量（常态化出清加速）</h2>
<div class="card">
<div class="kpi">
  <div><div class="n">46</div><div class="l">2022年退市</div></div>
  <div><div class="n">45</div><div class="l">2023年退市</div></div>
  <div><div class="n">52</div><div class="l">2024年退市<br>(历史新高)</div></div>
  <div><div class="n">31</div><div class="l">2025年退市<br>(主动退市增多)</div></div>
</div>
<p style="font-size:12px;color:#8b9098">退市新规（2024.4）后「应退尽退」常态化，壳价值从数十亿跌向归零，炒壳=赌博。</p>
</div>

<h2>五、ST/*ST 八类核心风险</h2>
{risk_cards}

<h2>六、你清单里 13 只的风险分级</h2>
<div class="card">
<table>
<tr><th>标的</th><th>代码</th><th>状态</th><th>现价(8/20)</th><th>优先级</th></tr>
{stock_rows}
</table>
<p style="font-size:12px;color:#ff9b9b;margin-top:8px">红底 = *ST（退市风险警示），保壳失败即退市，仓位须最轻甚至回避；其余为 ST（其他风险警示）。</p>
</div>

<h2>七、若一定要参与，最低防线（非建议，仅风控框架）</h2>
<div class="card">
<ul style="font-size:13px;color:#c2c7ce;padding-left:18px;line-height:1.9">
<li>只拿 <b>亏得起</b> 的小仓位，绝不用主仓/杠杆赌 ST；</li>
<li>优先选 <b>ST（非*ST）</b> 且重整/摘帽逻辑已落地的，回避仍在退市边缘的 *ST；</li>
<li>买点选 <b>摘帽申请已受理、尚未复牌炒作</b> 的早段，不追摘帽前已涨50%+的；</li>
<li>设 <b>硬止损</b>（如-15%~-20%），且对标的有「重新戴帽/退市」的退出预案；</li>
<li>分散，不单押一只；警惕换手异常放大、游资接力迹象；</li>
<li>每条买入前，用实时行情复核 ST 状态与最新公告，不凭记忆。</li>
</ul>
</div>

<footer>本报告由数据分析生成，仅供研究与风控参考 · 市场有风险，投资须谨慎 · 非投资建议</footer>
</div></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", OUT)
print("bytes:", len(html))
