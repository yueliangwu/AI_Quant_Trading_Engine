import urllib.request, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://gu.qq.com'})
    return urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8','ignore')

pre='sz002726'
k = get(f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={pre},day,2026-04-01,2026-08-21,150,qfq')
m = get(f'https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={pre}')

jk=json.loads(k)
kl=jk['data'][pre]['qfqday']
closes=[float(x[2]) for x in kl]; vols=[float(x[5]) for x in kl]
def ma(arr,n): return [round(sum(arr[i-n:i])/n,3) if i>=n else None for i in range(1,len(arr)+1)]
ma5=ma(closes,5);ma10=ma(closes,10);ma20=ma(closes,20);ma60=ma(closes,60)
vma5=ma(vols,5);vma10=ma(vols,10)
n=len(closes)
rec=[]
for i in range(max(0,n-18),n):
    o=float(kl[i][1]);c=float(kl[i][2]);h=float(kl[i][3]);l=float(kl[i][4]);v=float(kl[i][5])
    pct=(c-float(kl[i-1][2]))/float(kl[i-1][2])*100 if i>0 else 0
    rng=(h-l)/o*100
    rec.append({'d':kl[i][0][:10],'o':o,'c':c,'h':h,'l':l,'v':round(v/10000,1),
                'pct':round(pct,2),'range':round(rng,2),
                'ma5':ma5[i],'ma10':ma10[i],'ma20':ma20[i],'ma60':ma60[i],
                'vma5':round(vma5[i]/10000,1) if vma5[i] else None,
                'vma10':round(vma10[i]/10000,1) if vma10[i] else None})
print('=== LAST 18 DAYS (qfq) ===')
for r in rec:
    print(f"{r['d']} O={r['o']} C={r['c']} H={r['h']} L={r['l']} V={r['v']}万手 pct={r['pct']}% rng={r['range']}% MA5/10/20/60={r['ma5']}/{r['ma10']}/{r['ma20']}/{r['ma60']} VMA5={r['vma5']}")

# 分时
md=json.loads(m); mm=md['data'][pre]['data']['data']
print('\n=== MINUTE (%d pts) ===' % len(mm))
for idx in [0,20,40,60,90,120,150,180,210,239,len(mm)-1]:
    if 0<=idx<len(mm): print(mm[idx])
# 提取价格序列
mp=[float(x.split()[1]) for x in mm if ' ' in x]
print('\nMinute price range: low=%.2f high=%.2f open=%.2f close=%.2f' % (min(mp),max(mp),mp[0],mp[-1]))
# 找日内最低/最高出现时间
lo_i=mp.index(min(mp)); hi_i=mp.index(max(mp))
print('Intraday LOW at', mm[lo_i].split()[0], '| HIGH at', mm[hi_i].split()[0])

out={'kline':kl,'recent':rec,'minute':mm,'mp':mp}
json.dump(out, open('C:/Users/EDY/AppData/Local/Temp/wb_analysis/longda_tech.json','w',encoding='utf-8'), ensure_ascii=False)
print('\nSAVED longda_tech.json')
