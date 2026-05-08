# 智能体与 Skill 策略（按仓库约束）

## 智能体（Agents）

- **来源**：优先使用本地克隆的 **[agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)**；本仓库已在 `.cursor/agents/` 放入该库的 **原文拷贝**（非手写）。
- **当前记录的上游提交**：见仓库根目录 `AGENCY_AGENTS_REVISION.txt`（更新请执行 `scripts/sync-agency-agents.ps1`，会从 `third_party/agency-agents-zh` 拉取并覆盖拷贝）。
- **全链路工作流**：`workflows/agency-operating-model.md`（提示词 → PM → 编排者 → 基金域）。
- **基金域子流程**：`workflows/fund-advisory-pipeline.md`。

### 本项目选用的官方角色文件（8 个）

| 文件 | 上游路径 | 用途 |
|------|----------|------|
| `prompt-engineer.md` | `specialized/prompt-engineer.md` | **提示词工程师**：把用户输入改写为可执行「优化后指令」 |
| `project-manager-senior.md` | `project-management/project-manager-senior.md` | **高级项目经理**：拆任务、指派智能体、控范围 |
| `agents-orchestrator.md` | `specialized/agents-orchestrator.md` | **智能体编排者**：协调交接与质量循环、合成终稿 |
| `engineering-data-engineer.md` | `engineering/engineering-data-engineer.md` | 数据管线 / `cn-fund` 事实层 |
| `marketing-daily-news-briefing.md` | `marketing/marketing-daily-news-briefing.md` | 要闻简报 |
| `finance-investment-researcher.md` | `finance/finance-investment-researcher.md` | 投资研究（双面论证） |
| `testing-reality-checker.md` | `testing/testing-reality-checker.md` | 现实检验 / 质检 |
| `legal-compliance-checker.md` | `support/support-legal-compliance-checker.md` | **法务合规员**：面向公开分发的终稿用语、非投顾与宣传边界审查（可选门禁） |

### 输入网关（Cursor Rule）

默认对所有相关对话先产出「优化后指令」，详见 `.cursor/rules/user-input-prompt-gate.mdc`；用户以「**免优化**」开头可跳过。

### 若本机未克隆 agency-agents-zh

在仓库根目录执行：

```powershell
.\scripts\sync-agency-agents.ps1
```

脚本会把上游克隆到 `third_party/agency-agents-zh/`（默认 gitignore，仅本地使用）。若你已在其他磁盘克隆过 **agency-agents-zh**，也可手动将下列上游路径的文件 **原样覆盖**到 `.cursor/agents/`（勿改正文）：

- `specialized/prompt-engineer.md` → `prompt-engineer.md`
- `project-management/project-manager-senior.md` → `project-manager-senior.md`
- `specialized/agents-orchestrator.md` → `agents-orchestrator.md`
- `engineering/engineering-data-engineer.md`
- `marketing/marketing-daily-news-briefing.md`
- `finance/finance-investment-researcher.md`
- `testing/testing-reality-checker.md`

### agency-agents-zh 能力边界说明

上游库**没有**名为「公募基金专员」或「组合决策机器人」的单独 `.md`；“基金决策”在本项目中仅能落地为 **研究性排序、情景与风险框架**，投顾式结论须拒绝；执行侧仍为 **数据工程师 + 投资研究员 + 现实检验者**，若产出将对外发布或易被理解为投资建议，可加 **法务合规员** 做用语闸门。

---

## Skill（本仓库不托管、不自写）

按你的要求：**不在本仓库编写任何 `SKILL.md`**；Skill 须从**公开渠道**自行检索与安装（如 Cursor 技能目录、各厂商文档等）。

### 当前缺口说明（诚实列举）

| 需求 | 状态 |
|------|------|
| **「基金净值 / 公募数据抓取」专用 Cursor Skill** | 公开生态中**无**与本仓库 `cn-fund` 一一绑定的「官方唯一」Skill；量化层由 **Python 代码 + AKShare** 完成，不依赖项目内 Skill。 |
| **「新闻检索」专用 Skill** | 非必需；可用 Cursor **内置联网**或你本机已装的检索类 Skill（若有）。**本仓库不声明、不捆绑**具体 Skill 名称。 |
| **合规/质检类 Skill** | 非必需；质检由 `testing-reality-checker` + 编排者终稿约束完成。 |

**结论**：项目**没有**也**不会**内置自写 Skill；**未发现**必须安装的单一公开 Skill 才能完成流水线。

---

## 能力边界

- 不代下单；不索取账户信息。
- 「推荐」仅为研究性框架下的排序与情景讨论，须保留免责声明。

## 项目治理

- 范围、风险与 backlog 见 **`docs/PM_REVIEW.md`**（项目经理审查，随迭代更新）。
