# -*- coding: utf-8 -*-
import urllib.request, re

codes = ['000838','002726','002168','002542','300027','300147','600337','600340','600370','300020','600381']
url = 'http://qt.gtimg.cn/q=' + ','.join(codes)
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
body = urllib.request.urlopen(req, timeout=20).read().decode('gbk', errors='ignore')
print('---first 800---')
print(body[:800])
print('---len---', len(body))
# try parse
for line in body.split(';'):
    if line.strip():
        print('line len', len(line), line[:120])
