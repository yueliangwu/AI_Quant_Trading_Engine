"""ST京蓝(000711) 日K/周K/实时快照抓取与指标计算。仅放Temp，不写项目目录。"""
import requests, json, sys

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
     'Referer': 'https://gu.qq.com/'}

def get_json(url, tag):
    for _ in range(3):
        try:
            r = requests.get(url, headers=H, timeout=25)
            if r.status_code == 200 and r.text.strip():
                return r.json()
        except Exception as e:
            print('[retry]', tag, repr(e))
    return None

def kline(sym, ktype, n):
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={sym},{ktype},,,{n},qfq'
    j = get_json(url, ktype)
    if not j: return []
    node = j['data'][sym]
    arr = node.get('qfqday') or node.get('day') or node.get('qfqweek') or node.get('week') or []
    out = []
    for row in arr:
        out.append({'date': row[0], 'open': float(row[1]), 'close': float(row[2]),
                    'high': float(row[3]), 'low': float(row[4]), 'vol': float(row[5])})
    return out

def ma(closes, n):
    if len(closes) < n: return None
    return round(sum(closes[-n:]) / n, 3)

def compute(lst, label):
    print(f"\n===== {label} ({len(lst)} 根) 最新 {lst[-1]['date']} =====")
    closes = [x['close'] for x in lst]
    # 均线
    m = {n: ma(closes, n) for n in (5, 10, 20, 60)}
    print('MA:', m)
    last = lst[-1]
    print(f"最新: 开{last['open']} 收{last['close']} 高{last['high']} 低{last['low']} 量{last['vol']/1e4:.1f}万手")
    # 近10日
    print('近10日(日期,收,涨跌幅%):')
    for i in range(max(1, len(lst)-10), len(lst)):
        chg = (lst[i]['close']-lst[i-1]['close'])/lst[i-1]['close']*100
        print(f"  {lst[i]['date']} {lst[i]['close']:.2f} {chg:+.2f}%")
    # 支撑/压力：近期高/低
    recent = lst[-40:]
    highs = [x['high'] for x in recent]; lows = [x['low'] for x in recent]
    print(f"近40日高点 {max(highs):.2f}（{[x['date'] for x in recent if x['high']==max(highs)][-1]}） "
          f"低点 {min(lows):.2f}（{[x['date'] for x in recent if x['low']==min(lows)][-1]}）")
    if len(closes) >= 60:
        print(f"MA60={m[60]} MA20={m[20]} MA10={m[10]} MA5={m[5]} 排列:", 
              '多头' if m[5]>m[10]>m[20]>m[60] else ('空头' if m[5]<m[10]<m[20]<m[60] else '纠缠/黏合'))
    return m

# 实时快照
def snapshot(sym):
    r = requests.get(f'https://qt.gtimg.cn/q={sym}', headers=H, timeout=20)
    for line in r.text.strip().split(';'):
        line=line.strip()
        if line.startswith(f'v_{sym}'):
            f=line[line.index('"')+1:line.rindex('"')].split('~')
            return {'name':f[1],'price':f[3],'pct':f[32],'prev':f[4],'pe':f[39],'pb':f[46],
                    'mktcap':f[45],'turn':f[38],'amt':f[37]}
    return {}

daily = kline('sz000711', 'day', 70)
weekly = kline('sz000711', 'week', 60)
m_d = compute(daily, '日K')
m_w = compute(weekly, '周K')
snap = snapshot('sz000711')
print('\n===== 实时快照 =====')
print(snap)

# 输出JSON供后续使用
data = {'daily': daily, 'weekly': weekly, 'ma_daily': m_d, 'ma_weekly': m_w, 'snapshot': snap}
with open(r'C:\Users\EDY\AppData\Local\Temp\wb_analysis\jl_data.json','w') as fp:
    json.dump(data, fp, ensure_ascii=False)
print('\n[OK] 已写入 jl_data.json')
