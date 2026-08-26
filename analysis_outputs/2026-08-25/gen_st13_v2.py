# -*- coding: utf-8 -*-
"""基于2026.7.6新规重评13只ST/*ST风险等级与优先级，生成HTML报告"""
import json

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st13_v2.json","r",encoding="utf-8") as fp:
    q = {r["code"].strip(): r for r in json.load(fp)}

# 研判数据：priority, risk_level(中/高/极高), band(10%/20%), four_dims[退市,重组,基本面,关注],
# catalyst, risks[], note
data = {
"600079": dict(p=1, rl="中", band="10% (主板ST)",
    fd=[4.5,4.4,4.6,4.2],
    cat="央企中国医药入主+资金占用/违规担保整改完毕，麻醉龙头，A股ST里唯一正PE，摘帽条件最扎实。",
    risks=["摘帽需待整改满12个月(预计2027.1)，时间窗较远","定增摊薄短期EPS","麻醉集采降价压力"],
    note="风险可控性最佳，但仍是ST状态、10%波动，非无风险。"),
"002726": dict(p=2, rl="中", band="10% (主板ST)",
    fd=[3.6,4.8,3.4,4.6],
    cat="27家预重整投资人报名+莱阳国资代偿转债，重整预期最热；1250万头/年屠宰产能+海底捞/肯德基渠道是硬资产。",
    risks=["★修正：仍是ST未摘帽(8/20涨10.07%即ST新规下正常涨停)","预重整仅意向报名、未定案可黄/可拖","H1仍亏损PE为负，翻倍后预期充分"],
    note="此前误判'已摘帽'已撤回；翻倍全程在ST状态下完成，风险未降。"),
"000711": dict(p=3, rl="中", band="10% (主板ST)",
    fd=[3.8,4.3,3.6,4.0],
    cat="重整已执行完毕+中报扭亏+拟申请更名摘帽，鑫联科技资产注入预期。",
    risks=["扭亏水分大：归母7420万主要靠处置重整股票收益7600万(不可持续)","扣非仅570万、经营现金流-1.45亿","鑫联资产注入已逾期"],
    note="'改善信号'质量偏弱，摘帽看交易所审核。"),
"000838": dict(p=4, rl="极高", band="10% (主板ST)",
    fd=[3.0,4.7,3.2,4.3],
    cat="重整投资协议已签，景行新能入主确定性最高；程序推进最先进。",
    risks=["*ST且净资产约-2亿，保壳硬约束","重整稀释大、股本摊薄","仍处*ST退市警示期"],
    note="*ST类，保壳失败可归零，仓位须最轻。"),
"600337": dict(p=5, rl="中", band="10% (主板ST)",
    fd=[3.7,4.2,3.0,4.4],
    cat="产投协议已签，万德溙AI算力铜缆跨界概念强，想象力大。",
    risks=["跨界协同存疑、业绩仍亏","传统家居主业承压","概念炒作成分高"],
    note="主板ST 10%波动，重整未落地前波动随预期。"),
"002168": dict(p=6, rl="中", band="10% (主板ST)",
    fd=[3.6,4.3,3.2,3.8],
    cat="二债会已通过重整计划草案，程序推进快。",
    risks=["尚未获法院正式受理重整","净资产/营收承压","子公司失信等历史包袱"],
    note="程序快但落地前仍有不确定性。"),
"600381": dict(p=7, rl="极高", band="10% (主板ST)",
    fd=[3.2,3.8,3.4,4.0],
    cat="营收踩线达标，摘星摘帽申请进入交易所终审。",
    risks=["*ST，上半年仍亏损","问询函/审计风险","听花酒品牌修复难"],
    note="*ST但摘帽在即，确定性较高的一只*ST。"),
"300147": dict(p=8, rl="极高", band="20% (创业板ST)",
    fd=[2.8,3.6,3.0,3.8],
    cat="广药资本中选产业投资人，中药+生物药协同想象空间大。",
    risks=["★创业板ST=20%波动(主板ST的两倍)","预重整四次延期已逾期、协议未签","*ST+20%双高风险叠加"],
    note="波动最猛档位之一，保壳未定前慎追。"),
"002542": dict(p=9, rl="极高", band="10% (主板ST)",
    fd=[2.2,2.8,2.4,2.6],
    cat="成都国资背景+低空经济概念，仅'拟申请'预重整。",
    risks=["*ST，净资产为负","仅拟申请、未实质进入程序","低空概念兑现远"],
    note="预期最弱的一档*ST。"),
"300027": dict(p=10, rl="高", band="20% (创业板ST)",
    fd=[2.6,2.4,2.2,2.8],
    cat="影视IP知名，《前任》等系列有品牌价值。",
    risks=["★创业板ST=20%波动","七年累亏82亿，重整投资人未定","造血极差、保壳靠外部"],
    note="20%波动+基本面最差，高波动高风险。"),
"300020": dict(p=11, rl="高", band="20% (创业板ST)",
    fd=[2.4,2.6,2.4,2.6],
    cat="智慧城市主业仍在，部分项目有回款。",
    risks=["★创业板ST=20%波动","三重ST叠加(财务+内控+其他)","违规担保2.36亿未解、扭亏困难"],
    note="20%波动+多重风险，规避或极轻仓。"),
"600340": dict(p=12, rl="极高", band="10% (主板ST)",
    fd=[1.2,2.0,1.6,2.0],
    cat="债务重组规模大，若成功想象空间高。",
    risks=["*ST，净资产缺口约-177亿","协议未签、保壳极难","股本大、自救空间小"],
    note="保壳失败直接归零概率大。"),
"600370": dict(p=13, rl="极高", band="10% (主板ST)",
    fd=[1.0,1.8,1.4,1.8],
    cat="江阴国资入主预期，保壳有地方背书想象。",
    risks=["*ST，非标审计+内控否定","控股股权被拍卖、近面值","退市风险最高档"],
    note="列表中退市风险最高。"),
}

# 综合分（催化价值四维加权：退市30%重组30%基本面25%关注15%）
order = ["600079","002726","000711","000838","600337","002168","600381","300147","002542","300027","300020","600340","600370"]
weights=[0.30,0.30,0.25,0.15]
for c,d in data.items():
    d["score"]=round(sum(x*w for x,w in zip(d["fd"],weights)),3)

risk_color={"中":"#ffd43b","高":"#ffa94d","极高":"#ff6b6b"}

rows=""
for c in order:
    d=data[c]; qd=q[c]
    rows+=f"""<tr>
<td class="pri">{d['p']}</td>
<td><b>{qd['name']}</b><br><span class="code">{c}</span></td>
<td>{qd['price']:.2f}</td>
<td class="{('up' if qd['pct']>=0 else 'down')}">{qd['pct']:+.2f}%</td>
<td>{d['band']}</td>
<td>{qd['total_cap']:.1f}亿</td>
<td><span class="rl" style="background:{risk_color[d['rl']]}">{d['rl']}</span></td>
<td class="score">{d['score']:.2f}</td>
</tr>"""

cards=""
for c in order:
    d=data[c]; qd=q[c]
    bars="".join(
        f"<div class='dim'><span>{n}</span><div class='bar'><i style='width:{v*20}%;background:{risk_color[d['rl']]}'></i></div><b>{v}</b></div>"
        for n,v in zip(["退市风险","重组预期","基本面改善","市场关注"],d["fd"]))
    risks="".join(f"<li>{r}</li>" for r in d["risks"])
    cards+=f"""<div class="card">
<div class="ch"><span class="pri-badge">P{d['p']}</span>
<b>{qd['name']}</b> <span class="code">{c}</span>
<span class="rl" style="background:{risk_color[d['rl']]}">{d['rl']}风险</span>
<span class="band">{d['band']}</span></div>
<div class="price">现价 {qd['price']:.2f} ｜ 涨跌幅 {qd['pct']:+.2f}% ｜ 总市值 {qd['total_cap']:.1f}亿 ｜ 换手 {qd['turnover']:.2f}%</div>
<div class="sec"><b>催化逻辑：</b>{d['cat']}</div>
<div class="dims">{bars}</div>
<div class="sec"><b>主要风险：</b><ul>{risks}</ul></div>
<div class="note">⚠ {d['note']}</div>
</div>"""

html=f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ST/*ST 13只风险分级与优先级（2026.7.6新规修正版）</title>
<style>
body{{background:#1e1e1e;color:#e0e0e0;font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:0;padding:24px;}}
h1{{font-size:22px;margin:0 0 4px;}} .sub{{color:#9aa0a6;font-size:13px;margin-bottom:16px;}}
.box{{background:#3a1e1e;border:1px solid #ff6b6b;border-radius:8px;padding:12px 16px;margin-bottom:20px;font-size:13px;line-height:1.7;}}
.box b{{color:#ff8787;}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:24px;}}
th,td{{padding:8px 10px;border-bottom:1px solid #333;text-align:center;}}
th{{background:#2a2a2a;color:#bbb;}} td:nth-child(2){{text-align:left;}}
.pri{{color:#ffd43b;font-weight:700;}} .code{{color:#7a8288;font-size:11px;}}
.up{{color:#ff6b6b;}} .down{{color:#51cf66;}} .score{{color:#74c0fc;font-weight:700;}}
.rl{{color:#1e1e1e;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:700;}}
.card{{background:#2a2a2a;border-radius:10px;padding:14px 16px;margin-bottom:14px;}}
.ch{{font-size:15px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
.pri-badge{{background:#ffd43b;color:#1e1e1e;border-radius:6px;padding:1px 8px;font-weight:700;font-size:13px;}}
.band{{background:#3a3f47;color:#a5d8ff;padding:1px 8px;border-radius:10px;font-size:11px;}}
.price{{color:#bbb;font-size:12px;margin:6px 0 10px;}}
.sec{{font-size:13px;line-height:1.6;margin-bottom:8px;}}
.dims{{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0;}}
.dim{{flex:1;min-width:120px;font-size:11px;color:#bbb;}}
.dim span{{display:block;margin-bottom:2px;}} .dim b{{color:#e0e0e0;}}
.bar{{background:#1e1e1e;border-radius:4px;height:8px;overflow:hidden;}} .bar i{{display:block;height:100%;}}
.note{{background:#2f2a1e;border-left:3px solid #ffd43b;padding:6px 10px;font-size:12px;color:#ffe8a3;border-radius:4px;}}
ul{{margin:4px 0;padding-left:18px;}} li{{font-size:12px;line-height:1.6;}}
.legend{{font-size:12px;color:#9aa0a6;margin-bottom:16px;}}
</style></head><body>
<h1>ST / *ST 13只 · 风险分级与优先级（修正版）</h1>
<div class="sub">数据基准：2026-08-20 收盘实时行情（腾讯）｜ 全程未修改项目目录，脚本/报告仅落 Temp</div>
<div class="box">
<b>★ 规则纠正声明（重要）：</b>此前分析误用旧规"ST涨跌幅5%"。经核实，沪深交易所《交易规则(2026修订)》于
<b>2026-07-06 起实施</b>：<b>主板 ST/*ST 涨跌幅限制由 5% 上调至 10%</b>（与主板普通股统一）；
创业板/科创板 ST/*ST 维持 <b>20%</b>；北交所 ST/*ST 为 30%。<br>
因此：① 此前"ST龙大涨10%→推断已摘帽"结论<b>错误</b>，龙大8/20涨10.07%即ST新规下正常涨停，<b>仍是ST</b>；
② 此前"ST有5%缓冲、回撤温和=低风险档"的风险描述<b>全部作废</b>，现ST单日波动已与普通股票一致（主板10%/创业板20%），风险等级整体上调。
本版基于正确规则重评风险等级与优先级。
</div>
<div class="legend">风险等级：<span class="rl" style="background:#ffd43b">中</span> 主板ST重整/摘帽预期明确 ｜
<span class="rl" style="background:#ffa94d">高</span> 创业板ST(20%波动) ｜
<span class="rl" style="background:#ff6b6b">极高</span> *ST退市警示(保壳失败可归零)</div>
<table><tr><th>优先级</th><th>标的</th><th>现价</th><th>涨跌幅</th><th>涨跌停档位</th><th>总市值</th><th>风险等级</th><th>综合分</th></tr>
{rows}</table>
<h2 style="font-size:17px;border-left:4px solid #74c0fc;padding-left:10px;">逐只明细</h2>
{cards}
<div class="box" style="background:#2a2f3a;border-color:#74c0fc;">
<b>结论与纪律：</b>① 优先级（投资价值/催化确定性）维持原序，但<b>风险等级已按10%/20%新规重评</b>；
② 前段以主板ST(10%)为主、重整/摘帽预期明确，风险相对可控但绝非无风险；后半段*ST及创业板ST(20%)波动最猛、保壳失败可归零，建议回避或极轻仓；
③ 纯ST不再是"温和波动"——主板10%、创业板20%，回撤幅度与普通股票一致甚至更猛。<br>
<span style="color:#9aa0a6">⚠ 纯研究性排序，非投资建议、不代下单。ST/*ST退市/变脸风险极高，务必独立决策、严控仓位。</span>
</div>
</body></html>"""

with open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST13_risk_v2_20260820.html","w",encoding="utf-8") as fp:
    fp.write(html)
print("OK 报告已生成，共", len(order), "只")
