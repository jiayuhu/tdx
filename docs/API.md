# TDX API 接口文档 (API.md)

## 目录
1. [模块 API](#1-模块-api)
2. [配置文件 API](#2-配置文件-api)
3. [命令行工具 API](#3-命令行工具-api)
4. [数据库 Schema](#4-数据库-schema)
5. [TQ API 映射](#5-tq-api-映射)

---

## 1. 模块 API

### 1.1 base.py

#### 函数

##### `init_tq_context(script_path: str) -> None`
初始化 TdxQuant 上下文

**参数**:
- `script_path`: 调用脚本的路径

**异常**:
- `ConfigurationError`: 配置文件读取失败
- `ImportError`: TQ 模块导入失败

##### `close_tq_context() -> None`
关闭 TQ 上下文

##### `get_tq() -> Any`
获取全局 TQ 实例

**返回**: TdxQuant API 对象

##### `get_config() -> Dict`
获取配置信息

**返回**: 配置字典

### 1.2 selector.py

#### 类: `StockSelector`

##### `__init__()`
初始化选股器

##### `select_by_formula(stock_list: List[str], formula_name: str, stock_period: Optional[str] = None, filter_st: bool = True) -> List[str]`
使用公式选股

**参数**:
- `stock_list`: 股票代码列表
- `formula_name`: 公式名称
- `stock_period`: K线周期 ('1d', '1w', '1m')
- `filter_st`: 是否过滤 ST 股票

**返回**: 选中的股票代码列表

**异常**:
- `FormulaError`: 公式执行失败

##### `is_st_stock(stock_code: str) -> bool`
判断是否为 ST 股票

**参数**:
- `stock_code`: 股票代码

**返回**: 是否为 ST 股票

### 1.3 blocks.py

#### 类: `BlockManager`

##### `__init__(tq, delay_ms: Optional[int] = None)`
初始化板块管理器

**参数**:
- `tq`: TQ 实例
- `delay_ms`: 操作延时(毫秒)

##### `get_block_stocks(block_code: str) -> List[str]`
获取板块成分股

**参数**:
- `block_code`: 板块代码

**返回**: 股票代码列表

##### `prepare_target_block(block_code: str, block_name: str) -> bool`
准备目标板块(创建或清空)

**参数**:
- `block_code`: 板块代码
- `block_name`: 板块名称

**返回**: 操作是否成功

##### `add_stocks_to_block(block_code: str, stocks: List[str]) -> Dict`
添加股票到板块

**参数**:
- `block_code`: 板块代码
- `stocks`: 股票代码列表

**返回**: TQ API 返回结果

### 1.4 database.py

#### 类: `StockDatabase`

##### `__init__(db_path: Path)`
初始化数据库

**参数**:
- `db_path`: 数据库文件路径

##### `init(blocks: List[Dict[str, Any]]) -> None`
初始化数据库表结构

**参数**:
- `blocks`: 板块配置列表

##### `save_stocks(table_name: str, stock_data: Dict[str, str], record_date: str) -> None`
保存选股结果

**参数**:
- `table_name`: 表名
- `stock_data`: `{股票代码: 股票名称}` 字典
- `record_date`: 记录日期

##### `get_stocks_by_date(table_name: str, record_day: str) -> Dict[str, str]`
获取指定日期的股票数据

**参数**:
- `table_name`: 表名
- `record_day`: 日期 (YYYY-MM-DD)

**返回**: `{股票代码: 股票名称}` 字典

##### `process_block(block_config: Dict[str, Any], block_manager, keep_days: int) -> Dict`
处理板块数据(增量计算)

**参数**:
- `block_config`: 板块配置
- `block_manager`: 板块管理器
- `keep_days`: 数据保留天数

**返回**: 处理结果字典

#### 静态方法

##### `calculate_delta(curr_db: Dict[str, str], prev_db: Dict[str, str]) -> Tuple[set, set]`
计算增量

**参数**:
- `curr_db`: 当前数据
- `prev_db`: 前一日数据

**返回**: `(新增股票集合, 移除股票集合)`

##### `calculate_buy_point(tq, stock_code: str) -> float`
计算买点 EMA(C,2)

**参数**:
- `tq`: TQ 实例
- `stock_code`: 股票代码

**返回**: 买点价格

### 1.5 executor.py

#### 函数

##### `execute_strategy(config: Dict, selector, block_manager) -> Optional[Dict]`
执行选股策略

**参数**:
- `config`: 策略配置
- `selector`: 选股器
- `block_manager`: 板块管理器

**返回**: 执行结果字典，失败时返回 None

##### `execute_single_strategy(config: Dict, selector, block_manager) -> Optional[Dict]`
执行单公式策略

##### `execute_multi_strategy(config: Dict, selector, block_manager) -> Optional[Dict]`
执行多公式串行策略

##### `execute_parallel_strategy(config: Dict, selector, block_manager) -> Optional[Dict]`
执行多公式并行策略

##### `execute_db_update(config: Dict, block_manager) -> Optional[Dict]`
执行数据库更新策略

---

## 2. 配置文件 API

### 2.1 配置结构

```yaml
# 根级别配置
tdx_root: string              # 通达信安装路径
tq_delay_ms: integer          # TQ 操作延时(ms)
xg_programs: list             # 选股策略列表

# 策略配置
- name: string               # 策略名称
  desc: string               # 策略描述
  type: string               # 策略类型
  source_block: string       # 源板块代码
  target_block: string       # 目标板块代码
  target_block_name: string  # 目标板块名称
  formula_name: string       # 公式名称
  stock_period: string       # K线周期
  formulas: list             # 公式列表
  long_term_blocks: list     # 长线板块
  short_term_blocks: list    # 短线板块
  keep_days: integer         # 保留天数
```

### 2.2 策略类型配置

#### single (单公式)
```yaml
type: "single"
source_block: string      # 必填
target_block: string      # 必填
target_block_name: string # 必填
formula_name: string      # 必填
stock_period: string      # 可选，默认 "1d"
```

#### multi (多公式串行)
```yaml
type: "multi"
source_block: string      # 必填
target_block: string      # 必填
target_block_name: string # 必填
formulas:                 # 必填，列表
  - string
```

#### parallel (多公式并行)
```yaml
type: "parallel"
source_block: string      # 必填
formulas:                 # 必填，列表
  - formula_name: string    # 必填
    target_block: string    # 必填
    target_block_name: string # 必填
    stock_period: string    # 可选
```

#### db_update (数据库更新)
```yaml
type: "db_update"
long_term_blocks:         # 可选
  - code: string          # 必填
    target_block: string  # 必填
short_term_blocks:        # 可选
  - code: string          # 必填
    target_block: string  # 必填
keep_days: integer        # 必填，≥1
```

---

## 3. 命令行工具 API

### 3.1 xg.py

```bash
# 执行全部策略
uv run python xg.py

# 执行单个策略
uv run python xg.py --strategy STRATEGY_NAME

# 执行多个策略
uv run python xg.py --strategy STRATEGY1 STRATEGY2

# 列出所有策略
uv run python xg.py --list

# 查看策略详情
uv run python xg.py --info STRATEGY_NAME
```

### 3.2 blocks.py

```bash
# 列出所有板块
uv run python blocks.py list

# 查看板块详情
uv run python blocks.py info BLOCK_CODE

# 创建板块
uv run python blocks.py create BLOCK_CODE "板块名称"

# 清空板块
uv run python blocks.py clear BLOCK_CODE
```

### 3.3 dbview.py

```bash
# 交互模式
uv run python dbview.py

# 列出所有表
uv run python dbview.py --tables

# 查看表结构
uv run python dbview.py --schema TABLE_NAME

# 查看表数据
uv run python dbview.py --data TABLE_NAME [-n LIMIT]

# 搜索数据
uv run python dbview.py --search TABLE_NAME "WHERE_CONDITION"
```

### 3.4 dbclear.py

```bash
# 清空数据库
uv run python dbclear.py
```

---

## 4. 数据库 Schema

### 4.1 主表结构

```sql
-- 板块主表 (如 b01)
CREATE TABLE b01 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    record_date DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_b01_date ON b01(date(record_date));
```

### 4.2 增量表结构

```sql
-- 增量表 (如 b01_delta)
CREATE TABLE b01_delta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    entry_date DATETIME NOT NULL,
    buy_point REAL,
    record_date DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, record_date)
);

-- 索引
CREATE INDEX idx_b01_delta_date ON b01_delta(date(record_date));
```

### 4.3 日志表结构

```sql
-- 更新日志表
CREATE TABLE update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_date DATE NOT NULL,
    block_code TEXT NOT NULL,
    prev_count INTEGER,
    curr_count INTEGER,
    added_count INTEGER,
    removed_count INTEGER
);
```

---

## 5. TQ API 映射

### 5.1 核心 TQ 方法

| TQ 方法 | 功能 | 封装方法 |
|---------|------|----------|
| `tq.initialize()` | 初始化 TQ | `init_tq_context()` |
| `tq.get_stock_list_in_sector()` | 获取板块成分股 | `BlockManager.get_block_stocks()` |
| `tq.formula_process_mul_xg()` | 批量公式选股 | `StockSelector.select_by_formula()` |
| `tq.get_stock_info()` | 获取股票信息 | `StockSelector.get_stock_name()` |
| `tq.get_market_data()` | 获取行情数据 | `StockDatabase.calculate_buy_point()` |
| `tq.create_sector()` | 创建板块 | `BlockManager.create_block()` |
| `tq.clear_sector()` | 清空板块 | `BlockManager.clear_block_stocks()` |
| `tq.send_user_block()` | 添加股票到板块 | `BlockManager.add_stocks_to_block()` |

### 5.2 返回值格式

#### `formula_process_mul_xg()` 返回格式
```python
{
    "股票代码1": {
        "XG": "1",      # 选中标识
        "CLOSE": 10.5,  # 收盘价
        # ... 其他字段
    },
    "股票代码2": {
        "SELECT": "1",  # 选中标识
        # ...
    }
}
```

#### 板块操作返回格式
```python
{
    "ErrorId": "0",     # "0"表示成功
    "ErrorMsg": "成功",  # 错误信息
    # ... 其他字段
}
```
