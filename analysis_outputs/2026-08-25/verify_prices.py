import requests, time

# 上一轮所有提及代码（去重），以今天收盘真实行情逐只核对
codes = [
    # 重整组
    '000838','002726','002168','002542','300027','300147','600337','600340',
    # 重组/跨界
    '002289','002058','300093','600228',
    # 控股股东变更
    '000608','603637','600370',
    # 摘帽组
    '002047','300869','300020','300159','600381',
    # 1-2元清单
    '002717','688496','002146','002024','601005','000656','002482','002323',
    '600606','002501','600187','600022','600221','600567','002431','600518',
    '600491','601992','600239','600180','000564','601010','002269','000882',
    '002731','002217','000639','600881','601880','600157','600162','601588',
    '002936','002496','600743','600307','600653',
]

def pref(c):
    return ('sh' if c[0] in '69' else 'sz') + c

H = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36','Referer':'https://gu.qq.com/'}

rows = []
for i in range(0, len(codes), 20):
    seg = codes[i:i+20]
    q = ','.join(pref(c) for c in seg)
    try:
        r = requests.get('https://qt.gtimg.cn/q='+q, headers=H, timeout=25)
        for line in r.text.strip().split(';'):
            line = line.strip()
            if not line.startswith('v_'):
                continue
            code = line[2:line.index('=')]
            inner = line[line.index('"')+1:line.rindex('"')]
            f = inner.split('~')
            if len(f) < 47:
                rows.append((code,'PARSE_FAIL','','','','',''))
                continue
            name = f[1]; price = f[3]; pct = f[32]; prev = f[4]
            pe = f[39]; mktcap = f[45]
            rows.append((code, name, price, pct, prev, mktcap))
    except Exception as e:
        print('BATCH_ERR', seg[0], repr(e))
    time.sleep(0.5)

print(f"{'代码':<8}{'名称':<12}{'现价':>8}{'涨跌幅%':>9}{'昨收':>8}{'总市值(亿)':>12}")
for code, name, price, pct, prev, mktcap in rows:
    print(f"{code:<8}{name:<12}{price:>8}{pct:>9}{prev:>8}{mktcap:>12}")
print('TOTAL', len(rows))
