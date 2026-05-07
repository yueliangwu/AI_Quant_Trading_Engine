from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def _pick_date_col(df: pd.DataFrame) -> str | None:
    for c in ("净值日期", "日期", "date", "DAY"):
        if c in df.columns:
            return c
    return None


def _pick_nav_col(df: pd.DataFrame) -> str | None:
    for c in ("单位净值", "净值", "close", "收盘"):
        if c in df.columns:
            return c
    return None


def normalize_nav_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    dc = _pick_date_col(df)
    nc = _pick_nav_col(df)
    if not dc or not nc:
        raise ValueError(f"无法识别日期/净值列，当前列: {list(df.columns)}")
    out = df[[dc, nc]].copy()
    out.columns = ["date", "nav"]
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["nav"] = pd.to_numeric(out["nav"], errors="coerce")
    out = out.dropna().sort_values("date").reset_index(drop=True)
    return out


def compute_metrics(nav: pd.DataFrame) -> dict[str, float | str]:
    """基于日净值序列计算区间收益、年化、波动、最大回撤。"""
    if nav.empty or len(nav) < 2:
        return {}
    r = nav["nav"].pct_change().dropna()
    last_dt = nav["date"].iloc[-1]
    start_dt = nav["date"].iloc[0]

    def _window(days: int) -> tuple[pd.Timestamp | None, slice]:
        end = nav["date"].iloc[-1]
        start = end - pd.Timedelta(days=days)
        idx = nav["date"] >= start
        return start, idx

    def _total_return(sub: pd.DataFrame) -> float | None:
        if len(sub) < 2:
            return None
        a, b = float(sub["nav"].iloc[0]), float(sub["nav"].iloc[-1])
        if a <= 0:
            return None
        return b / a - 1.0

    def _ann_return(sub: pd.DataFrame) -> float | None:
        tr = _total_return(sub)
        if tr is None:
            return None
        days = (sub["date"].iloc[-1] - sub["date"].iloc[0]).days
        if days < 30:
            return None
        years = days / 365.25
        return (1.0 + tr) ** (1.0 / years) - 1.0 if years > 0 else None

    windows = {
        "ret_1m": 31,
        "ret_3m": 93,
        "ret_6m": 186,
        "ret_1y": 372,
    }
    metrics: dict[str, float | str] = {
        "样本起始": start_dt.strftime("%Y-%m-%d"),
        "样本截止": last_dt.strftime("%Y-%m-%d"),
        "样本天数": int((last_dt - start_dt).days),
    }

    for key, days in windows.items():
        _, sl = _window(days)
        sub = nav.loc[sl]
        tr = _total_return(sub)
        metrics[key] = float(tr) if tr is not None else float("nan")

    ytd_start = pd.Timestamp(year=int(last_dt.year), month=1, day=1)
    sub_ytd = nav.loc[nav["date"] >= ytd_start]
    tr_ytd = _total_return(sub_ytd)
    metrics["ret_ytd"] = float(tr_ytd) if tr_ytd is not None else float("nan")

    full_tr = _total_return(nav)
    metrics["成立以来累计收益"] = float(full_tr) if full_tr is not None else float("nan")
    ann = _ann_return(nav)
    metrics["成立以来年化收益"] = float(ann) if ann is not None else float("nan")

    if len(r) > 5:
        metrics["日收益年化波动率"] = float(r.std() * np.sqrt(252))
    else:
        metrics["日收益年化波动率"] = float("nan")

    cummax = nav["nav"].cummax()
    dd = nav["nav"] / cummax - 1.0
    metrics["历史最大回撤"] = float(dd.min()) if len(dd) else float("nan")

    return metrics


def format_metrics(m: dict[str, float | str]) -> str:
    lines: list[str] = []
    pct_keys = {
        "ret_1m",
        "ret_3m",
        "ret_6m",
        "ret_1y",
        "ret_ytd",
        "成立以来累计收益",
        "成立以来年化收益",
        "历史最大回撤",
        "日收益年化波动率",
    }
    for k, v in m.items():
        if k in pct_keys and isinstance(v, (float, int)) and np.isfinite(v):
            lines.append(f"  {k}: {v * 100:.2f}%")
        else:
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)
