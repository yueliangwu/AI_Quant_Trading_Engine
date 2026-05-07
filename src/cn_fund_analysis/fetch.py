from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, TypeVar

import pandas as pd

T = TypeVar("T")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cache_dir() -> Path:
    d = project_root() / "data" / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _with_optional_cache(
    name: str,
    loader: Callable[[], pd.DataFrame],
    *,
    max_age_hours: float = 6.0,
) -> pd.DataFrame:
    path = cache_dir() / f"{name}.pkl"
    import time

    if path.exists():
        age_h = (time.time() - path.stat().st_mtime) / 3600.0
        if age_h < max_age_hours:
            return pd.read_pickle(path)
    df = loader()
    try:
        df.to_pickle(path)
    except Exception:
        pass
    return df


@functools.lru_cache(maxsize=1)
def load_all_fund_names() -> pd.DataFrame:
    import akshare as ak

    def _load() -> pd.DataFrame:
        return ak.fund_name_em()

    return _with_optional_cache("fund_name_em", _load, max_age_hours=12.0)


def search_funds(keyword: str, *, limit: int = 30) -> pd.DataFrame:
    kw = keyword.strip().lower()
    if not kw:
        return pd.DataFrame()
    df = load_all_fund_names()
    if df.empty:
        return df
    mask = (
        df.astype(str)
        .apply(lambda s: s.str.lower().str.contains(kw, na=False))
        .any(axis=1)
    )
    out = df.loc[mask].head(limit).copy()
    return out


def fetch_open_fund_nav(symbol: str) -> pd.DataFrame:
    """场外开放式基金：单位净值走势（东方财富）。"""
    import akshare as ak

    code = symbol.strip()
    df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
    if df is None or df.empty:
        return pd.DataFrame()
    return df


def fetch_fund_basic_ths(symbol: str) -> pd.DataFrame:
    """同花顺基金概况（字段较全，可选）。"""
    import akshare as ak

    return ak.fund_info_ths(symbol=symbol.strip())


def fetch_etf_daily(symbol: str, start_date: str = "20100101") -> pd.DataFrame:
    """场内 ETF 日线（东财），symbol 为 6 位交易代码。"""
    import akshare as ak
    from datetime import datetime

    end = datetime.now().strftime("%Y%m%d")
    return ak.fund_etf_hist_em(
        symbol=symbol.strip(),
        period="daily",
        start_date=start_date,
        end_date=end,
        adjust="",
    )
