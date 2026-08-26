# -*- coding: utf-8 -*-
import urllib.request, re, json

codes = ['000838','002726','002168','002542','300027','300147','600337','600340','600370','300020','600381']
url = 'http://qt.gtimg.cn/q=' + ','.join(codes)
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
body = urllib.request.urlopen(req, timeout=20).read().decode('gbk', errors='ignore')
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
    open_ = parts[5]
    high = parts[33]
    low = parts[34]
    change_pct = parts[32]
    turnover = parts[36]
    total_cap = parts[44]  # 总市值（亿元）
    float_cap = parts[45]  # 流通市值（亿元）
    rows.append({
        'code': code, 'name': name, 'price': price, 'prev_close': prev_close,
        'open': open_, 'high': high, 'low': low, 'change_pct': change_pct,
        'turnover': turnover, 'total_cap': total_cap, 'float_cap': float_cap
    })

out_path = r'C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_11_quote_20260820.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(json.dumps(rows, ensure_ascii=False, indent=2))
