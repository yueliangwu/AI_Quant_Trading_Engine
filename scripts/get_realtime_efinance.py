#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
使用efinance库获取A股实时数据
"""

import efinance as ef
import pandas as pd
from datetime import datetime
import time

def get_all_stocks_efinance():
    """
    使用efinance获取所有A股实时行情数据
    """
    print("正在获取A股实时行情数据（efinance）...")
    
    try:
        # 获取全市场股票实时行情
        df = ef.stock.get_realtime_quotes()
        
        print(f"成功获取 {len(df)} 只股票数据")
        return df
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 80)
    print(f"A股实时数据获取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 获取实时数据
    df = get_all_stocks_efinance()
    
    if df is not None and len(df) > 0:
        # 保存原始数据
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import os
        os.makedirs(f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15', exist_ok=True)
        
        raw_file = f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15\\raw_stocks_efinance_{timestamp}.csv'
        df.to_csv(raw_file, index=False, encoding='utf-8-sig')
        print(f"\n原始数据已保存至: {raw_file}")
        
        # 显示数据概况
        print("\n数据列名：")
        print(df.columns.tolist())
        
        print("\n前10只股票数据：")
        print(df.head(10).to_string())
        
        # 统计数据
        print(f"\n数据总数: {len(df)}")
        
        return df
    else:
        print("获取数据失败")
        return None

if __name__ == "__main__":
    result = main()