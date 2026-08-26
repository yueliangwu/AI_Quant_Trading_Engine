import re, html as h, json

p = r"C:/Users/EDY/Documents/xwechat_files/wxid_g1ux6d3mps4x22_92ba/msg/file/2026-08/ST13_final_priority_20260820.html"
s = open(p, encoding='utf-8', errors='ignore').read()
s = re.sub(r'<script.*?</script>', '', s, flags=re.S|re.I)
s = re.sub(r'<style.*?</style>', '', s, flags=re.S|re.I)
plain = h.unescape(re.sub(r'<[^>]+>',' ', s))
plain = re.sub(r'\s+',' ', plain)

# split by P-sections
parts = re.split(r'(P\d+\s)', plain)
# parts: ['intro', 'P1 ', 'text', 'P2 ', 'text', ...]
details = []
i = 1
while i < len(parts)-1:
    tag = parts[i].strip()  # Pn
    body = parts[i+1]
    if '四、关键结论' in body:
        body = body.split('四、关键结论')[0]
    code = re.search(r'(\d{6})', body)
    name = re.search(r'(ST[^ ]+|[*\*]?ST\S+|ST\S+)', body)
    # name: capture before code-ish; use pattern "ST人福 ST 600079"
    mname = re.search(r'(ST[^*\s][^\s]*|[*]ST[^\s][^\s]*)', body)
    # four dims
    dims = re.search(r'退市风险\s*([\d.]+)\s*重组预期\s*([\d.]+)\s*基本面改善\s*([\d.]+)\s*市场关注度\s*([\d.]+)', body)
    risk_lv = re.search(r'风险等级[:：]\s*([^排序理由]+?)(?=排序理由|$)', body)
    reason = re.search(r'排序理由[:：]\s*([^核心催化]+?)(?=核心催化|$)', body)
    catalyst = re.search(r'核心催化[:：]\s*([^主要风险]+?)(?=主要风险|$)', body)
    risk = re.search(r'主要风险[:：]\s*(.+?)(?=P\d+|四、关键结论|$)', body)
    rec = {
        'pri': tag,
        'name': mname.group(1) if mname else '',
        'code': code.group(1) if code else '',
        'dims': [float(x) for x in dims.groups()] if dims else None,
        'risk_level': risk_lv.group(1).strip()[:60] if risk_lv else '',
        'reason': reason.group(1).strip()[:300] if reason else '',
        'catalyst': catalyst.group(1).strip()[:200] if catalyst else '',
        'risk': risk.group(1).strip()[:200] if risk else '',
    }
    details.append(rec)
    i += 2

json.dump(details, open(r"C:/Users/EDY/AppData/Local/Temp/wb_analysis/st13_details.json","w",encoding='utf-8'), ensure_ascii=False, indent=2)
print("extracted:", len(details))
for d in details:
    print(d['pri'], d['code'], d['name'], d['dims'])
