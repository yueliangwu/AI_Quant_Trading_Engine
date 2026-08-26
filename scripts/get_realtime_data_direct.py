#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
直接请求东方财富API获取A股实时数据
绕过AKShare中间层，直接使用requests请求
"""

import requests
import pandas as pd
import time
from datetime import datetime
import json

def get_all_stocks_direct():
    """
    直接请求东方财富API获取所有A股实时行情数据
    """
    print("正在获取A股实时行情数据（直接API）...")
    
    # 东方财富API接口
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    
    # 请求参数
    params = {
        "pn": "1",
        "pz": "5000",  # 获取5000条数据
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data and 'data' in data and 'diff' in data['data']:
            stock_list = data['data']['diff']
            
            # 解析数据
            result_list = []
            for stock in stock_list:
                result_list.append({
                    '代码': stock.get('f12', ''),
                    '名称': stock.get('f14', ''),
                    '最新价': stock.get('f2', 0) / 100 if stock.get('f2') else 0,
                    '涨跌幅': stock.get('f3', 0) / 100 if stock.get('f3') else 0,
                    '涨跌额': stock.get('f4', 0) / 100 if stock.get('f4') else 0,
                    '成交量': stock.get('f5', 0),
                    '成交额': stock.get('f6', 0),
                    '振幅': stock.get('f7', 0) / 100 if stock.get('f7') else 0,
                    '最高': stock.get('f15', 0) / 100 if stock.get('f15') else 0,
                    '最低': stock.get('f16', 0) / 100 if stock.get('f16') else 0,
                    '今开': stock.get('f17', 0) / 100 if stock.get('f17') else 0,
                    '昨收': stock.get('f18', 0) / 100 if stock.get('f18') else 0,
                    '量比': stock.get('f10', 0) / 100 if stock.get('f10') else 0,
                    '换手率': stock.get('f8', 0) / 100 if stock.get('f8') else 0,
                    '市盈率-动态': stock.get('f9', 0) / 100 if stock.get('f9') else 0,
                    '市净率': stock.get('f23', 0) / 100 if stock.get('f23') else 0,
                    '总市值': stock.get('f20', 0),
                    '流通市值': stock.get('f21', 0),
                    '涨速': stock.get('f22', 0) / 100 if stock.get('f22') else 0,
                    '60日涨跌幅': stock.get('f25', 0) / 100 if stock.get('f25') else 0,
                    '年初至今涨跌幅': stock.get('f26', 0) / 100 if stock.get('f26') else 0,
                })
            
            df = pd.DataFrame(result_list)
            print(f"成功获取 {len(df)} 只股票数据")
            return df
        else:
            print("未获取到数据")
            return None
            
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def get_shareholder_count_direct(stock_code):
    """
    从互动平台获取股东户数数据
    由于无法直接获取，这里返回None
    """
    return None

def main():
    """主函数"""
    print("=" * 80)
    print(f"A股实时数据获取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 获取实时数据
    df = get_all_stocks_direct()
    
    if df is not None and len(df) > 0:
        # 先保存原始数据用于分析
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import os
        os.makedirs(f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15', exist_ok=True)
        
        # 保存原始数据
        raw_file = f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15\\raw_stocks_{timestamp}.csv'
        df.to_csv(raw_file, index=False, encoding='utf-8-sig')
        print(f"\n原始数据已保存至: {raw_file}")
        
        # 显示数据概况
        print("\n数据概况：")
        print(df.info())
        print("\n前10只股票数据：")
        print(df[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率', '60日涨跌幅']].head(10).to_string())
        
        # 排除科创板
        df_filtered = df[~df['代码'].str.startswith('688')]
        print(f"\n排除科创板后剩余 {len(df_filtered)} 只股票")
        
        # 筛选业绩好的股票（放宽条件）
        df_filtered = df_filtered[df_filtered['市盈率-动态'] > 0]
        print(f"筛选市盈率为正后剩余 {len(df_filtered)} 只")
        
        df_filtered = df_filtered[(df_filtered['市盈率-动态'] >= 5) & (df_filtered['市盈率-动态'] <= 50)]
        print(f"筛选市盈率5-50倍后剩余 {len(df_filtered)} 只")
        
        df_filtered = df_filtered[(df_filtered['市净率'] >= 0.5) & (df_filtered['市净率'] <= 10)]
        print(f"筛选市净率0.5-10倍后剩余 {len(df_filtered)} 只")
        
        # 筛选上升趋势（放宽条件）
        if len(df_filtered) > 0:
            print("\n上升趋势筛选：")
            df_filtered = df_filtered[df_filtered['60日涨跌幅'] > 0]
            print(f"筛选60日涨幅为正后剩余 {len(df_filtered)} 只")
            
            if len(df_filtered) > 0:
                df_filtered = df_filtered[df_filtered['年初至今涨跌幅'] > -10]
                print(f"筛选年内跌幅不超过10%后剩余 {len(df_filtered)} 只")
                
                if len(df_filtered) > 0:
                    df_filtered = df_filtered[(df_filtered['涨跌幅'] >= -3) & (df_filtered['涨跌幅'] <= 5)]
                    print(f"筛选今日涨幅-3%到5%后剩余 {len(df_filtered)} 只")
        
        # 按流通市值排序
        if len(df_filtered) > 0:
            df_filtered = df_filtered.sort_values('流通市值', ascending=True)
            
            # 保存筛选结果
            output_file = f'd:\\AI_Quant_Trading_Engine\\data\\2026-07-15\\realtime_stocks_{timestamp}.csv'
            df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n筛选结果已保存至: {output_file}")
            
            # 显示结果
            print("\n前20只符合条件的股票：")
            print(df_filtered[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率', '60日涨跌幅', '流通市值']].head(20).to_string())
        else:
            print("\n没有符合条件的股票")
        
        return df_filtered
    else:
        print("获取数据失败")
        return None

if __name__ == "__main__":
    result = main()