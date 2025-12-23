#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常数据生成模块
包含故障、风险、异常等相关数据的生成函数
"""

import random
from datetime import datetime, timedelta
from utils import generate_id, get_unified_org_no
from config import ANOMALY_TYPES
import math

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
