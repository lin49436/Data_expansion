#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含所有配置常量和参数
"""

import os
from datetime import datetime

# 时间配置
START_DATE = datetime(2025, 9, 1, 0, 0, 0)
END_DATE = datetime(2025, 9, 7, 23, 45, 0)
INTERVAL_MINUTES = 15

# 台区和电表配置
NUM_DISTRICTS = 16  # 台区数量
TOTAL_METERS = 1150  # 所有台区电表总数量(包括总表)
# 计算每个台区的分表数量(不包括总表)
# 总表数 = 台区数，分表总数 = 总电表数 - 总表数
NUM_SUB_METERS = (TOTAL_METERS - NUM_DISTRICTS) // NUM_DISTRICTS  # 每个台区的分表数量

# 输出目录配置
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs", "electric_meter_data")

# 供电单位编号配置 - 16个台区对应0501-0516
SUPPLY_ORG_NUMBERS = [f'05{i:02d}' for i in range(1, 17)]  # ['0501', '0502', ..., '0516']

# 为了兼容性，保留原有的函数接口
UNIFIED_SUPPLY_ORG_NO = SUPPLY_ORG_NUMBERS[0]  # 默认使用第一个编号

# 数据异常类型配置
ANOMALY_TYPES = {
    '计量失准': ['计量失准'],
    '接线错误': [
        '单相电流反接',
        '两相电流反接',
        '三相电流全反',
        '电流错相接入',
        '电压相序错误',
        '混合错误'
    ],
    '通信异常': [
        '4G信号模块异常',
        'SIM卡异常',
        '集中器电源故障',
        '集中器与模块档案一致性',
        '电表模块异常',
        '电表本体异常'
    ]
}