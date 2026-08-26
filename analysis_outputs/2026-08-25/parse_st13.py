import re, html as h

p = r"C:/Users/EDY/Documents/xwechat_files/wxid_g1ux6d3mps4x22_92ba/msg/file/2026-08/ST13_final_priority_20260820.html"
s = open(p, encoding='utf-8', errors='ignore').read()

# strip scripts/styles
s = re.sub(r'<script.*?</script>', '', s, flags=re.S|re.I)
s = re.sub(r'<style.*?</style>', '', s, flags=re.S|re.I)

def table_to_text(t):
    rows = re.findall(r'<tr.*?</tr>', t, flags=re.S|re.I)
    lines=[]
    for r in rows:
        cells = re.findall(r'<t[dh].*?</t[dh]>', r, flags=re.S|re.I)
        vals=[h.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in cells]
        lines.append(' | '.join(vals))
    return '\n'.join(lines)

tables = re.findall(r'<table.*?</table>', s, flags=re.S|re.I)
out=[]
for i,t in enumerate(tables):
    out.append(f"=== TABLE {i} ===")
    out.append(table_to_text(t))

heads = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', s, flags=re.S|re.I)
heads=[h.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in heads]

plain = re.sub(r'<[^>]+>',' ', s)
plain = h.unescape(plain)
plain = re.sub(r'\s+',' ', plain)

with open(r"C:/Users/EDY/AppData/Local/Temp/wb_analysis/st13_parsed.txt","w",encoding='utf-8') as f:
    f.write("### HEADINGS ###\n" + "\n".join(heads) + "\n\n")
    f.write("### TABLES ###\n\n" + "\n\n".join(out) + "\n\n")
    f.write("### PLAIN (method hints) ###\n" + plain[:8000])

print("tables:",len(tables),"heads:",len(heads))
print("written")
