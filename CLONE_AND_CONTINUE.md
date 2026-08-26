# 换电脑续用指南（Clone & Continue）

本仓库已包含：全部源码、配置文件、`.workbuddy` 使用历史（记忆+自动化日志）、`data/` 工作数据、本次会话的 ST 分析产出（`analysis_outputs/`）。

## 一、克隆

```bash
git clone https://github.com/yueliangwu/AI_Quant_Trading_Engine.git
cd AI_Quant_Trading_Engine
```

## 二、恢复使用历史（已随仓库，无需额外操作）

- `.workbuddy/memory/`：每日工作日志与长期笔记，WorkBuddy 打开项目即自动加载 → **操作日志/使用历史已保留**。
- `.workbuddy/automations/`：自动化运行笔记（非运行时配置）。
- git 提交历史：`git log` 可见全部本地提交。

> ⚠️ WorkBuddy 自动化（如每日 ST 进度推送）的**运行时调度**存于用户级 `~/.workbuddy/workbuddy.db`，不随 git 迁移。需按 `automations/st_monitor_automation.md` 在新机重建（见第三节）。

## 三、重建每日 ST 进度推送自动化

1. 安装并登录 WorkBuddy，连接飞书连接器（lark-cli），确保 bot 可私信你的 open_id。
2. 打开 `automations/st_monitor_automation.md`，按表新建自动化（名称/类型 `recurring`/rrule `FREQ=DAILY;BYHOUR=9;BYMINUTE=0`/cwds=仓库根/connectorIds=feishu），粘贴 Prompt（把 `<仓库>` 替换为实际克隆路径）。
3. 验证：`python scripts/st_monitor/st_progress_collector.py --test-send` → 飞书收到自测消息即通。
4. 设为 ACTIVE，次日 09:00 自动首跑。

## 四、运行环境

- Python：建议用受管运行时 `...\python\versions\3.13.12\python.exe`（程序仅用标准库，无需 pip 安装）。
- 数据源：腾讯行情快照（`qt.gtimg.cn`）+ 东方财富资金流（`push2.eastmoney.com`），沙箱内可用；公告文本进度由自动化每日 WebSearch 刷新 `scripts/st_monitor/progress_db.json`。
- 若沙箱网络下资金流偶发断连，程序会自动降级（主力列显示 `—`），不影响报告与推送。

## 五、日常同步（本机或新机通用）

```bash
python scripts/sync_to_github.py            # 自动 commit(日期) + push
# 或 Windows 双击：
scripts\sync_to_github.bat
```

## 六、目录速查

| 路径 | 内容 |
|---|---|
| `scripts/st_monitor/` | ST 进度收集主程序 + 进度库（可迁移运行副本） |
| `analysis_outputs/2026-08-25/` | 本次会话全部 ST 分析源码与报告（含并购重组跨界分析） |
| `automations/` | 自动化导出配置（换机重建用） |
| `.workbuddy/memory/` | 使用历史（每日日志 + 长期笔记） |
| `data/` | 各日期工作数据（历史保留） |
| `src/ scripts/ workflows/` | 原有量化脚手架源码 |

> ⚠️ 免责：仓库内容为个人投研事件监控与量价分析工具，所有输出非投资建议。ST/*ST 退市风险极高，据此交易风险自担。
