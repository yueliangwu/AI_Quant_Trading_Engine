# -*- coding: utf-8 -*-
import urllib.request, re, json

codes = ['sz000838','sz002726','sz002168','sz002542','sz300027','sz300147','sh600337','sh600340','sh600370','sz300020','sh600381']
url = 'http://qt.gtimg.cn/q=' + ','.join(codes)
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
body = urllib.request.urlopen(req, timeout=20).read().decode('gbk', errors='ignore')
print('---raw---')
print(body[:1000])
rows = []
for line in body.split(';'):
    m = re.search(r'v_\w+="([^"]+)"', line)
    if not m:
        continue
    parts = m.group(1).split('~')
    if len(parts) < 45:
        continue
    code = parts[2]
    name = parts[1]
    price = parts[3]
    prev_close = parts[4]
    change_pct = parts[32]
    turnover = parts[36]
    total_cap = parts[44]
    float_cap = parts[45]
    rows.append({
        'code': code, 'name': name, 'price': price, 'prev_close': prev_close,
        'change_pct': change_pct, 'turnover': turnover,
        'total_cap': total_cap, 'float_cap': float_cap
    })
print('---parsed---')
print(json.dumps(rows, ensure_ascii=False, indent=2))
