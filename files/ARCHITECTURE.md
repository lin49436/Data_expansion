# 项目架构说明

## 模块依赖关系

```
main.py (主程序)
    ├── config.py (配置)
    ├── utils.py (工具函数)
    │   └── config.py
    ├── csv_handler.py (CSV处理)
    │   └── config.py
    ├── basic_generators.py (基础数据生成)
    │   ├── config.py
    │   └── utils.py
    └── anomaly_generators.py (异常数据生成)
        ├── config.py
        └── utils.py
```

## 数据流程图

```
1. 配置加载 (config.py)
   ↓
2. 生成时间序列 (utils.py)
   ↓
3. 生成台区和电表 (utils.py)
   ↓
4. 生成基础数据
   ├─→ 运行电能表 (basic_generators.py)
   └─→ 运行终端 (basic_generators.py)
   ↓
5. 生成异常数据 (anomaly_generators.py)
   ├─→ 数据异常清单
   ├─→ 计算异常清单
   ├─→ 终端异常清单
   ├─→ 电表异常清单
   └─→ 抄表不成功清单
   ↓
6. 写入CSV文件 (csv_handler.py)
```

## 核心类和函数

### config.py
```python
# 常量
START_DATE, END_DATE, INTERVAL_MINUTES
NUM_DISTRICTS, NUM_SUB_METERS
OUTPUT_DIR
UNIFIED_SUPPLY_ORG_NO
ANOMALY_TYPES

# 函数
get_unified_org_no() -> str
```

### utils.py
```python
generate_time_series() -> List[datetime]
generate_id(prefix: str, length: int) -> str
generate_district_and_meters() -> Tuple[List[dict], List[dict]]
```

### csv_handler.py
```python
write_csv(filename: str, data: List[dict], 
          headers: List[str], comments: dict) -> None
```

### basic_generators.py
```python
generate_table_1_3(meters: List[dict]) -> List[dict]
generate_table_1_4(districts: List[dict]) -> List[dict]
```

### anomaly_generators.py
```python
generate_table_1_32(time_series: List[datetime]) -> List[dict]
generate_table_1_33(time_series: List[datetime]) -> List[dict]
generate_table_1_34(time_series: List[datetime], 
                    terminals: List[dict]) -> List[dict]
generate_table_ri_abnormal_meter(...) -> List[dict]
generate_table_ri_unsuccessful_meter(...) -> List[dict]
```

## 数据表关系

```
MK_1_3 (运行电能表)
    ↓ RUN_METER_ID
    ├─→ MK_1_35 (状态异常清单-电能表)
    └─→ MK_1_36 (抄表不成功清单)

MK_1_4 (运行终端)
    ↓ RUN_TERM_ID
    ├─→ MK_1_34 (状态异常清单-终端)
    └─→ MK_1_36 (抄表不成功清单)

MK_1_32 (数据异常清单)
    ↓ DATA_ANOMALY_TYPE
    ├─→ MK_1_35 (状态异常清单-电能表)
    └─→ MK_1_36 (抄表不成功清单)
```

## 扩展指南

### 添加新的数据表生成器

#### 步骤1: 创建生成函数
在合适的生成器模块中添加函数：

```python
# 在 basic_generators.py 或 anomaly_generators.py
def generate_table_xxx(params):
    """生成XXX表数据"""
    data = []
    for item in params:
        row = {
            'FIELD1': value1,
            'FIELD2': value2,
            # ...
        }
        data.append(row)
    return data
```

#### 步骤2: 在主程序中调用
```python
# 在 main.py 中
from xxx_generators import generate_table_xxx

data_xxx = generate_table_xxx(params)
headers_xxx = list(data_xxx[0].keys())
comments_xxx = {
    'FIELD1': '字段1说明',
    'FIELD2': '字段2说明',
}
write_csv('表名.csv', data_xxx, headers_xxx, comments_xxx)
```

### 添加新的配置项

在 `config.py` 中添加：
```python
# 新配置项
NEW_CONFIG_ITEM = value

def get_new_config():
    """获取新配置"""
    return NEW_CONFIG_ITEM
```

### 添加新的工具函数

在 `utils.py` 中添加：
```python
def new_utility_function(params):
    """新工具函数说明"""
    # 实现
    return result
```

## 设计原则

1. **单一职责**: 每个模块只负责一类功能
2. **低耦合**: 模块间通过明确的接口交互
3. **高内聚**: 相关功能集中在同一模块
4. **可扩展**: 易于添加新功能而不影响现有代码
5. **可配置**: 关键参数集中管理，便于调整

## 性能优化建议

1. **批量处理**: 生成大量数据时考虑分批写入
2. **内存管理**: 对于超大数据集，使用生成器而非列表
3. **并行处理**: 独立的表生成可以考虑并行执行
4. **缓存机制**: 重复计算的数据可以缓存

## 测试建议

1. **单元测试**: 为每个生成函数编写单元测试
2. **集成测试**: 测试完整的数据生成流程
3. **数据验证**: 验证生成数据的格式和关联关系
4. **性能测试**: 测试大数据量下的性能表现
