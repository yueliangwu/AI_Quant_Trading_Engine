# 自动化导出：ST股摘星摘帽进度每日收集推送

> 本文件由 `D:\AI_Quant_Trading_Engine\.workbuddy\memory` 工作流沉淀导出。
> **用途**：换电脑克隆仓库后，照此文件在 WorkBuddy 中一键重建「每日 09:00 自动收集 17 只 ST 进度并飞书推送」的自动化。
> 注意：WorkBuddy 的自动化运行时配置存于用户级 `~/.workbuddy/workbuddy.db`，**不在项目内**，无法随 git 迁移，故需本文件重建。

## 自动化参数（在 WorkBuddy 自动化面板创建）

| 字段 | 值 |
|---|---|
| 自动化 ID | `automation-1787294825559`（原机，仅供对照） |
| 名称 | `ST股摘星摘帽进度每日收集推送` |
| 类型 | recurring（周期性） |
| 调度规则 (rrule) | `FREQ=DAILY;BYHOUR=9;BYMINUTE=0`（每日 09:00，开盘前） |
| 状态 | ACTIVE |
| 工作目录 (cwds) | 仓库根目录，如 `D:\AI_Quant_Trading_Engine` |
| 连接器 (connectorIds) | feishu（用于 `lark-cli` 推送） |
| Expert | 无 |

## 提示词（Prompt，原样粘贴）

```
运行 ST/*ST 摘星摘帽进度每日收集程序并向飞书推送老板(固定每日09:00开盘前)：

1. 刷新进度库(最关键一步)：用 WebSearch 逐一检索以下17只股票的最新摘星/摘帽/重整进展公告，对 progress_db.json 中 updated 距今日>3天、或当日行情异动(涨停/跌停/量比>3)的标的优先复核，把最新 stage / last_event / catalyst_window / risks / updated(今日日期) 写回 <仓库>/scripts/st_monitor/progress_db.json。17只代码：600079 002726 000711 000838 600337 002168 600381 300147 002542 300027 300020 600340 600370 600165 600525 603843 603377

2. 执行程序：用受管 python 运行 <仓库>/scripts/st_monitor/st_progress_collector.py 。程序自动判断交易日(周末/法定节假日跳过)、采集腾讯行情快照+东财主力资金流、读取进度库、生成 HTML 报告并自动经 lark-cli(bot)推送给老板 open_id(ou_10cdef8ea8a202ab450597b1501eb8dd)。

3. 通道验证：正式运行前可先 `python st_progress_collector.py --test-send` 发一条自测消息确认 lark-cli 通道；运行后检查 <仓库>/scripts/st_monitor/logs/st_collector_send_log.jsonl 确认 send_ok=true。若推送失败用 `lark-cli --version` 确认 CLI 可用，重试一次。

4. 回报：本次运行日期、监控标的数、各标的判定(利好/利空/需关注/中性)、飞书发送结果、进度库今日刷新了几只。

注意：沙箱内公告接口(东财/巨潮/腾讯)全部失效，真实文本进度只能靠第1步 WebSearch 刷新进度库；这是程序自动生成的事件监控，非投资建议，ST/*ST退市风险极高。
```

## 重建步骤（新电脑）

1. 安装并登录 WorkBuddy，确保飞书连接器(lark-cli)已连接、bot 可私信老板 open_id。
2. 克隆本仓库：`git clone https://github.com/yueliangwu/AI_Quant_Trading_Engine.git`
3. 在 WorkBuddy 自动化面板新建自动化，填上方「名称/类型/rrule/cwds/connectorIds」并粘贴 Prompt（把 `<仓库>` 替换为实际克隆路径）。
4. 用受管 python 建 venv：`...\python\versions\3.13.12\python.exe -m venv ...\python\envs\default`（程序仅用标准库，可不装额外包）。
5. 手动跑一次验证：`python scripts/st_monitor/st_progress_collector.py --test-send`，确认飞书收到自测消息。
6. 设为 ACTIVE，次日 09:00 自动首跑。

## 关键路径（原机 vs 仓库）

| 用途 | 原机路径 | 仓库路径 |
|---|---|---|
| 主程序 | `C:\Users\EDY\AppData\Local\Temp\wb_analysis\st_progress_collector.py` | `scripts/st_monitor/st_progress_collector.py` |
| 进度库 | `...\wb_analysis\progress_db.json` | `scripts/st_monitor/progress_db.json` |
| 发送日志 | `...\wb_analysis\logs\st_collector_send_log.jsonl` | `scripts/st_monitor/logs\st_collector_send_log.jsonl` |

> 原机自动化仍跑 Temp 副本；仓库副本供迁移/版本管理。若想让原机也改用仓库副本，把自动化 Prompt 第2步路径改为仓库路径即可（两副本内容一致）。
