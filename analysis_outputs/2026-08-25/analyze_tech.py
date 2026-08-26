# -*- coding: utf-8 -*-
import json

with open("C:/Users/EDY/AppData/Local/Temp/wb_analysis/tech_data_20260825.json", encoding="utf-8") as f:
    D = json.load(f)

def ma(vals, n):
    if len(vals) < n: return None
    return sum(vals[-n:]) / n

# EastMoney fflow day fields mapping (klt=101)
# f51 date, f52 主力净流入(元), f53 主力占比%, f54 超大单净流入(元), f55 超大单占比%,
# f56 大单净流入(元), f57 大单占比%, f58 中单净流入(元), f59 中单占比%,
# f60 小单净流入(元), f61 小单占比%, f62 收盘价, f63 涨跌幅%
def parse_fflow_day(rows):
    out = []
    for r in rows:
        try:
            out.append({
                "date": r[0], "main": float(r[1]), "main_pct": float(r[2]),
                "xl": float(r[3]), "xl_pct": float(r[4]),
                "lg": float(r[5]), "lg_pct": float(r[6]),
                "mid": float(r[7]), "mid_pct": float(r[8]),
                "sm": float(r[9]), "sm_pct": float(r[10]),
                "close": float(r[11]) if len(r) > 11 else None,
                "pct": float(r[12]) if len(r) > 12 else None,
            })
        except Exception as e:
            out.append({"date": r[0] if r else "?", "err": str(e)})
    return out

# minute fflow klt=1 : f51 time(HHMM), f52 主力净流入(累计? per-min?), same fields
def parse_fflow_min(rows):
    out = []
    for r in rows:
        try:
            out.append({
                "t": r[0], "main": float(r[1]), "main_pct": float(r[2]),
                "xl": float(r[3]), "lg": float(r[5]), "mid": float(r[7]), "sm": float(r[9]),
            })
        except Exception as e:
            out.append({"t": r[0] if r else "?", "err": str(e)})
    return out

for key in ["longda", "jinglan"]:
    s = D[key]
    kl = s["kline"]
    snap = s["snapshot"]
    print("="*70)
    print(f"{key.upper()}  {snap.get('name')} 现价={snap.get('price')} 涨跌幅={snap.get('pct')}% 换手={snap.get('turnover')}% 量比={snap.get('wb')}")
    print(f"  今开={snap.get('open')} 昨收={snap.get('prev_close')} 最高={snap.get('high')} 最低={snap.get('low')} 均价={snap.get('avg')}")
    print(f"  成交量(手)={snap.get('volume_hand')} 流通市值={snap.get('circ_mv')}亿 总市值={snap.get('total_mv')}亿")
    closes = [b["close"] for b in kl]
    vols = [b["vol"] for b in kl]
    # verify fflow close mapping
    fd = parse_fflow_day(s["em_fflow_day"]) if isinstance(s["em_fflow_day"], list) else []
    print(f"  fflow_day bars={len(fd)}; verify last fflow close vs kline close: fflow={fd[-1] if fd else None}")
    print("\n  近15日 日期 收 开 高 低 量(万手) MA5 MA10 MA20 MA60 主力净流入(万) 主力%")
    for i in range(max(0,len(kl)-15), len(kl)):
        b = kl[i]
        c5 = ma(closes[:i+1],5); c10=ma(closes[:i+1],10); c20=ma(closes[:i+1],20); c60=ma(closes[:i+1],60)
        fmatch = next((x for x in fd if x.get("date")==b["date"]), None)
        mainw = fmatch["main"]/1e4 if fmatch and "main" in fmatch else None
        mainp = fmatch["main_pct"] if fmatch and "main_pct" in fmatch else None
        print(f"  {b['date']} {b['close']:.2f} {b['open']:.2f} {b['high']:.2f} {b['low']:.2f} {b['vol']/1e4:.1f} "
              f"{c5:.2f} {c10:.2f} {c20:.2f} {c60:.2f}  {mainw if mainw is not None else '-':}  {mainp if mainp is not None else '-'}")
    # today minute flow
    fm = parse_fflow_min(s["em_fflow_min"]) if isinstance(s["em_fflow_min"], list) else []
    print(f"\n  分时资金流(分钟级) bars={len(fm)}; 末值主力累计={fm[-1] if fm else None}")
    if fm:
        # split morning/afternoon by time string 'HHMM'
        morn = [x for x in fm if x.get("t") and str(x["t"])[:2] in ("09","10","11")]
        aft = [x for x in fm if x.get("t") and str(x["t"])[:2] in ("13","14","15")]
        def summ(lst):
            return {
                "main": sum(x["main"] for x in lst if "main" in x)/1e4,
                "xl": sum(x["xl"] for x in lst if "xl" in x)/1e4,
                "lg": sum(x["lg"] for x in lst if "lg" in x)/1e4,
                "mid": sum(x["mid"] for x in lst if "mid" in x)/1e4,
                "sm": sum(x["sm"] for x in lst if "sm" in x)/1e4,
            } if lst else {}
        ms, as_ = summ(morn), summ(aft)
        print(f"  上午 主力={ms.get('main'):.1f}万 超大={ms.get('xl'):.1f} 大={ms.get('lg'):.1f} 中={ms.get('mid'):.1f} 小={ms.get('sm'):.1f}")
        print(f"  下午 主力={as_.get('main'):.1f}万 超大={as_.get('xl'):.1f} 大={as_.get('lg'):.1f} 中={as_.get('mid'):.1f} 小={as_.get('sm'):.1f}")
