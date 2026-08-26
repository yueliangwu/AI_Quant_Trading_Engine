# -*- coding: utf-8 -*-
import json, datetime

data = json.load(open(r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_restructure_low.json", encoding="utf-8"))

# 已剔除（已大涨）：ST龙元 +97.8%、*ST英飞 +28.4%(贴近高点)、ST金鸿 +33.1%(贴近高点)、*ST启环 +48.9%

rows = [
  {
    "pri": "P1", "code": "600537", "name": "*ST亿晶", "board": "沪主板", "st": "*ST",
    "price": 2.11, "up_low": 1.9, "drawdown": -40.4, "mcap": 24.98,
    "stage": "S5 已签协议",
    "progress": "2026/2 法院预重整备案；4/26 与产业投资人宁波瑞廉+中润光能签《预重整投资协议》出资8.19亿；6/11 与财务投资人签协议。监管函回复中，尚未正式受理。",
    "catalyst": "产投+财投协议齐签，重整对价已定（1.80元/股），光伏组件主业+产业协同，位置处60日底部。",
    "risk": "*ST（净资产为负）；全椒百亿项目烂尾引发17.77亿追偿、监管追问；仍未正式受理重整，存在退市风险。",
    "tier": "high"
  },
  {
    "pri": "P2", "code": "603377", "name": "ST东时", "board": "沪主板", "st": "ST",
    "price": 2.90, "up_low": 9.8, "drawdown": -25.3, "mcap": 20.96,
    "stage": "S4 协议+补充+债权人会已过",
    "progress": "2025/7 北京一中院启动预重整；2025/8 签《重整投资协议》；2026/6 签补充协议（调价至1.81元/股）；2026/6 预重整第一次债权人会议通过方案；8/7 披露仍处预重整未受理。",
    "catalyst": "协议+补充+债权人会三步走完，进度在6只里最靠前；且为ST非*ST，风险层级低于其余4只*ST；位置处60日低位。",
    "risk": "ST（其他风险警示，非*ST）；东时转债2026/4到期未兑付可能转*ST；部分股份9/12司法拍卖；主业驾驶培训持续承压。",
    "tier": "mid"
  },
  {
    "pri": "P3", "code": "002360", "name": "ST同德", "board": "深主板", "st": "ST",
    "price": 5.41, "up_low": 20.8, "drawdown": -16.6, "mcap": 21.74,
    "stage": "S2 预重整备案+招募完成",
    "progress": "2026/4/20 忻州中院预重整备案；5/15 公开招募投资人，5/29 报名截止，意向投资人已提交方案；7/17 法院同意延长预重整至2026/10/20。",
    "catalyst": "备案+招募完成待遴选，进度较早但确定性尚可；ST非*ST；民爆主业+PBAT新材料项目（主体完工未投产）有转型想象。",
    "risk": "ST（非*ST）；仅备案尚未签协议，遴选结果未定；PBAT项目未投产、行业供大于求风险高；延长期限内若未推进将加大不确定性。",
    "tier": "mid"
  },
  {
    "pri": "P4", "code": "002634", "name": "*ST棒杰", "board": "深主板", "st": "*ST",
    "price": 4.25, "up_low": 21.1, "drawdown": -21.0, "mcap": 19.52,
    "stage": "S5 已签协议",
    "progress": "预重整推进中；8/1、8/17 与财务投资人（美年大健康产业集团指定）签《重整投资协议》认购5870万股合计1.53亿；产业投资人为美年。尚未收到法院受理文书。",
    "catalyst": "产投（美年健康）+财投协议齐签，医疗健康产业协同明确；位置处60日低位（距高点-21%）。",
    "risk": "*ST；预重整尚未被法院正式受理；协议存在无法履行/被解除风险；主业光伏电池组件持续亏损。",
    "tier": "high"
  },
  {
    "pri": "P5", "code": "002620", "name": "*ST瑞和", "board": "深主板", "st": "*ST",
    "price": 5.00, "up_low": 21.7, "drawdown": -54.1, "mcap": 18.87,
    "stage": "S5 已签协议但未受理",
    "progress": "2025/7 深圳中院启动预重整；2026/5/15 与产业投资人槟城电子（3.90元/股受让2.44亿股）及财务投资人签《重整投资协议》出资9.51亿；截至2026/7/2 法院尚未正式受理。",
    "catalyst": "协议已签、产业投资人明确（槟城电子将控股）；距60日高点回撤达-54%，位置最低之一。",
    "risk": "*ST（净资产为负、连续三年亏损）；180个账户冻结超1亿、欠薪舆情、涉讼1954万；仍未正式受理，重整失败将退市。",
    "tier": "high"
  },
  {
    "pri": "P6", "code": "603843", "name": "*ST正平", "board": "沪主板", "st": "*ST",
    "price": 6.94, "up_low": 31.7, "drawdown": -25.9, "mcap": 48.55,
    "stage": "S2-S3 招募报名多",
    "progress": "2026/2 发布预重整投资人招募；3/5 共有44家意向投资人报名（市场关注度极高）；但2025年曾被爆炒（区间涨幅超100%），目前为回调后的中低位。",
    "catalyst": "44家投资人报名显示重整价值受认可；基建+有色主业；距高点回撤-26%提供一定安全垫。",
    "risk": "*ST；2025年已被大幅炒作，预期较充分；净资产下修至可能为负，退市风险；进度仍处早期（遴选未定）。",
    "tier": "high"
  },
]

def tier_color(t):
    return {"high":"#c0392b","mid":"#d68910","low":"#27ae60"}[t]

html = []
html.append("""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>主板低位重整预期差清单 2026-08-21</title>
<style>
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:0;background:#f5f6f8;color:#1f2933;}
.wrap{max-width:1180px;margin:0 auto;padding:24px;}
h1{font-size:22px;margin:0 0 4px;}
.sub{color:#667;font-size:13px;margin-bottom:18px;}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0;font-size:13px;}
.badge{padding:3px 9px;border-radius:10px;color:#fff;font-size:12px;}
.b-high{background:#c0392b;} .b-mid{background:#d68910;} .b-low{background:#27ae60;}
.note{background:#fff8e1;border-left:4px solid #f0a020;padding:10px 14px;font-size:13px;margin:14px 0;border-radius:4px;}
table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.08);font-size:13px;}
th,td{border:1px solid #e3e6ea;padding:9px 10px;vertical-align:top;text-align:left;}
th{background:#2c3e50;color:#fff;font-weight:600;}
tr:nth-child(even){background:#fafbfc;}
.pri{font-weight:700;font-size:15px;}
.code{font-family:monospace;color:#34495e;}
.up{color:#c0392b;font-weight:600;} .down{color:#27ae60;font-weight:600;}
.card{background:#fff;border:1px solid #e3e6ea;border-radius:6px;padding:14px 16px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.card h3{margin:0 0 6px;font-size:16px;}
.k{color:#667;font-size:12px;display:inline-block;width:74px;}
.disclaim{background:#fdecea;border:1px solid #f5c6cb;color:#922;padding:12px 16px;border-radius:6px;font-size:12px;margin-top:20px;}
</style></head><body><div class="wrap">""")

html.append("<h1>主板「低位 + 重整进行中」预期差清单</h1>")
html.append("<div class='sub'>数据基准：2026-08-21 实时行情（腾讯 qt.gtimg.cn）｜筛选口径：非创业板（主板 000/002/600/601/603）、重整进度 S2–S5（准备中/未落地）、剔除已大涨标的</div>")

html.append("<div class='legend'>")
html.append("<span class='badge b-high'>极高 *ST</span> 退市风险警示，保壳失败可归零")
html.append("<span class='badge b-mid'>高 ST</span> 其他风险警示，非*ST，风险相对可控")
html.append("</div>")

html.append("<div class='note'>⚠️ <b>已剔除的「已大涨」标的</b>：ST龙元(600491) 距60日低点 +97.8%（已翻倍）、*ST英飞(002528) +28.4%且贴近高点、ST金鸿(000669) +33.1%贴近高点、*ST启环(000826) +48.9%——均不符合「还没大幅涨过」。</div>")

# 表格
html.append("<table><tr><th>优先级</th><th>标的</th><th>状态</th><th>现价</th><th>距60日低点</th><th>距60日高点</th><th>总市值</th><th>重整进度</th><th>核心催化</th><th>主要风险</th></tr>")
for r in rows:
    upcls = "up" if r["up_low"]>=0 else "down"
    html.append("<tr>")
    html.append(f"<td class='pri'>{r['pri']}</td>")
    html.append(f"<td><b>{r['name']}</b><br><span class='code'>{r['board']} {r['code']}</span></td>")
    html.append(f"<td><span class='badge b-{r['tier']}'>{r['st']}</span></td>")
    html.append(f"<td>{r['price']}</td>")
    html.append(f"<td class='{upcls}'>{'+' if r['up_low']>=0 else ''}{r['up_low']}%</td>")
    html.append(f"<td class='down'>{r['drawdown']}%</td>")
    html.append(f"<td>{r['mcap']}亿</td>")
    html.append(f"<td>{r['stage']}<br><span style='color:#667;font-size:12px'>{r['progress']}</span></td>")
    html.append(f"<td>{r['catalyst']}</td>")
    html.append(f"<td>{r['risk']}</td>")
    html.append("</tr>")
html.append("</table>")

# 卡片详情
for r in rows:
    html.append(f"<div class='card'><h3>{r['pri']} · {r['name']}（{r['board']} {r['code']}） <span class='badge b-{r['tier']}'>{r['st']}</span></h3>")
    html.append(f"<div><span class='k'>现价</span>{r['price']} 元 ｜ <span class='k'>距低点</span><span class='up'>{'+' if r['up_low']>=0 else ''}{r['up_low']}%</span> ｜ <span class='k'>距高点</span><span class='down'>{r['drawdown']}%</span> ｜ <span class='k'>市值</span>{r['mcap']}亿</div>")
    html.append(f"<div><span class='k'>重整进度</span>{r['progress']}</div>")
    html.append(f"<div><span class='k'>核心催化</span>{r['catalyst']}</div>")
    html.append(f"<div><span class='k'>主要风险</span>{r['risk']}</div>")
    html.append("</div>")

html.append("<div class='disclaim'>⚠️ <b>免责声明</b>：本清单为研究性排序，非投资建议、不代下单。ST/*ST 板块退市/变脸风险极高，*ST 类保壳失败可直接归零。所有价格已用实时行情核验，但重整成败、法院是否受理、协议是否履行均存在重大不确定性，务必独立决策、严控仓位。主板 ST/*ST 涨跌幅限制为 10%（2026-07-06 新规）。</div>")
html.append("</div></body></html>")

out = r"C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_low_restructure_20260821.html"
open(out, "w", encoding="utf-8").write("\n".join(html))
print("OK", out)
