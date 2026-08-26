#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股监控大盘 - HTML实时仪表盘
监控指定股票的实时行情与涨跌幅告警

数据源: 新浪财经(稳定,不会被封IP)
报警规则:
  - 涨跌幅 <= -5% : 跌幅告警(红色闪烁)
  - 跌破止损位(收盘价×0.95) : 止损预警(红色闪烁)
  - 涨跌幅 >= +3.5% : 涨幅提示(蓝色)
  - 主力净流出 >= 3000万 : 主力流出(黄色) [需东方财富接口]
  - 主力净流入 >= 5000万 : 主力流入(绿色) [需东方财富接口]
"""

import json
import time
import threading
import socketserver
import http.server
import urllib.request
import urllib.parse
import re
from datetime import datetime

# ===================== 配置区 =====================
# 监控股票列表 (代码, 名称, 市场[sz/sh], 止损位)
MONITOR_STOCKS = [
    ("600664", "哈药股份", "sh", 7.86),
    ("002354", "天娱数科", "sz", 7.95),
    ("001258", "立新能源", "sz", 15.13),
    ("000636", "风华高科", "sz", 62.56),
    ("600667", "太极实业", "sh", 20.14),
]

# 报警阈值
ALERT_DROP_PCT = -5.0          # 跌幅超5%告警
ALERT_SURGE_PCT = 3.5          # 涨幅超3.5%提示
ALERT_MAIN_OUTFLOW = 3000      # 主力净流出3000万警告
ALERT_MAIN_INFLOW = 5000       # 主力净流入5000万提示

# 服务配置
HOST = "0.0.0.0"
PORT = 8888
REFRESH_INTERVAL = 30          # 数据刷新间隔(秒)

# ===================== 数据存储 =====================
latest_data = {
    "stocks": [],
    "update_time": "",
    "alerts": [],
}
data_lock = threading.Lock()

# 记录上一次涨跌幅,用于计算变动
last_pct = {}  # {code: pct}


# ===================== 数据获取 =====================
def get_realtime_quotes_sina():
    """从新浪财经获取实时行情(批量)"""
    codes = [f"{s[2]}{s[0]}" for s in MONITOR_STOCKS]
    url = f"http://hq.sinajs.cn/list={','.join(codes)}"

    req = urllib.request.Request(url)
    req.add_header("Referer", "http://finance.sina.com.cn")
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode("gbk", errors="ignore")
    except Exception as e:
        print(f"[ERROR] 新浪行情获取失败: {e}")
        return {}

    result = {}
    for line in content.strip().split("\n"):
        m = re.match(r'var hq_str_(\w+)="(.+)"', line)
        if not m:
            continue
        code_full = m.group(1)
        fields = m.group(2).split(",")
        if len(fields) < 32:
            continue

        name = fields[0]
        open_p = float(fields[1]) if fields[1] else 0
        pre_close = float(fields[2]) if fields[2] else 0
        current = float(fields[3]) if fields[3] else 0
        high = float(fields[4]) if fields[4] else 0
        low = float(fields[5]) if fields[5] else 0
        volume = float(fields[8]) if fields[8] else 0  # 手
        amount = float(fields[9]) if fields[9] else 0  # 元

        if pre_close > 0 and current > 0:
            pct = (current - pre_close) / pre_close * 100
        else:
            pct = 0

        result[code_full[2:]] = {
            "name": name,
            "code": code_full[2:],
            "price": current,
            "open": open_p,
            "pre_close": pre_close,
            "high": high,
            "low": low,
            "volume": volume,
            "amount": amount,
            "pct": round(pct, 2),
        }

    return result


def collect_data():
    """采集所有监控股票数据"""
    quotes = get_realtime_quotes_sina()
    if not quotes:
        print("[WARN] 未获取到行情数据")
        return

    stocks = []
    new_alerts = []

    for code, name, market, stop_loss in MONITOR_STOCKS:
        q = quotes.get(code, {})
        if not q:
            stocks.append({
                "name": name, "code": code, "price": 0, "pct": 0,
                "status": "数据加载中", "stop_loss": stop_loss,
                "main_net": 0, "alert_level": "normal"
            })
            continue

        pct = q["pct"]
        price = q["price"]

        # 计算涨跌幅变动(与上次相比)
        old_pct = last_pct.get(code)
        pct_change = None
        if old_pct is not None:
            pct_change = round(pct - old_pct, 2)

        # 判断报警级别
        alert_level = "normal"
        status = "正常"

        # 1. 跌幅告警(当前涨幅≤-5%)
        if pct <= ALERT_DROP_PCT:
            alert_level = "critical"
            status = "🔴跌幅告警"
            new_alerts.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "stock": name,
                "msg": f"跌幅 {pct}% 触发告警",
                "level": "critical"
            })

        # 2. 止损预警(跌破止损位)
        if price > 0 and price <= stop_loss:
            alert_level = "critical"
            status = "🔴止损预警"
            new_alerts.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "stock": name,
                "msg": f"现价 {price} 跌破止损位 {stop_loss}",
                "level": "critical"
            })

        # 3. 涨跌幅变动提示(变动幅度≥3.5%)
        if pct_change is not None and abs(pct_change) >= ALERT_SURGE_PCT:
            if alert_level != "critical":  # 跌幅告警/止损优先
                alert_level = "surge"
                status = "🔵变动提示"
            change_str = f"{'+' if pct_change > 0 else ''}{pct_change}%"
            new_alerts.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "stock": name,
                "msg": f"涨跌幅变动 {change_str}({old_pct}%→{pct}%)",
                "level": "surge"
            })

        # 更新上一次涨跌幅
        last_pct[code] = pct

        stocks.append({
            "name": name,
            "code": code,
            "price": price,
            "pct": pct,
            "pct_change": pct_change,  # 与上次相比的变动
            "open": q["open"],
            "high": q["high"],
            "low": q["low"],
            "pre_close": q["pre_close"],
            "volume": q["volume"],
            "amount": q["amount"],
            "stop_loss": stop_loss,
            "main_net": 0,  # 新浪无资金流向,显示0
            "status": status,
            "alert_level": alert_level,
        })

    with data_lock:
        latest_data["stocks"] = stocks
        latest_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 保留最近20条报警
        latest_data["alerts"] = (new_alerts + latest_data["alerts"])[:20]

    print(f"[{latest_data['update_time']}] 数据已更新,共 {len(stocks)} 只股票")


def data_loop():
    """后台数据采集循环"""
    while True:
        try:
            collect_data()
        except Exception as e:
            print(f"[ERROR] 数据采集异常: {e}")
        time.sleep(REFRESH_INTERVAL)


# ===================== HTML页面 =====================
HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A股监控大盘</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    padding: 20px;
}
.header {
    background: linear-gradient(135deg, #1a2332, #0d1117);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px solid #30363d;
}
.header h1 {
    color: #58a6ff;
    font-size: 24px;
    margin-bottom: 10px;
}
.header .info {
    color: #8b949e;
    font-size: 14px;
}
.stats {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.stat-card {
    background: #161b22;
    padding: 15px 20px;
    border-radius: 8px;
    border: 1px solid #30363d;
    min-width: 140px;
}
.stat-card .label { color: #8b949e; font-size: 12px; }
.stat-card .value { color: #58a6ff; font-size: 22px; font-weight: bold; margin-top: 5px; }
.stock-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}
.stock-card {
    background: #161b22;
    border-radius: 10px;
    padding: 18px;
    border: 2px solid #30363d;
    transition: all 0.3s;
}
.stock-card.critical {
    border-color: #f85149;
    animation: pulse 1.5s infinite;
}
.stock-card.surge { border-color: #58a6ff; }
.stock-card.inflow { border-color: #3fb950; }
.stock-card.warning { border-color: #d29922; }
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 5px #f85149; }
    50% { box-shadow: 0 0 20px #f85149; }
}
.stock-name {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.stock-code { color: #8b949e; font-size: 13px; font-weight: normal; }
.stock-price {
    font-size: 28px;
    font-weight: bold;
    margin: 8px 0;
}
.up { color: #f85149; }
.down { color: #3fb950; }
.stock-detail {
    font-size: 13px;
    color: #8b949e;
    line-height: 1.6;
}
.status-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
.status-normal { background: #21262d; color: #8b949e; }
.status-critical { background: #f8514922; color: #f85149; }
.status-surge { background: #58a6ff22; color: #58a6ff; }
.status-warning { background: #d2992222; color: #d29922; }
.alerts-section {
    background: #161b22;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #30363d;
}
.alerts-section h2 {
    color: #58a6ff;
    font-size: 16px;
    margin-bottom: 10px;
}
.alert-item {
    padding: 6px 10px;
    margin: 4px 0;
    border-radius: 4px;
    font-size: 13px;
    background: #21262d;
}
.alert-critical { border-left: 3px solid #f85149; }
.alert-surge { border-left: 3px solid #58a6ff; }
.alert-warning { border-left: 3px solid #d29922; }
.footer {
    text-align: center;
    color: #484f58;
    font-size: 12px;
    margin-top: 20px;
    padding: 10px;
}
</style>
</head>
<body>
<div class="header">
    <h1>📊 A股监控大盘</h1>
    <div class="info">
        更新时间: <span id="updateTime">--</span> |
        监控股票: <span id="stockCount">--</span> 只 |
        刷新间隔: 30秒 |
        <span style="color:#3fb950">● 服务运行中</span>
    </div>
</div>

<div class="stats">
    <div class="stat-card">
        <div class="label">上涨/下跌</div>
        <div class="value" id="upDownCount">--</div>
    </div>
    <div class="stat-card">
        <div class="label">跌幅告警</div>
        <div class="value" id="dropAlertCount" style="color:#f85149">0</div>
    </div>
    <div class="stat-card">
        <div class="label">涨幅提示</div>
        <div class="value" id="surgeCount" style="color:#58a6ff">0</div>
    </div>
    <div class="stat-card">
        <div class="label">止损预警</div>
        <div class="value" id="stopLossCount" style="color:#f85149">0</div>
    </div>
</div>

<div class="stock-grid" id="stockGrid">加载中...</div>

<div class="alerts-section">
    <h2>🔔 报警日志</h2>
    <div id="alertsList">暂无报警</div>
</div>

<div class="footer">
    数据来源: 新浪财经 | 报警规则: 跌幅≤-5%告警, 涨幅≥3.5%提示, 跌破止损位预警<br>
    ⚠️ 本监控仅供研究参考,不构成投资建议
</div>

<script>
async function refresh() {
    try {
        const resp = await fetch('/api/data');
        const data = await resp.json();
        document.getElementById('updateTime').textContent = data.update_time;
        document.getElementById('stockCount').textContent = data.stocks.length;

        let upCount = 0, downCount = 0;
        let dropAlerts = 0, surgeAlerts = 0, stopLossAlerts = 0;

        data.stocks.forEach(s => {
            if (s.pct > 0) upCount++;
            else if (s.pct < 0) downCount++;
            if (s.alert_level === 'critical') {
                if (s.pct <= -5) dropAlerts++;
                else stopLossAlerts++;
            }
            if (s.alert_level === 'surge') surgeAlerts++;
        });

        document.getElementById('upDownCount').textContent = upCount + '涨 / ' + downCount + '跌';
        document.getElementById('dropAlertCount').textContent = dropAlerts;
        document.getElementById('surgeCount').textContent = surgeAlerts;
        document.getElementById('stopLossCount').textContent = stopLossAlerts;

        const grid = document.getElementById('stockGrid');
        grid.innerHTML = data.stocks.map(s => {
            const priceClass = s.pct >= 0 ? 'up' : 'down';
            const pctText = (s.pct >= 0 ? '+' : '') + s.pct + '%';
            const amountYi = (s.amount / 100000000).toFixed(2);
            const statusClass = 'status-' + s.alert_level;
            let changeText = '';
            if (s.pct_change !== null && s.pct_change !== undefined) {
                const changeStr = (s.pct_change >= 0 ? '+' : '') + s.pct_change + '%';
                const changeColor = s.pct_change >= 0 ? '#f85149' : '#3fb950';
                changeText = ` | 变动: <span style="color:${changeColor}">${changeStr}</span>`;
            }
            return `
            <div class="stock-card ${s.alert_level}">
                <div class="stock-name">
                    <span>${s.name}</span>
                    <span class="stock-code">${s.code}</span>
                </div>
                <div class="stock-price ${priceClass}">
                    ${s.price.toFixed(2)}
                    <span style="font-size:16px">(${pctText})</span>
                </div>
                <div class="stock-detail">
                    开盘: ${s.open.toFixed(2)} | 最高: ${s.high.toFixed(2)} | 最低: ${s.low.toFixed(2)}<br>
                    昨收: ${s.pre_close.toFixed(2)} | 成交额: ${amountYi}亿<br>
                    止损位: ${s.stop_loss.toFixed(2)}${changeText}<br>
                    <span class="status-tag ${statusClass}">${s.status}</span>
                </div>
            </div>`;
        }).join('');

        const alertsList = document.getElementById('alertsList');
        if (data.alerts.length === 0) {
            alertsList.innerHTML = '暂无报警';
        } else {
            alertsList.innerHTML = data.alerts.map(a => `
                <div class="alert-item alert-${a.level}">
                    [${a.time}] ${a.stock}: ${a.msg}
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('刷新失败:', e);
    }
}

refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>
"""


# ===================== HTTP服务器 =====================
class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/data":
            with data_lock:
                data = json.dumps(latest_data, ensure_ascii=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        elif self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # 静默日志


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def main():
    # 启动数据采集线程
    t = threading.Thread(target=data_loop, daemon=True)
    t.start()

    # 启动HTTP服务器
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"=" * 60)
    print(f"  A股监控大盘已启动")
    print(f"  访问地址: http://localhost:{PORT}")
    print(f"  监控股票: {len(MONITOR_STOCKS)} 只")
    print(f"  刷新间隔: {REFRESH_INTERVAL}秒")
    print(f"  报警规则: 跌幅≤{ALERT_DROP_PCT}%告警, 涨幅≥{ALERT_SURGE_PCT}%提示")
    print(f"=" * 60)
    print(f"  按 Ctrl+C 停止服务")
    print(f"=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.shutdown()


if __name__ == "__main__":
    main()
