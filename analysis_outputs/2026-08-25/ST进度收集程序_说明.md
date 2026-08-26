# ST/*ST 摘星摘帽进度 每日自动收集与推送程序 · 说明文档

> 配套程序：`st_progress_collector.py`（仅依赖 Python 标准库）
> 进度缓存库：`progress_db.json`
> 发送日志：`logs/st_collector_send_log.jsonl`
> 每日报告：`st_progress_daily_YYYYMMDD.html`

---

## 一、任务调度配置

| 项 | 内容 |
|---|---|
| 触发方式 | WorkBuddy 自动化 `automation-1787294825559` |
| 调度规则 | `FREQ=DAILY;BYHOUR=9;BYMINUTE=0`（每日 **09:00**，Asia/Shanghai，开盘前推送） |
| 当前状态 | ACTIVE，`nextRunAt` 已排程 |
| 非交易日 | 程序内置 `is_trading_day()` 判断：自动排除周六/周日 + 2026 法定节假日，非交易日跳过并写日志 |
| 触发动作 | ① 自动化先 WebSearch 刷新 `progress_db.json` → ② 运行 `st_progress_collector.py` → ③ 经飞书推送 |
| 失败处理 | 推送失败自动重试 1 次；仍失败写错误日志并回报；报告 HTML 始终落盘不丢 |
| 手动运行 | `python st_progress_collector.py`（正式） / `--no-send`（只分析不推送） / `--test-send`（仅发通道自测） |

**为什么之前"没正常执行"**：原 `st_monitor.py` 其实**每天 09:00 都在自动跑且飞书推送成功**，但沙箱内公告接口（东财 RPTA/np-anotice、巨潮、腾讯 notice）已全部失效，程序抓不到任何文本进度，只能输出"全中性"假结论。本次重写为 `st_progress_collector.py`：实时行情+主力资金流照常抓，文本进度改读 `progress_db.json`（由自动化每日 WebSearch 刷新），异动自动标红。

---

## 二、信息收集字段定义

### 1. 行情字段（数据源：腾讯 `qt.gtimg.cn`，GBK 解码）
| 字段 | 含义 |
|---|---|
| code/name | 代码 / 名称 |
| price | 现价（元） |
| pct | 涨跌幅（%） |
| amplitude | 振幅（%） |
| turnover | 换手率（%） |
| vol_ratio | 量比 |
| open/high/low/prev_close | 今开/最高/最低/昨收 |
| volume | 成交量（手） |
| amount | 成交额（元） |
| total_mv | 总市值（**亿元**，腾讯 f[44] 已是亿单位，无需再除 1e8） |

### 2. 资金字段（数据源：东财 `push2.eastmoney.com/.../fflow`，best-effort）
| 字段 | 含义 |
|---|---|
| main_net | 当日主力净流入（亿元，正=流入/负=流出；接口抖动时显示 —） |
| main_net_pct | 主力净流入占比（%） |
| am_main / pm_main | 上午 / 下午 主力净流入（亿元，由分时 240 条拆分） |

### 3. 进度字段（数据源：`progress_db.json`，每日 WebSearch 刷新）
| 字段 | 含义 |
|---|---|
| st_type | ST 或 *ST（*ST=退市风险警示） |
| stage | 阶段：已摘帽 / 申请待审 / 投资人已签 / 预重整中 / 等待摘帽门槛 / 滞后 |
| last_event_date | 最近关键事件日期 |
| last_event | 最新进展摘要 |
| catalyst_window | 关键催化时间窗 |
| risks | 主要风险点 |
| updated | 进度更新日期（距今日>3天自动标"需关注核实"） |

### 4. 派生字段（程序计算）
| 字段 | 含义 |
|---|---|
| flags | 异动/信号：放量(量比≥3) / 涨停·跌停(±9.5%) / 大涨·大跌(±4.9%) / 主力净流入·流出(≥0.3亿) / 进度N天前未更新 |
| verdict | 判定：利好 / 利空 / 需关注(异动) / 需关注核实 / 中性 |

---

## 三、通知方式说明

| 项 | 内容 |
|---|---|
| 默认通道 | **lark-cli**（bot 身份 P2P 私信发给老板） |
| 接收人 | `feishu_receive_id = ou_10cdef8ea8a202ab450597b1501eb8dd`（老板 open_id） |
| 命令原型 | `lark-cli im +messages-send --as bot --user-id <open_id> --msg-type text --content {"text":"..."}` |
| 备选通道 | webhook 群机器人（`feishu_push_mode=webhook`）、app(`tenant_access_token`, `feishu_push_mode=app`）——改 `CONFIG` 即可切换 |
| 推送内容 | 文本版日报（17 只速览，含价/涨跌幅/主力/阶段/进展/异动/判定） |
| 落盘产物 | 同步生成 HTML 图文报告 + JSONL 发送日志，便于回溯 |

---

## 四、17 只股票清单

```
600079 ST人福   002726 ST龙大   000711 ST京蓝   000838 *ST发展
600337 ST美克   002168 ST惠程   600381 *ST春天  300147 *ST香雪
002542 *ST中岩  300027 ST华谊   300020 ST银江   600340 *ST华幸
600370 *ST三房  600165 ST宁科   600525 ST长圆   603843 *ST正平
603377 ST东时
```
（market：sh=上交所 secid 1.x；sz=深交所含创业板 secid 0.x）

---

## 五、排查与维护

- **收不到推送**：先 `python st_progress_collector.py --test-send` 验证通道；查 `lark-cli --version`；查 `logs/st_collector_send_log.jsonl` 的 `send_ok`。
- **文本进度陈旧**：检查 `progress_db.json` 的 `updated`；确认自动化第①步 WebSearch 是否执行（网络/接口可用时）。
- **主力资金流显示 —**：东财 fflow 接口在沙箱偶发断连，程序已重试+降级，属正常现象；交易时段通常恢复。
- **增删标的**：改 `STOCKS` 列表；新增标的需同步在 `progress_db.json` 加条目。

> ⚠️ 免责：本程序为事件/量价监控工具，所有输出非投资建议。ST/*ST 波动剧烈、退市风险极高，据此交易风险自担。
