#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈药股份(600664) 累计涨幅异动识别函数
=====================================
功能：在滚动时间窗口内计算个股累计涨跌幅（或相对指数的偏离值），
      按阈值标记交易异常波动，输出异动时间点与对应涨幅数据。
适用：沪市主板（3日±20%偏离为异常波动；此处通用化，参数可调）。
零依赖：仅用 Python 标准库。
"""

from typing import List, Optional, Dict, Any


def _is_missing(v) -> bool:
    """判断是否为缺失值（None / NaN / 空字符串）。"""
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    try:
        return isinstance(v, float) and v != v  # NaN
    except Exception:
        return False


def _to_float(v) -> float:
    """将输入转为 float，无法转换则抛错。"""
    try:
        return float(v)
    except (TypeError, ValueError):
        raise ValueError(f"收盘价/指数涨跌幅必须为数值，收到: {v!r}")


def detect_cumulative_anomaly(
    dates: List[str],
    closes: List[float],
    window: int = 3,
    threshold: float = 0.20,
    index_returns: Optional[List[float]] = None,
    dropna: bool = True,
    mode: str = "deviation",
) -> Dict[str, Any]:
    """
    识别滚动窗口内的累计涨幅异动。

    参数
    ----
    dates : List[str]
        交易日日期列表，如 ['2026-08-18', ...]，须与 closes 等长且按时间升序。
    closes : List[float]
        对应收盘价列表（元）。允许含 None/NaN（见 dropna）。
    window : int, default 3
        滚动窗口长度（交易日数）。沪市主板异常波动认定窗口为 3 日。
    threshold : float, default 0.20
        累计偏离值（或累计涨幅）的绝对阈值。|metric| >= threshold 触发异动。
    index_returns : Optional[List[float]], default None
        对应交易日的大盘/板块指数涨跌幅（小数，如 0.012 = +1.2%）。
        若提供，则偏差 = 个股累计涨幅 - 指数累计涨幅（监管口径）；
        若 None 且 mode='deviation'，则退化为个股自身累计涨幅。
    dropna : bool, default True
        缺失值处理策略：
          True  -> 剔除含缺失的整行后，用剩余连续序列计算；
          False -> 保留，窗口内若含缺失则标记 data_gap 并跳过该窗口判断。
    mode : str, default 'deviation'
        'deviation'：使用「个股累计涨幅 − 指数累计涨幅」；
        'absolute' ：仅用个股自身累计涨幅（不扣指数）。

    返回
    ----
    Dict，含 daily_returns / cum_window / dev_window / anomalies / stats / warnings。
    anomalies 中每条记录异动的 start_date, end_date, cum_return, deviation,
    direction(up/down), breach(超出阈值幅度)。
    """
    warnings: List[str] = []

    # ---- 1. 输入校验 ----
    if not isinstance(dates, list) or not isinstance(closes, list):
        raise TypeError("dates 与 closes 必须为列表")
    if len(dates) != len(closes):
        raise ValueError(f"dates 与 closes 长度不一致: {len(dates)} vs {len(closes)}")
    if window < 1:
        raise ValueError("window 必须 >= 1")
    if mode not in ("deviation", "absolute"):
        raise ValueError("mode 必须为 'deviation' 或 'absolute'")

    # ---- 2. 缺失值处理 ----
    if dropna:
        clean = [(d, c) for d, c in zip(dates, closes) if not _is_missing(c)]
        if len(clean) < len(dates):
            warnings.append(f"dropna 已剔除 {len(dates)-len(clean)} 行缺失收盘价")
        dates = [x[0] for x in clean]
        closes = [_to_float(x[1]) for x in clean]
        if index_returns is not None:
            if len(index_returns) != len(dates):
                # 用原始长度对齐后再按 clean 索引截取
                idx_full = index_returns
                idx_clean = [idx_full[i] for i, (d, c) in enumerate(zip(dates, closes))]
            else:
                idx_clean = index_returns
            valid = [(d, c, i) for d, c, i in zip(dates, closes, idx_clean)
                     if (i is not None) and (not _is_missing(i))]
            if len(valid) < len(dates):
                warnings.append(f"dropna 已剔除 {len(dates)-len(valid)} 行缺失指数涨跌幅")
            dates = [v[0] for v in valid]
            closes = [v[1] for v in valid]
            index_returns = [_to_float(v[2]) for v in valid]
    else:
        closes = [None if _is_missing(c) else _to_float(c) for c in closes]
        if index_returns is not None:
            if len(index_returns) != len(closes):
                raise ValueError("index_returns 与 closes 长度不一致")
            index_returns = [None if _is_missing(i) else _to_float(i) for i in index_returns]

    n = len(closes)

    # ---- 3. 长度 / 边界 ----
    if n == 0:
        warnings.append("清洗后无有效数据，返回空结果")
        return _empty_result(window, threshold, mode, warnings)
    if n < window:
        warnings.append(f"有效样本 {n} < 窗口 {window}，无法构成完整窗口，无异动输出")

    # ---- 4. 每日涨跌幅（首日为 None，无前收）----
    daily: List[Optional[float]] = [None] * n
    for i in range(1, n):
        if closes[i] is None or closes[i - 1] is None or closes[i - 1] == 0:
            daily[i] = None
        else:
            daily[i] = (closes[i] - closes[i - 1]) / closes[i - 1]

    # ---- 5. 滚动累计 + 阈值判断 ----
    cum_window: List[Optional[float]] = [None] * n
    dev_window: List[Optional[float]] = [None] * n
    anomalies: List[Dict[str, Any]] = []

    for end in range(n):
        start = end - window + 1
        if start < 0:
            continue  # 窗口不足
        seg = daily[start:end + 1]
        if None in seg:
            if not dropna:
                cum_window[end] = None  # 标记 data_gap，跳过
                continue
            else:
                continue  # dropna 模式已无缺失
        cw = sum(seg)
        cum_window[end] = cw

        if mode == "deviation" and index_returns is not None:
            idx_seg = index_returns[start:end + 1]
            if None in idx_seg:
                dev_window[end] = None
                continue
            dev = cw - sum(idx_seg)
            dev_window[end] = dev
            metric = dev
        else:
            metric = cw

        if abs(metric) >= threshold:
            anomalies.append({
                "start_date": dates[start],
                "end_date": dates[end],
                "cum_return": round(cw, 4),
                "deviation": round(dev_window[end], 4) if dev_window[end] is not None else None,
                "direction": "up" if metric > 0 else "down",
                "breach": round(abs(metric) - threshold, 4),
            })

    # ---- 6. 汇总统计 ----
    stats = {
        "n_anomalies": len(anomalies),
        "first_anomaly": anomalies[0]["end_date"] if anomalies else None,
        "last_anomaly": anomalies[-1]["end_date"] if anomalies else None,
        "max_abs_metric": round(max(
            (abs(a["deviation"] if a["deviation"] is not None else a["cum_return"])
             for a in anomalies), default=0.0), 4),
    }

    return {
        "window": window, "threshold": threshold, "mode": mode, "n_obs": n,
        "daily_returns": daily, "cum_window": cum_window,
        "dev_window": dev_window if (mode == "deviation" and index_returns) else None,
        "anomalies": anomalies, "stats": stats, "warnings": warnings,
    }


def _empty_result(window, threshold, mode, warnings):
    return {
        "window": window, "threshold": threshold, "mode": mode, "n_obs": 0,
        "daily_returns": [], "cum_window": [], "dev_window": None,
        "anomalies": [],
        "stats": {"n_anomalies": 0, "first_anomaly": None, "last_anomaly": None, "max_abs_metric": 0.0},
        "warnings": warnings,
    }


def print_report(res: Dict[str, Any]) -> None:
    """友好打印异动报告。"""
    print(f"\n=== 异动检测报告 ===")
    print(f"窗口={res['window']}日  阈值=±{res['threshold']*100:.0f}%  "
          f"模式={res['mode']}  有效样本={res['n_obs']}")
    for w in res["warnings"]:
        print(f"  [WARN] {w}")
    if not res["anomalies"]:
        print("✅ 未检测到累计涨幅异动。")
        return
    print(f"检测到 {res['stats']['n_anomalies']} 次异动：")
    print(f"{'起始日':<12}{'结束日':<12}{'累计涨幅':>10}{'偏离值':>10}{'方向':>6}{'超限幅度':>10}")
    for a in res["anomalies"]:
        dev = f"{a['deviation']*100:+.1f}%" if a["deviation"] is not None else "  N/A"
        print(f"{a['start_date']:<12}{a['end_date']:<12}{a['cum_return']*100:>+9.1f}%"
              f"{dev:>10}{a['direction']:>6}{a['breach']*100:>+9.1f}%")


# ======================= 演示 / 测试 =======================
if __name__ == "__main__":
    # —— 场景A：哈药真实数据（8/5–8/20，来源腾讯行情）——
    dates_hy = ['2026-08-05','2026-08-06','2026-08-07','2026-08-10','2026-08-11',
                '2026-08-12','2026-08-13','2026-08-14','2026-08-17','2026-08-18',
                '2026-08-19','2026-08-20']
    closes_hy = [6.77,6.22,6.84,7.52,8.27,8.81,8.86,8.91,9.01,9.12,9.06,9.23]
    idx_ret   = [0.0147,0.0057,0.0102,0.0067,-0.0082,0.0032,-0.0050,0.0001,0.0141,0.0019,-0.0240,0.0028]

    print(">>> 场景A：哈药 3日窗口 ±20% 偏离值（监管口径）")
    print_report(detect_cumulative_anomaly(dates_hy, closes_hy, window=3, threshold=0.20,
                                           index_returns=idx_ret, mode="deviation", dropna=True))

    # —— 场景B：假设 8/18-8/20 连续涨停，验证阈值能抓异动 ——
    print("\n>>> 场景B：假设哈药 8/18-8/20 连续3涨停")
    resB = detect_cumulative_anomaly(
        ['2026-08-17','2026-08-18','2026-08-19','2026-08-20'],
        [9.01,9.12,10.03,11.03], window=3, threshold=0.20,
        index_returns=[0.0141,0.0019,-0.0240,0.0028], mode="deviation")
    print_report(resB)

    # —— 场景C：边界——空列表 ——
    print("\n>>> 场景C：边界测试 空列表")
    print_report(detect_cumulative_anomaly([], []))

    # —— 场景D：边界——含 None 缺失（dropna=False 标记 gap）——
    print("\n>>> 场景D：边界测试 含 None 缺失（dropna=False）")
    resD = detect_cumulative_anomaly(
        ['2026-08-17','2026-08-18','2026-08-19','2026-08-20'],
        [9.01, None, 9.06, 9.23], window=3, threshold=0.20,
        index_returns=[0.0141,0.0019,None,0.0028], mode="deviation", dropna=False)
    print_report(resD)
    print(f"  cum_window（含gap标记）: {resD['cum_window']}")

    # —— 场景E：边界——样本数 < 窗口 ——
    print("\n>>> 场景E：边界测试 样本数 < 窗口")
    print_report(detect_cumulative_anomaly(['2026-08-19','2026-08-20'], [9.06, 9.23], window=3))
