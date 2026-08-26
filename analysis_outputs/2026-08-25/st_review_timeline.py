# -*- coding: utf-8 -*-
"""
ST摘帽审核时长测算 + 京蓝通过日预测
数据源：公开披露（巨潮/上交所/公司正式公告），按信源优先级录入。
- 宁科(600165): 申请日以公司正式公告(上海证券报 2026-047) 2026-08-15 为准；部分媒体记作 08-14
- 长圆(600525): 申请 2026-08-14，上交所同意 2026-08-24
- 京蓝(000711): 申请 2026-08-24（公告 2026-079），审核中
规则基准：上交所/深交所对撤销其他风险警示申请，在收到后 15 个交易日内决定是否同意（补材料不计入）。
"""
from datetime import date, timedelta
import json

# ---- 数据源（均为已核验公开披露）----
DATA = {
    "宁科(600165)": {
        "apply": date(2026, 8, 15),
        "approve": date(2026, 8, 24),
        "note": "申请日以公司正式公告(上海证券报2026-047)为准；新浪/腾讯/央广新闻稿记作08-14，存在公开源分歧",
        "exchange": "上交所",
    },
    "长圆(600525)": {
        "apply": date(2026, 8, 14),
        "approve": date(2026, 8, 24),
        "note": "8-14申请→8-24上交所同意撤销其他风险警示",
        "exchange": "上交所",
    },
    "京蓝(000711)": {
        "apply": date(2026, 8, 24),       # 申请提交日：8-24盘后董事会通过并正式向深交所提交
        "receipt": date(2026, 8, 25),     # 深交所受理日(推定)：盘后提交，次一交易日(8-25)受理
        "disclose": date(2026, 8, 25),    # 对外披露日：巨潮/三大报 8-25 刊登公告2026-079
        "approve": None,  # 审核中
        "note": "申请提交日8-24(董事会决议公告2026-078/申请公告2026-079落款均为8-24)；"
                "对外披露日8-25；深交所受理日推定8-25(盘后提交,次一交易日受理)。"
                "审核期不停牌,15交易日上限自受理次日起算",
        "exchange": "深交所",
    },
}


def trading_days_inclusive(a: date, b: date) -> int:
    """含 a、含 b 的交易日数（仅排除周末，忽略法定节假日；测算区间无长假，可接受）。"""
    if b < a:
        a, b = b, a
    cnt, d = 0, a
    while d <= b:
        if d.weekday() < 5:
            cnt += 1
        d += timedelta(days=1)
    return cnt


def cal_days(a: date, b: date) -> int:
    return (b - a).days


def trading_days_from_receipt(a: date, b: date) -> int:
    """按规则口径：自申请受理次日起算的交易日数（不含申请日）。"""
    next_d = a + timedelta(days=1)
    return trading_days_inclusive(next_d, b)


def main():
    print("=" * 78)
    print("  ST摘帽审核时长测算与京蓝通过日预测")
    print("  生成时间基准：2026-08-25")
    print("=" * 78)

    hist = []
    print("\n【一、宁科 / 长圆 历史审核时长】")
    print("-" * 78)
    print(f"{'主体':<12}{'申请日':<14}{'通过日':<14}{'自然日':>6}{'交易日(含申请)':>14}{'交易日(受理次日起)':>16}")
    for name, info in DATA.items():
        if info["approve"] is None:
            continue
        a, b = info["apply"], info["approve"]
        cd = cal_days(a, b)
        td_inc = trading_days_inclusive(a, b)
        td_rec = trading_days_from_receipt(a, b)
        hist.append(td_inc)
        print(f"{name:<10}{a.isoformat():<14}{b.isoformat():<14}{cd:>6}{td_inc:>14}{td_rec:>16}")
        print(f"    ↳ {info['note']}")

    avg_cd = sum(cal_days(info['apply'], info['approve']) for n, info in DATA.items() if info['approve']) / len(hist)
    avg_td = sum(hist) / len(hist)
    print("-" * 78)
    print(f"历史均值：自然日 {avg_cd:.1f} 天 | 交易日(含申请) {avg_td:.1f} 天")

    print("\n【二、京蓝(000711) 预测】")
    print("-" * 78)
    j = DATA["京蓝(000711)"]
    ja = j["apply"]
    jr = j.get("receipt", ja)   # 受理日(推定)：盘后提交则次一交易日受理
    jd = j.get("disclose", ja)
    print(f"京蓝申请提交日：{ja.isoformat()}  ({j['exchange']})")
    print(f"京蓝对外披露日：{jd.isoformat()}  (巨潮/三大报刊登公告2026-079)")
    print(f"京蓝深交所受理日(推定)：{jr.isoformat()}  (盘后提交→次一交易日受理)")
    # 历史两只"受理次日起"均为 6 交易日 → 最贴合规则口径的基准
    hist_receipt = [trading_days_from_receipt(info["apply"], info["approve"])
                    for n, info in DATA.items() if info["approve"]]
    base_receipt = sum(hist_receipt) / len(hist_receipt)
    pred_base = trading_days_to_target(jr, round(base_receipt), start_next=True)   # 受理次日起6交易日
    pred_upper = trading_days_to_target(jr, 15, start_next=True)                    # 规则上限15交易日(受理次日起)
    pred_upper_incl = trading_days_to_target(jr, 15)                               # 含受理日15交易日(偏早口径)
    print(f"历史基准(受理次日起交易日均值)：{base_receipt:.0f} 交易日")
    print(f"规则上限：收到后 15 个交易日内(受理次日起算) → 最迟 {pred_upper.isoformat()}")
    print(f"        （若以含受理日第15交易日计则为 {pred_upper_incl.isoformat()}，偏早1日，非标准口径）")
    print(f"\n预测通过日（多情景）：")
    print(f"  · 主预测(历史基准{round(base_receipt)}交易日,受理次日起): {pred_base.isoformat()}  (自然间隔 {cal_days(jr, pred_base)} 天)")
    print(f"  · 偏早口径(含受理日{round(avg_td)}交易日): {trading_days_to_target(jr, round(avg_td)).isoformat()}  (自然间隔 {cal_days(jr, trading_days_to_target(jr, round(avg_td)))} 天)")
    print(f"  · 上限(规则15交易日,受理次日起): {pred_upper.isoformat()}  (自然间隔 {cal_days(jr, pred_upper)} 天)")

    print("\n【三、结论】")
    print("-" * 78)
    nk = DATA["宁科(600165)"]
    cy = DATA["长圆(600525)"]
    print(f"宁科审核耗时：自然日 {cal_days(nk['apply'], nk['approve'])} 天，"
          f"交易日(含申请) {trading_days_inclusive(nk['apply'], nk['approve'])} 天，"
          f"受理次日起 {trading_days_from_receipt(nk['apply'], nk['approve'])} 天")
    print(f"长圆审核耗时：自然日 {cal_days(cy['apply'], cy['approve'])} 天，"
          f"交易日(含申请) {trading_days_inclusive(cy['apply'], cy['approve'])} 天，"
          f"受理次日起 {trading_days_from_receipt(cy['apply'], cy['approve'])} 天")
    print(f"京蓝预测通过日：主预测 {pred_base.isoformat()}（受理次日起{round(base_receipt)}交易日），"
          f"法定最迟 {pred_upper.isoformat()}（规则15交易日,受理次日起）")
    print(f"预测依据：宁科/长圆均于 8 月中旬申请、8-24 同日通过，且『受理次日起』均为 6 个交易日；")
    print(f"          京蓝 8-24(周一)盘后提交申请、8-25(周二)受理 → 平移同等节奏 → "
          f"{pred_base.isoformat()}(周三)过会概率最高；若被问询补材料则顺延至 {pred_upper.isoformat()}。")

    # 结构化输出（供下游/日志使用）
    out = {
        "generated": "2026-08-25",
        "history": [
            {"name": n, "apply": info["apply"].isoformat(), "approve": info["approve"].isoformat(),
             "calendar_days": cal_days(info["apply"], info["approve"]),
             "trading_days": trading_days_inclusive(info["apply"], info["approve"]),
             "note": info["note"]}
            for n, info in DATA.items() if info["approve"]
        ],
        "history_avg": {"calendar_days": round(avg_cd, 1), "trading_days": round(avg_td, 1)},
        "jinglan": {
            "apply": ja.isoformat(),
            "receipt": jr.isoformat(),
            "disclose": jd.isoformat(),
            "predict_main": pred_base.isoformat(),
            "predict_early": trading_days_to_target(jr, round(avg_td)).isoformat(),
            "predict_upper_limit": pred_upper.isoformat(),
            "rule_upper_limit_trading_days": 15,
        },
    }
    with open("st_review_timeline_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n[√] 结构化结果已写入 st_review_timeline_result.json")


def trading_days_to_target(start: date, n: int, start_next: bool = False) -> date:
    """返回从 start 起第 n 个交易日的日期。start_next=True 表示从 start 的次日起算。"""
    d = start + timedelta(days=1) if start_next else start
    cnt = 0
    while True:
        if d.weekday() < 5:
            cnt += 1
            if cnt == n:
                return d
        d += timedelta(days=1)


if __name__ == "__main__":
    main()
