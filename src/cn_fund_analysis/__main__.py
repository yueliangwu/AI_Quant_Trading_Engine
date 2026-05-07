from __future__ import annotations

import sys
import time
from pathlib import Path

import typer

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from cn_fund_analysis import fetch, metrics
from cn_fund_analysis.persist_workbook import (
    append_fund_metrics_sheet,
    load_auto_mapping,
    load_rows_from_json,
    row_from_compute_metrics,
)

app = typer.Typer(no_args_is_help=True, help="国内基金数据分析 CLI（数据来自 AKShare / 东方财富等）")


@app.command()
def search(q: str = typer.Argument(..., help="基金代码或名称关键字"), limit: int = 25):
    """按关键字筛选基金列表（本地缓存基金名录）。"""
    df = fetch.search_funds(q, limit=limit)
    if df.empty:
        typer.echo("未匹配到基金（或名录加载失败）。")
        raise typer.Exit(1)
    typer.echo(df.to_string(index=False))


@app.command("nav")
def cmd_nav(
    symbol: str = typer.Argument(..., help="场外基金代码，如 161725"),
    json_out: bool = typer.Option(False, "--json", help="输出 JSON"),
):
    """拉取场外开放式基金单位净值走势并打印尾部。"""
    raw = fetch.fetch_open_fund_nav(symbol)
    if raw.empty:
        typer.echo(f"未获取到净值数据: {symbol}")
        raise typer.Exit(1)
    nav = metrics.normalize_nav_frame(raw)
    if json_out:
        typer.echo(nav.tail(60).to_json(orient="records", force_ascii=False, date_format="iso"))
    else:
        typer.echo(nav.tail(15).to_string(index=False))


@app.command("etf")
def cmd_etf(
    symbol: str = typer.Argument(..., help="场内 ETF 代码，如 510300"),
    json_out: bool = typer.Option(False, "--json"),
):
    """场内 ETF 日线行情（开高低收量额）。"""
    df = fetch.fetch_etf_daily(symbol)
    if df is None or df.empty:
        typer.echo(f"未获取到 ETF 数据: {symbol}")
        raise typer.Exit(1)
    if json_out:
        typer.echo(df.tail(40).to_json(orient="records", force_ascii=False))
    else:
        typer.echo(df.tail(12).to_string(index=False))


@app.command("report")
def cmd_report(
    symbol: str = typer.Argument(..., help="场外基金代码"),
    basic: bool = typer.Option(False, "--basic", help="附带同花顺基金概况"),
):
    """净值序列 + 区间收益 / 年化 / 波动 / 最大回撤。"""
    raw = fetch.fetch_open_fund_nav(symbol)
    if raw.empty:
        typer.echo(f"未获取到净值: {symbol}")
        raise typer.Exit(1)
    nav = metrics.normalize_nav_frame(raw)
    m = metrics.compute_metrics(nav)
    typer.echo(f"\n基金 {symbol}\n")
    typer.echo(metrics.format_metrics(m))
    if basic:
        typer.echo("\n【概况 - 同花顺】")
        try:
            info = fetch.fetch_fund_basic_ths(symbol)
            typer.echo(info.to_string(index=False))
        except Exception as e:  # noqa: BLE001
            typer.echo(f"(概况获取失败: {e})", err=True)


@app.command("export-nav")
def cmd_export_nav(
    symbol: str = typer.Argument(...),
    out: str = typer.Option("data/export_nav.csv", "--out", "-o"),
):
    """导出规范化净值 CSV 到 data/。"""
    raw = fetch.fetch_open_fund_nav(symbol)
    nav = metrics.normalize_nav_frame(raw)
    if nav.empty:
        typer.echo("无数据可导出")
        raise typer.Exit(1)
    path = Path(out)
    if not path.is_absolute():
        path = fetch.project_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    nav.to_csv(path, index=False)
    typer.echo(str(path))


@app.command("persist-run")
def cmd_persist_run(
    run_date: str = typer.Option(..., "--date", "-d", help="运行日目录 YYYY-MM-DD（将创建 data/<date>/）"),
    json_path: Path = typer.Option(..., "--json", "-j", help="含 rows/funds 与 fund_nav_as_of 的 JSON"),
):
    """将基金指标表追加写入 data/<date>/fund_metrics_runs.xlsx 的新 Sheet（同日多次即多 Sheet）。"""
    root = fetch.project_root()
    jp = json_path if json_path.is_absolute() else root / json_path
    if not jp.is_file():
        typer.echo(f"找不到 JSON: {jp}", err=True)
        raise typer.Exit(1)
    rows, as_of, topic = load_rows_from_json(jp)
    path, sheet = append_fund_metrics_sheet(
        root,
        run_date,
        rows,
        fund_nav_as_of=as_of,
        topic=topic,
    )
    typer.echo(f"已写入: {path}  →  sheet [{sheet}]")


@app.command("persist-auto")
def cmd_persist_auto(
    run_date: str = typer.Option(..., "--date", "-d", help="运行日目录 YYYY-MM-DD"),
    mapping: Path = typer.Option(..., "--mapping", "-m", help="JSON：topic + funds[{code,板块,简称}]"),
    throttle_sec: float = typer.Option(
        0.25,
        "--throttle",
        help="两次拉取净值之间的间隔（秒），降低接口频率",
    ),
):
    """按映射批量拉取场外基金净值指标，追加写入 fund_metrics_runs.xlsx（新 Sheet）。"""
    root = fetch.project_root()
    mp = mapping if mapping.is_absolute() else root / mapping
    if not mp.is_file():
        typer.echo(f"找不到 mapping: {mp}", err=True)
        raise typer.Exit(1)
    specs, topic = load_auto_mapping(mp)
    rows_out: list[dict] = []
    as_of = ""
    for i, spec in enumerate(specs):
        if i > 0 and throttle_sec > 0:
            time.sleep(throttle_sec)
        code = spec["code"]
        display_name = spec["简称"].strip()
        if not display_name:
            try:
                df = fetch.load_all_fund_names()
                hit = df[df["基金代码"].astype(str).str.strip() == code]
                if not hit.empty:
                    display_name = str(hit.iloc[0]["基金简称"])
            except Exception:
                display_name = code
        if not display_name:
            display_name = code
        raw = fetch.fetch_open_fund_nav(code)
        nav = metrics.normalize_nav_frame(raw)
        m = metrics.compute_metrics(nav)
        if not m:
            typer.echo(f"[跳过] {code} 无有效净值序列", err=True)
            continue
        rows_out.append(
            row_from_compute_metrics(
                m,
                sector=spec["板块"],
                code=code,
                name=display_name,
            )
        )
        cs = str(m.get("样本截止") or "")
        if cs:
            as_of = cs
    if not rows_out:
        typer.echo("没有可写入的行", err=True)
        raise typer.Exit(1)
    path, sheet = append_fund_metrics_sheet(
        root,
        run_date,
        rows_out,
        fund_nav_as_of=as_of or "unknown",
        topic=topic,
    )
    typer.echo(f"已写入: {path}  →  sheet [{sheet}]  行数={len(rows_out)}  as_of={as_of or 'unknown'}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
