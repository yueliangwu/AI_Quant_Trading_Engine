import urllib.request, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://gu.qq.com'})
    return urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8','ignore')

code='002726'
k = get(f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,2026-05-01,2026-08-21,120,qfq')
m = get(f'https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={code}')

jk=json.loads(k)
print('KLINE top type:', type(jk), 'keys:', list(jk.keys()) if isinstance(jk,dict) else 'LIST')
d=jk.get('data')
print('data type:', type(d))
if isinstance(d,dict):
    print('data keys:', list(d.keys()))
    for kk in d.keys():
        v=d[kk]
        print(' ', kk, type(v))
        if isinstance(v,dict):
            print('   subkeys:', list(v.keys()))
            for sk in v.keys():
                sv=v[sk]
                if isinstance(sv,list):
                    print('     ',sk,'list len',len(sv),'sample',sv[0] if sv else None)
print('\nRAW head:', k[:300])

jm=json.loads(m)
print('\nMINUTE top type:', type(jm))
md=jm.get('data')
print('min data type:', type(md))
if isinstance(md,dict):
    print('min data keys:', list(md.keys()))
    for kk in md.keys():
        v=md[kk]
        print(' ',kk,type(v))
        if isinstance(v,dict):
            print('   subkeys:', list(v.keys()))
            for sk in v.keys():
                sv=v[sk]
                if isinstance(sv,list):
                    print('     ',sk,'len',len(sv),'sample',sv[0] if sv else None)
print('\nMIN RAW head:', m[:300])
