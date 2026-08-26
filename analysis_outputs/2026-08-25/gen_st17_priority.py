# -*- coding: utf-8 -*-
import json

W = [0.30, 0.30, 0.25, 0.15]  # 退市风险 / 重组预期 / 基本面改善 / 市场关注度

# ---- 原13只：四维分来自 ST13_final_priority_20260820.html（已反算验证与总表一致）----
orig = json.load(open(r"C:/Users/EDY/AppData/Local/Temp/wb_analysis/st13_details.json", encoding='utf-8'))
status_map = {'600079':'ST','002726':'ST','000711':'ST','000838':'*ST','600337':'ST','002168':'ST',
              '600381':'*ST','300147':'*ST','002542':'*ST','300027':'ST','300020':'ST','600340':'*ST','600370':'*ST'}
price_map  = {'600079':'17.86','002726':'2.95','000711':'6.11','000838':'2.75','600337':'3.12','002168':'3.82',
              '600381':'4.91','300147':'7.09','002542':'1.82','300027':'1.77','300020':'3.36','600340':'1.09','600370':'1.47'}
mcap_map   = {'600079':'291.5','002726':'40.1','000711':'180.5','000838':'30.3','600337':'44.8','002168':'30.0',
              '600381':'28.8','300147':'46.9','002542':'32.9','300027':'49.1','300020':'26.7','600340':'42.4','600370':'59.1'}

orig_list = []
for d in orig:
    c = d['code']; dims = d['dims']
    comp = round(sum(x*w for x, w in zip(dims, W)), 3)
    orig_list.append({'name': d['name'], 'code': c, 'status': status_map.get(c,'ST'), 'dims': dims,
                      'comp': comp, 'price': price_map.get(c,'-'), 'mcap': mcap_map.get(c,'-'),
                      'risk_lv': d.get('risk_level',''), 'is_new': False,
                      'reason':'', 'catalyst':'', 'risk':''})

# ---- 新增4只（2026-08-25 增补，原 ST13 文档未纳入）----
new4 = [
 {'name':'ST长园','code':'600525','status':'已摘帽','dims':[4.5,5.0,4.0,4.5],'price':'5.78(8-24停牌)','mcap':'-',
  'risk_lv':'低（ST非*ST，8-26摘帽；治理重塑+2026H1扭亏3500~5200万）',
  'reason':'珠海科技产业集团入主后治理重构，2024内控否定意见已整改消除（德皓国际标准无保留）；2026H1预计归母扭亏3500~5200万。8-14申请、8-24上交所同意撤销其他风险警示、8-26复牌更名「长园集团」，涨跌幅恢复10%。摘帽确定性全场最高（上交所已批），主业盈利已现改善，属反转线最干净标的。',
  'catalyst':'摘帽复牌(8-26)+治理重塑+半年度扭亏+珠海国资赋能',
  'risk':'摘帽后「卖事实」波动（停牌前已从低位累计上涨）；主业盈利改善持续性待验证；8-26复牌首日量价定方向'},
 {'name':'ST宁科','code':'600165','status':'已摘帽','dims':[4.5,5.0,2.5,4.5],'price':'3.27(8-24停牌)','mcap':'52.84',
  'risk_lv':'低（ST非*ST，8-26摘帽；但曾*ST、主业仍亏）',
  'reason':'重整计划2025年内执行完毕+2024审计持续经营不确定性段落消除+宁夏证监局处罚满12月，8-24上交所同意撤销其他风险警示，8-26复牌更名「宁科生物」。摘帽确定性高（已批）。但核心业务长链二元酸毛利率-43.78%持续为负，2026H1仍预亏1.2~1.5亿，基本面改善最弱——摘帽≠业绩反转。',
  'catalyst':'摘帽复牌(8-26)+合成生物赛道+实控人增持计划(3000~6000万)',
  'risk':'主业盈利失效、经营现金流-3.73亿、5.45亿扩产资金压力、摘帽后卖事实、曾年报虚增财务违规污点'},
 {'name':'*ST正平','code':'603843','status':'*ST','dims':[3.5,4.0,3.0,3.5],'price':'7.16(8-16)','mcap':'50.09',
  'risk_lv':'中（*ST，已递交摘星申请+净资产转正5049万；但重整未正式受理、采矿权冻结风险）',
  'reason':'青海国资牵头重整+河北地矿核心战投（8-15~17高层实地调研M1矿区尽职摸底），44家意向战投报名，一债会债权通过率97.22%；已向上交所递交撤销*ST（摘星）申请，当前补充问询材料；2026H1预亏1.3~1.8亿为一次性洗报表。底层硬资产（昆仑算电1.1万P绿电算力+格尔木M1多金属矿）提供估值安全垫。退市风险因国资兜底基本锁死，但重整受理仍不确定。',
  'catalyst':'摘星申请审核+河北地矿战投签约+国资算力/矿产平台定位',
  'risk':'预重整≠正式受理（失败则终止上市）、采矿权冻结/开采能力不足、净资产转正但边际、诉讼多'},
 {'name':'ST东时','code':'603377','status':'ST','dims':[2.5,3.5,1.5,2.5],'price':'2.94(8-07)','mcap':'21.25',
  'risk_lv':'高（ST，若法院受理重整将被叠加*ST；转债违约+连续3年扣非负+持续经营重大不确定）',
  'reason':'预重整2025-7-10启动，已签重整投资协议及补充协议，小额现金清偿方案(≥15万)；但至今未正式进入重整程序（重大不确定性）。东时转债2026-4-8到期违约（108元/张无法兑付），连续3年扣非-3.73/-6.08/-6.80亿，2025净亏7.66亿，流动负债高于流动资产16.75亿，短期借款3.48亿全部逾期；8-24公告部分募资账户冻结；持续经营重大不确定性。重整协议已签是最大亮点，但财务质量全场最差。',
  'catalyst':'重整协议签署+预重整推进+小额清偿方案+若受理重整触发*ST(博弈反转)',
  'risk':'转债违约/债务危机、受理不确定、若受理即*ST、财务造假&税务处罚、募资账户冻结、持续经营不确定'},
]
for n in new4:
    n['comp'] = round(sum(x*w for x, w in zip(n['dims'], W)), 3)
    n['is_new'] = True

allst = orig_list + new4
allst.sort(key=lambda x: -x['comp'])
for i, s in enumerate(allst, 1):
    s['pri'] = i

# ---------- HTML ----------
L = []
L.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
L.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
L.append('<title>ST/*ST 反转预期 · 全17只统一优先级排序（更新版）</title>')
L.append('''<style>
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;max-width:1000px;margin:0 auto;padding:24px;background:#fff;color:#1a1a1a;line-height:1.7;}
h1{font-size:24px;border-bottom:3px solid #c0392b;padding-bottom:8px;}
h2{font-size:19px;margin-top:28px;color:#c0392b;border-left:4px solid #c0392b;padding-left:10px;}
h3{font-size:16px;color:#2c3e50;margin-top:18px;}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13px;}
th,td{border:1px solid #ddd;padding:7px 9px;text-align:left;vertical-align:top;}
th{background:#f5f5f5;font-weight:600;}
.box{background:#fbf5f5;border:1px solid #f0d4d4;border-radius:6px;padding:12px 16px;margin:14px 0;}
.ok{background:#e8f5e9;border:1px solid #c8e6c9;border-radius:6px;padding:12px 16px;margin:14px 0;}
.warn{background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:12px 16px;margin:14px 0;}
.meta{color:#666;font-size:12px;}
.tag{display:inline-block;background:#c0392b;color:#fff;font-size:11px;padding:2px 7px;border-radius:3px;margin-right:6px;}
.new{background:#1565c0;}
ul{margin:8px 0;padding-left:22px;}
.hl{background:#fff3cd;}
</style></head><body>''')

L.append('<h1>ST/*ST 反转预期 · 全17只统一优先级排序（更新版）</h1>')
L.append('<p class="meta">更新时间：2026-08-25 ｜ 方法论基准：<b>ST13_final_priority_20260820.html</b>（四维加权模型）｜ 本次动作：纳入 8-25 增补的 4 只未纳入标的（宁科/长园/正平/东时），统一重算综合得分与排序 ｜ 评分模型：退市风险30%＋重组预期30%＋基本面改善25%＋市场关注度15%（退市风险分越高=风险越低=越安全）</p>')

L.append('<div class="box"><h2 style="margin-top:6px">模型与数据口径说明</h2>')
L.append('<p><b>四维加权</b>：综合分 = 退市风险×0.30 + 重组预期×0.30 + 基本面改善×0.25 + 市场关注度×0.15，各维满分 5.0。原 13 只四维分直接取自 ST13 文档（已用总表综合分反算校验完全一致）。</p>')
L.append('<p><b>价格/市值基准</b>：原 13 只取 2026-08-20 收盘（来自原文档）；新增 4 只取 2026-08-25 附近公开行情（宁科/长园为 8-24 停牌价）。综合分由四维定性模型决定，<b>不随短期价格波动变动</b>。</p>')
L.append('<p><b>新增标的</b>：<span class="tag new">NEW</span>ST长园(600525)、<span class="tag new">NEW</span>ST宁科(600165)、<span class="tag new">NEW</span>*ST正平(603843)、<span class="tag new">NEW</span>ST东时(603377)。其中宁科、长园已于 8-26 摘帽复牌。</p></div>')

# 总表
L.append('<h2>一、最终排序总表（全17只）</h2>')
L.append('<table><tr><th>优先级</th><th>标的</th><th>状态</th><th>退市风险<br>(30%)</th><th>重组预期<br>(30%)</th><th>基本面改善<br>(25%)</th><th>市场关注度<br>(15%)</th><th>四维综合分</th><th>参考价</th></tr>')
for s in allst:
    tag = ' <span class="tag new">NEW</span>' if s['is_new'] else ''
    hl = ' class="hl"' if s['is_new'] else ''
    L.append('<tr%s><td>%d</td><td>%s%s</td><td>%s</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td><b>%.3f</b></td><td>%s</td></tr>' % (
        hl, s['pri'], s['name'], tag, s['status'], s['dims'][0], s['dims'][1], s['dims'][2], s['dims'][3], s['comp'], s['price']))
L.append('</table>')
L.append('<p class="meta">注：标 <span class="tag new">NEW</span> 为本次新增纳入；浅黄高亮行为新增标的。综合分降序排列。</p>')

# 新增4只逐只明细
L.append('<h2>二、新增标的逐只明细（按优先级，本次补充分析）</h2>')
for s in [x for x in allst if x['is_new']]:
    L.append('<div class="box"><h3>%s NEW %s %s ｜ 综合分 %.3f（原池第 %d 位）</h3>' % (s['name'], s['code'], s['status'], s['comp'], s['pri']))
    L.append('<p><b>四维分</b>：退市风险 %.1f ｜ 重组预期 %.1f ｜ 基本面改善 %.1f ｜ 市场关注度 %.1f</p>' % tuple(s['dims']))
    L.append('<p><span class="tag">风险等级</span>%s</p>' % s['risk_lv'])
    L.append('<p><span class="tag">排序理由</span>%s</p>' % s['reason'])
    L.append('<p><span class="tag">核心催化</span>%s</p>' % s['catalyst'])
    L.append('<p><span class="tag">主要风险</span>%s</p>' % s['risk'])
    L.append('</div>')

# 原13只速览 + 引用
L.append('<h2>三、原13只四维分速览（详述见 ST13_final_priority_20260820.html）</h2>')
L.append('<table><tr><th>标的</th><th>状态</th><th>退市风险</th><th>重组预期</th><th>基本面改善</th><th>市场关注度</th><th>综合分</th><th>原排名</th></tr>')
orig_sorted = sorted(orig_list, key=lambda x: -x['comp'])
for i, s in enumerate(orig_sorted, 1):
    L.append('<tr><td>%s</td><td>%s</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td><b>%.3f</b></td><td>%d</td></tr>' % (
        s['name'], s['status'], s['dims'][0], s['dims'][1], s['dims'][2], s['dims'][3], s['comp'], i))
L.append('</table>')

# 关键结论
L.append('<h2>四、关键结论与排序变化</h2>')
L.append('<div class="ok"><ul>')
L.append('<li><b>头部洗牌</b>：新增的<b>长园(600525)综合分4.525 升至全场第1</b>（原13只最高为人福4.475），超越人福/龙大；<b>宁科(600165)4.150 插入第4</b>，位于龙大之后、京蓝之前。</li>')
L.append('<li><b>正平(603843)3.525 列第10</b>，介于春天(3.600)与香雪(3.150)之间——*ST但国资兜底+已申请摘星，确定性优于纯预重整票。</li>')
L.append('<li><b>东时(603377)2.550 列第15</b>，高于华幸(1.875)/三房(1.800)：重整协议已签是亮点，但转债违约+连续3年扣非负+持续经营重大不确定，财务质量全场最差，仅因"协议已签"略优于滞后的华幸/三房。</li>')
L.append('<li><b>原13只内部相对序不变</b>：人福→龙大→京蓝→发展=美克→惠程→春天→香雪→中岩→华谊→银江→华幸→三房，综合分与新池完全可比（同模型同权重）。</li>')
L.append('<li><b>监控建议</b>：宁科、长园已摘帽（8-26），若按"反转线已兑现"逻辑可单列归档；正平、东时纳入活跃池跟踪（正平盯摘星审核+战投签约，东时盯法院是否受理重整）。</li>')
L.append('</ul></div>')

L.append('<div class="warn"><h2 style="margin-top:6px">风险提示</h2>')
L.append('<p>本报告为<b>事件监控与进度梳理+四维定性打分</b>，非投资建议。ST/*ST 板块退市风险极高：预重整备案/投资人选定 ≠ 法院正式受理（失败则终止上市）；摘帽/摘星申请 ≠ 交易所核准；净资产为负、审计非标、面值低于1元均为硬性退市红线。据此交易风险自担。</p></div>')

L.append('</body></html>')

out = r"C:/Users/EDY/AppData/Local/Temp/wb_analysis/ST17_priority_updated_20260825.html"
open(out, 'w', encoding='utf-8').write('\n'.join(L))
print('written:', out)
print('--- ranking ---')
for s in allst:
    print('%2d  %s %s  %.3f' % (s['pri'], s['code'], s['name'], s['comp']))
