# TASK_BOARD（高级项目经理）

| 任务ID | 负责文件名 | 输入 | 输出 | DoD | 依赖 |
|--------|------------|------|------|-----|------|
| TB-ORCH-01 | agents-orchestrator.md | OPTIMIZED_BRIEF；板块集合；6 个月 horizon | 派发与交接计划 | 覆盖数据/资讯/研究/质检/终稿 | — |
| TB-DATA-01 | engineering-data-engineer.md | TB-ORCH-01 | cn-fund 事实包 | 数字可复核 | TB-ORCH-01 |
| TB-NEWS-01 | marketing-daily-news-briefing.md | TB-ORCH-01 | NEWS01 结构化资讯 | 无虚构链接 | TB-ORCH-01 |
| TB-RES-01 | finance-investment-researcher.md | DATA + NEWS | RES01 研究论证稿 | 双面论证、禁稳赚 | DATA、NEWS |
| TB-QC-01 | testing-reality-checker.md | RES + DATA + NEWS | QC01 质检修订包 | 矛盾闭环 | TB-RES-01 |
| TB-ORCH-02 | agents-orchestrator.md | 上游全集 | FINAL + 交接摘要 | 免责与映射完整 | TB-QC-01 |

TB-DATA-01 ∥ TB-NEWS-01 并行。
