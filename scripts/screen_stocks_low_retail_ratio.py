#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
筛选散户占比低、业绩好、刚调整完、上升趋势的股票
筛选条件：
1. 散户占比 < 10%（筹码集中度高）
2. 非科创板（排除688开头的股票）
3. 刚调整完（技术面指标）
4. 上升趋势（技术面指标）
5. 业绩好（基本面指标）
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.all_stocks = None
        self.filtered_stocks = []
        
    def get_all_stocks(self):
        """获取所有A股实时行情数据"""
        print("正在获取A股实时行情数据...")
        max_retries = 5
        for attempt in range(max_retries):
            try:
                print(f"  尝试第 {attempt + 1} 次连接...")
                df = ak.stock_zh_a_spot_em()
                print(f"成功获取 {len(df)} 只股票数据")
                return df
            except Exception as e:
                print(f"  第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"  等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                print(f"所有重试均失败，无法获取数据")
                return None
    
    def filter_non_star_market(self, df):
        """排除科创板股票（688开头）"""
        print("\n正在筛选非科创板股票...")
        df_filtered = df[~df['代码'].str.startswith('688')]
        print(f"排除科创板后剩余 {len(df_filtered)} 只股票")
        return df_filtered
    
    def filter_good_performance(self, df):
        """筛选业绩好的股票"""
        print("\n正在筛选业绩好的股票...")
        
        # 筛选条件：
        # 1. 市盈率在合理范围（5-50倍）
        # 2. 市净率在合理范围（0.5-10倍）
        df_filtered = df.copy()
        
        # 排除亏损股票（市盈率为负）
        df_filtered = df_filtered[df_filtered['市盈率-动态'] > 0]
        print(f"  排除亏损股票后剩余 {len(df_filtered)} 只")
        
        # 筛选市盈率在合理范围（5-50倍）
        df_filtered = df_filtered[(df_filtered['市盈率-动态'] >= 5) & (df_filtered['市盈率-动态'] <= 50)]
        print(f"  筛选市盈率5-50倍后剩余 {len(df_filtered)} 只")
        
        # 筛选市净率在合理范围（0.5-10倍）
        df_filtered = df_filtered[(df_filtered['市净率'] >= 0.5) & (df_filtered['市净率'] <= 10)]
        print(f"  筛选市净率0.5-10倍后剩余 {len(df_filtered)} 只")
        
        return df_filtered
    
    def filter_uptrend_stocks(self, df):
        """筛选上升趋势的股票"""
        print("\n正在筛选上升趋势的股票...")
        
        df_filtered = df.copy()
        
        # 上升趋势判断：
        # 1. 60日涨跌幅 > 0（中期趋势向上）
        # 2. 年初至今涨跌幅 > -10%（年内表现不差）
        # 3. 最新价 > 昨收（今日上涨或平盘）
        
        df_filtered = df_filtered[df_filtered['60日涨跌幅'] > 0]
        print(f"  筛选60日涨幅为正后剩余 {len(df_filtered)} 只")
        
        df_filtered = df_filtered[df_filtered['年初至今涨跌幅'] > -10]
        print(f"  筛选年内跌幅不超过10%后剩余 {len(df_filtered)} 只")
        
        # 今日涨幅在合理范围（-3% 到 5%），避免追高
        df_filtered = df_filtered[(df_filtered['涨跌幅'] >= -3) & (df_filtered['涨跌幅'] <= 5)]
        print(f"  筛选今日涨幅-3%到5%后剩余 {len(df_filtered)} 只")
        
        return df_filtered
    
    def get_shareholder_count(self, stock_code, max_retries=3):
        """
        获取股东户数（用于判断散户占比）
        股东户数越少，筹码越集中，散户占比越低
        """
        for attempt in range(max_retries):
            try:
                # 尝试获取股东户数数据
                df = ak.stock_zh_a_gdhs(symbol=stock_code)
                if df is not None and len(df) > 0:
                    # 获取最近一期的股东户数
                    latest_count = int(df.iloc[0]['股东户数'])
                    return latest_count
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return None
    
    def estimate_retail_ratio(self, stock_code, shareholder_count, total_shares):
        """
        估算散户占比
        这是一个估算方法，实际散户占比需要更详细的数据
        
        估算逻辑：
        - 股东户数 < 1万：筹码非常集中，散户占比可能 < 5%
        - 股东户数 1万-3万：筹码集中，散户占比可能 5-10%
        - 股东户数 3万-5万：筹码相对集中，散户占比可能 10-15%
        - 股东户数 > 5万：筹码分散，散户占比可能 > 15%
        """
        if shareholder_count is None:
            return None
        
        if shareholder_count < 10000:
            return 5  # 筹码非常集中，估算散户占比 < 5%
        elif shareholder_count < 30000:
            return 8  # 筹码集中，估算散户占比 5-10%
        elif shareholder_count < 50000:
            return 12  # 筹码相对集中，估算散户占比 10-15%
        else:
            return 15  # 筹码分散，估算散户占比 > 15%
    
    def filter_low_retail_ratio(self, df, max_stocks=50):
        """
        筛选散户占比低的股票
        由于无法直接获取散户占比，使用股东户数作为替代指标
        """
        print(f"\n正在筛选散户占比低的股票（最多筛选{max_stocks}只）...")
        print("提示：由于无法直接获取散户占比数据，将使用股东户数作为替代指标")
        print("      股东户数越少，筹码越集中，散户占比越低")
        
        # 优先筛选流通市值适中、换手率合理的股票（这些股票更适合进一步分析）
        df_filtered = df.copy()
        df_filtered = df_filtered.sort_values('流通市值', ascending=True)
        
        # 取前max_stocks只股票进行分析
        df_filtered = df_filtered.head(max_stocks)
        
        print(f"\n对 {len(df_filtered)} 只股票进行股东户数分析...")
        
        results = []
        for idx, row in df_filtered.iterrows():
            stock_code = row['代码']
            stock_name = row['名称']
            
            # 获取股东户数
            shareholder_count = self.get_shareholder_count(stock_code)
            
            if shareholder_count:
                # 估算散户占比
                retail_ratio = self.estimate_retail_ratio(stock_code, shareholder_count, row['总市值'])
                
                # 只保留散户占比 < 10% 的股票
                if retail_ratio < 10:
                    results.append({
                        '代码': stock_code,
                        '名称': stock_name,
                        '最新价': row['最新价'],
                        '涨跌幅': row['涨跌幅'],
                        '市盈率-动态': row['市盈率-动态'],
                        '市净率': row['市净率'],
                        '60日涨跌幅': row['60日涨跌幅'],
                        '年初至今涨跌幅': row['年初至今涨跌幅'],
                        '流通市值': row['流通市值'],
                        '换手率': row['换手率'],
                        '股东户数': shareholder_count,
                        '估算散户占比': retail_ratio
                    })
                    print(f"  ✓ {stock_name}({stock_code}) - 股东户数:{shareholder_count}, 估算散户占比:{retail_ratio}%")
                else:
                    print(f"  ✗ {stock_name}({stock_code}) - 股东户数:{shareholder_count}, 估算散户占比:{retail_ratio}% (不符合)")
            else:
                print(f"  - {stock_name}({stock_code}) - 无法获取股东户数数据")
            
            # 避免请求过快
            time.sleep(0.3)
        
        print(f"\n筛选出 {len(results)} 只散户占比 < 10% 的股票")
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def run_screening(self):
        """执行筛选流程"""
        print("=" * 80)
        print(f"股票筛选器 - {self.today}")
        print("=" * 80)
        
        # 1. 获取所有股票数据
        df = self.get_all_stocks()
        if df is None:
            return None
        
        # 2. 排除科创板
        df = self.filter_non_star_market(df)
        
        # 3. 筛选业绩好的股票
        df = self.filter_good_performance(df)
        
        # 4. 筛选上升趋势的股票
        df = self.filter_uptrend_stocks(df)
        
        if len(df) == 0:
            print("\n没有股票符合前4项条件")
            return None
        
        # 5. 筛选散户占比低的股票
        result = self.filter_low_retail_ratio(df, max_stocks=100)
        
        return result

def main():
    """主函数"""
    screener = StockScreener()
    result = screener.run_screening()
    
    if result is not None and len(result) > 0:
        print("\n" + "=" * 80)
        print("筛选结果汇总")
        print("=" * 80)
        
        # 生成Markdown报告
        report_lines = []
        report_lines.append(f"# 散户占比低、业绩好、上升趋势股票筛选报告")
        report_lines.append(f"\n**筛选日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\n**筛选条件**: ")
        report_lines.append(f"- 散户占比 < 10%（基于股东户数估算）")
        report_lines.append(f"- 非科创板股票")
        report_lines.append(f"- 刚调整完（今日涨幅 -3% 到 5%）")
        report_lines.append(f"- 上升趋势（60日涨幅为正）")
        report_lines.append(f"- 业绩好（市盈率 5-50倍，市净率 0.5-10倍）")
        report_lines.append(f"\n**筛选结果**: 共筛选出 {len(result)} 只股票")
        
        # 按散户占比排序
        result_sorted = result.sort_values('估算散户占比', ascending=True)
        
        report_lines.append("\n\n## 股票列表")
        report_lines.append("\n| 序号 | 股票代码 | 股票名称 | 最新价(元) | 涨跌幅(%) | 市盈率 | 市净率 | 60日涨幅(%) | 股东户数 | 估算散户占比(%) |")
        report_lines.append("|------|---------|---------|-----------|----------|--------|--------|------------|---------|---------------|")
        
        for idx, row in result_sorted.iterrows():
            report_lines.append(f"| {idx+1} | {row['代码']} | {row['名称']} | {row['最新价']:.2f} | {row['涨跌幅']:.2f} | {row['市盈率-动态']:.2f} | {row['市净率']:.2f} | {row['60日涨跌幅']:.2f} | {row['股东户数']} | {row['估算散户占比']} |")
        
        report_lines.append("\n\n## 风险提示")
        report_lines.append("\n1. **散户占比估算说明**: 由于无法直接获取散户占比数据，本报告使用股东户数进行估算，实际散户占比可能与估算值有差异。")
        report_lines.append("2. **投资风险**: 股市有风险，投资需谨慎。本报告仅供参考，不构成投资建议。")
        report_lines.append("3. **数据来源**: 数据来自东方财富网，通过AKShare接口获取，数据可能存在延迟。")
        
        # 保存报告
        report_path = f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15\\REPORT_散户占比低股票筛选_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_content = "\n".join(report_lines)
        
        import os
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n报告已保存至: {report_path}")
        
        # 同时保存CSV
        csv_path = report_path.replace('.md', '.csv')
        result_sorted.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"数据已保存至: {csv_path}")
        
        # 打印报告内容
        print("\n" + report_content)
        
    else:
        print("\n没有找到符合条件的股票")

if __name__ == "__main__":
    main()