# cn-fund-analysis

国内公募基金 / 场内 ETF 的**离线分析脚手架**：用 [AKShare](https://github.com/akfamily/akshare) 拉取东方财富、同花顺等公开数据，在本地计算区间收益、年化、波动与最大回撤。

> 仅供研究与学习，不构成投资建议。数据延迟与字段变更以数据源为准。

## 环境

- Python 3.10+
- 推荐使用 [uv](https://github.com/astral-sh/uv)：`uv sync` 或 `uv pip install -e .`

```bash
cd AI_Quant_Trading_Engine
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## CLI

```bash
cn-fund search 沪深300
cn-fund nav 110022
cn-fund report 110022 --basic
cn-fund etf 510300
cn-fund export-nav 161725 -o data/my_nav.csv

# 将指标宽表追加写入 data/<运行日>/fund_metrics_runs.xlsx（同日多次 = 多 Sheet：Run_001…）
cn-fund persist-run --date 2026-05-06 --json data/2026-05-06/run_table_seed.json

# 按映射自动拉取净值并写入（免手工填百分比）；mapping 见 data/templates/persist_mapping.example.json
cn-fund persist-auto --date 2026-05-06 --mapping data/templates/persist_mapping.example.json
```

项目经理审查与 backlog：`docs/PM_REVIEW.md`。

也可用：`python -m cn_fund_analysis search 沪深300`

## 项目结构

| 路径 | 说明 |
|------|------|
| `src/cn_fund_analysis/fetch.py` | 基金名录缓存、净值、ETF、概况 |
| `src/cn_fund_analysis/metrics.py` | 净值序列规范化与风险收益指标 |
| `src/cn_fund_analysis/__main__.py` | Typer CLI |
| `data/cache/` | 基金名录缓存（自动生成，默认已 gitignore） |
| `data/YYYY-MM-DD/` | 某次多智能体跑批的落盘结果（按**运行日**建子目录） |

## 借鉴来源

- 与本机 **a-stock-analysis** skill 类似：优先使用东方财富体系公开接口，批量请求时注意频率。
- 字段与接口名以 [AKShare 公募基金文档](https://akshare.akfamily.xyz/data/fund/fund_public.html) 为准。

多 Agent：**全链路**见 `workflows/agency-operating-model.md`（提示词工程师 → 高级项目经理 → 智能体编排者 → 基金域）；基金域子流程见 `workflows/fund-advisory-pipeline.md`。角色均来自 **[agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)** 原文拷贝（`.cursor/agents/`）。同步：`scripts/sync-agency-agents.ps1`。默认输入先经提示词优化：`.cursor/rules/user-input-prompt-gate.mdc`（可用「免优化」跳过）。  
若要让 **多个 Agent 各自独立产出**（而非单对话扮演），见 `workflows/how-to-invoke-real-agents.md`。
