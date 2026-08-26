#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
获取A股实时股价数据
使用akshare库从东方财富网获取实时行情
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_realtime_price(stock_codes):
    """
    获取指定股票代码的实时股价
    
    Args:
        stock_codes: 股票代码列表，如 ['000636', '600664', '002636']
    
    Returns:
        DataFrame: 包含股票代码、名称、最新价、涨跌幅等信息
    """
    try:
        # 获取沪深京A股实时行情
        print("正在获取实时股价数据...")
        df = ak.stock_zh_a_spot_em()
        
        # 筛选指定股票
        result_list = []
        for code in stock_codes:
            # 确保代码格式正确（6位数字）
            code = code.strip()
            if len(code) == 6:
                # 查找匹配的股票
                stock_data = df[df['代码'] == code]
                if not stock_data.empty:
                    result_list.append({
                        '代码': stock_data['代码'].values[0],
                        '名称': stock_data['名称'].values[0],
                        '最新价': stock_data['最新价'].values[0],
                        '涨跌幅': stock_data['涨跌幅'].values[0],
                        '涨跌额': stock_data['涨跌额'].values[0],
                        '成交量': stock_data['成交量'].values[0],
                        '成交额': stock_data['成交额'].values[0],
                        '换手率': stock_data['换手率'].values[0],
                        '市盈率-动态': stock_data['市盈率-动态'].values[0],
                    })
        
        if result_list:
            result_df = pd.DataFrame(result_list)
            return result_df
        else:
            print(f"未找到匹配的股票: {stock_codes}")
            return None
            
    except Exception as e:
        print(f"获取股价数据时出错: {e}")
        return None

def main():
    """
    主函数 - 获取推荐股票的实时股价
    """
    # 推荐的股票代码列表
    stock_codes = [
        '002636',  # 金安国纪
        '002042',  # 华孚时尚
        '600354',  # 敦煌种业
        '603197',  # 保隆科技
        '600183',  # 生益科技
        '002463',  # 沪电股份
        '000636',  # 风华高科
        '600664',  # 哈药股份
        '603065',  # 宿迁联盛
        '603137',  # 恒尚节能
    ]
    
    print("=" * 80)
    print(f"A股实时股价查询 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 获取实时股价
    result = get_realtime_price(stock_codes)
    
    if result is not None:
        print("\n实时股价数据：")
        print("=" * 80)
        # 设置显示选项，确保所有列都能显示
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        # 格式化输出
        for idx, row in result.iterrows():
            print(f"\n【{row['名称']}】({row['代码']})")
            print(f"  最新价: {row['最新价']:.2f} 元")
            print(f"  涨跌幅: {row['涨跌幅']:.2f}%")
            print(f"  涨跌额: {row['涨跌额']:.2f} 元")
            print(f"  换手率: {row['换手率']:.2f}%")
            print(f"  市盈率: {row['市盈率-动态']:.2f}")
            print(f"  成交额: {row['成交额']:.2f} 万元")
        
        print("\n" + "=" * 80)
        
        # 保存到CSV文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'd:\\AI_Quant_Trading_Engine\\data\\realtime_stock_price_{timestamp}.csv'
        result.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存至: {filename}")
    else:
        print("\n获取股价数据失败！")

if __name__ == "__main__":
    main()