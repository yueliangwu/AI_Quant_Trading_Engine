#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
筛选散户占比小于10%的股票（真实数据）
散户占比 = 100% - 机构持股比例（前十大流通股东持股比例之和）
"""

import akshare as ak
import pandas as pd
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_all_stocks():
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
                wait_time = (attempt + 1) * 2
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            print(f"所有重试均失败")
            return None

def get_retail_ratio(stock_code):
    """
    获取散户占比
    散户占比 = 100% - 前十大流通股东持股比例之和
    
    Args:
        stock_code: 股票代码（6位数字）
    
    Returns:
        散户占比（百分比）或None（获取失败）
    """
    try:
        # 构造带市场标识的股票代码
        if stock_code.startswith('6'):
            symbol = f"SH{stock_code}"
        else:
            symbol = f"SZ{stock_code}"
        
        # 获取十大流通股东数据
        df = ak.stock_gdfx_free_top_10_em(symbol=symbol)
        
        if df is not None and len(df) > 0:
            # 计算前十大流通股东持股比例之和
            # 注意：不同数据源的列名可能不同，需要查看实际返回的数据
            # 常见的列名：'持股数量', '持股比例', '占流通股比例'等
            
            # 尝试不同的列名
            ratio_column = None
            possible_columns = ['占总流通股本持股比例', '持股比例', '占流通股比例', '持股数量占比']
            
            for col in possible_columns:
                if col in df.columns:
                    ratio_column = col
                    break
            
            if ratio_column:
                # 持股比例可能是百分比格式或小数格式
                # 需要根据实际情况处理
                total_ratio = df[ratio_column].sum()
                
                # 如果数据是百分比格式（如"5.23%"），需要转换
                # 如果是小数格式（如0.0523），直接使用
                
                # 假设数据已经是百分比格式
                # 散户占比 = 100% - 机构持股比例
                retail_ratio = 100 - total_ratio
                
                return retail_ratio
            else:
                # 如果找不到持股比例列，打印列名以便调试
                print(f"    警告：找不到持股比例列，可用列：{df.columns.tolist()}")
                return None
        else:
            return None
            
    except Exception as e:
        print(f"    获取散户占比失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 80)
    print(f"散户占比筛选器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. 获取所有股票数据
    df = get_all_stocks()
    if df is None:
        print("获取股票数据失败")
        return None
    
    # 2. 排除科创板
    print("\n正在排除科创板股票...")
    df_filtered = df[~df['代码'].str.startswith('688')]
    print(f"排除科创板后剩余 {len(df_filtered)} 只股票")
    
    # 3. 筛选业绩好的股票
    print("\n正在筛选业绩好的股票...")
    df_filtered = df_filtered[df_filtered['市盈率-动态'] > 0]
    print(f"  排除亏损股票后剩余 {len(df_filtered)} 只")
    
    df_filtered = df_filtered[(df_filtered['市盈率-动态'] >= 5) & (df_filtered['市盈率-动态'] <= 50)]
    print(f"  筛选市盈率5-50倍后剩余 {len(df_filtered)} 只")
    
    df_filtered = df_filtered[(df_filtered['市净率'] >= 0.5) & (df_filtered['市净率'] <= 10)]
    print(f"  筛选市净率0.5-10倍后剩余 {len(df_filtered)} 只")
    
    # 4. 筛选上升趋势
    print("\n正在筛选上升趋势的股票...")
    df_filtered = df_filtered[df_filtered['60日涨跌幅'] > 0]
    print(f"  筛选60日涨幅为正后剩余 {len(df_filtered)} 只")
    
    df_filtered = df_filtered[df_filtered['年初至今涨跌幅'] > -10]
    print(f"  筛选年内跌幅不超过10%后剩余 {len(df_filtered)} 只")
    
    df_filtered = df_filtered[(df_filtered['涨跌幅'] >= -3) & (df_filtered['涨跌幅'] <= 5)]
    print(f"  筛选今日涨幅-3%到5%后剩余 {len(df_filtered)} 只")
    
    if len(df_filtered) == 0:
        print("\n没有股票符合前4项条件")
        return None
    
    # 5. 获取散户占比数据
    print(f"\n正在获取 {len(df_filtered)} 只股票的散户占比数据...")
    print("（这可能需要较长时间，请耐心等待...）")
    
    results = []
    for idx, row in df_filtered.iterrows():
        stock_code = row['代码']
        stock_name = row['名称']
        
        print(f"  正在处理 {stock_name}({stock_code})...", end='')
        
        retail_ratio = get_retail_ratio(stock_code)
        
        if retail_ratio is not None:
            print(f" 散户占比: {retail_ratio:.2f}%")
            
            # 只保留散户占比 < 10%的股票
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
                    '散户占比': retail_ratio
                })
                print(f"    ✓ 符合条件（散户占比 < 10%）")
        else:
            print(f" 无法获取数据")
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 6. 生成结果
    if len(results) > 0:
        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values('散户占比', ascending=True)
        
        print("\n" + "=" * 80)
        print(f"筛选完成，共筛选出 {len(result_df)} 只散户占比 < 10% 的股票")
        print("=" * 80)
        
        return result_df
    else:
        print("\n没有股票符合所有筛选条件")
        return None

if __name__ == "__main__":
    result = main()
    
    if result is not None:
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15\\real_stocks_{timestamp}.csv'
        
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        result.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存至: {output_file}")
        
        # 显示结果
        print("\n筛选结果：")
        print(result[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '散户占比']].to_string())