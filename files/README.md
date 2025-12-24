# 电能表数据生成系统

## 项目简介

本项目用于生成电能表虚拟数据,包含多个数据表的生成,时间范围为2025-09-01到2025-09-07,每15分钟一条数据。

## 文件结构

```
├── config.py                    # 配置文件 - 所有配置常量和参数
├── utils.py                     # 工具函数 - 通用辅助函数
├── basic_data_generators.py    # 基础数据生成 - 台区、电表、终端等
├── anomaly_generators.py       # 异常数据生成 - 故障、风险、异常等
├── curve_generators.py         # 曲线数据生成 - 功率曲线、电压电流曲线
├── csv_writer_and_main.py      # CSV写入和主程序逻辑
├── main.py                      # 程序入口文件
└── README.md                    # 本说明文档
```

## 模块说明

### 1. config.py - 配置模块
包含所有配置参数:
- 时间配置(开始时间、结束时间、时间间隔)
- 台区和电表数量配置
- 输出目录配置
- 供电单位编号配置
- 数据异常类型配置

### 2. utils.py - 工具模块
提供通用辅助函数:
- `get_unified_org_no()`: 获取统一供电单位编号
- `generate_time_series()`: 生成时间序列
- `generate_id(prefix, length)`: 生成指定格式的ID

### 3. basic_data_generators.py - 基础数据生成模块
生成基础数据表:
- `generate_district_and_meters()`: 生成台区和电表信息
- `generate_table_1_3()`: MK_1_3运行电能表
- `generate_table_1_4()`: MK_1_4_运行计量自动化终端

### 4. anomaly_generators.py - 异常数据生成模块
生成异常相关数据表:
- `generate_table_1_27()`: MK_1_27历史故障清单
- `generate_table_1_29()`: MK_1_29_历史运维日志清单
- `generate_table_1_30()`: MK_1_30_风险等级清单
- `generate_table_1_31()`: MK_1_31_硬件状态
- `generate_table_1_32()`: MK_1_32_数据异常清单
- `generate_table_1_33()`: MK_1_33计算异常清单
- `generate_table_1_34()`: MK_1_34_状态异常清单终端
- `generate_table_ri_abnormal_meter()`: MK_1_35_状态异常清单电能表
- `generate_table_ri_unsuccessful_meter()`: MK_1_36_抄表不成功清单

### 5. curve_generators.py - 曲线数据生成模块
生成曲线数据表:
- `generate_table_1_15()`: MK_1_15_运行电能表功率曲线
- `generate_table_1_16()`: MK_1_16_运行电能表电压电流曲线

### 6. csv_writer_and_main.py - CSV写入和主程序模块
包含:
- `write_csv()`: CSV文件写入函数(包含字段注释)
- `main()`: 主程序逻辑,协调所有模块生成数据

### 7. main.py - 程序入口
程序的启动入口,调用主程序函数

## 使用方法

### 1. 修改配置(可选)
编辑 `config.py` 文件,修改相关配置参数:
```python
START_DATE = datetime(2025, 9, 1, 0, 0, 0)  # 开始时间
END_DATE = datetime(2025, 9, 7, 23, 45, 0)  # 结束时间
INTERVAL_MINUTES = 15                        # 时间间隔(分钟)
NUM_DISTRICTS = 1                            # 台区数量
NUM_SUB_METERS = 35                          # 每个台区的分表数量
UNIFIED_SUPPLY_ORG_NO = '0501'              # 供电单位编号
```

### 2. 运行程序
```bash
python main.py
```

或者

```bash
python3 main.py
```

### 3. 查看输出
生成的CSV文件将保存在 `outputs/electric_meter_data/` 目录下

## 生成的数据表

程序将生成以下13个CSV文件:

1. MK_1_3运行电能表.csv
2. MK_1_4_运行计量自动化终端.csv
3. MK_1_27历史故障清单.csv
4. MK_1_29_历史运维日志清单.csv
5. MK_1_30_风险等级清单_手动录入.csv
6. MK_1_31_硬件状态.csv
7. MK_1_32_数据异常清单.csv
8. MK_1_33计算异常清单_手工录入_增量数据上送.csv
9. MK_1_34_状态异常清单终端.csv
10. MK_1_35_状态异常清单电能表.csv
11. MK_1_36_抄表不成功清单.csv
12. MK_1_15_运行电能表功率曲线.csv
13. MK_1_16_运行电能表电压电流曲线.csv

## 数据特点

### 时间格式
所有时间数据严格按照 "yyyy-mm-dd HH:MM:SS" 格式(24小时制)

### 供电单位编号
所有数据使用统一的供电单位编号(默认: 0501)

### 接线错误逻辑
修正了接线错误逻辑,使其符合三相四线制电表实际测量特性:

**功率曲线表(MK_1_15):**
- 单相电流反接: 该相有功/无功功率符号反转,功率因数为负
- 两相电流反接: 两相功率皆为负,总功率偏小
- 三相电流全反: 全部功率为负,电表倒走
- 电流错相: 功率因数异常波动,可能>1或为负,无功方向错乱
- 电压相序错误: 功率因数异常,无功功率方向错乱
- 混合错误: 功率值和功率因数无规律,数据跳变

**电压电流表(MK_1_16):**
- 接线错误不影响电压电流幅值测量
- 电压电流始终保持在正常范围内
- 只有硬件故障才会影响测量精度

## 数据关联

各表之间的数据通过以下字段进行关联:
- RUN_METER_ID: 运行电能表标识
- RUN_TERM_ID: 终端标识
- SUPPLY_ORG_NO: 供电单位编号
- ASSETS_NO: 资产编号
- METERING_POINT_NUMBER: 计量点编号

## 注意事项

1. 程序运行前会自动创建输出目录
2. 如果输出目录已存在同名文件,将被覆盖
3. 所有CSV文件使用UTF-8 BOM编码,方便Excel打开
4. 每个CSV文件的第一行是英文字段名,第二行是中文注释

## 技术依赖

- Python 3.6+
- 标准库: csv, os, datetime, random, string, math

无需安装额外的第三方依赖包。
