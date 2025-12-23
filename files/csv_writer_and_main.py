#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV写入和主程序模块
"""

import csv
import os
from config import OUTPUT_DIR, START_DATE, END_DATE, INTERVAL_MINUTES, NUM_DISTRICTS, NUM_SUB_METERS, UNIFIED_SUPPLY_ORG_NO
from utils import generate_time_series
from basic_data_generators import generate_district_and_meters, generate_table_1_3, generate_table_1_4
from anomaly_generators import (generate_table_1_27, generate_table_1_29, generate_table_1_30,
                                generate_table_1_31, generate_table_1_32, generate_table_1_33,
                                generate_table_1_34, generate_table_ri_abnormal_meter,
                                generate_table_ri_unsuccessful_meter)
from curve_generators import generate_table_1_15, generate_table_1_16

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