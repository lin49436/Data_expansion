#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础数据生成模块
包含台区、电表等基础数据的生成函数
"""

import random
from datetime import datetime, timedelta
from utils import generate_id, get_unified_org_no
from config import NUM_DISTRICTS, NUM_SUB_METERS


def generate_district_and_meters():
    """生成台区和电表的基础信息"""
    from config import SUPPLY_ORG_NUMBERS

    districts = []
    meters = []

    for i in range(NUM_DISTRICTS):
        district_no = f"TQ{i + 1:04d}"
        district_name = f"台区{i + 1}"
        district_addr = f"测试地址{i + 1}号"
        supply_org_no = SUPPLY_ORG_NUMBERS[i]  # 每个台区对应一个供电单位编号

        districts.append({
            'ta_no': district_no,
            'ta_name': district_name,
            'ta_addr': district_addr,
            'ta_type': '1',  # 1-居民台区
            'supply_org_no': supply_org_no  # 新增：供电单位编号
        })

        # 生成总表
        total_meter = {
            'run_meter_id': generate_id(f'M{district_no}T', 16),
            'ta_no': district_no,
            'ma_auxil_table_signs': '1',  # 1-主表(总表)
            'meter_type': 'total',
            'supply_org_no': supply_org_no  # 新增：供电单位编号
        }
        meters.append(total_meter)

        # 生成分表
        for j in range(NUM_SUB_METERS):
            sub_meter = {
                'run_meter_id': generate_id(f'M{district_no}S{j + 1:02d}', 16),
                'ta_no': district_no,
                'ma_auxil_table_signs': '0',  # 0-副表(分表)
                'meter_type': 'sub',
                'supply_org_no': supply_org_no  # 新增：供电单位编号
            }
            meters.append(sub_meter)

    return districts, meters


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
            'SUPPLY_ORG_CODE': meter['supply_org_no'],  # 使用电表对应的供电单位编号
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
        }
        data.append(row)

    return data


def generate_table_1_4(districts):
    """生成运行计量自动化终端数据 - 每个台区生成一个终端记录"""
    data = []
    current_time = datetime.now()

    # 为每个台区生成一个终端
    for district in districts:
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
            'SUPPLY_ORG_NO': district['supply_org_no'],  # 使用台区对应的供电单位编号
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
            'DOWN_COMM_CHANNEL': 'RS485',
            'METERING_POINT_NAME': f'{district["ta_name"]}计量点',
            'COMM_TYPE': 'GPRS',
            'PROTOCOL_TYPE': 'DL/T645-2007',
            'TERM_TYPE_CODE': '1',
            'PRESET_AMT': str(random.uniform(100, 500)),
            'REMARKS': '正常运行',
        }
        data.append(row)

    return data