#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
曲线数据生成模块
包含功率曲线和电压电流曲线的生成函数
"""

import random
from datetime import datetime
from utils import generate_id, get_unified_org_no
import math

def generate_table_1_15(time_series, meters, anomaly_records):
    """
    生成运行电能表功率曲线数据,与接线错误关联
    
    关键修改:
    1. 接线错误会影响功率符号和功率因数
    2. 接线错误不影响电压电流幅值
    3. 根据接线错误类型调整功率方向
    """
    data = []
    current_time = datetime.now()
    
    # 从数据异常清单中获取接线错误的信息
    wiring_errors = {}
    for anomaly in anomaly_records:
        if any(keyword in anomaly['DATA_ANOMALY_TYPE'] for keyword in ['接线', '电流反接', '错相', '相序']):
            time_str = anomaly['DATA_TIME']
            if time_str not in wiring_errors:
                wiring_errors[time_str] = []
            wiring_errors[time_str].append(anomaly['DATA_ANOMALY_TYPE'])
    
    for data_time in time_series:
        time_str = data_time.strftime('%Y-%m-%d %H:%M:%S')
        has_wiring_error = time_str in wiring_errors
        
        for meter in meters:
            # 根据是否为总表决定功率大小
            if meter['meter_type'] == 'total':
                power_base = random.uniform(50, 150)  # 总表功率较大
            else:
                power_base = random.uniform(1, 10)  # 分表功率较小
            
            # 默认正常情况:正功率因数,正功率
            tp_factor_a = round(random.uniform(0.85, 0.99), 3)
            tp_factor_b = round(random.uniform(0.85, 0.99), 3)
            tp_factor_c = round(random.uniform(0.85, 0.99), 3)
            tp_factor_total = round(random.uniform(0.85, 0.99), 3)
            
            # 正常的有功、无功、视在功率
            power_a = round(power_base * random.uniform(0.3, 0.35), 4)
            power_b = round(power_base * random.uniform(0.3, 0.35), 4)
            power_c = round(power_base * random.uniform(0.3, 0.35), 4)
            power_total = round(power_base, 4)
            
            rpower_a = round(power_base * random.uniform(0.2, 0.4), 4)
            rpower_b = round(power_base * random.uniform(0.2, 0.4), 4)
            rpower_c = round(power_base * random.uniform(0.2, 0.4), 4)
            rpower_total = round(power_base * random.uniform(0.6, 1.2), 4)
            
            apower_a = round(power_base * random.uniform(0.32, 0.37), 4)
            apower_b = round(power_base * random.uniform(0.32, 0.37), 4)
            apower_c = round(power_base * random.uniform(0.32, 0.37), 4)
            apower_total = round(power_base * random.uniform(1.0, 1.1), 4)
            
            # 如果这个时间点有接线错误,随机选择一些电表受影响
            if has_wiring_error and random.random() < 0.3:  # 30%的电表受影响
                error_type = random.choice(wiring_errors[time_str])
                
                if '单相电流反接' in error_type:
                    # 单相电流反接:该相有功和无功功率符号反转,功率因数为负
                    power_a = -abs(power_a)
                    rpower_a = -abs(rpower_a)
                    tp_factor_a = -abs(tp_factor_a)
                    # 总功率偏小
                    power_total = round(power_b + power_c + power_a, 4)
                    rpower_total = round(rpower_b + rpower_c + rpower_a, 4)
                    tp_factor_total = round(random.uniform(0.5, 0.75), 3)
                    
                elif '两相电流反接' in error_type:
                    # 两相电流反接:两相功率皆为负,总功率偏小
                    power_a = -abs(power_a)
                    power_b = -abs(power_b)
                    rpower_a = -abs(rpower_a)
                    rpower_b = -abs(rpower_b)
                    tp_factor_a = -abs(tp_factor_a)
                    tp_factor_b = -abs(tp_factor_b)
                    # 总功率明显偏小
                    power_total = round(power_a + power_b + power_c, 4)
                    rpower_total = round(rpower_a + rpower_b + rpower_c, 4)
                    tp_factor_total = round(random.uniform(0.2, 0.5), 3)
                    
                elif '三相电流全反' in error_type:
                    # 三相全反:全部功率为负,电表"倒走"
                    power_a = -abs(power_a)
                    power_b = -abs(power_b)
                    power_c = -abs(power_c)
                    rpower_a = -abs(rpower_a)
                    rpower_b = -abs(rpower_b)
                    rpower_c = -abs(rpower_c)
                    tp_factor_a = -abs(tp_factor_a)
                    tp_factor_b = -abs(tp_factor_b)
                    tp_factor_c = -abs(tp_factor_c)
                    # 总功率为负
                    power_total = round(power_a + power_b + power_c, 4)
                    rpower_total = round(rpower_a + rpower_b + rpower_c, 4)
                    tp_factor_total = -abs(tp_factor_total)
                    
                elif '电流错相接入' in error_type:
                    # 电流错相:功率因数异常波动,甚至大于1或为负,无功方向错乱
                    tp_factor_a = round(random.uniform(-0.5, 1.2), 3)
                    tp_factor_b = round(random.uniform(-0.5, 1.2), 3)
                    tp_factor_c = round(random.uniform(-0.5, 1.2), 3)
                    # 无功功率方向可能错乱
                    if random.random() < 0.5:
                        rpower_a = -abs(rpower_a)
                    if random.random() < 0.5:
                        rpower_b = -abs(rpower_b)
                    if random.random() < 0.5:
                        rpower_c = -abs(rpower_c)
                    # 总功率因数异常
                    tp_factor_total = round(random.uniform(-0.3, 1.15), 3)
                    rpower_total = round(rpower_a + rpower_b + rpower_c, 4)
                    
                elif '电压相序错误' in error_type:
                    # 电压相序错误:功率因数异常,无功功率方向错乱
                    tp_factor_a = round(random.uniform(-0.8, 0.3), 3)
                    tp_factor_b = round(random.uniform(-0.8, 0.3), 3)
                    tp_factor_c = round(random.uniform(-0.8, 0.3), 3)
                    # 无功功率方向错乱
                    if random.random() < 0.7:
                        rpower_a = -abs(rpower_a)
                    if random.random() < 0.7:
                        rpower_b = -abs(rpower_b)
                    if random.random() < 0.7:
                        rpower_c = -abs(rpower_c)
                    # 总功率因数可能为负
                    tp_factor_total = round(random.uniform(-0.6, 0.5), 3)
                    rpower_total = round(rpower_a + rpower_b + rpower_c, 4)
                    
                elif '混合错误' in error_type:
                    # 混合错误:功率值和功率因数无明显规律,数据跳变不稳
                    # 有功功率随机正负
                    if random.random() < 0.5:
                        power_a = -abs(power_a)
                    if random.random() < 0.5:
                        power_b = -abs(power_b)
                    if random.random() < 0.5:
                        power_c = -abs(power_c)
                    # 无功功率随机正负
                    if random.random() < 0.6:
                        rpower_a = -abs(rpower_a)
                    if random.random() < 0.6:
                        rpower_b = -abs(rpower_b)
                    if random.random() < 0.6:
                        rpower_c = -abs(rpower_c)
                    # 功率因数无规律跳变
                    tp_factor_a = round(random.uniform(-1.0, 1.2), 3)
                    tp_factor_b = round(random.uniform(-1.0, 1.2), 3)
                    tp_factor_c = round(random.uniform(-1.0, 1.2), 3)
                    # 总功率方向不稳
                    power_total = round(power_a + power_b + power_c, 4)
                    rpower_total = round(rpower_a + rpower_b + rpower_c, 4)
                    tp_factor_total = round(random.uniform(-0.9, 1.1), 3)
            
            row = {
                'RUN_METER_ID': meter['run_meter_id'],
                'DATA_TIME': time_str,
                'TP_FACTOR_A': str(tp_factor_a),
                'RPOWER_A': str(rpower_a),
                'POWER_A': str(power_a),
                'APOWER_A': str(apower_a),
                'TP_FACTOR_B': str(tp_factor_b),
                'RPOWER_B': str(rpower_b),
                'POWER_B': str(power_b),
                'APOWER_B': str(apower_b),
                'TP_FACTOR_C': str(tp_factor_c),
                'RPOWER_C': str(rpower_c),
                'POWER_C': str(power_c),
                'APOWER_C': str(apower_c),
                'LOAD_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'PREPOSITION_TIME': time_str,
                'TP_FACTOR': str(tp_factor_total),
                'RPOWER': str(rpower_total),
                'POWER': str(power_total),
                'APOWER': str(apower_total),
                'DATA_SOURCE_CODE': '1',  # 1-自动采集
                'CREATOR_ID': 'SYSTEM',
                'CREATE_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'MODIFIER_ID': 'SYSTEM',
                'UPDATE_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'DATA_FROM': 'AUTO_COLLECT',
                'AREA_CODE': '440000',
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'OPTIMISTIC_LOCK_VERSION': '1',
                'DELETE_FLAG': '1'  # 1-正常
            }
            data.append(row)
    
    return data

# 表13: MK_1_16_运行电能表电压电流曲线(修改版:不受接线错误影响)
def generate_table_1_16(time_series, meters, anomaly_records):
    """
    生成运行电能表电压电流曲线数据
    
    关键修改:
    1. 接线错误不影响电压、电流幅值的测量
    2. 电压电流始终保持正常范围
    3. 只有硬件故障或电网异常才会影响电压电流
    """
    data = []
    current_time = datetime.now()
    
    # 从数据异常清单中获取非接线错误的硬件/电网异常
    hardware_errors = {}
    for anomaly in anomaly_records:
        # 只关注可能影响电压电流测量的硬件异常,排除接线错误
        if any(keyword in anomaly['DATA_ANOMALY_TYPE'] for keyword in ['模块异常', '本体异常', '电源故障']) \
           and not any(kw in anomaly['DATA_ANOMALY_TYPE'] for kw in ['接线', '反接', '错相', '相序']):
            time_str = anomaly['DATA_TIME']
            if time_str not in hardware_errors:
                hardware_errors[time_str] = []
            hardware_errors[time_str].append(anomaly['DATA_ANOMALY_TYPE'])
    
    for data_time in time_series:
        time_str = data_time.strftime('%Y-%m-%d %H:%M:%S')
        has_hardware_error = time_str in hardware_errors
        
        for meter in meters:
            # 正常电压和电流(始终在合理范围内)
            voltage_base = 220.0
            current_base = random.uniform(1.0, 20.0) if meter['meter_type'] == 'sub' else random.uniform(20.0, 100.0)
            
            # 电压在正常范围波动(±5%)
            p_volt_a = voltage_base * random.uniform(0.95, 1.05)
            p_volt_b = voltage_base * random.uniform(0.95, 1.05)
            p_volt_c = voltage_base * random.uniform(0.95, 1.05)
            
            # 电流在正常范围波动
            p_curr_a = current_base * random.uniform(0.3, 0.35)
            p_curr_b = current_base * random.uniform(0.3, 0.35)
            p_curr_c = current_base * random.uniform(0.3, 0.35)
            
            # 只有在硬件故障时才可能影响测量值(非接线错误)
            if has_hardware_error and random.random() < 0.1:  # 10%概率受影响
                error_type = random.choice(hardware_errors[time_str])
                
                if '模块异常' in error_type or '本体异常' in error_type:
                    # 测量精度下降,但仍在合理范围
                    p_volt_a = voltage_base * random.uniform(0.90, 1.10)
                    p_volt_b = voltage_base * random.uniform(0.90, 1.10)
                    p_volt_c = voltage_base * random.uniform(0.90, 1.10)
                    p_curr_a = current_base * random.uniform(0.25, 0.40)
                    p_curr_b = current_base * random.uniform(0.25, 0.40)
                    p_curr_c = current_base * random.uniform(0.25, 0.40)
                elif '电源故障' in error_type:
                    # 电源不稳可能导致测量波动
                    p_volt_a = voltage_base * random.uniform(0.85, 1.15)
                    p_volt_b = voltage_base * random.uniform(0.85, 1.15)
                    p_volt_c = voltage_base * random.uniform(0.85, 1.15)
            
            # 零线电流根据三相电流计算
            zl_curr = abs(p_curr_a + p_curr_b + p_curr_c) * 0.1
            
            row = {
                'RUN_METER_ID': meter['run_meter_id'],
                'DATA_TIME': time_str,
                'P_VOLT_A': str(round(p_volt_a, 3)),
                'P_CURR_A': str(round(p_curr_a, 3)),
                'P_VOLT_B': str(round(p_volt_b, 3)),
                'P_CURR_B': str(round(p_curr_b, 3)),
                'P_VOLT_C': str(round(p_volt_c, 3)),
                'P_CURR_C': str(round(p_curr_c, 3)),
                'LOAD_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'PREPOSITION_TIME': time_str,
                'DATA_SOURCE_CODE': '1',
                'ZL_CURR': str(round(zl_curr, 3)),
                'CREATOR_ID': 'SYSTEM',
                'CREATE_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'MODIFIER_ID': 'SYSTEM',
                'UPDATE_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'DATA_FROM': 'AUTO_COLLECT',
                'AREA_CODE': '440000',
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'OPTIMISTIC_LOCK_VERSION': '1',
                'DELETE_FLAG': '1'
            }
            data.append(row)
    
    return data

# 写入CSV文件
