# 项目经理审查（范围 / 风险 /  backlog）

## 结论摘要

项目在「数据管线 + 多 Agent 工作流约定 + 按日落盘」方向清晰，但 **工程化成熟度仍偏 MVP**：JSON/Excel 契约未版本化、`persist-run` 仍可手工拼表（也可用 `persist-auto`），且 **vendor 体量**（若误提交 `third_party`）会拖垮仓库。下列按优先级排列。

---

## P0 — 建议尽快处理

| 项 | 问题 | 建议 |
|----|------|------|
| **指标落盘闭环** | 手工维护 `run_table_seed.json` 易与真实 `cn-fund` 漂移 | ✅ 已增加 **`cn-fund persist-auto`**：按映射批量拉取净值并追加 Sheet |
| **契约说明** | `persist-run` 的 JSON 字段未集中文档化 | 见 `data/templates/persist_mapping.example.json` 与 README |
| **规则摩擦** | `user-input-prompt-gate.mdc` 为 `alwaysApply: true`，纯语法/调试类对话也被迫「优化后指令」 | 可改为 **按 glob 生效** 或约定 **`免优化`** 前缀已够用——团队需统一习惯 |

## P1 — 短期增强

| 项 | 建议 |
|----|------|
| **CI（可选）** | GitHub Actions：`ruff check`、`pip install -e .`（本项目**不包含**自动化测试套件） |
| **速率与稳定性** | `persist-auto` 批量时对东财接口 **sleep / 重试**（可配置），避免封 IP |
| **简称回填** | 映射里 `简称` 可选空：自动 `fund_name_em` 查表填充（✅ 已在 `persist-auto` 部分支持） |

## P2 — 中期能力

| 项 | 说明 |
|----|------|
| **场内 ETF 行** | 与场外净值字段对齐（需统一 `metrics` 或由 ETF 日线重算区间收益） |
| **重叠区间对比** | 多基金截取同一 `history_start` 再比夏普/回撤（研究可比性） |
| **配置化** | `pyproject.toml` 或 `config.toml` 统一默认 `run_date`、请求间隔 |

## P3 — 文档与协作

| 项 | 说明 |
|----|------|
| **LICENSE** | 开源协作前须补 |
| **ADR** | 为何选 agency-agents-zh 原文拷贝、为何 Excel 多 Sheet 等 |
| **数据目录** | `data/*` 是否入库：团队需约定（业绩文件可能较大） |

---

## 已落地的改进（摘录）

- `cn-fund persist-auto` + `data/templates/persist_mapping.example.json`
- 本审查文档

---

## 验收（项目经理）

- [ ] 新同事仅凭 README 能完成：`persist-auto` 一次跑通并打开 `fund_metrics_runs.xlsx`
- [ ] 多智能体工作流与数据目录约定无冲突（见 `agency-operating-model.md` §0）
