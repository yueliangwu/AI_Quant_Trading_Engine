"""
哈药股份(600664) 今日收盘价"不触发异动"的安全区间计算函数
================================================================

依据 A 股（沪市主板）异动规则，构造一个可复用的函数：
  输入  昨日收盘价 + 今日实际/假设收盘价（必填）
        + 前 2 日个股/指数涨跌幅、今日指数涨跌幅、今日换手率（可选，缺失则相应约束降级）
  输出  不触发异动的最大允许涨跌幅区间（小数）与对应价格区间，并标注所用阈值参数

【本函数遵循的异动阈值参数（均为可配置入参，默认值见函数签名）】
  T1 日涨跌幅偏离值阈值       daily_dev_threshold = 0.07   (±7%，本次任务指定；主板标准异动以 T2 为准)
  T2 连续3日涨跌幅累计偏离值   cum_dev_threshold    = 0.20   (±20%，上交所主板"交易异常波动"认定口径)
  T3 日涨跌幅停硬约束          daily_limit          = 0.10   (主板 ±10% 涨跌停，硬边界)
  T4 日换手率阈值             turnover_threshold    = 0.20   (20%，达到即记为换手率异动)
  ※ 说明：±7% 日偏离为需求方指定阈值；A 股主板标准异动以"连续3日累计偏离±20%"为准，
          本函数将其作为独立约束实现，便于按需调整。
"""

from typing import List, Optional, Dict, Any, Tuple


def _clamp_range(lo: float, hi: float) -> Optional[Tuple[float, float]]:
    """返回区间交集；若 lo>hi 说明无解（任何价格都会触发异动）。"""
    if lo > hi:
        return None
    return (lo, hi)


def _intersect(ranges: List[Optional[Tuple[float, float]]]) -> Optional[Tuple[float, float]]:
    """对多个区间取交集，忽略 None（数据缺失被降级的约束）。"""
    valid = [r for r in ranges if r is not None]
    if not valid:
        return None
    lo = max(r[0] for r in valid)
    hi = min(r[1] for r in valid)
    return _clamp_range(lo, hi)


def compute_safe_range(
    yesterday_close: float,
    today_close: Optional[float] = None,
    # —— 前 2 个交易日（用于 3 日累计偏离）——
    prior_individual_returns: Optional[List[float]] = None,   # 个股前2日日涨跌幅(小数)，如 [0.0122, -0.0066]
    prior_index_returns: Optional[List[float]] = None,       # 指数前2日日涨跌幅(小数)，如 [0.0019, -0.0240]
    # —— 今日指数涨跌幅（用于日偏离 & 3日累计偏离的今日项）——
    index_today_return: float = 0.0,
    # —— 今日换手率（用于换手率异动判定，不参与价格边界计算）——
    today_turnover: Optional[float] = None,
    # —— 阈值参数（可配置）——
    daily_dev_threshold: float = 0.07,    # T1 ±7%
    cum_dev_threshold: float = 0.20,      # T2 ±20%
    daily_limit: float = 0.10,            # T3 ±10% 涨跌停
    turnover_threshold: float = 0.20,     # T4 20%
) -> Dict[str, Any]:
    """
    计算今日收盘价相对昨收，不触发任何异动规则的最大允许涨跌幅区间与价格区间。

    返回字典含：
      threshold_params        实际使用的阈值参数（透明可核）
      daily_change_constraints 各价格类约束推导出的涨跌幅区间(小数)
      allowed_change_range    综合交集（小数），None 表示无解
      allowed_price_range     对应价格区间（元），None 表示无解
      binding_constraints     构成最紧边界的约束名
      turnover_check          换手率约束判定（独立非价格约束）
      warnings               数据缺失/降级的提示
      evaluation             若传入 today_close，给出是否触发及触发项
    """
    warnings: List[str] = []

    # ---------- 输入校验 ----------
    if not isinstance(yesterday_close, (int, float)) or yesterday_close <= 0:
        raise ValueError("yesterday_close 必须为正数")
    yesterday_close = float(yesterday_close)

    # ---------- 约束推导：各价格类约束 -> 今日涨跌幅 r3 的允许区间 ----------
    constraints: Dict[str, Optional[Tuple[float, float]]] = {}

    # T3 日涨跌停硬约束（不依赖外部数据）
    constraints["daily_limit"] = (-daily_limit, daily_limit)

    # T1 日涨跌幅偏离值：|r3 - index_today| < daily_dev_threshold
    constraints["daily_deviation"] = (
        -daily_dev_threshold + index_today_return,
        daily_dev_threshold + index_today_return,
    )

    # T2 连续3日累计偏离（需前2日数据；缺失则降级跳过）
    cum_constraint: Optional[Tuple[float, float]] = None
    if prior_individual_returns is not None and prior_index_returns is not None:
        if len(prior_individual_returns) != 2 or len(prior_index_returns) != 2:
            warnings.append("prior_individual_returns / prior_index_returns 需各含前2日数据，已忽略T2累计偏离约束")
        else:
            prior_ind_cum = sum(prior_individual_returns)
            prior_idx_cum = sum(prior_index_returns)
            prior_net_dev = prior_ind_cum - prior_idx_cum          # 前2日已积累净偏离
            # |prior_net_dev + r3 - index_today| < cum_dev_threshold
            lo = -cum_dev_threshold - prior_net_dev + index_today_return
            hi = cum_dev_threshold - prior_net_dev + index_today_return
            cum_constraint = _clamp_range(lo, hi)
            if cum_constraint is None:
                warnings.append("基于前2日数据，3日累计偏离约束无可行区间（当前基线已逼近阈值）")
    else:
        warnings.append("未提供前2日数据，T2(连续3日累计偏离)约束已降级跳过；安全区间仅由T1/T3决定")
    constraints["cum_3day_deviation"] = cum_constraint

    # ---------- 交集：综合允许涨跌幅区间 ----------
    allowed = _intersect([v for v in constraints.values()])
    if allowed is None:
        allowed_change_range = None
        allowed_price_range = None
        binding = ["<无解：任一硬约束已突破，任何价格均触发异动>"]
    else:
        lo, hi = allowed
        allowed_change_range = (round(lo, 6), round(hi, 6))
        allowed_price_range = (
            round(yesterday_close * (1 + lo), 4),
            round(yesterday_close * (1 + hi), 4),
        )
        # 找最紧边界（区间宽度最小者）
        binding = [
            name for name, rng in constraints.items()
            if rng is not None and abs(rng[1] - rng[0]) <= (hi - lo) + 1e-9
        ]

    # ---------- T4 换手率约束（非价格，独立判定） ----------
    turnover_check: Optional[Dict[str, Any]] = None
    if today_turnover is not None:
        turnover_check = {
            "today_turnover": today_turnover,
            "threshold": turnover_threshold,
            "ok": today_turnover < turnover_threshold,
            "note": "低于阈值安全；达到/超过即记为换手率异动",
        }
    else:
        warnings.append("未提供今日换手率，T4(日换手率)约束已降级跳过")

    # ---------- 若传入 today_close，做逐项触发判定 ----------
    evaluation: Optional[Dict[str, Any]] = None
    if today_close is not None:
        today_close = float(today_close)
        r3 = (today_close - yesterday_close) / yesterday_close
        breaches = []
        # T3
        if abs(r3) >= daily_limit - 1e-12:
            breaches.append(f"日涨跌停约束(±{daily_limit*100:.0f}%): 实际 {r3*100:+.2f}%")
        # T1
        dev1 = r3 - index_today_return
        if abs(dev1) >= daily_dev_threshold - 1e-12:
            breaches.append(f"日偏离±{daily_dev_threshold*100:.0f}%: 实际 {dev1*100:+.2f}%")
        # T2
        if cum_constraint is not None:
            dev2 = (sum(prior_individual_returns) + r3) - (sum(prior_index_returns) + index_today_return)
            if abs(dev2) >= cum_dev_threshold - 1e-12:
                breaches.append(f"3日累计偏离±{cum_dev_threshold*100:.0f}%: 实际 {dev2*100:+.2f}%")
        # T4
        if turnover_check is not None and not turnover_check["ok"]:
            breaches.append(f"日换手率≥{turnover_threshold*100:.0f}%: 实际 {today_turnover*100:.2f}%")
        evaluation = {
            "today_close": today_close,
            "today_change_pct": round(r3 * 100, 4),
            "triggered": len(breaches) > 0,
            "breached_rules": breaches,
            "within_safe_range": (allowed is not None and lo <= r3 <= hi),
        }

    return {
        "threshold_params": {
            "daily_dev_threshold": daily_dev_threshold,
            "cum_dev_threshold": cum_dev_threshold,
            "daily_limit": daily_limit,
            "turnover_threshold": turnover_threshold,
        },
        "yesterday_close": yesterday_close,
        "index_today_return": index_today_return,
        "daily_change_constraints": {k: (round(v[0], 6), round(v[1], 6)) if v else None
                                     for k, v in constraints.items()},
        "allowed_change_range": allowed_change_range,
        "allowed_price_range": allowed_price_range,
        "binding_constraints": binding,
        "turnover_check": turnover_check,
        "evaluation": evaluation,
        "warnings": warnings,
    }


# ============================ 自验证 ============================
if __name__ == "__main__":
    def show(title, res):
        print(f"\n==== {title} ====")
        print(f"  昨日收盘: {res['yesterday_close']}  指数今日涨跌幅: {res['index_today_return']*100:+.2f}%")
        print(f"  各约束涨跌幅区间: {res['daily_change_constraints']}")
        print(f"  允许涨跌幅区间: {res['allowed_change_range']}")
        print(f"  允许价格区间  : {res['allowed_price_range']}")
        print(f"  最紧边界约束  : {res['binding_constraints']}")
        if res['turnover_check']:
            print(f"  换手率判定    : {res['turnover_check']}")
        if res['evaluation']:
            e = res['evaluation']
            print(f"  [评估] 今日收盘={e['today_close']} 涨跌={e['today_change_pct']:+.2f}% "
                  f"触发={e['triggered']} 安全区={e['within_safe_range']}")
            if e['breached_rules']:
                for b in e['breached_rules']:
                    print(f"        ✗ {b}")
        if res['warnings']:
            print(f"  ⚠ 警告: {res['warnings']}")

    # —— 场景A：哈药真实基线（基于之前分析的真实数据）——
    # 昨日收盘 9.06；前2日个股 +1.22%/-0.66% 累计 +0.56%；指数 +0.19%/-2.40% 累计 -2.21%
    # 今日指数近似 +0.28%（盘中）；今日换手假设 11.8%（不触发T4）
    resA = compute_safe_range(
        yesterday_close=9.06,
        today_close=9.50,                      # 假设今日收 9.50 (+4.86%)
        prior_individual_returns=[0.0122, -0.0066],
        prior_index_returns=[0.0019, -0.0240],
        index_today_return=0.0028,
        today_turnover=0.118,
    )
    show("场景A 哈药真实基线 + 假设收9.50", resA)

    # —— 场景B：今日涨停 9.97 (+10%)，应触发 T1 日偏离 ——
    resB = compute_safe_range(
        yesterday_close=9.06, today_close=9.97,
        prior_individual_returns=[0.0122, -0.0066],
        prior_index_returns=[0.0019, -0.0240],
        index_today_return=0.0028, today_turnover=0.118,
    )
    show("场景B 今日涨停9.97(应触发T1)", resB)

    # —— 场景C：不提供前2日数据（降级，仅T1/T3）——
    resC = compute_safe_range(yesterday_close=9.06, today_close=9.50,
                              index_today_return=0.0028, today_turnover=0.118)
    show("场景C 缺前2日数据(降级跳过T2)", resC)

    # —— 场景D：边界——昨日收盘缺失/非法 ——
    try:
        compute_safe_range(yesterday_close=-5)
    except ValueError as ex:
        print(f"\n==== 场景D 边界校验 ====\n  ✓ 正确抛出: {ex}")

    # —— 场景E：无解情形（前2日已逼近阈值，今日任何价都触发）——
    # 构造：前2日个股 +15%/+15% 指数 0/0 → 净偏离 +30% → T2 已无可行区间
    resE = compute_safe_range(
        yesterday_close=9.06, today_close=9.06,
        prior_individual_returns=[0.15, 0.15],
        prior_index_returns=[0.0, 0.0],
        index_today_return=0.0,
    )
    show("场景E 基线已破(T2无解)", resE)
