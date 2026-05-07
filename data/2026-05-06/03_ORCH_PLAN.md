# ORCH_PLAN（智能体编排者 TB-ORCH-01）

- **Run ID**：`RUN-FUND-SECTOR-20260506`
- **顺序**：ORCH-01 → DATA ∥ NEWS → RES → QC → ORCH-02（终稿）
- **并行**：TB-DATA-01 ∥ TB-NEWS-01
- **产物路径约定（本项目采用）**：`data/2026-05-06/` 下顺序编号 `.md` / `meta.json`；原始 `cn-fund` 控制台输出见 `04_DATA01_fund_metrics.md`
- **质量门禁**：研究结论无法回溯 DATA/NEWS → 退回 RES；合规措辞问题 → 退回 RES；同一循环建议 ≤3 轮
- **宿主 Shell**：仓库根目录执行 `cn-fund report <代码>`（见 `meta.json`）
