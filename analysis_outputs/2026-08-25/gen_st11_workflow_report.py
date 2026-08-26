# -*- coding: utf-8 -*-
"""生成11只截图ST股的工作流评估与优先级报告"""
import os, json

OUT = r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_11_workflow_priority_20260820.html"

# 实时行情（8/20 收盘，腾讯）
quotes = {
    '000838': {'name':'*ST发展','price':'2.75','chg':'+4.96%','cap':'28.98','turn':'441835'},
    '002726': {'name':'ST龙大','price':'2.95','chg':'+10.07%','cap':'40.13','turn':'1409080'},
    '002168': {'name':'ST惠程','price':'3.82','chg':'+1.60%','cap':'29.96','turn':'40381'},
    '002542': {'name':'*ST中岩','price':'1.82','chg':'+4.60%','cap':'32.02','turn':'405145'},
    '300027': {'name':'ST华谊','price':'1.77','chg':'+0.57%','cap':'45.42','turn':'328625'},
    '300147': {'name':'*ST香雪','price':'7.09','chg':'+2.31%','cap':'46.61','turn':'89832'},
    '600337': {'name':'ST美克','price':'3.12','chg':'+3.65%','cap':'44.83','turn':'202320'},
    '600340': {'name':'*ST华幸','price':'1.09','chg':'+0.93%','cap':'42.44','turn':'381963'},
    '600370': {'name':'*ST三房','price':'1.47','chg':'+2.08%','cap':'59.13','turn':'138536'},
    '300020': {'name':'ST银江','price':'3.36','chg':'+1.51%','cap':'25.76','turn':'76288'},
    '600381': {'name':'*ST春天','price':'4.91','chg':'+9.35%','cap':'28.82','turn':'139918'},
}

# 四维评分与关键信息（退市风险30%、重组预期30%、基本面改善25%、市场关注度15%）
stocks = [
    {
        'code':'002726','status':'ST','driver':'预重整（27家报名，国资代偿转债）',
        'scores':[3,4,4,5],'total':3.85,
        'key':['被ST因内控否定+连续三年扣非为负','2023-2025累计亏23亿，实控人戴学斌被刑拘','莱阳国资3.63亿代偿转债，7/30共27家意向投资人报名','核心资产1250万头/年屠宰产能，绑定海底捞/肯德基/麦当劳'],
        'risk':'预重整尚未被法院正式受理；持续亏损；控股股东股权被司法拍卖'
    },
    {
        'code':'000838','status':'*ST','driver':'已签重整协议（景行新能6.26亿入主）',
        'scores':[3,5,3,4],'total':3.75,
        'key':['2025年末净资产-2.00亿，扣除后营收2.82亿，踩退市线','8/7与景行新能签重整投资协议，1元/股受让6.26亿股','景行新能为中稀天马实控人林平夫妇控制','承诺2026年末净资产转正、营收≥3亿，锁定期60月'],
        'risk':'*ST身份；年底前能否完成重整及净资产转正存不确定性；股本大幅稀释'
    },
    {
        'code':'600337','status':'ST','driver':'签产投（AI算力跨界）',
        'scores':[2,5,4,4],'total':3.70,
        'key':['7/22与铜光互联产融联合体签重整投资协议，投资款10.72亿','牵头方小磁投资实控人李少锋即万德溙实控人','万德溙为英伟达/Google/Meta供应高速铜缆/AEC','重整后"家居+高速铜光互联"双主业'],
        'risk':'跨界协同待验证；2026上半年预亏3.5-4.5亿；原收购方案终止，未来资产注入或36月后；类借壳监管风险'
    },
    {
        'code':'600381','status':'*ST','driver':'听花酒营收达标',
        'scores':[3,4,3,5],'total':3.60,
        'key':['2025年营收3.43亿，扣除后3.33亿，踩线过3亿','4/29同步申请摘星+摘帽，目前交易所终审阶段','主营高端白酒听花酒+冬虫夏草，资产负债率低','5/19年报问询函已两度延期，6月下旬回复'],
        'risk':'2026上半年预亏；若全年扣非营收<3亿或净利为负将退市；监管可能追溯调减2025Q4收入；审核结果不确定'
    },
    {
        'code':'002168','status':'ST','driver':'预重整+债权人申请重整',
        'scores':[3,4,3,3],'total':3.30,
        'key':['2023-2025连续扣非为负+持续经营不确定性','8/14二债会表决通过重整计划草案','7/30出资人组会议通过权益调整方案','待证监会无异议函+最高法同意批复'],
        'risk':'尚未收到法院受理重整申请；若受理将被实施*ST；重整失败可能破产退市'
    },
    {
        'code':'300147','status':'*ST','driver':'预重整（广药资本）',
        'scores':[4,3,3,3],'total':3.25,
        'key':['连续五年亏损，总负债67亿，2026Q1净资产-4.71亿','7/3广药资本中选投资人，但协议尚未签署','预重整已四次延期，最新期限7/11已逾期','广药集团产业协同强（中药+细胞治疗管线）'],
        'risk':'中选后协议迟迟未签，谈判可能破裂；预重整程序严重滞后；若2026年重整未获批且净资产为负将退市'
    },
    {
        'code':'002542','status':'*ST','driver':'预重整（成都国资）',
        'scores':[4,2,2,3],'total':2.75,
        'key':['2025年末净资产为负，2026上半年预亏1.2-1.8亿','7/17董事会通过拟申请预重整/重整，尚需股东会','成都兴城（成都国资）持股29.27%，曾多次担保输血','有低空经济、数据中心概念'],
        'risk':'仅"拟申请"，法院尚未受理；资产负债率103.56%；现金2.21亿难覆盖一年内到期债务10.72亿'
    },
    {
        'code':'600340','status':'*ST','driver':'债务重组+预重整',
        'scores':[5,2,1,2],'total':2.65,
        'key':['2025年末净资产-177.43亿，累计亏超700亿','6月确定重整投资人（杭州骋风而来+南阳木兰花），协议未签','债务重组1926.69亿，保交楼基本完成','若2026年末净资产无法转正将退市'],
        'risk':'净资产缺口巨大；重整投资协议未签；平安追索64亿仲裁；主营地产造血弱'
    },
    {
        'code':'600370','status':'*ST','driver':'国资冻结控股',
        'scores':[5,2,1,2],'total':2.55,
        'key':['2025年报被出具无法表示意见+内控否定意见','控股股东三房巷集团73.76%持股全被质押/司法冻结','累计将被司法拍卖3.84亿股（9.55%）','子公司逾期债务5.31亿，股价逼近1元面值'],
        'risk':'非标审计意见极难消除；退市风险高；股权拍卖；基本面未实质好转（Q1扣非仍亏）'
    },
    {
        'code':'300027','status':'ST','driver':'预重整（影视化债）',
        'scores':[4,2,1,2],'total':2.35,
        'key':['2025年营收3.1亿，归母净利-3.3亿','4/23法院批准预重整，7/7公告6家意向投资人报名','8/7全资子公司华谊电影被申请重整+协同审理','2018-2024连续七年亏损，累计超82亿'],
        'risk':'重整投资人尚未确定；子公司重整增加复杂性；若受理公司重整将被*ST；影视寒冬，造血能力差'
    },
    {
        'code':'300020','status':'ST','driver':'内控整改摘帽预期',
        'scores':[2,2,3,2],'total':2.25,
        'key':['三重其他风险警示：行政处罚、持续经营不确定性、违规担保2.36亿未解除','原实控人王辉历史违规，新管理层姚成岭整改','智慧城市/智慧交通主业在手订单存在'],
        'risk':'2026Q1亏7114万，全年扭亏难度大；违规担保2.36亿未解除；持续经营不确定性短期难消；摘帽预期延后'
    },
]

# 按total排序
stocks.sort(key=lambda x: x['total'], reverse=True)

# 生成HTML
html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>11只ST/*ST工作流评估与优先级排序</title>
<style>
* {box-sizing:border-box;margin:0;padding:0}
body {background:#0f1115;color:#e6e6e6;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.6;padding:24px}
.wrap {max-width:1100px;margin:0 auto}
h1 {font-size:22px;color:#fff;margin-bottom:4px}
h2 {font-size:16px;color:#ffd24a;margin:22px 0 10px;border-left:4px solid #ffd24a;padding-left:10px}
h3 {font-size:14px;color:#fff;margin:12px 0 6px}
.sub {color:#9aa0a6;font-size:12px;margin-bottom:10px}
.disclaimer {background:#2a1f1a;border:1px solid #5a3a2a;color:#ffb38a;padding:10px 14px;border-radius:8px;font-size:12px;margin:12px 0}
.card {background:#1a1d24;border:1px solid #2a2e37;border-radius:10px;padding:16px;margin:12px 0}
.workflow {display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;font-size:12px}
.workflow span {background:#262a33;padding:4px 10px;border-radius:6px;color:#9aa0a6}
.workflow .active {background:#3a3f4a;color:#fff}
table {width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
th,td {padding:8px;border-bottom:1px solid #2a2e37;text-align:left;vertical-align:top}
th {color:#ffd24a;font-weight:600;background:#161a20}
.rank {font-size:16px;font-weight:800;color:#ffd24a}
.score {font-size:13px;font-weight:700;color:#9be29b}
.badge-st {background:#3a5a3a;color:#9be29b;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:700}
.badge-ast {background:#5a2a2a;color:#ff9b9b;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:700}
.scorebar {display:flex;align-items:center;gap:6px;margin:3px 0}
.scorebar .track {flex:1;height:8px;background:#262a33;border-radius:4px;overflow:hidden}
.scorebar .fill {height:100%;border-radius:4px}
.dims {display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px}
.dim {background:#161a20;border-radius:6px;padding:8px;text-align:center;border:1px solid #2a2e37}
.dim .n {font-size:18px;font-weight:800}
.dim .l {font-size:11px;color:#9aa0a6;margin-top:2px}
ul.key {padding-left:16px;font-size:12px;color:#c2c7ce;margin:8px 0}
ul.key li {margin:4px 0}
.risk {font-size:12px;color:#ff9b9b;margin-top:8px;border-top:1px solid #3a2a2a;padding-top:8px}
footer {margin-top:24px;color:#666;font-size:11px;text-align:center}
@media(max-width:720px){.dims{grid-template-columns:repeat(2,1fr)}}
</style></head>
<body><div class="wrap">

<h1>11只ST/*ST工作流评估与优先级排序</h1>
<div class="sub">项目工作流：提示词工程师 → 高级PM → 编排者 → 数据工程师/新闻简报 → 投资研究员 → 现实检验者 → 终稿 | 数据复核 2026-08-20 收盘</div>
<div class="disclaimer">⚠️ 本报告为研究性评估，<b>不构成投资建议，不代客下单</b>。ST/*ST风险极高，*ST可能直接退市致本金归零，请独立决策、严控仓位。</div>

<h2>一、工作流执行摘要</h2>
<div class="card">
<div class="workflow">
  <span>1 输入网关</span><span>2 提示词工程师</span><span class="active">3 数据工程师</span><span class="active">4 投资研究员</span><span class="active">5 现实检验者</span><span>6 法务合规员</span><span>7 终稿</span>
</div>
<p style="font-size:12px;color:#c2c7ce;margin-top:8px">数据工程师完成：截图OCR提取、腾讯实时行情核验、最新公告/重整进展检索；投资研究员完成：退市风险/重组预期/基本面/市场关注度四维评分；现实检验者完成：行情与公告交叉验证、风险提示。</p>
</div>

<h2>二、实时行情快照（8/20 收盘）</h2>
<div class="card">
<table>
<tr><th>代码</th><th>名称</th><th>现价</th><th>涨跌幅</th><th>总市值(亿)</th><th>成交量(手)</th><th>驱动</th></tr>"""

for code, q in quotes.items():
    status = 'badge-ast' if q['name'].startswith('*') else 'badge-st'
    html += f"""
<tr><td>{code}</td><td><span class="{status}">{q['name']}</span></td><td>{q['price']}</td><td>{q['chg']}</td><td>{q['cap']}</td><td>{q['turn']}</td><td>{next((s['driver'] for s in stocks if s['code']==code), '')}</td></tr>"""

html += """
</table>
</div>

<h2>三、优先级排序（综合分 = 退市风险30% + 重组预期30% + 基本面改善25% + 市场关注度15%）</h2>
"""

colors = ['#e0483e','#f5a623','#ffd24a','#9be29b','#4ecdc4']
for i, s in enumerate(stocks, 1):
    q = quotes[s['code']]
    risk, reorg, funda, market = s['scores']
    total = s['total']
    # 颜色映射：综合分
    if total >= 3.5: rank_color = '#9be29b'
    elif total >= 3.0: rank_color = '#ffd24a'
    elif total >= 2.5: rank_color = '#f5a623'
    else: rank_color = '#e0483e'
    html += f"""
<div class="card">
  <table>
    <tr>
      <td style="width:60px"><div class="rank" style="color:{rank_color}">P{i}</div></td>
      <td style="width:120px"><b>{q['name']}</b><br><span style="font-size:11px;color:#9aa0a6">{s['code']}</span></td>
      <td style="width:80px">现价 <b>{q['price']}</b><br>涨幅 {q['chg']}</td>
      <td style="width:80px">总市值<br><b>{q['cap']}亿</b></td>
      <td style="width:90px">综合得分<br><span class="score">{total:.2f}</span></td>
      <td>驱动：{s['driver']}</td>
    </tr>
  </table>
  <div class="dims">
    <div class="dim"><div class="n" style="color:{colors[5-risk]}">{risk}</div><div class="l">退市风险<br>（1=低，5=高）</div></div>
    <div class="dim"><div class="n" style="color:{colors[reorg-1]}">{reorg}</div><div class="l">重组预期</div></div>
    <div class="dim"><div class="n" style="color:{colors[funda-1]}">{funda}</div><div class="l">基本面改善</div></div>
    <div class="dim"><div class="n" style="color:{colors[market-1]}">{market}</div><div class="l">市场关注度</div></div>
  </div>
  <h3>关键信息</h3>
  <ul class="key">"""
    for k in s['key']:
        html += f"<li>{k}</li>"
    html += f"""
  </ul>
  <div class="risk"><b>主要风险：</b>{s['risk']}</div>
</div>
"""

html += """
<h2>四、排序理由总览</h2>
<div class="card">
<table>
<tr><th>优先级</th><th>标的</th><th>核心排序理由</th></tr>
<tr><td>P1</td><td>ST龙大</td><td>ST非*ST，核心屠宰产能+B端渠道是硬资产；27家投资人报名+莱阳国资代偿转债，重整预期强；今日涨停，市场热度最高。</td></tr>
<tr><td>P2</td><td>*ST发展</td><td>重整投资协议已签，景行新能入主确定性较高；但*ST且净资产为负，稀释大，排龙大之后。</td></tr>
<tr><td>P3</td><td>ST美克</td><td>产投协议已签，万德溙AI算力铜缆概念热门；但跨界协同与业绩亏损压制，略低于前二。</td></tr>
<tr><td>P4</td><td>*ST春天</td><td>营收踩线达标，摘星摘帽申请已进入交易所终审；但2026上半年亏损+问询函风险，存在审核不确定性。</td></tr>
<tr><td>P5</td><td>ST惠程</td><td>二债会通过重整计划草案，程序推进较快；但尚未获法院受理，若受理将变*ST。</td></tr>
<tr><td>P6</td><td>*ST香雪</td><td>广药资本中选，产业协同想象空间大；但协议未签+预重整四次延期逾期，卡壳风险高。</td></tr>
<tr><td>P7</td><td>*ST中岩</td><td>成都国资背景+低空/数据中心概念；但仅是"拟申请"预重整，净资产为负且持续亏损。</td></tr>
<tr><td>P8</td><td>*ST华幸</td><td>债务重组规模大，重整投资人已确定；但净资产缺口-177亿，协议未签，保壳难度极大。</td></tr>
<tr><td>P9</td><td>*ST三房</td><td>江阴国资入主预期；但非标审计+内控否定+股权拍卖+近面值，退市风险极高。</td></tr>
<tr><td>P10</td><td>ST华谊</td><td>影视IP有知名度；但七年累亏82亿，重整投资人未定，造血能力极差。</td></tr>
<tr><td>P11</td><td>ST银江</td><td>智慧城市主业仍在；但三重ST叠加，违规担保2.36亿未解，2026扭亏困难，摘帽最遥远。</td></tr>
</table>
</div>

<h2>五、现实检验者特别提示</h2>
<div class="card">
<ul class="key">
<li>所有价格经腾讯实时行情核验（8/20收盘），与截图一致。</li>
<li><b>*ST京化、*ST南置</b>不在本次截图中；截图11只里<b>*ST发展、*ST中岩、*ST香雪、*ST华幸、*ST三房、*ST春天</b>为*ST（退市风险警示），其余5只为ST。</li>
<li>重整/预重整进度以最新公告为准：ST惠程二债会通过、*ST发展协议已签、ST美克协议已签，这三只程序最先进；*ST香雪、*ST华幸、*ST三房协议未签或仅预期，不确定性最大。</li>
<li>本排序按"催化确定性"加权，不代表绝对投资价值；P8-P11建议回避或极轻仓博弈。</li>
</ul>
</div>

<footer>本报告由工作流多角色协作生成，仅供研究与风控参考 · 市场有风险，投资须谨慎 · 非投资建议</footer>
</div></body></html>"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('written', OUT, 'bytes', len(html))
