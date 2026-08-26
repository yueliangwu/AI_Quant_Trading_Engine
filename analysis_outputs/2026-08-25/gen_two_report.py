# -*- coding: utf-8 -*-
'''生成 ST龙大(002726) / ST京蓝(000711) 8-21 异动分析报告（基于实时核验数据）'''
import datetime

DATA = {
    'date': '2026-08-21',
    'longda': {
        'code': '002726', 'name': 'ST龙大 (龙大美食)',
        'close': 2.77, 'prev': 2.95, 'chg': -6.10, 'open': 2.94,
        'high': 3.02, 'low': 2.66, 'turnover': 11.40, 'mktcap': 37.70,
        'pe': -6.16, 'pb': 5.52,
        'limit_down': 2.66,
        'drivers': [
            ('异动公告"见光死"——预期兑现场内兑现',
             '8/20 收 2.95（+10.07% 涨停），8/18-20 连续 3 日涨幅偏离累计超 20%，公司 8/20 盘后发布《股票交易异常波动公告》(2026-148)。这是典型的炒预期到公告后资金兑现节奏，与此前统计的利好出尽回撤一致。'),
            ('重整遴选进度停滞，低于预期',
             '截至 7/30 共 27 家意向投资人完成报名，但公司证券部 8/18 明确表示尚未收到临时管理人进一步信息，遴选久无进展。8/24 债权申报截止临近，部分资金选择利好出尽或观望。'),
            ('基本面仍亏损，无反转实锤',
             '2026H1 预告归母亏损 8500万-10900万、扣非亏损 13400万-15800万；生猪养殖亏损扩大，仅屠宰业务因库存出清扭亏。基本面未真正反转。'),
            ('大股东减持传递负面信号',
             '控股股东蓝润发展 7 月中旬至 8 月初累计减持超 800 万股，叠加其持股 70%+ 质押冻结、实控人戴学斌被刑拘，控制权不稳，压制风险偏好。'),
            ('板块与 ST 整体风险偏好收缩',
             '8/21 食品加工板块盘中跌 2%，农牧饲渔 ST 标的批量回调；市场风险偏好收缩、资金从高风险的 ST 类撤离，龙大作为未化解风险标的被同步抛售。'),
            ('翻倍后获利盘踩踏 + 技术破位',
             '自 1.18 低点涨至 2.95（翻倍），获利盘巨大；技术面跌破 BOLL 下轨，空头集中释放，盘中一度砸至跌停 2.66。'),
        ],
        'timeline': [
            ('2026-04-30', '因 2025 内控否定意见 + 连续 3 年扣非为负 + 持续经营不确定性，被实施其他风险警示，简称变 ST龙大'),
            ('2026-07-04', '发布重整投资人招募公告（产业投资人保证金 3000 万 / 财务投资人 1000 万）'),
            ('2026-07-09', '烟台中院裁定启动预重整，指定预重整清算组为临时管理人'),
            ('2026-07-13/17', '龙大转债到期违约（2026 国内第二只违约转债）；莱阳恒基（地方国资）提供 3.63 亿贷款全额兑付，7/17 摘牌'),
            ('2026-07-21', '预重整债权申报公告，申报截止日 2026-08-24'),
            ('2026-07-23/30', '意向投资人报名：7/23 达 24 家、7/30 达 27 家（单体+联合体），此后无新进展披露'),
            ('2026-08-07', '控股股东 1194.74 万股解除质押、593.16 万股解除冻结'),
            ('2026-08-13-14', '蓝润发展 6683.31 万股司法拍卖（占 4.90%），3 人报名无竞买记录'),
            ('2026-08-18', '证券部称尚未收到临时管理人进一步信息，遴选停滞'),
            ('2026-08-20', '连续 3 日涨幅偏离超 20%，发布异动公告 (2026-148)'),
            ('近期', '牛散"魏巍"撞名者 1.3 亿拍下近 5% 股份（身份未确认）'),
            ('当前状态', '预重整进行中；法院受理重整申请尚未下达。若受理则实施 *ST；若重整失败则破产退市'),
        ],
        'outlook': ('短线偏弱、围绕 2.6-3.0 区间震荡。8/21 盘中跌停 2.66 后被拉回至 2.77，说明有承接但弱势。\n'
                    '关键变量：① 8/24 债权申报截止后，临时管理人/法院是否给出受理或遴选结果；② 有无法院受理重整或产业投资人敲定公告。\n'
                    '· 若下周出实质重整利好 -> 可反弹修复；\n'
                    '· 若继续无进展或减持/亏损压制 -> 弱势震荡，跌破 2.66 且放量则下看 2.4-2.5。\n'
                    'ST 板块整体风险偏好收缩 + 翻倍获利盘未出清，反弹高度受限。'),
    },
    'jinglan': {
        'code': '000711', 'name': 'ST京蓝 (铟靶新材)',
        'close': 6.44, 'prev': 6.11, 'chg': 5.40, 'open': 6.30,
        'high': 6.47, 'low': 6.20, 'turnover': 5.95, 'mktcap': 190.21,
        'pe': -266.89, 'pb': 26.05,
        'limit_up': 6.72, 'limit_down': 5.50,
        'drivers': [
            ('中报正式扭亏，营收翻倍（核心催化）',
             '8/19-20 披露 2026 中报：营收 4.45 亿（+98.07%）、归母 7420 万（同比扭亏 +213.11%）、扣非 570 万（转正）。业绩反转直接提振预期。'),
            ('摘帽申请已正式提交（最直接利好）',
             '8/18 董事会公告已向深交所正式提交撤销其他风险警示申请，申请期间股票正常交易。这是摘帽预期落地的第一步，资金提前博弈。'),
            ('1.51 亿业绩补偿款全额到账',
             '8/20 收到剩余 7537.59 万，累计 1.51 亿全额到账，直接改善现金流、增厚净资产。'),
            ('"铟靶新材"更名 + 半导体新材料题材',
             '拟更名铟靶新材(哈尔滨)股份，主营含铟固危废资源化 + ITO 靶材（半导体/面板稀缺题材），在铟价上行期享受估值溢价。'),
            ('资金面：盘中快速拉升，动量仍在',
             '9:31 五分钟涨超 2%，全天收 +5.40%，换手 5.95% 未爆量，说明上行动能未耗尽；环保/摘帽板块整体偏暖形成共振。'),
        ],
        'timeline': [
            ('2023年', '完成破产重整，控股股东变更为云南佳骏靶材科技，实控人马黎阳；主业由土壤修复转型工业固危废资源化（铟回收）'),
            ('2025-09-08', '撤销退市风险警示及部分其他风险警示，*ST京蓝 -> ST京蓝（继续其他风险警示）'),
            ('2025全年', '营收 4.75 亿（+25.76%），但归母亏损 2.11 亿'),
            ('2026-07-13', '半年度业绩预告：预计归母 6800-8300 万扭亏，扣非仅 500-750 万'),
            ('2026-07-29', '收到业绩补偿款 7600 万；2026-08-20 收到剩余 7537.59 万，累计 1.51 亿全额到账'),
            ('2026-08-18', '董事会公告向深交所提交撤销其他风险警示（摘帽）申请，尚需审核'),
            ('2026-08-19/20', '正式披露 2026 中报：扭亏为盈（归母 7420 万、扣非 570 万）'),
            ('进行中', '拟更名铟靶新材；鑫联科技资产注入延期（3 年内无法定增收购，仅现金）；ITO 靶材尚未量产无营收'),
            ('当前状态', 'ST（非 *ST），摘帽申请审核中，预计 2-4 周反馈（9 月上旬为乐观窗口）'),
        ],
        'outlook': ('短期偏强、波动加大。摘帽申请已提交，审核周期 2-4 周，资金会提前博弈摘帽；8/21 收 6.44 逼近涨停价 6.72，动量延续。\n'
                    '关键变量：① 深交所摘帽审核反馈节奏（多轮问询可能拉长至 10 月）；② 铟价/靶材题材热度；③ 获利盘了结压力。\n'
                    '· 若审核顺利出进展 -> 冲击 6.72 甚至更高；\n'
                    '· 若遇问询函/获利了结 -> 回踩 6.0-6.2 支撑。\n'
                    '提示：股价年初至今 +276% 已大幅反映预期，扣非仅 570 万（利润靠 7600 万一次性处置收益），追高性价比下降。'),
    },
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f1419;color:#e6e6e6;font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.6;padding:24px}
.wrap{max-width:1000px;margin:0 auto}
h1{font-size:24px;color:#fff;border-left:5px solid #4a9eff;padding-left:12px;margin-bottom:6px}
.sub{color:#9aa0a6;font-size:13px;margin-bottom:20px}
.card{background:#1a1f26;border:1px solid #2a313a;border-radius:10px;padding:20px;margin-bottom:22px}
.card h2{font-size:20px;color:#fff;margin-bottom:4px}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:bold;margin-left:8px}
.up{background:#3a1f1f;color:#ff6b6b}
.down{background:#1f2a3a;color:#5aa9ff}
.qtab{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px}
.qtab td{padding:7px 10px;border-bottom:1px solid #262d36}
.qtab td:first-child{color:#9aa0a6;width:140px}
.pos{color:#ff6b6b}.neg{color:#5aa9ff}
.sec{font-size:15px;color:#4a9eff;font-weight:bold;margin:18px 0 8px;border-bottom:1px solid #2a313a;padding-bottom:4px}
.drv{margin:8px 0;padding-left:18px;position:relative}
.drv:before{content:"\u2022";color:#4a9eff;position:absolute;left:4px}
.drv b{color:#fff}
.tl{list-style:none;margin:8px 0}
.tl li{padding:6px 0 6px 14px;border-left:2px solid #2a313a;margin-left:6px;position:relative}
.tl li:before{content:"";position:absolute;left:-5px;top:12px;width:8px;height:8px;border-radius:50%;background:#4a9eff}
.tl .d{color:#4a9eff;font-size:12px;font-weight:bold}
.out{background:#141a21;border-radius:8px;padding:14px;margin-top:10px;white-space:pre-wrap;color:#d8d8d8;font-size:13.5px}
.note{background:#2a1f14;border:1px solid #4a3a1a;border-radius:8px;padding:12px;margin-top:18px;color:#e8c887;font-size:13px}
"""

html = ['''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>ST龙大/ST京蓝 8-21 异动分析</title><style>''' + CSS + '''</style></head><body><div class="wrap">
<h1>ST龙大(002726) / ST京蓝(000711) · 8月21日异动分析</h1>
<div class="sub">分析日期 2026-08-21 ｜ 行情数据：腾讯实时核验（8/21收盘）｜ 消息源：巨潮/上证报/公司公告/东方财富/新浪财经</div>''']

for key, s in [('longda', DATA['longda']), ('jinglan', DATA['jinglan'])]:
    cls = 'down' if s['chg'] < 0 else 'up'
    arrow = '▼' if s['chg'] < 0 else '▲'
    html.append('''
<div class="card">
  <h2>''' + s['name'] + ''' <span class="badge ''' + cls + '''">''' + s['code'] + '''</span></h2>
  <table class="qtab">
    <tr><td>现价 / 昨收</td><td><b>''' + str(s['close']) + '''</b> / ''' + str(s['prev']) + '''</td>
        <td>涨跌幅</td><td class="''' + cls + '''">''' + arrow + ' ' + format(s['chg'], '+.2f') + '''%</td></tr>
    <tr><td>今开 / 最高 / 最低</td><td colspan="3">''' + str(s['open']) + ' / ' + str(s['high']) + ' / <span class="' + cls + '">' + str(s['low']) + '''</span></td></tr>
    <tr><td>换手率</td><td>''' + str(s['turnover']) + '''%</td><td>总市值</td><td>''' + str(s['mktcap']) + ''' 亿</td></tr>
    <tr><td>市盈率TTM</td><td>''' + str(s['pe']) + '''</td><td>市净率</td><td>''' + str(s['pb']) + '''</td></tr>
  </table>
  <div class="sec">一、''' + ('下跌' if s['chg'] < 0 else '上涨') + '''驱动因素</div>''')
    for t, d in s['drivers']:
        html.append('<div class="drv"><b>' + t + '</b>：' + d + '</div>')
    html.append('<div class="sec">二、破产重整 / 摘帽相关消息梳理</div><ul class="tl">')
    for d, e in s['timeline']:
        html.append('<li><span class="d">' + d + '</span><br>' + e + '</li>')
    html.append('</ul>')
    html.append('<div class="sec">三、下周（8/24起）走势预判</div><div class="out">' + s['outlook'] + '</div>')
    html.append('</div>')

html.append('''<div class="note">⚠️ 风险提示：本报告为基于公开信息的事件/情绪分析，<b>非投资建议、不代下单</b>。
ST/*ST 股票退市/变脸风险极高，且 2026-7-6 新规后主板 ST 涨跌停已为 10%、创业板为 20%，单日波动显著放大。
所有价格以腾讯实时行情核验为准；重整/摘帽进度以公司公告与交易所审核结果为准，存在重大不确定性。请独立决策、严控仓位。</div>
</div></body></html>''')

out = r'C:\Users\EDY\AppData\Local\Temp\wb_analysis\ST_two_analysis_20260821.html'
open(out, 'w', encoding='utf-8').write('\n'.join(html))
print('WROTE', out)
