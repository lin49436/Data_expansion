#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含通用的辅助函数
"""

import random
import string
from datetime import timedelta
from config import START_DATE, END_DATE, INTERVAL_MINUTES, UNIFIED_SUPPLY_ORG_NO


def get_unified_org_no():
    """返回统一的供电单位编号"""
    return UNIFIED_SUPPLY_ORG_NO


def generate_time_series():
    """生成从开始到结束的时间序列,间隔15分钟"""
    times = []
    current = START_DATE
    while current <= END_DATE:
        times.append(current)
        current += timedelta(minutes=INTERVAL_MINUTES)
    return times


def generate_id(prefix, length=16):
    """生成指定长度的ID"""
    random_part = ''.join(random.choices(string.digits, k=length-len(prefix)))
    return prefix + random_part
