#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
使用baostock获取股东数据，计算散户占比
"""

import baostock as bs
import pandas as pd
from datetime import datetime
import time

def get_shareholder_ratio_baostock(stock_code):
    """
    使用baostock获取股东持股比例
    """
    try:
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"登录失败: {lg.error_msg}")
            return None
        
        # 构造股票代码（格式：sh.600519 或 sz.000001）
        if stock_code.startswith('6'):
            bs_code = f"sh.{stock_code}"
        else:
            bs_code = f"sz.{stock_code}"
        
        # 获取最近一期的十大股东数据
        rs = bs.query_stock_basic(code=bs_code)
        if rs.error_code != '0':
            print(f"查询失败: {rs.error_msg}")
            return None
        
        # 获取股东持股数据
        rs = bs.query_shareholder_num(code=bs_code, year='2026', quarter='2')
        if rs.error_code != '0':
            print(f"查询股东数据失败: {rs.error_msg}")
            return None
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if len(data_list) > 0:
            df = pd.DataFrame(data_list, columns=rs.fields)
            # 返回股东户数
            return int(df.iloc[0]['shareholder_num'])
        else:
            return None
            
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None
    finally:
        bs.logout()

def main():
    """主函数"""
    print("=" * 80)
    print(f"股东数据获取测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试贵州茅台
    print("\n测试贵州茅台（600519）的股东数据...")
    result = get_shareholder_ratio_baostock('600519')
    
    if result:
        print(f"股东户数: {result}")
    else:
        print("获取失败")

if __name__ == "__main__":
    main()