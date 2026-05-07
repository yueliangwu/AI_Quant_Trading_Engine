# 如何「真正调用」多个 Agent（而非单人扮演）

单一对话里的模型可以**模仿**多个角色，但那**不是**多个独立 Agent。要满足「每个 Agent 自己的产出、再协同」，请用下面两种方式之一。

---

## 方式 A：Cursor 原生 Subagent（推荐）

本项目已将 agency-agents-zh 原文放在 `.cursor/agents/*.md`。在 Cursor 里需要**显式委派**，模型才会以该文件的 **system prompt** 单独跑一轮。

1. 打开 Chat / Agent 面板，找到 **Subagent / 自定义智能体**（名称与 `.md` 里 `name` 或文件名对应，以你当前 Cursor 版本为准）。
2. **一轮只选一个 Agent**，把上一棒的产出粘贴进输入框作为上下文。
3. 建议顺序（与 `agency-operating-model.md` 一致）：
   - **提示词工程师** → 产出 `OPTIMIZED_BRIEF`
   - **高级项目经理** → 产出 `TASK_BOARD`
   - **智能体编排者** → 根据 `TASK_BOARD` 调度后续子任务
   - **数据工程师 / 每日新闻简报 / 投资研究员 / 现实检验者** → 各产出各自段落或 JSON

4. 在对话里用明确委派句式（Cursor 文档示例）：

```text
请使用「提示词工程师」Subagent，读取 .cursor/agents/prompt-engineer.md，仅输出 OPTIMIZED_BRIEF。
```

若界面支持 **@Agent**，则 `@提示词工程师` 并附上用户原始需求。

> **你怎么看出是谁产的**：每一轮切换 Subagent 后，该轮回复即该 Agent 的独立产出；请复制保存到 `data/reports/` 以便编排者汇总。

---

## 方式 B：在本对话中用 Task 拉起隔离子代理（适合自动化演示）

父助手可通过 **Task 工具**多次调用 `generalPurpose` 子代理；每次子代理在**独立上下文**中运行，并在完成时返回一段可粘贴交接的文本。

约束：子代理**默认看不到**整条聊天历史，必须在 Prompt 里附上：**上游文件路径** + **上一棒完整产出**。

编排脚本思路：

1. Task #1：只读 `prompt-engineer.md`，输入用户原话 → 返回 `OPTIMIZED_BRIEF`
2. Task #2：只读 `project-manager-senior.md`，输入 Task #1 全文 → 返回 `TASK_BOARD`
3. **Task #3（关键，易被跳过）**：只读 `agents-orchestrator.md`，输入 `TASK_BOARD` + 用户主题 → 返回 **`ORCH_PLAN`**（执行顺序、并行边界、每步输入摘要模板、Run ID、质量循环/重试规则、下一步要派发的子任务列表）。**没有这一步，编排者在事实上就没「出场」。**
4. Task #4…：严格按 `ORCH_PLAN` 逐项委派（`engineering-data-engineer` / `marketing-daily-news-briefing` / …）

父助手**禁止**替子代理重写正文，只做复制交接与最终拼装。

### 为何你会觉得「智能体编排者」没起作用？

- `.cursor/agents/agents-orchestrator.md` **不会自动运行**；只有你 **委派了这一轮 Subagent / Task**，它才有独立产出。
- 若父助手在拿到 `TASK_BOARD` 后**直接**去跑数据/新闻/研究，等于父助手代行了编排逻辑——**编排者 Agent 仍然没有自己的 Run**，因此你看不见它的正文交付物。

---

## 父助手默认行为约定（避免再次「扮演」）

当你写：

```text
按 workflows/agency-operating-model.md，用真实多 Agent 执行；不要在一个回复里扮演全部角色。
```

父助手应：**只做编排**（发起 Subagent 或 Task），或 **逐步提示你去 UI 里点选下一个 Agent**；而不在同一气泡内生成全部角色的长文。

---

## 落盘交接物（推荐）

每次完整流水线在仓库 **`data/YYYY-MM-DD/`** 下建**当日目录**（运行日，非净值 `as_of`），例如 `data/2026-05-06/`：

| 文件 | 含义 |
|------|------|
| `meta.json` | 运行日、`fund_nav_as_of`、主题、所用命令列表 |
| `01_OPTIMIZED_BRIEF.md` … `09_ORCH02_handoff_trace.md` | 各 Agent 产物（编号可依项目约定增减） |
| **`fund_metrics_runs.xlsx`** | **必选**：基金指标宽表；内置 meta 区 + 数据表。**同一天多次运行**执行多次 `cn-fund persist-run`，每次 **新增 Sheet** `Run_001`、`Run_002`… |

净值若导出为 `.csv`，注意根目录 `.gitignore` 当前 **`*.csv` 全局忽略**；可改用 `.md` 表格落盘或调整 gitignore。
