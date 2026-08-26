# -*- coding: utf-8 -*-
"""抓取 ST龙大(002726) 日K/周K/实时快照，计算均线与支撑压力。仅存 Temp。"""
import requests, json, sys

H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://gu.qq.com/'
}

def get_kline(sym, ktype, n):
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={sym},{ktype},,,{n},qfq'
    r = requests.get(url, headers=H, timeout=20)
    j = r.json()
    node = j['data'][sym]
    k = node.get('qfq' + ktype) or node.get(ktype)
    return k

def ma(vals, w):
    if len(vals) < w:
        return None
    return round(sum(vals[-w:]) / w, 3)

def analyze(sym='sz002726'):
    day = get_kline(sym, 'day', 90)
    week = get_kline(sym, 'week', 60)
    # 实时快照
    r = requests.get(f'https://qt.gtimg.cn/q={sym}', headers=H, timeout=20)
    f = r.text.split('"')[1].split('~')

    closes_d = [float(x[2]) for x in day]
    dates_d = [x[0] for x in day]
    highs_d = [float(x[3]) for x in day]
    lows_d = [float(x[4]) for x in day]
    vols_d = [float(x[5]) for x in day]

    out = {
        'name': f[1], 'code': f[2], 'price': float(f[3]), 'prev_close': float(f[4]),
        'open': float(f[5]), 'high': float(f[6]), 'low': float(f[7]),
        'pct': f[32], 'turnover': f[38], 'pe': f[39], 'pb': f[46],
        'mktcap': f[45], 'circ_mktcap': f[44],
        'date_last': dates_d[-1],
        'ma_daily': {
            'MA5': ma(closes_d, 5), 'MA10': ma(closes_d, 10),
            'MA20': ma(closes_d, 20), 'MA60': ma(closes_d, 60)
        },
        'last5_daily': [{'date': dates_d[-i], 'o': day[-i][1], 'c': day[-i][2],
                         'h': day[-i][3], 'l': day[-i][4], 'v': day[-i][5],
                         'pct': round((float(day[-i][2])-float(day[-i-1][2]))/float(day[-i-1][2])*100, 2)}
                        for i in range(1, 9)][::-1],
        'weekly_close': [{'date': w[0], 'c': float(w[2]), 'h': float(w[3]), 'l': float(w[4])} for w in week[-12:]],
        'ma_weekly': {
            'MA5': ma([float(x[2]) for x in week], 5),
            'MA10': ma([float(x[2]) for x in week], 10),
            'MA20': ma([float(x[2]) for x in week], 20),
            'MA60': ma([float(x[2]) for x in week], 60),
        },
    }
    # 近60日高低与密集成交区(简单用最近20日)
    recent20 = closes_d[-20:]
    out['range_60d'] = {'high': max(highs_d[-60:]), 'low': min(lows_d[-60:]),
                        'close_min20': min(recent20), 'close_max20': max(recent20)}
    # 量能
    out['vol_avg5'] = round(sum(vols_d[-5:])/5, 1)
    out['vol_avg20'] = round(sum(vols_d[-20:])/20, 1)
    out['vol_last'] = vols_d[-1]
    out['vol_ratio'] = round(vols_d[-1] / (sum(vols_d[-6:-1])/5), 2)
    print(json.dumps(out, ensure_ascii=False, indent=2))

analyze()
