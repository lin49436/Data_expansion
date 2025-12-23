#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电能表数据生成脚本
生成12个表的虚拟数据,时间范围为2025-09-01到2025-09-07,每15分钟一条数据
修改说明:
1. 时间数据格式严格按照"yyyy-mm-dd HH:MM:SS"格式(注意HH为24小时制的大写)
2. 所有供电单位编号数据根据mk_sys_org_202409131555.csv文件的org_no列中编号制定
3. 修正接线错误逻辑,使其符合三相四线制电表实际测量特性
"""

import csv
import os
from datetime import datetime, timedelta
import random
import string
import math

# 配置参数
START_DATE = datetime(2025, 9, 1, 0, 0, 0)
END_DATE = datetime(2025, 9, 7, 23, 45, 0)
INTERVAL_MINUTES = 15
NUM_DISTRICTS = 1  # 台区数量
NUM_SUB_METERS = 35  # 每个台区的分表数量(不包括总表)
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs", "electric_meter_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
# 【修改1】统一供电单位编号 - 所有数据使用同一个供电单位编号
UNIFIED_SUPPLY_ORG_NO = '0501'  # 统一的供电单位编号

def get_unified_org_no():
    """返回统一的供电单位编号"""
    return UNIFIED_SUPPLY_ORG_NO


# 生成时间序列
def generate_time_series():
    """生成从开始到结束的时间序列,间隔15分钟"""
    times = []
    current = START_DATE
    while current <= END_DATE:
        times.append(current)
        current += timedelta(minutes=INTERVAL_MINUTES)
    return times

# 生成随机ID
def generate_id(prefix, length=16):
    """生成指定长度的ID"""
    random_part = ''.join(random.choices(string.digits, k=length-len(prefix)))
    return prefix + random_part

# 生成台区和电表信息
def generate_district_and_meters():
    """生成台区和电表的基础信息"""
    districts = []
    meters = []
    
    for i in range(NUM_DISTRICTS):
        district_no = f"TQ{i+1:04d}"
        district_name = f"台区{i+1}"
        district_addr = f"测试地址{i+1}号"
        
        districts.append({
            'ta_no': district_no,
            'ta_name': district_name,
            'ta_addr': district_addr,
            'ta_type': '1'  # 1-居民台区
        })
        
        # 生成总表
        total_meter = {
            'run_meter_id': generate_id(f'M{district_no}T', 16),
            'ta_no': district_no,
            'ma_auxil_table_signs': '1',  # 1-主表(总表)
            'meter_type': 'total'
        }
        meters.append(total_meter)
        
        # 生成分表
        for j in range(NUM_SUB_METERS):
            sub_meter = {
                'run_meter_id': generate_id(f'M{district_no}S{j+1:02d}', 16),
                'ta_no': district_no,
                'ma_auxil_table_signs': '0',  # 0-副表(分表)
                'meter_type': 'sub'
            }
            meters.append(sub_meter)
    
    return districts, meters

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

# 表1: MK_1_3运行电能表
def generate_table_1_3(meters):
    """生成运行电能表数据"""
    data = []
    current_time = datetime.now()
    
    for meter in meters:
        row = {
            'RUN_METER_ID': meter['run_meter_id'],
            'AREA_CODE': '440000',  # 广东省代码
            'LT_CHK_DATE': (current_time - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d %H:%M:%S'),
            'MA_AUXIL_TABLE_SIGNS': meter['ma_auxil_table_signs'],
            'PR_CODE': '1',  # 1-供电局
            'MANU_FLAG': '0',  # 0-否(非人工控制)
            'ED_BGN_TIME': None,
            'ED_RATIO': None,
            'ED_TYPE': None,
            'ED_END_TIME': None,
            'ED_AMT': None,
            'SUPPLY_ORG_CODE': get_unified_org_no(),
            'PF_THRESHHOLD': '100.00',
            'MADE_NO': f'MFG{random.randint(100000, 999999)}',
            'TIME_DIGIT_CODE': '6.2',
            'CREATE_TIME': (current_time - timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S'),
            'ARRIVE_BATCH': f'BATCH{random.randint(1000, 9999)}',
            'AGREE_TIP_PRC': str(round(random.uniform(0.8, 1.2), 4)),
            'AGREE_PEAK_PRC': str(round(random.uniform(0.6, 0.9), 4)),
            'AGREE_FLAT_PRC': str(round(random.uniform(0.4, 0.6), 4)),
            'AGREE_PRC': str(round(random.uniform(0.5, 0.7), 4)),
            'AGREE_VALLEY_PRC': str(round(random.uniform(0.2, 0.4), 4)),
            'PLANT_AREA': str(random.randint(50, 200)),
            'OLD_READ_NO': None,
            'PARAM_ID': generate_id('PARAM', 16),
            'REMARKS': '正常运行',
            'RP_NEED_AMT': '50.00',
            'INSTALL_POSITION': f'{meter["ta_no"]}台区内',
            'INSTALL_DATE': (current_time - timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d %H:%M:%S'),
            'SWITCH_FLAG': '1',  # 1-带开关
            'READ_ORDER': str(meters.index(meter) + 1),
            'OPERATED_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'DATA_PLAT_CHG_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'SUPER_CAPACIT_FLAG': '0',
            'DIRECT_COLLECT_SEND_FLAG': '1',
            'PREPAY_DEDUCT_FLAG': '0',
            'BAUD_RATE': '9600',
            'PHASE_CODE': str(random.randint(1, 3)),  # 1-A相, 2-B相, 3-C相
            'BOX_CABINET_POSITION_NO': str(meters.index(meter) + 1),
            'LAT': f'{random.uniform(22.0, 24.0):.6f}',
            'LNG': f'{random.uniform(113.0, 115.0):.6f}',
            'TOTAL_FACTOR': str(round(random.uniform(1.0, 10.0), 3)),
            'MARKET_PRJ_ID': generate_id('PRJ', 16),
            'METER_DIGITS_CODE': '6.2',
            'METER_BOX_CABINET_ID': generate_id('BOX', 16),
            'EQU_ID': generate_id('EQU', 16),
            'EQU_MAIN_PERSON_ID': generate_id('PER', 16),
            'CC_SWITCH_TYPE': 'TYPE_A',
            'ASSETS_NO': f'ASSET{random.randint(100000, 999999)}',
            'ROTATE_CYCLE': '8',  # 8年轮换周期
            'ROTATE_VAILD_DATE': None,
            'MAINTAIN_GROUP': '运维班组A',
            'OPER_COMM_PROTOCOL': 'DL/T645',
            'OPER_COMM_MODE': 'RS485',
            'OVERDRAFT_FLAG': '0',
            'OVERDRAFT_QUOTA': None,
            'COMM_ADDR1': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'COMM_ADDR2': None,
            'COMM_MODE_CODE': 'RS485',
            'COMM_PROTOCOL_CODE': 'DL/T645-2007',
            'AREA_SORT_CODE': '1',
            'PRESET_AMT': str(random.uniform(100, 500)),
            'WARN_THRESHOLD1': '100.00',
            'WARN_THRESHOLD2': '50.00',
            'WARN_THRESHOLD3': '20.00',
            # 'MANUFACTURER_NAME': random.choice(['国电南瑞', '许继电气', '长园深瑞', '科陆电子', '威胜集团', '海兴电力'])  # 【新增】生产厂家名称
        }
        data.append(row)
    

    return data

# 表2: MK_1_4_运行计量自动化终端
def generate_table_1_4(districts):
    """生成运行计量自动化终端数据 - 只生成一个终端记录"""
    data = []
    current_time = datetime.now()
    
    # 只为第一个台区生成一个终端
    district = districts[0]
    row = {
        'RUN_TERM_ID': generate_id('TERM', 16),
        'IP_ADDR': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
        'LT_CHK_DATE': (current_time - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d %H:%M:%S'),
        'UP_COMM_CODE': 'GPRS',
        'UP_PROTOCOL_CODE': 'DL/T645-2007',
        'UP_CHANNEL_1': 'CHANNEL_1',
        'UP_CHANNEL_2': 'CHANNEL_2',
        'DOWN_COMM_CODE': 'RS485',
        'DOWN_PROTOCOL_CODE': 'DL/T645-2007',
        'MAIN_COMM_MODE': 'GPRS',
        'MAIN_TERM_FLAG': '1',
        'MAIN_TERM_COMM_ADDR': f'{random.randint(1000000000, 9999999999)}',
        'SUPPLY_ORG_NO': get_unified_org_no(),
        'TIME_MP_FUNCTION_CODE': '1',
        'CREATE_TIME': (current_time - timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S'),
        'ARRIVE_BATCH': f'BATCH{random.randint(1000, 9999)}',
        'PARAM_ID': generate_id('PARAM', 16),
        'AREA_CODE': '440000',
        'SESERVE_COMM_MODE': 'GPRS',
        'SAFE_INTER_MODE': '1',
        'INSTALL_ADDR': district['ta_addr'],
        'INSTALL_DATE': (current_time - timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d %H:%M:%S'),
        'WIRE_MODE_CODE': '1',
        'OPERATED_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'DATA_PLAT_CHG_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'IS_INSTALL_BRANCH_EQU': '1',
        'FACTORY_ID': generate_id('FAC', 16),
        'ELEC_CUST_NO': f'CUST{random.randint(100000, 999999)}',
        'OFFLINE_FLAG': '0',
        'BOX_CABINET_POSITION_NO': '1',
        'LAT': f'{random.uniform(22.0, 24.0):.6f}',
        'TERM_USEAGE': '1',
        'LNG': f'{random.uniform(113.0, 115.0):.6f}',
        'TOTAL_FACTOR': str(round(random.uniform(1.0, 10.0), 3)),
        'MARKET_PRJ_ID': generate_id('PRJ', 16),
        'MARKET_PRJ_NO': f'PRJ{random.randint(100000, 999999)}',
        'METER_BOX_CABINET_ID': generate_id('BOX', 16),
        'METERING_POINT_NUMBER': f'MP{random.randint(100000, 999999)}',
        'EQU_ID': generate_id('EQU', 16),
        'EQU_MODEL_CODE': f'MODEL{random.randint(100, 999)}',
        'EQU_SORT_CODE': '1',
        'EQU_TYPE_CODE': '1',
        'EQU_MAIN_PERSON_ID': generate_id('PER', 16),
        'ASSETS_NO': f'ASSET{random.randint(100000, 999999)}',
        'CONVERTER1': 'RS485',
        'CONVERTER2': 'GPRS',
        'ROTATE_CYCLE': '8',
        'MAINTAIN_GROUP': '运维班组A',
        'RUN_UP_COMM_CODE': 'GPRS',
        'RUN_DOWN_COMM_CODE': 'RS485',
        'COMM_ADDR': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
        'COMM_ADDR2': None,
        'COMM_MODULA_TYPE_CODE': 'GPRS',
        'MANUFACTURER_NAME': random.choice(['国电南瑞', '许继电气', '长园深瑞', '科陆电子', '威胜集团', '海兴电力'])  # 生产厂家名称
    }
    data.append(row)
    
    return data

# 表3: MK_1_27历史故障清单
def generate_table_1_27(time_series, meters, terminals, hardware_data):
    """生成历史故障清单数据（手工录入数据）- 与终端数据联动"""
    data = []
    current_time = datetime.now()
    
    # 获取唯一终端信息
    terminal = terminals[0] if terminals else None
    
    # 【新增】从硬件状态表(1-31)创建EQU_ID到MANUFACTURER_NAME的映射
    equ_to_manufacturer = {}
    if hardware_data:
        for hw in hardware_data:
            equ_to_manufacturer[hw['EQU_ID']] = hw['MANUFACTURER_NAME']
    
    # 设置随机种子以保证数据一致性
    random.seed(42)
    
    # 为一些电表生成故障记录
    fault_meters = random.sample(meters, max(1, len(meters) // 5))  # 约20%的表有故障
    
    for meter in fault_meters:
        # 每个故障表生成1-3条故障记录
        num_faults = random.randint(1, 3)
        selected_times = random.sample(time_series, min(num_faults, len(time_series)))
        
        for data_time in selected_times:
            # 先生成风险因子(数值)
            risk_factor_value = round(random.uniform(0.0, 1.0), 2)
            
            # 根据风险因子值确定风险等级
            if risk_factor_value >= 0.80:
                risk_grade = '一级风险'  # 极高风险
            elif risk_factor_value >= 0.65:
                risk_grade = '二级风险'  # 高风险
            elif risk_factor_value >= 0.50:
                risk_grade = '三级风险'  # 中风险
            elif risk_factor_value >= 0.35:
                risk_grade = '四级风险'  # 低风险
            else:
                risk_grade = '五级风险'  # 极低风险
            
            # 故障状态相关字段
            box_rust = random.choice(['0', '1'])  # 0-正常 1-故障
            door_rust = random.choice(['0', '1'])
            door_lock = random.choice(['0', '1'])
            door_lock_damaged = random.choice(['0', '1'])
            incoming_damaged = random.choice(['0', '1'])
            incoming_burn = random.choice(['0', '1'])
            terminal_block_damaged = random.choice(['0', '1'])
            terminal_block_burn = random.choice(['0', '1'])
            wire_burn = random.choice(['0', '1'])
            damage_insulation = random.choice(['0', '1'])
            connector_oxidation = random.choice(['0', '1'])
            connector_damage = random.choice(['0', '1'])
            
            row = {
                # 原有字段
                'DATA_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'LOAD_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'CREATOR_ID': generate_id('USER', 16),
                'CREATE_TIME': (current_time - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                'MODIFIER_ID': generate_id('USER', 16),
                'UPDATE_TIME': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'DATA_FROM': '1',  # 1-手工录入
                'AREA_CODE': '440000',  # 广东省代码
                'TERMINAL_ID': terminal['ASSETS_NO'] if terminal else f'TERM{random.randint(100000, 999999)}',  # 【修改】使用终端资产编号
                'RUN_TERM_ID': terminal['RUN_TERM_ID'] if terminal else generate_id('RTERM', 16),  # 【修改】使用终端标识
                'COMM_ADDR': terminal['COMM_ADDR'] if terminal else f'{random.randint(1, 255)}',
                'REASON_SWITCH': random.choice(['设备故障', '通信故障', '计量异常', '参数错误', '定期轮换', '现场烧毁']),
                'MANUFACTURER_NAME': equ_to_manufacturer.get(terminal['EQU_ID'], '未知厂家') if terminal else '未知厂家',  # 从硬件状态表(1-31)获取
                'REASON_SWITCH_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                
                # 故障状态字段
                'THE_BOX_RUST': box_rust,
                'THE_DOOR_RUST': door_rust,
                'THE_DOOR_LOCK': door_lock,
                'DOOR_LOCK_DAMAGED': door_lock_damaged,
                'THE_INCOMING_DAMAGED': incoming_damaged,
                'THE_INCOMING_BURN': incoming_burn,
                'TERMINAL_BLOCK_DAMAGED': terminal_block_damaged,
                'TERMINAL_BLOCK_BURN': terminal_block_burn,
                'WIRE_BURN': wire_burn,
                'DAMAGE_INSULATION': damage_insulation,
                'CONNECTOR_OXIDATION': connector_oxidation,
                'CONNECTOR_DAMAGE': connector_damage,
                
                # 环境参数
                'SALT_MIST': str(round(random.uniform(0, 100), 2)),  # 盐雾浓度
                'TEMPERATURE': str(round(random.uniform(15, 40), 2)),  # 温度
                'HUMIDITY': str(round(random.uniform(30, 90), 2)),  # 湿度
                
                # 电表和终端相关
                'RUN_METER_ID': meter['run_meter_id'],
                'ELECTRICITY_ID': generate_id('ELEC', 16),
                'TERMINAL_STATUS': random.choice(['1', '2', '3']),  # 1-正常 2-异常 3-停运
                
                # 工单相关
                'WORD_ORDER_ID': generate_id('WO', 16),
                'WORD_ORDER_CATEGORY': random.choice(['故障处理', '设备更换', '例行维护', '应急抢修']),
                'DEVOPS_STATE': random.choice(['待处理', '处理中', '已完成', '已关闭']),
                'DEVOPS_SCHEME': random.choice(['现场检修', '更换设备', '软件升级', '参数调整']),
                
                # 计量点和风险相关
                'METERING_POINT_STATE': random.choice(['正常', '异常', '停运']),
                'RISK_TYPE': random.choice(['设备故障', '通信故障', '数据异常', '环境因素']),
                'RISK_GRADE': risk_grade,
                'RISK_FACTOR': str(risk_factor_value),
                
                # 新增字段 - 设备信息
                'equ_type': random.choice(['集中器', '采集器', '专变终端', '配变终端']),
                'terminal_type': random.choice(['I型', 'II型', 'III型']),
                'batch_to_which_it_belongs': f'BATCH{random.randint(2020, 2024)}{random.randint(1, 12):02d}',
                'communication_model': random.choice(['GPRS', '4G', '光纤', 'RS485', '载波']),
                'connection_method': random.choice(['直接接入', '经互感器接入']),
                'protocol_type': random.choice(['DL/T645-2007']),
                
                # 新增字段 - 计量点信息
                'measurement_point_number': terminal['METERING_POINT_NUMBER'] if terminal else f'MP{random.randint(100000, 999999)}',  # 【修改】使用终端计量点编号
                'measurement_point_category': random.choice(['居民', '一般工商业', '大工业', '农业']),
                'measurement_point_capacity': str(round(random.uniform(5, 1000), 2)),
                'wiring_method': random.choice(['三相四线', '三相三线', '单相']),
                
                # 新增字段 - 用户信息
                'user_id': f'USER{random.randint(100000, 999999)}',
                'user_name': f'用户{random.randint(1, 1000)}',
                'user_class': random.choice(['居民', '工商业', '大工业', '农业', '临时']),
                'user_address': f'测试地址{random.randint(1, 999)}号',
                
                # 新增字段 - 电表运行信息
                'running_state': random.choice(['运行', '异常', '停运', '待送电']),
                'install_date': (data_time - timedelta(days=random.randint(365, 2000))).strftime('%Y-%m-%d %H:%M:%S'),
                'nominal_voltage': None,
                'rated_current': None
            }
            data.append(row)
    
    # 恢复随机种子
    random.seed()
    
    return data

# 表4: MK_1_29_历史运维日志清单
def generate_table_1_29(time_series, meters, terminals):
    """生成历史运维日志清单数据 - 与终端数据联动"""
    data = []
    
    # 获取唯一终端信息
    terminal = terminals[0] if terminals else None
    
    # 每个表每天生成1-2条运维记录
    for meter in meters:
        num_records = random.randint(7, 14)  # 7天,每天1-2条
        selected_times = random.sample(time_series, min(num_records, len(time_series)))
        
        for data_time in selected_times:
            row = {
                'RUN_METER_ID': meter['run_meter_id'],
                'RUN_TERM_ID': terminal['RUN_TERM_ID'] if terminal else generate_id('RTERM', 16),  # 【修改】使用终端标识
                'REASON_SWITCH': random.choice(['正常巡检', '故障检修', '设备更换', '参数调整']),
                'REASON_SWITCH_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'DATA_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'OPERATION_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'OPERATION_CONTENT': random.choice(['抄表', '巡检', '维修', '更换', '校准']),
                'OPERATION_STAFF': f'运维人员{random.randint(1, 10)}',
                'OPERATION_DESCRIBE': random.choice(['设备运行正常', '发现轻微异常已处理', '更换配件', '参数调整完成']),
                'REASON_DESCRIBE': random.choice(['例行维护', '响应报警', '用户报修', '定期检查']),
                'EQU_SORT_CODE': '1',
                'EQU_TYPE_CODE': '1',
                'EQU_ID': generate_id('EQU', 16),
                'METERING_POINT_NUMBER': terminal['METERING_POINT_NUMBER'] if terminal else f'MP{random.randint(100000, 999999)}'  # 【修改】使用终端计量点编号
            }
            data.append(row)
    
    return data

# 表5: MK_1_30_风险等级清单
# 表5: MK_1_30_风险等级清单
def generate_table_1_30(time_series, meters, districts, terminals, hardware_data):
    """生成风险等级清单数据 - 关联到终端"""
    data = []
    
    # 为每个有风险的电表在时间序列中生成记录
    risk_meters = random.sample(meters, max(1, len(meters) // 10))  # 约10%的表有风险
    
    # 获取终端信息
    terminal = terminals[0] if terminals else None
    
    # 【新增】从硬件状态表(1-31)创建EQU_ID到MANUFACTURER_NAME的映射
    equ_to_manufacturer = {}
    if hardware_data:
        for hw in hardware_data:
            equ_to_manufacturer[hw['EQU_ID']] = hw['MANUFACTURER_NAME']
    
    for meter in risk_meters:
        district = next(d for d in districts if d['ta_no'] == meter['ta_no'])
        # 每个风险表在时间范围内选择几个时间点
        selected_times = random.sample(time_series, min(5, len(time_series)))
        
        for data_time in selected_times:
            # RISK字段是风险因子的数值
            risk_value = round(random.uniform(0.0, 1.0), 2)
            
            # 根据风险因子值确定风险等级
            if risk_value >= 0.80:
                risk_grade = '一级风险'  # 极高风险
            elif risk_value >= 0.65:
                risk_grade = '二级风险'  # 高风险
            elif risk_value >= 0.50:
                risk_grade = '三级风险'  # 中风险
            elif risk_value >= 0.35:
                risk_grade = '四级风险'  # 低风险
            else:
                risk_grade = '五级风险'  # 极低风险
            
            row = {
                'DATA_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'DATA_FROM': 'AUTO',
                'AREA_CODE': '440000',
                'TERMINAL_ID': terminal['ASSETS_NO'] if terminal else f'TERM{random.randint(100000, 999999)}',  # 使用终端资产编码
                'RUN_TERM_ID': terminal['RUN_TERM_ID'] if terminal else generate_id('RTERM', 16),  # 使用终端标识
                'COMM_ADDR': terminal['COMM_ADDR'] if terminal else f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',  # 使用终端通讯地址
                'REASON_SWITCH': random.choice(['设备老化', '通信异常', '数据异常', '正常']),
                'REASON_SWITCH_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'RUN_METER_ID': meter['run_meter_id'],
                'ELECTRICITY_ID': f'ELEC{random.randint(100000, 999999)}',
                'TERMINAL_STATUS': random.choice(['在线', '离线', '故障']),
                'METERING_POINT_STATE': random.choice(['正常', '异常', '停运']),
                'RISK_TYPE': random.choice(['设备风险', '通信风险', '数据风险', '运维风险']),
                'RISK_GRADE': risk_grade,
                'RISK_FACTOR': random.choice(['计量失准', '接线错误', '通信故障', '设备老化']),
                'RISK': str(risk_value),
                
                # 用户相关字段
                'user_name': f'用户{random.randint(1, 1000)}',
                'user_id': f'USER{random.randint(100000, 999999)}',
                'user_type': random.choice(['居民', '工商业', '大工业']),
                'user_addr': f'{meter["ta_no"]}台区',
                
                # 【修改3】基础风险因子字段
                'base_risk_MANUFACTURER': str(round(random.uniform(0.0, 1.0), 3)),
                'base_risk_BATCH': str(round(random.uniform(0.0, 1.0), 3)),
                'base_risk_LOAD': str(round(random.uniform(0.0, 1.0), 3)),
                'base_risk_data_security': str(round(random.uniform(0.0, 1.0), 3)),
                'base_risk_uncap_event': str(round(random.uniform(0.0, 1.0), 3)),
                
                # 增量基础因子 - 合并为一个字段
                'incr_risk': str(round(random.uniform(0.0, 0.5), 3)),
                
                # 生产厂家和批次
                'MANUFACTURER_NAME': equ_to_manufacturer.get(terminal['EQU_ID'], '未知厂家') if terminal else '未知厂家',  # 从硬件状态表(1-31)获取
                'ARRIVE_BATCH': terminal['ARRIVE_BATCH'] if terminal else f'BATCH{random.randint(1000, 9999)}'
            }
            
            data.append(row)
    
    return data

# 表6: MK_1_31_硬件状态
def generate_table_1_31(districts, terminals, meters):
    """生成硬件状态数据 - 关联到终端"""
    data = []
    
    # 为每个终端生成硬件状态数据
    for terminal in terminals:
        district = districts[0]  # 因为只有一个台区
        row = {
            'KEEPER_ID': generate_id('KEEP', 16),
            'TA_NO': district['ta_no'],
            'TA_NAME': district['ta_name'],
            'TA_ADDR': district['ta_addr'],
            'TA_TYPE': district['ta_type'],
            'EQU_ID': terminal['EQU_ID'],  # 使用终端的设备ID
            'ASSETS_NO': terminal['ASSETS_NO'],  # 使用终端的资产编号
            'DEVICE_TYPE': '终端',  # 【新增】设备类型
            'MANUFACTURER_NAME': terminal.get('MANUFACTURER_NAME', '国电南瑞'),
            'COMM_PROTOCOL_CODE': terminal.get('UP_PROTOCOL_CODE', 'DL/T645-2007'),
            'COMM_INTERFACE_MODE_CODE': terminal.get('DOWN_COMM_CODE', 'RS485'),
            'LOCAL_INTERFACE': random.choice(['正常', '异常']),
            'CPU_RATE': f'{random.randint(20, 80)}%',
            'MEMORY_RATE': f'{random.randint(30, 85)}%',
            'SYSTEM_NUMBER': f'V{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}',
            'SYSTEM_ROOT': random.choice(['正常', '异常']),
            # 'SYSTEM_PERMISSION': random.choice(['正常', '异常']),
            'IMPORTANT_DATA': random.choice(['已备份', '未备份']),
            'OPEN_PORT_LIST': f'{random.randint(1000, 9999)}',
            'NETWORK_COMMUNICATION_OBJECT': f'{random.randint(1, 100)}个',
            'REAL_TIME_SENDING_RATE': f'{random.randint(100, 1000)}Kbps',
            'REAL_TIME_RECEIVING_RAT': f'{random.randint(100, 1000)}Kbps',
            'TCP_RUNOFF': f'{random.randint(60, 95)}%',
            'UDP_PROPORTION': f'{random.randint(5, 30)}%',
            'BISINESS_PROPORTION': f'{random.randint(70, 95)}%',
            'DEDICACED_CHANNEL': random.choice(['启用', '禁用']),
            'DISABLE_CONNECTION': random.choice(['启用', '禁用'])
        }
        data.append(row)
    
    # 2. 为部分电能表生成硬件状态数据
    sample_meters = random.sample(meters, min(10, len(meters)))  # 选择部分电表
    for meter in sample_meters:
        district = districts[0]
        row = {
            'KEEPER_ID': generate_id('KEEP', 16),
            'TA_NO': district['ta_no'],
            'TA_NAME': district['ta_name'],
            'TA_ADDR': district['ta_addr'],
            'TA_TYPE': district['ta_type'],
            'EQU_ID': meter['run_meter_id'],  # 使用电表的ID作为设备ID
            'ASSETS_NO': f'ASSET_METER{random.randint(100000, 999999)}',  # 电表资产编号
            'DEVICE_TYPE': '电能表',  # 【新增】设备类型
            'MANUFACTURER_NAME': random.choice(['国电南瑞', '许继电气', '长园深瑞', '科陆电子', '威胜集团', '海兴电力']),
            'COMM_PROTOCOL_CODE': 'DL/T645-2007',
            'COMM_INTERFACE_MODE_CODE': 'RS485',
            'LOCAL_INTERFACE': random.choice(['正常', '异常']),
            'CPU_RATE': f'{random.randint(10, 50)}%',
            'MEMORY_RATE': f'{random.randint(20, 60)}%',
            'SYSTEM_NUMBER': f'V{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}',
            'SYSTEM_ROOT': '正常',
            # 'SYSTEM_PERMISSION': '正常',
            'IMPORTANT_DATA': '已备份',
            'OPEN_PORT_LIST': None,
            'NETWORK_COMMUNICATION_OBJECT': None,
            'REAL_TIME_SENDING_RATE': None,
            'REAL_TIME_RECEIVING_RAT': None,
            'TCP_RUNOFF': None,
            'UDP_PROPORTION': None,
            'BISINESS_PROPORTION': None,
            'DEDICACED_CHANNEL': None,
            'DISABLE_CONNECTION': None
        }
        data.append(row)
    

    # 2. 为部分电能表生成硬件状态数据
    sample_meters = random.sample(meters, min(10, len(meters)))  # 选择部分电表
    for meter in sample_meters:
        district = districts[0]
        row = {
            'KEEPER_ID': generate_id('KEEP', 16),
            'TA_NO': district['ta_no'],
            'TA_NAME': district['ta_name'],
            'TA_ADDR': district['ta_addr'],
            'TA_TYPE': district['ta_type'],
            'EQU_ID': meter['run_meter_id'],  # 使用电表的ID作为设备ID
            'ASSETS_NO': f'ASSET_METER{random.randint(100000, 999999)}',  # 电表资产编号
            'DEVICE_TYPE': '电能表',  # 【新增】设备类型
            'MANUFACTURER_NAME': random.choice(['国电南瑞', '许继电气', '长园深瑞', '科陆电子', '威胜集团', '海兴电力']),
            'COMM_PROTOCOL_CODE': 'DL/T645-2007',
            'COMM_INTERFACE_MODE_CODE': 'RS485',
            'LOCAL_INTERFACE': random.choice(['正常', '异常']),
            'CPU_RATE': f'{random.randint(10, 50)}%',
            'MEMORY_RATE': f'{random.randint(20, 60)}%',
            'SYSTEM_NUMBER': f'V{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}',
            'SYSTEM_ROOT': '正常',
            # 'SYSTEM_PERMISSION': '正常',
            'IMPORTANT_DATA': '已备份',
            'OPEN_PORT_LIST': None,
            'NETWORK_COMMUNICATION_OBJECT': None,
            'REAL_TIME_SENDING_RATE': None,
            'REAL_TIME_RECEIVING_RAT': None,
            'TCP_RUNOFF': None,
            'UDP_PROPORTION': None,
            'BISINESS_PROPORTION': None,
            'DEDICACED_CHANNEL': None,
            'DISABLE_CONNECTION': None
        }
        data.append(row)
    
    return data

# 表7: MK_1_32_数据异常清单
def generate_table_1_32(time_series):
    """生成数据异常清单数据(手工录入 增量数据上送)"""
    data = []
    
    # 所有异常类型
    all_anomaly_subtypes = []
    for main_type, subtypes in ANOMALY_TYPES.items():
        for subtype in subtypes:
            all_anomaly_subtypes.append((main_type, subtype))
    
    # 为每个时间点生成一些异常记录
    for data_time in time_series:
        # 每个时间点随机生成0-3条异常记录
        num_anomalies = random.randint(0, 3)
        selected_anomalies = random.sample(all_anomaly_subtypes, min(num_anomalies, len(all_anomaly_subtypes)))
        
        for main_type, sub_type in selected_anomalies:
            row = {
                'DATA_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'DATA_ANOMALY_TYPE': sub_type,  # 使用细分的异常类型
                'TABLES': random.choice(['源表', '业务表']),
                'TABLES_ENGLISH_NAME': random.choice([
                    'MK_1_15_运行电能表功率曲线',
                    'MK_1_16_运行电能表电压电流曲线',
                    'MK_RI_ABNORMAL_METER',
                    'MK_RI_UNSUCCESSFUL_METER'
                ]),
                'TABLES_CHINESE_NAME': random.choice(['功率曲线表', '电压电流表', '异常电表', '抄表失败表']),
                'NUMBER_OF': str(random.randint(1, 50))
            }
            data.append(row)
    
    return data

# 表8: MK_1_33计算异常清单
def generate_table_1_33(time_series):
    """生成计算异常清单数据"""
    data = []
    
    # 每个时间点有一定概率出现计算异常
    for data_time in time_series:
        if random.random() < 0.1:  # 10%的概率出现异常
            row = {
                'DATA_TIME': data_time.strftime('%Y-%m-%d %H:%M:%S'),
                'SUPPLY_ORG_NO': get_unified_org_no(),
                'RUNNING_STATE': random.choice(['运行中', '异常', '停止']),
                'CALCULATIN_TASK_NAME': random.choice(['线损计算', '负荷预测', '电量统计', '三相不平衡计算']),
                'CALCULATIN_ID': generate_id('CALC', 16),
                'ABNORMAL_TIME': data_time.strftime('%Y-%m-%d'),
                'ABNORMAL_CAUSE': random.choice(['数据缺失', '算法超时', '内存溢出', '参数错误']),
                'CALCULATIN_TIME': str(round(random.uniform(0.1, 24.0), 2))
            }
            data.append(row)
    
    return data

# 表9: MK_1_34_状态异常清单终端
# 表9: MK_1_34_状态异常清单终端
def generate_table_1_34(time_series, terminals):
    """
    生成终端异常清单数据,每个台区对应一个终端(集中器)
    参数:
    - time_series: 时间序列
    - terminals: 终端数据列表(来自表2)
    """
    data = []
    
    # 为每个终端在时间序列中生成异常记录
    for terminal in terminals:
        # 获取终端的固定信息
        terminal_asset_no = terminal['ASSETS_NO']
        terminal_run_term_id = terminal['RUN_TERM_ID']  # 使用RUN_TERM_ID
        terminal_addr = terminal['INSTALL_ADDR']
        
        # 每个终端有3%的概率在某个时间点出现异常(7天约20条异常记录)
        for data_time in time_series:
            if random.random() < 0.03:  # 3%的概率出现终端异常
                row = {
                    'SUPPLY_ORG_NO': terminal.get('SUPPLY_ORG_NO', get_unified_org_no()),
                    'RUN_TERM_ID': terminal_run_term_id,  # 终端标识
                    'ASSETS_NO': terminal_asset_no,  # 终端资产编号
                    'RUN_STATUS_CODE': random.choice(['离线', '故障', '异常']),  # 运行状态
                    'EXCEPTION_TYPE': random.choice(['通信中断', '数据上报失败', '设备无响应', '参数异常']),  # 异常类型
                    'TERM_TYPE_CODE': '集中器',  # 终端类型
                    'METERING_POINT_NUMBER': terminal['METERING_POINT_NUMBER'],  # 计量点编号
                    'ELEC_CUST_NO': terminal['ELEC_CUST_NO'],  # 用户编号
                    'CUST_TYPE_CODE': random.choice(['居民', '工商业', '大工业']),  # 用户类型
                    'ELEC_ADDR': terminal_addr,  # 用户地址
                    'ABNORMAL_DATE': data_time.strftime('%Y-%m-%d %H:%M:%S'),  # 异常日期
                    'ELEC_CUST_NAME': f'用户{random.randint(1, 1000)}'  # 用户名称
                }
                data.append(row)
    
    return data

# 表10: MK_1_35_状态异常清单电能表
# 表10: MK_1_35_状态异常清单电能表
def generate_table_ri_abnormal_meter(time_series, meters, anomaly_records, meter_master_data):
    """生成异常电表清单数据,与数据异常清单关联
    
    Args:
        time_series: 时间序列
        meters: 电表基础信息列表
        anomaly_records: 数据异常清单记录
        meter_master_data: 表1(MK_1_3)的完整数据,用于关联字段
    """
    data = []
    
    # 建立meter_id到表1数据的映射
    meter_master_map = {m['RUN_METER_ID']: m for m in meter_master_data}
    
    # 从数据异常清单中提取计量失准、接线错误、通信异常的信息
    anomaly_by_time = {}
    for anomaly in anomaly_records:
        time_str = anomaly['DATA_TIME']
        anomaly_type = anomaly['DATA_ANOMALY_TYPE']
        
        # 只处理与电表相关的异常(排除终端异常)
        if any(keyword in anomaly_type for keyword in ['计量失准', '接线', '电流反接', '错相', '相序', '通信']):
            if time_str not in anomaly_by_time:
                anomaly_by_time[time_str] = []
            anomaly_by_time[time_str].append(anomaly_type)
    
    # 为有异常的时间点生成异常电表记录
    for time_str, anomaly_types in anomaly_by_time.items():
        # 随机选择一些电表受影响
        affected_meters = random.sample(meters, min(random.randint(1, 5), len(meters)))
        
        for meter in affected_meters:
            meter_id = meter['run_meter_id']
            master_data = meter_master_map.get(meter_id, {})
            
            anomaly_type = random.choice(anomaly_types)
            row = {
                'SUPPLY_ORG_NO': master_data.get('SUPPLY_ORG_CODE', get_unified_org_no()),  # 供电单位
                'energy_meter_identification': meter_id,  # 运行电能表标识
                'asset_code_meter': master_data.get('ASSETS_NO', f'ASSET{random.randint(100000, 999999)}'),  # 电能表资产编码
                'EXCEPTION_TYPE': anomaly_type,  # 异常类型
                'running_state': random.choice(['运行', '异常', '停运']),  # 运行状态
                'measurement_point_number': f'MP{random.randint(100000, 999999)}',  # 计量点编号
                'user_id': f'USER{random.randint(100000, 999999)}',  # 用户编号
                'customer_type': random.choice(['居民', '工商业', '大工业']),  # 用户类型
                'user_address': master_data.get('INSTALL_POSITION', f'{meter["ta_no"]}台区'),  # 用户地址
                'abnormal_date': time_str,  # 异常日期
                'user_name': f'用户{random.randint(1, 1000)}'  # 用户名称
            }
            data.append(row)
    
    return data

# 表11: MK_RI_UNSUCCESSFUL_METER
# 表11: MK_RI_UNSUCCESSFUL_METER
def generate_table_ri_unsuccessful_meter(time_series, meters, anomaly_records, meter_master_data, terminals):
    """生成抄表失败清单数据,与通信异常关联,并与基础数据联动"""
    data = []
    
    # 建立meter_id到表1数据的映射
    meter_master_map = {m['RUN_METER_ID']: m for m in meter_master_data}
    
    # 获取终端信息
    terminal = terminals[0] if terminals else None
    
    # 从数据异常清单中提取通信异常的信息
    comm_errors = {}
    for anomaly in anomaly_records:
        if '通信' in anomaly['DATA_ANOMALY_TYPE'] or any(keyword in anomaly['DATA_ANOMALY_TYPE'] for keyword in ['4G', 'SIM', '集中器', '模块', '电表']):
            time_str = anomaly['DATA_TIME']
            if time_str not in comm_errors:
                comm_errors[time_str] = []
            comm_errors[time_str].append(anomaly['DATA_ANOMALY_TYPE'])
    
    # 为有通信异常的时间点生成抄表失败记录
    for time_str in comm_errors:
        # 随机选择一些电表抄表失败
        failed_meters = random.sample(meters, min(random.randint(1, 3), len(meters)))
        
        for meter in failed_meters:
            meter_id = meter['run_meter_id']
            master_data = meter_master_map.get(meter_id, {})
            
            row = {
                'SUPPLY_ORG_NO': get_unified_org_no(),  # 【修改】使用统一供电单位编号
                'data_time': time_str,  # 数据时间
                'EQU_ID': meter_id,  # 设备标识
                'ASSETS_NO': master_data.get('ASSETS_NO', f'ASSET{random.randint(100000, 999999)}'),  # 【修改】使用表1中的资产编号
                'RUN_STATUS_CODE': random.choice(['在线', '离线', '故障']),  # 设备运行状态
                'COMM_ADDR': master_data.get('COMM_ADDR1', f'{random.randint(1, 255)}'),  # 【修改】使用表1中的通讯地址
                'COMM_MODE': master_data.get('COMM_MODE_CODE', 'GPRS'),  # 【修改】使用表1中的通信方式
                'PROTOCOL_CODE': master_data.get('COMM_PROTOCOL_CODE', 'DL/T645-2007'),  # 【修改】使用表1中的规约类型
                'WIRE_MODE_CODE': random.choice(['三相四线', '三相三线', '单相']),  # 接线方式
                'meter_reading_status': '失败',  # 抄表状态
                # 'RUN_TERM_ID': terminal['RUN_TERM_ID'] if terminal else None,  # 【新增】终端标识
                # 'MANUFACTURER_NAME': master_data.get('MANUFACTURER_NAME', '国电南瑞')  # 【新增】生产厂家名称
            }
            data.append(row)
    
    return data

# 表12: MK_1_15_运行电能表功率曲线(修改版:与接线错误关联)
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
def write_csv(filename, data, headers, comments):
    """写入CSV文件,包含字段名(英文)和注释(中文)"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # 写入英文字段名
        writer.writeheader()
        
        # 写入中文注释
        comment_row = {header: comments.get(header, '') for header in headers}
        writer.writerow(comment_row)
        
        # 写入数据
        writer.writerows(data)
    
    print(f"已生成文件: {filename}, 记录数: {len(data)}")

# 主函数
def main():
    print("开始生成虚拟数据...")
    print(f"时间范围: {START_DATE} 至 {END_DATE}")
    print(f"时间间隔: {INTERVAL_MINUTES}分钟")
    print(f"台区数量: {NUM_DISTRICTS}")
    print(f"每台区分表数量: {NUM_SUB_METERS}")
    print(f"统一供电单位编号: {UNIFIED_SUPPLY_ORG_NO}")
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成时间序列
    time_series = generate_time_series()
    print(f"生成时间点数: {len(time_series)}")
    
    # 生成台区和电表信息
    districts, meters = generate_district_and_meters()
    print(f"生成台区数: {len(districts)}")
    print(f"生成电表数: {len(meters)} (其中总表 {NUM_DISTRICTS} 个, 分表 {NUM_DISTRICTS * NUM_SUB_METERS} 个)")
    
    # 表1: MK_1_3运行电能表
    print("\n生成表1: MK_1_3运行电能表...")
    data_1_3 = generate_table_1_3(meters)
    headers_1_3 = list(data_1_3[0].keys())
    comments_1_3 = {
        'RUN_METER_ID': '主键,运行电能表的唯一标识',
        'AREA_CODE': '用户所在的地区编码',
        'LT_CHK_DATE': '上次现场检验日期',
        'MA_AUXIL_TABLE_SIGNS': '主副表标志',
        'PR_CODE': '产权归属',
        'MANU_FLAG': '是否是人工控制',
        'ED_BGN_TIME': '代扣开始时间',
        'ED_RATIO': '代扣比例',
        'ED_TYPE': '代扣类型',
        'ED_END_TIME': '代扣结束时间',
        'ED_AMT': '代扣金额',
        'SUPPLY_ORG_CODE': '供电单位编码',
        'PF_THRESHHOLD': '停电阀值',
        'MADE_NO': '电能表出厂编号',
        'TIME_DIGIT_CODE': '分时位数',
        'CREATE_TIME': '数据创建时间',
        'ARRIVE_BATCH': '到货批次号',
        'AGREE_TIP_PRC': '协议尖电价',
        'AGREE_PEAK_PRC': '协议峰电价',
        'AGREE_FLAT_PRC': '协议平电价',
        'AGREE_PRC': '协议电价',
        'AGREE_VALLEY_PRC': '协议谷电价',
        'PLANT_AREA': '面积',
        'OLD_READ_NO': '原抄表号',
        'PARAM_ID': '参数标识',
        'REMARKS': '备注',
        'RP_NEED_AMT': '复电允许金额',
        'INSTALL_POSITION': '电能表安装的物理位置',
        'INSTALL_DATE': '安装日期',
        'SWITCH_FLAG': '是否带开关',
        'READ_ORDER': '抄表顺序号',
        'OPERATED_TIME': '数据最近一次变更时间',
        'DATA_PLAT_CHG_TIME': '数据资源管理平台变更时间',
        'SUPER_CAPACIT_FLAG': '是否安装超级电容',
        'DIRECT_COLLECT_SEND_FLAG': '是否实现直采直送',
        'PREPAY_DEDUCT_FLAG': '本条记录是否开通预付费代扣',
        'BAUD_RATE': '电能表的波特率',
        'PHASE_CODE': '相位',
        'BOX_CABINET_POSITION_NO': '箱(柜)内位置号',
        'LAT': '纬度',
        'LNG': '经度',
        'TOTAL_FACTOR': '电能表综合倍率',
        'MARKET_PRJ_ID': '营销项目标识',
        'METER_DIGITS_CODE': '表码位数',
        'METER_BOX_CABINET_ID': '表箱(柜)设备唯一标识',
        'EQU_ID': '电能计量设备唯一标识',
        'EQU_MAIN_PERSON_ID': '设备运维主人标识',
        'CC_SWITCH_TYPE': '费控开关型号',
        'ASSETS_NO': '电能表资产编号(条形码)',
        'ROTATE_CYCLE': '轮换周期',
        'ROTATE_VAILD_DATE': '轮换有效日期',
        'MAINTAIN_GROUP': '运维班组',
        'OPER_COMM_PROTOCOL': '运行通信协议',
        'OPER_COMM_MODE': '运行通信方式',
        'OVERDRAFT_FLAG': '是否允许透支标志',
        'OVERDRAFT_QUOTA': '透支限额',
        'COMM_ADDR1': '通讯地址1',
        'COMM_ADDR2': '通讯地址2',
        'COMM_MODE_CODE': '通讯方式',
        'COMM_PROTOCOL_CODE': '通讯规约',
        'AREA_SORT_CODE': '面积类型代码',
        'PRESET_AMT': '预置电费金额',
        'WARN_THRESHOLD1': '预警阀值1',
        'WARN_THRESHOLD2': '预警阀值2',
        'WARN_THRESHOLD3': '预警阀值3',
        'MANUFACTURER_NAME': '生产厂家名称'
    }
    write_csv('MK_1_3运行电能表.csv', data_1_3, headers_1_3, comments_1_3)
    
    # 表2: MK_1_4_运行计量自动化终端
    print("\n生成表2: MK_1_4_运行计量自动化终端...")
    data_1_4 = generate_table_1_4(districts)
    headers_1_4 = list(data_1_4[0].keys())
    comments_1_4 = {
        'RUN_TERM_ID': '运行计量自动化终端标识',
        'IP_ADDR': 'IP地址',
        'LT_CHK_DATE': '上次检验日期',
        'UP_COMM_CODE': '上行通讯方式代码',
        'UP_PROTOCOL_CODE': '上行通讯规约代码',
        'UP_CHANNEL_1': '上行通道1',
        'UP_CHANNEL_2': '上行通道2',
        'DOWN_COMM_CODE': '下行通讯方式代码',
        'DOWN_PROTOCOL_CODE': '下行通讯规约代码',
        'MAIN_COMM_MODE': '主用通信方式',
        'MAIN_TERM_FLAG': '主终端标志',
        'MAIN_TERM_COMM_ADDR': '主终端通信地址',
        'SUPPLY_ORG_NO': '供电单位编码',
        'TIME_MP_FUNCTION_CODE': '分时计量功能代码',
        'CREATE_TIME': '创建时间',
        'ARRIVE_BATCH': '到货批次',
        'PARAM_ID': '参数标识',
        'AREA_CODE': '地区编码',
        'SESERVE_COMM_MODE': '备用通信方式',
        'SAFE_INTER_MODE': '安全接入方式',
        'INSTALL_ADDR': '安装地址',
        'INSTALL_DATE': '安装日期',
        'WIRE_MODE_CODE': '接线方式代码',
        'OPERATED_TIME': '数据最近一次变更时间',
        'DATA_PLAT_CHG_TIME': '数据资源管理平台变更时间',
        'IS_INSTALL_BRANCH_EQU': '是否安装分支设备',
        'FACTORY_ID': '厂家标识',
        'ELEC_CUST_NO': '用电客户号',
        'OFFLINE_FLAG': '离线标志',
        'BOX_CABINET_POSITION_NO': '箱(柜)内位置号',
        'LAT': '纬度',
        'TERM_USEAGE': '终端用途',
        'LNG': '经度',
        'TOTAL_FACTOR': '综合倍率',
        'MARKET_PRJ_ID': '营销项目标识',
        'MARKET_PRJ_NO': '营销项目编号',
        'METER_BOX_CABINET_ID': '表箱(柜)设备唯一标识',
        'METERING_POINT_NUMBER': '计量点编号',
        'EQU_ID': '电能计量设备唯一标识',
        'EQU_MODEL_CODE': '设备型号代码',
        'EQU_SORT_CODE': '设备类别代码',
        'EQU_TYPE_CODE': '设备类型代码',
        'EQU_MAIN_PERSON_ID': '设备运维主人标识',
        'ASSETS_NO': '资产编号',
        'CONVERTER1': '转换器1',
        'CONVERTER2': '转换器2',
        'ROTATE_CYCLE': '轮换周期',
        'MAINTAIN_GROUP': '运维班组',
        'RUN_UP_COMM_CODE': '运行上行通信代码',
        'RUN_DOWN_COMM_CODE': '运行下行通信代码',
        'COMM_ADDR': '通讯地址',
        'COMM_ADDR2': '通讯地址2',
        'COMM_MODULA_TYPE_CODE': '通信模块类型代码',
        'MANUFACTURER_NAME': '生产厂家名称'
    }
    write_csv('MK_1_4_运行计量自动化终端.csv', data_1_4, headers_1_4, comments_1_4)
    
    # 表6: MK_1_31_硬件状态（需要先生成，因为1-27和1-30依赖它）
    print("\n生成表6: MK_1_31_硬件状态...")
    data_1_31 = generate_table_1_31(districts, data_1_4, meters)  # 传入终端数据
    headers_1_31 = list(data_1_31[0].keys())
    comments_1_31 = {
        'KEEPER_ID': 'SIM卡的当前持有人的唯一标识',
        'TA_NO': '台区编号',
        'TA_NAME': '台区名称',
        'TA_ADDR': '台区地址',
        'TA_TYPE': '台区类型',
        'EQU_ID': '电能计量设备唯一标识',
        'ASSETS_NO': '资产编号',
        'DEVICE_TYPE': '设备类型(终端/电能表)',
        'MANUFACTURER_NAME': '生产厂商名称',
        'COMM_PROTOCOL_CODE': '通讯规约',
        'COMM_INTERFACE_MODE_CODE': '通信接口方式',
        'LOCAL_INTERFACE': '本地接口状态',
        'CPU_RATE': 'CPU占用率',
        'MEMORY_RATE': '内存占用率',
        'SYSTEM_NUMBER': '系统版本号',
        'SYSTEM_ROOT': '系统ROOT',
        # 'SYSTEM_PERMISSION': '系统文件权限',
        'IMPORTANT_DATA': '重要数据备份',
        'OPEN_PORT_LIST': '开启端口列表',
        'NETWORK_COMMUNICATION_OBJECT': '网络通信对象',
        'REAL_TIME_SENDING_RATE': '实时发送速率',
        'REAL_TIME_RECEIVING_RAT': '实时接收速率',
        'TCP_RUNOFF': 'TCP流量占比',
        'UDP_PROPORTION': 'UDP流量占比',
        'BISINESS_PROPORTION': '业务流量占比',
        'DEDICACED_CHANNEL': '专用网络通道',
        'DISABLE_CONNECTION': '禁用网络自连'
    }
    write_csv('MK_1_31_硬件状态.csv', data_1_31, headers_1_31, comments_1_31)

    
    # 表3: MK_1_27历史故障清单
    print("\n生成表3: MK_1_27历史故障清单...")
    data_1_27 = generate_table_1_27(time_series, meters, data_1_4, data_1_31)
    headers_1_27 = list(data_1_27[0].keys()) if data_1_27 else ['RUN_METER_ID', 'RUN_TERM_ID', 'REASON_SWITCH', 'REASON_SWITCH_TIME', 'SUPPLY_ORG_NO', 'DATA_TIME', 'WORD_ORDER_CATEGORY', 'DEVOPS_STATE', 'DEVOPS_SCHEME', 'METERING_POINT_STATE', 'RISK_TYPE', 'RISK_GRADE', 'RISK_FACTOR']
    comments_1_27 = {
        'DATA_TIME': '数据时间',
        'SUPPLY_ORG_NO': '供电单位编码',
        'LOAD_TIME': '入库时间',
        'CREATOR_ID': '创建人ID',
        'CREATE_TIME': '创建时间',
        'MODIFIER_ID': '修改人ID',
        'UPDATE_TIME': '更新时间',
        'DATA_FROM': '数据来源',
        'AREA_CODE': '地区编码',
        'TERMINAL_ID': '终端资产编码',
        'RUN_TERM_ID': '终端标识',
        'COMM_ADDR': '终端逻辑地址',
        'REASON_SWITCH': '换表原因',
        'MANUFACTURER_NAME': '生产厂家',
        'REASON_SWITCH_TIME': '换表日期',
        'THE_BOX_RUST': '箱体锈蚀腐烂',
        'THE_DOOR_RUST': '箱门锈蚀腐烂',
        'THE_DOOR_LOCK': '门锁无法打开',
        'DOOR_LOCK_DAMAGED': '门锁损坏',
        'THE_INCOMING_DAMAGED': '进出线开关破损',
        'THE_INCOMING_BURN': '进出线开关烧毁',
        'TERMINAL_BLOCK_DAMAGED': '接线端子损坏',
        'TERMINAL_BLOCK_BURN': '接线端子烧毁',
        'WIRE_BURN': '导线烧毁',
        'DAMAGE_INSULATION': '导线绝缘破损',
        'CONNECTOR_OXIDATION': '接插件氧化',
        'CONNECTOR_DAMAGE': '接插件损坏',
        'SALT_MIST': '盐雾',
        'TEMPERATURE': '温度',
        'HUMIDITY': '湿度',
        'RUN_METER_ID': '运行电表标识',
        'ELECTRICITY_ID': '电表资产编码',
        'TERMINAL_STATUS': '终端运行状态',
        'WORD_ORDER_ID': '工单编号',
        'WORD_ORDER_CATEGORY': '工单类别',
        'DEVOPS_STATE': '运维状态',
        'DEVOPS_SCHEME': '运维方案',
        'METERING_POINT_STATE': '计量点运行状态',
        'RISK_TYPE': '风险类型',
        'RISK_GRADE': '风险等级',
        'RISK_FACTOR': '风险因子',
        'equ_type': '设备类型',
        'terminal_type': '终端类型',
        'batch_to_which_it_belongs': '所属批次',
        'communication_model': '通信方式',
        'connection_method': '接线方式',
        'protocol_type': '规约类型',
        'measurement_point_number': '计量点编号',
        'measurement_point_category': '计量点类别',
        'measurement_point_capacity': '计量点容量',
        'wiring_method': '计量点接线方式',
        'user_id': '用户编号',
        'user_name': '用户名称',
        'user_class': '用户类别',
        'user_address': '用户地址',
        'running_state': '电能表运行状态',
        'install_date': '安装日期',
        'nominal_voltage': '额定电压',
        'rated_current': '额定电流'
    }
    write_csv('MK_1_27历史故障清单.csv', data_1_27, headers_1_27, comments_1_27)
    
    # 表4: MK_1_29_历史运维日志清单
    print("\n生成表4: MK_1_29_历史运维日志清单...")
    data_1_29 = generate_table_1_29(time_series, meters, data_1_4)
    headers_1_29 = list(data_1_29[0].keys())
    comments_1_29 = {
        'RUN_METER_ID': '主键,运行电能表标识',
        'RUN_TERM_ID': '运行终端标识',
        'REASON_SWITCH': '切换原因',
        'REASON_SWITCH_TIME': '切换原因时间',
        'SUPPLY_ORG_NO': '供电单位编号',
        'DATA_TIME': '数据时间',
        'OPERATION_TIME': '操作时间',
        'OPERATION_CONTENT': '操作内容',
        'OPERATION_STAFF': '操作人员',
        'OPERATION_DESCRIBE': '操作描述',
        'REASON_DESCRIBE': '原因描述',
        'EQU_SORT_CODE': '设备类别代码',
        'EQU_TYPE_CODE': '设备类型代码',
        'EQU_ID': '电能计量设备唯一标识',
        'METERING_POINT_NUMBER': '计量点编号'
    }
    write_csv('MK_1_29_历史运维日志清单.csv', data_1_29, headers_1_29, comments_1_29)
    
    # 表7: MK_1_32_数据异常清单(需要先生成,因为其他表依赖它)
    print("\n生成表7: MK_1_32_数据异常清单...")
    data_1_32 = generate_table_1_32(time_series)
    headers_1_32 = list(data_1_32[0].keys()) if data_1_32 else ['DATA_TIME', 'SUPPLY_ORG_NO', 'DATA_ANOMALY_TYPE', 'TABLES', 'TABLES_ENGLISH_NAME', 'TABLES_CHINESE_NAME', 'NUMBER_OF']
    comments_1_32 = {
        'DATA_TIME': '主键,数据时间',
        'SUPPLY_ORG_NO': '主键,供电单位编码',
        'DATA_ANOMALY_TYPE': '数据异常类型',
        'TABLES': '表格类型',
        'TABLES_ENGLISH_NAME': '表英文名称',
        'TABLES_CHINESE_NAME': '表中文名称',
        'NUMBER_OF': '异常条数'
    }
    write_csv('MK_1_32_数据异常清单_手工录入_增量数据上送.csv', data_1_32, headers_1_32, comments_1_32)
    
    # 表5: MK_1_30_风险等级清单
    print("\n生成表5: MK_1_30_风险等级清单...")
    data_1_30 = generate_table_1_30(time_series, meters, districts, data_1_4, data_1_31)  # 传入终端数据和硬件数据
    
    # 备用表头,防止数据为空时无法获取keys
    fallback_headers_1_30 = [
        'DATA_TIME', 'SUPPLY_ORG_NO', 'DATA_FROM', 'AREA_CODE', 'TERMINAL_ID', 
        'RUN_TERM_ID', 'COMM_ADDR', 'REASON_SWITCH', 'REASON_SWITCH_TIME', 
        'RUN_METER_ID', 'ELECTRICITY_ID', 'TERMINAL_STATUS', 'METERING_POINT_STATE', 
        'RISK_TYPE', 'RISK_GRADE', 'RISK_FACTOR', 'RISK',
        'user_name', 'user_id', 'user_type', 'user_addr', 
        'base_risk_MANUFACTURER', 'base_risk_BATCH', 'base_risk_LOAD', 
        'base_risk_data_security', 'base_risk_uncap_event'
    ]
    for i in range(1, 11):
        fallback_headers_1_30.append(f'inc_risk_{i}')
        
    headers_1_30 = list(data_1_30[0].keys()) if data_1_30 else fallback_headers_1_30
    
    comments_1_30 = {
        'DATA_TIME': '主键,数据时间',
        'SUPPLY_ORG_NO': '供电单位编号',
        'DATA_FROM': '数据来源',
        'AREA_CODE': '地区编码',
        'TERMINAL_ID': '终端标识',
        'RUN_TERM_ID': '运行终端标识',
        'COMM_ADDR': '通讯地址',
        'REASON_SWITCH': '切换原因',
        'REASON_SWITCH_TIME': '切换原因时间',
        'RUN_METER_ID': '运行电能表标识',
        'ELECTRICITY_ID': '用电标识',
        'TERMINAL_STATUS': '终端状态',
        'METERING_POINT_STATE': '计量点状态',
        'RISK_TYPE': '风险类型',
        'RISK_GRADE': '风险等级',
        'RISK_FACTOR': '风险因子',
        'RISK': '风险系数',
        
        # --- 新增注释 ---
        'user_name': '用户名称',
        'user_id': '用户编号',
        'user_type': '用户类型',
        'user_addr': '用户地址',
        'base_risk_MANUFACTURER': '电能表厂家贡献度',
        'base_risk_BATCH': '电能表批次贡献度',
        'base_risk_LOAD': '负荷水平贡献度',
        'base_risk_data_security': '数据安全贡献度',
        'base_risk_uncap_event': '开盖事件记录贡献度',
        
        # 增量基础因子注释
        'incr_risk': '增量基础因子',
        
        # 生产厂家和批次注释
        'MANUFACTURER_NAME': '生产厂家名称',
        'ARRIVE_BATCH': '所属批次'
    }
    
    write_csv('MK_1_30_风险等级清单_手动录入.csv', data_1_30, headers_1_30, comments_1_30)
    
    # 表8: MK_1_33计算异常清单
    print("\n生成表8: MK_1_33计算异常清单...")
    data_1_33 = generate_table_1_33(time_series)
    headers_1_33 = list(data_1_33[0].keys()) if data_1_33 else ['DATA_TIME', 'SUPPLY_ORG_NO', 'RUNNING_STATE', 'CALCULATIN_TASK_NAME', 'CALCULATIN_ID', 'ABNORMAL_TIME', 'ABNORMAL_CAUSE', 'CALCULATIN_TIME']
    comments_1_33 = {
        'DATA_TIME': '主键,数据时间',
        'SUPPLY_ORG_NO': '主键,供电单位编码',
        'RUNNING_STATE': '运行状态',
        'CALCULATIN_TASK_NAME': '计算任务名称',
        'CALCULATIN_ID': '计算任务ID',
        'ABNORMAL_TIME': '异常时间',
        'ABNORMAL_CAUSE': '异常原因',
        'CALCULATIN_TIME': '计算时长(按天累计)(H)'
    }
    write_csv('MK_1_33计算异常清单_手工录入_增量数据上送.csv', data_1_33, headers_1_33, comments_1_33)
    
   # 表9: MK_1_34_状态异常清单终端
    print("\n生成表9: MK_1_34_状态异常清单终端...")
    data_1_34 = generate_table_1_34(time_series, data_1_4)  # 传入终端数据
    headers_1_34 = list(data_1_34[0].keys()) if data_1_34 else ['SUPPLY_ORG_NO', 'RUN_TERM_ID', 'ASSETS_NO', 'RUN_STATUS_CODE', 'EXCEPTION_TYPE', 'TERM_TYPE_CODE', 'METERING_POINT_NUMBER', 'ELEC_CUST_NO', 'CUST_TYPE_CODE', 'ELEC_ADDR', 'ABNORMAL_DATE', 'ELEC_CUST_NAME']
    comments_1_34 = {
        'SUPPLY_ORG_NO': '供电单位',
        'RUN_TERM_ID': '终端标识',
        'ASSETS_NO': '终端资产编号',
        'RUN_STATUS_CODE': '运行状态',
        'EXCEPTION_TYPE': '异常类型',
        'TERM_TYPE_CODE': '终端类型',
        'METERING_POINT_NUMBER': '计量点编号',
        'ELEC_CUST_NO': '用户编号',
        'CUST_TYPE_CODE': '用户类型',
        'ELEC_ADDR': '用户地址',
        'ABNORMAL_DATE': '异常日期',
        'ELEC_CUST_NAME': '用户名称'
    }
    write_csv('MK_1_34_状态异常清单终端.csv', data_1_34, headers_1_34, comments_1_34)
    
    # 表10: MK_1_35_状态异常清单电能表(需要关联数据异常清单)
    print("\n生成表10: MK_1_35_状态异常清单电能表...")
    data_1_35 = generate_table_ri_abnormal_meter(time_series, meters, data_1_32, data_1_3)
    headers_1_35 = list(data_1_35[0].keys()) if data_1_35 else ['SUPPLY_ORG_NO', 'energy_meter_identification', 'asset_code_meter', 'EXCEPTION_TYPE', 'running_state', 'measurement_point_number', 'user_id', 'customer_type', 'user_address', 'abnormal_date', 'user_name']
    comments_1_35 = {
        'SUPPLY_ORG_NO': '供电单位',
        'energy_meter_identification': '运行电能表标识',
        'asset_code_meter': '电能表资产编码',
        'EXCEPTION_TYPE': '异常类型',
        'running_state': '运行状态',
        'measurement_point_number': '计量点编号',
        'user_id': '用户编号',
        'customer_type': '用户类型',
        'user_address': '用户地址',
        'abnormal_date': '异常日期',
        'user_name': '用户名称'
    }
    write_csv('MK_1_35_状态异常清单电能表.csv', data_1_35, headers_1_35, comments_1_35)
    
    # 表11: MK_RI_UNSUCCESSFUL_METER(需要关联通信异常)
    print("\n生成表11: MK_1_36_抄表不成功清单...")
    data_ri_um = generate_table_ri_unsuccessful_meter(time_series, meters, data_1_32, data_1_3, data_1_4)
    headers_ri_um = list(data_ri_um[0].keys()) if data_ri_um else ['SUPPLY_ORG_NO', 'data_time', 'EQU_ID', 'ASSETS_NO', 'RUN_STATUS_CODE', 'COMM_ADDR', 'COMM_MODE', 'PROTOCOL_CODE', 'WIRE_MODE_CODE', 'meter_reading_status']
    comments_ri_um = {
        'SUPPLY_ORG_NO': '供电单位',
        'data_time': '数据时间',
        'EQU_ID': '设备标识',
        'ASSETS_NO': '设备资产编码',
        'RUN_STATUS_CODE': '设备运行状态',
        'COMM_ADDR': '设备逻辑地址',
        'COMM_MODE': '通信方式',
        'PROTOCOL_CODE': '规约类型',
        'WIRE_MODE_CODE': '接线方式',
        'meter_reading_status': '抄表状态',
        'RUN_TERM_ID': '终端标识',
        'MANUFACTURER_NAME': '生产厂家名称'
    }
    write_csv('MK_1_36_抄表不成功清单.csv', data_ri_um, headers_ri_um, comments_ri_um)
    
    # 表12: MK_1_15_运行电能表功率曲线
    print("\n生成表12: MK_1_15_运行电能表功率曲线...")
    data_1_15 = generate_table_1_15(time_series, meters, data_1_32)
    headers_1_15 = list(data_1_15[0].keys())
    comments_1_15 = {
        'RUN_METER_ID': '主键。运行电能表的唯一标识',
        'DATA_TIME': '主键。数据时间',
        'TP_FACTOR_A': 'A相功率因数',
        'RPOWER_A': 'A相无功功率',
        'POWER_A': 'A相有功功率',
        'APOWER_A': 'A相视在功率',
        'TP_FACTOR_B': 'B相功率因数',
        'RPOWER_B': 'B相无功功率',
        'POWER_B': 'B相有功功率',
        'APOWER_B': 'B相视在功率',
        'TP_FACTOR_C': 'C相功率因数',
        'RPOWER_C': 'C相无功功率',
        'POWER_C': 'C相有功功率',
        'APOWER_C': 'C相视在功率',
        'LOAD_TIME': '数据入库时间',
        'PREPOSITION_TIME': '安全接入区前置接收到报文数据的时间',
        'TP_FACTOR': '总功率因数',
        'RPOWER': '总无功功率',
        'POWER': '总有功功率',
        'APOWER': '总视在功率',
        'DATA_SOURCE_CODE': '数据采集方式',
        'CREATOR_ID': '记录数据创建人',
        'CREATE_TIME': '创建时间',
        'MODIFIER_ID': '修改人',
        'UPDATE_TIME': '数据修改时间',
        'DATA_FROM': '用于数据迁移标识',
        'AREA_CODE': '区分分省数据',
        'SUPPLY_ORG_NO': '区分地市局',
        'OPTIMISTIC_LOCK_VERSION': '用于控制并发脏数据',
        'DELETE_FLAG': '数据逻辑删除'
    }
    write_csv('MK_1_15_运行电能表功率曲线.csv', data_1_15, headers_1_15, comments_1_15)
    
    # 表13: MK_1_16_运行电能表电压电流曲线
    print("\n生成表13: MK_1_16_运行电能表电压电流曲线...")
    data_1_16 = generate_table_1_16(time_series, meters, data_1_32)
    headers_1_16 = list(data_1_16[0].keys())
    comments_1_16 = {
        'RUN_METER_ID': '主键。运行电能表的唯一标识',
        'DATA_TIME': '主键。数据时间',
        'P_VOLT_A': 'A相电压',
        'P_CURR_A': 'A相电流',
        'P_VOLT_B': 'B相电压',
        'P_CURR_B': 'B相电流',
        'P_VOLT_C': 'C相电压',
        'P_CURR_C': 'C相电流',
        'LOAD_TIME': '数据入库时间',
        'PREPOSITION_TIME': '安全接入区前置接收到报文数据的时间',
        'DATA_SOURCE_CODE': '数据采集方式',
        'ZL_CURR': '零线电流',
        'CREATOR_ID': '记录数据创建人',
        'CREATE_TIME': '创建时间',
        'MODIFIER_ID': '修改人',
        'UPDATE_TIME': '数据修改时间',
        'DATA_FROM': '用于数据迁移标识',
        'AREA_CODE': '区分分省数据',
        'SUPPLY_ORG_NO': '区分地市局',
        'OPTIMISTIC_LOCK_VERSION': '用于控制并发脏数据',
        'DELETE_FLAG': '数据逻辑删除'
    }
    write_csv('MK_1_16_运行电能表电压电流曲线.csv', data_1_16, headers_1_16, comments_1_16)
    
    print("\n" + "="*80)
    print("所有数据生成完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("="*80)
    print("\n数据统计:")
    print(f"1. MK_1_3运行电能表: {len(data_1_3)} 条记录")
    print(f"2. MK_1_4_运行计量自动化终端: {len(data_1_4)} 条记录 (唯一终端)")
    print(f"3. MK_1_27历史故障清单: {len(data_1_27)} 条记录")
    print(f"4. MK_1_29_历史运维日志清单: {len(data_1_29)} 条记录")
    print(f"5. MK_1_30_风险等级清单: {len(data_1_30)} 条记录")
    print(f"6. MK_1_31_硬件状态: {len(data_1_31)} 条记录 (包含终端和电能表)")
    print(f"7. MK_1_32_数据异常清单: {len(data_1_32)} 条记录")
    print(f"8. MK_1_33计算异常清单: {len(data_1_33)} 条记录")
    print(f"9. MK_1_34_状态异常清单终端: {len(data_1_34)} 条记录")
    print(f"10. MK_1_35_状态异常清单电能表: {len(data_1_35)} 条记录")
    print(f"11. MK_RI_UNSUCCESSFUL_METER: {len(data_ri_um)} 条记录")
    print(f"12. MK_1_15_运行电能表功率曲线: {len(data_1_15)} 条记录")
    print(f"13. MK_1_16_运行电能表电压电流曲线: {len(data_1_16)} 条记录")
    
    print("\n" + "="*80)
    print("主要修改说明:")
    print("="*80)
    print("✓ 修改1: 所有供电单位编号统一使用: " + UNIFIED_SUPPLY_ORG_NO)
    print("✓ 修改2: RUN_TERM_ID只有一个终端,所有关联字段与此唯一终端保持一致")
    print("✓ 修改3: 1-30风险等级清单增加字段注释:")
    print("  - inc_risk_1~10: 增量基础因子1~10")
    print("  - MANUFACTURER_NAME: 生产厂家名称")
    print("  - ARRIVE_BATCH: 所属批次")
    print("✓ 修改4: 1-31硬件状态表格生成终端和电能表两种数据")
    print("✓ 修改5: 1-36抄表不成功数据与基础数据联动(使用表1的资产编号、通讯地址等)")
    print("✓ 修改6: 各表格间实体关系字段数据联动匹配")
    print("\n接线错误逻辑说明:")
    print("  1. 功率曲线表(MK_1_15):")
    print("     - 单相电流反接: 该相有功/无功功率符号反转,功率因数为负")
    print("     - 两相电流反接: 两相功率皆为负,总功率偏小")
    print("     - 三相电流全反: 全部功率为负,电表倒走")
    print("     - 电流错相: 功率因数异常波动,可能>1或为负,无功方向错乱")
    print("     - 电压相序错误: 功率因数异常,无功功率方向错乱")
    print("     - 混合错误: 功率值和功率因数无规律,数据跳变")
    print("  2. 电压电流表(MK_1_16):")
    print("     - 接线错误不影响电压电流幅值测量")
    print("     - 电压电流始终保持在正常范围内")
    print("     - 只有硬件故障才会影响测量精度")

if __name__ == "__main__":
    main()