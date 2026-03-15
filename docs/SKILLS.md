# TDX 开发技能手册 (SKILLS.md)

## 目录
1. [如何添加新选股策略](#1-如何添加新选股策略)
2. [如何扩展选股公式](#2-如何扩展选股公式)
3. [数据库表结构说明](#3-数据库表结构说明)
4. [TQ API 使用指南](#4-tq-api-使用指南)
5. [常见开发模式](#5-常见开发模式)
6. [调试技巧](#6-调试技巧)
7. [性能优化技巧](#7-性能优化技巧)

---

## 1. 如何添加新选股策略

### 1.1 在 config.yaml 中定义策略

```yaml
# 示例：添加一个新的单公式策略
- name: "new_strategy"
  desc: "新策略描述"
  type: "single"  # 或 multi/parallel/db_update
  source_block: "SOURCE_BLOCK_CODE"
  target_block: "TARGET_BLOCK_CODE"
  target_block_name: "目标板块显示名称"
  formula_name: "NEW_FORMULA_NAME"
  stock_period: "1d"  # 1d(日线), 1w(周线), 1m(月线)
```

### 1.2 策略类型配置详解

#### 单公式策略 (single)
```yaml
- name: "example_single"
  desc: "单公式选股"
  type: "single"
  source_block: "AAA"
  target_block: "X03"
  target_block_name: "新板块"
  formula_name: "CUSTOM_FORMULA"
  stock_period: "1w"
```

#### 多公式串行策略 (multi)
```yaml
- name: "example_multi"
  desc: "多公式串行选股"
  type: "multi"
  source_block: "X01"
  target_block: "X03"
  target_block_name: "筛选结果"
  formulas:
    - "FORMULA_1"
    - "FORMULA_2"
    - "FORMULA_3"
```

#### 多公式并行策略 (parallel)
```yaml
- name: "example_parallel"
  desc: "多公式并行选股"
  type: "parallel"
  source_block: "X02"
  formulas:
    - formula_name: "FORMULA_A"
      target_block: "B03"
      target_block_name: "结果A"
      stock_period: "1d"
    - formula_name: "FORMULA_B"
      target_block: "B04"
      target_block_name: "结果B"
      stock_period: "1w"
```

#### 数据库更新策略 (db_update)
```yaml
- name: "example_db_update"
  desc: "数据库更新策略"
  type: "db_update"
  long_term_blocks:
    - code: "B01"
      target_block: "B01_delta"
      target_block_name: "B01增量"
  short_term_blocks:
    - code: "B02"
      target_block: "B02_delta"
      target_block_name: "B02增量"
  keep_days: 10
```

### 1.3 测试新策略

```bash
# 执行单个新策略
uv run python xg.py --strategy new_strategy

# 查看策略详情
uv run python xg.py --info new_strategy

# 检查结果
uv run python blocks.py info TARGET_BLOCK_CODE
uv run python dbview.py --data target_block_table -n 10
```

---

## 2. 如何扩展选股公式

### 2.1 在通达信中创建公式

1. 打开通达信客户端
2. 进入【公式管理器】
3. 选择【条件选股公式】→【其他类型】
4. 点击【新建】
5. 输入公式名称（需与 config.yaml 中一致）
6. 编写选股逻辑

### 2.2 公式编写示例

#### 基础选股公式
```pascal
{收盘价高于开盘价}
CLOSE > OPEN;
```

#### 带参数的公式
```pascal
{股价在均线之上}
MA5: MA(CLOSE, 5);
CLOSE > MA5;
```

#### 复杂条件公式
```pascal
{多条件组合}
MA20 := MA(CLOSE, 20);
VOL_MA5 := MA(VOL, 5);
{收盘价高于20日均线 且 成交量大于5日均量}
CLOSE > MA20 AND VOL > VOL_MA5;
```

### 2.3 公式调试技巧

1. **先在K线图中测试**：确保公式逻辑正确
2. **使用输出函数**：`DRAWTEXT` 显示中间结果
3. **分步验证**：将复杂条件拆分为多个简单条件

```pascal
{调试示例}
MA20 := MA(CLOSE, 20);
DRAWTEXT(CLOSE > MA20, LOW, '↑');  {在图上标记}
CLOSE > MA20;
```

---

## 3. 数据库表结构说明

> 说明：数据库文件路径固定为 `data/quant.db`。`data/` 目录不提交到 Git，会在运行时自动创建。

### 3.1 基础表结构

每个板块对应两张表：

#### 主表 (如 `b01`)
```sql
CREATE TABLE b01 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,      -- 股票代码
    stock_name TEXT,               -- 股票名称
    record_date DATETIME NOT NULL, -- 记录日期时间 (UTC)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_b01_date ON b01(date(record_date));
```

#### 增量表 (如 `b01_delta`)
```sql
CREATE TABLE b01_delta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,      -- 股票代码
    stock_name TEXT,               -- 股票名称
    entry_date DATETIME NOT NULL,  -- 入选日期
    buy_point REAL,                -- 买入点 (EMA(C,2))
    record_date DATETIME NOT NULL, -- 记录日期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, record_date) -- 防重复
);

-- 索引
CREATE INDEX idx_b01_delta_date ON b01_delta(date(record_date));
```

#### 更新日志表
```sql
CREATE TABLE update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_date DATE NOT NULL,     -- 更新日期
    block_code TEXT NOT NULL,      -- 板块代码
    prev_count INTEGER,            -- 更新前数量
    curr_count INTEGER,            -- 更新后数量
    added_count INTEGER,           -- 新增数量
    removed_count INTEGER          -- 移除数量
);
```

### 3.2 数据查询示例

```sql
-- 查看某日选股结果
SELECT stock_code, stock_name 
FROM b01 
WHERE date(record_date) = '2026-03-10';

-- 查看增量股票
SELECT stock_code, stock_name, entry_date, buy_point
FROM b01_delta
WHERE date(record_date) = '2026-03-10'
ORDER BY buy_point DESC;

-- 统计每日选股数量
SELECT date(record_date) as date, COUNT(*) as count
FROM b01
GROUP BY date(record_date)
ORDER BY date DESC;
```

### 3.3 使用 dbview.py 查询

```bash
# 查看表结构
uv run python dbview.py --schema b01

# 查看最新数据
uv run python dbview.py --data b01 -n 20

# 按条件查询
uv run python dbview.py --search b01_delta "date(record_date) = '2026-03-10'"

# 交互模式
uv run python dbview.py
```

---

## 4. TQ API 使用指南

### 4.1 核心 API 方法

#### 获取板块成分股
```python
def get_source_stocks(self, block_code: str) -> List[str]:
    """获取板块成分股代码列表"""
    return self.tq.get_stock_list_in_sector(block_code, block_type=1)
```

#### 执行选股公式
```python
def select_by_formula(
    self, 
    stock_list: List[str], 
    formula_name: str, 
    stock_period: str = None
) -> List[str]:
    """使用公式选股"""
    result = self.tq.formula_process_mul_xg(
        formula_name=formula_name,
        stock_list=stock_list,
        stock_period=stock_period,
        count=-1,           # 返回全部数据
        dividend_type=1,    # 前复权
    )
    # 解析结果
    selected = []
    for stock_code, stock_data in result.items():
        if stock_data.get('XG') == '1' or stock_data.get('SELECT') == '1':
            selected.append(stock_code)
    return selected
```

#### 获取股票信息
```python
def get_stock_name(self, stock_code: str) -> str:
    """获取股票名称"""
    info = self.tq.get_stock_info(stock_code, field_list=['Name'])
    return info.get('Name', stock_code)
```

#### 获取市场数据
```python
def get_close_prices(self, stock_code: str, days: int = 10) -> list:
    """获取收盘价序列"""
    result = self.tq.get_market_data(
        field_list=['Close'],
        stock_list=[stock_code],
        period='1d',
        count=days,
        dividend_type='front',  # 前复权
    )
    return result['Close'][stock_code].values
```

### 4.2 板块管理 API

#### 创建板块
```python
def create_block(self, block_code: str, block_name: str) -> Dict:
    """创建自定义板块"""
    return self.tq.create_sector(
        block_code=block_code, 
        block_name=block_name
    )
```

#### 清空板块
```python
def clear_block_stocks(self, block_code: str) -> Dict:
    """清空板块中的股票"""
    return self.tq.clear_sector(block_code=block_code)
```

#### 添加股票到板块
```python
def add_stocks_to_block(self, block_code: str, stocks: List[str]) -> Dict:
    """批量添加股票到板块"""
    return self.tq.send_user_block(
        block_code=block_code, 
        stocks=stocks
    )
```

### 4.3 API 调用注意事项

1. **延时控制**: 板块操作后需延时 100ms
2. **批量处理**: 股票列表超过 200 支需分批处理
3. **错误处理**: 检查返回结果的 `ErrorId` 字段
4. **连接管理**: 使用全局单例，避免重复初始化

---

## 5. 常见开发模式

### 5.1 策略执行器模式

```python
# executor.py 中的策略分发
def execute_strategy(config: Dict, selector, block_manager) -> Optional[Dict]:
    strategy_type = config.get('type')
    
    if strategy_type == 'single':
        return execute_single_strategy(config, selector, block_manager)
    elif strategy_type == 'multi':
        return execute_multi_strategy(config, selector, block_manager)
    elif strategy_type == 'parallel':
        return execute_parallel_strategy(config, selector, block_manager)
    elif strategy_type == 'db_update':
        return execute_db_update(config, selector, block_manager)
    else:
        raise ValueError(f"未知策略类型: {strategy_type}")
```

### 5.2 上下文管理器模式

```python
# 数据库连接管理
@contextmanager
def get_db_connection(db_path: str):
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(str(db_path))
    try:
        yield conn
    finally:
        conn.close()

# 使用示例
with get_db_connection(self.db_path) as conn:
    cursor = conn.cursor()
    # 数据库操作...
    conn.commit()
```

### 5.3 装饰器模式

```python
def log_execution_time(func):
    """执行时间日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f"开始执行: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"完成执行: {func.__name__} (耗时 {elapsed:.2f}s)")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"执行失败: {func.__name__} (耗时 {elapsed:.2f}s) - {e}")
            raise
    return wrapper

@log_execution_time
def my_function():
    # 业务逻辑
    pass
```

### 5.4 配置驱动模式

```python
# 通过配置决定行为
strategy_config = {
    'type': 'single',
    'source_block': 'AAA',
    'target_block': 'X01',
    'formula_name': 'X01_BELOW240W'
}

# 无需修改代码，只需调整配置
if strategy_config['type'] == 'single':
    # 单公式逻辑
elif strategy_config['type'] == 'multi':
    # 多公式逻辑
```

---

## 6. 调试技巧

### 6.1 日志调试

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用不同级别
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 6.2 交互式调试

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 或使用 IPython
from IPython import embed; embed()
```

### 6.3 数据验证

```python
def validate_result(stocks: List[str], expected_count: int = None):
    """验证选股结果"""
    print(f"选股结果: {len(stocks)} 支")
    if expected_count:
        print(f"预期数量: {expected_count} 支")
        print(f"差异: {len(stocks) - expected_count}")
    
    # 显示前几支股票
    print("前5支股票:", stocks[:5] if stocks else "无")

# 使用示例
selected = selector.select_by_formula(stock_list, "FORMULA")
validate_result(selected, expected_count=50)
```

### 6.4 性能分析

```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} 耗时: {end - start:.4f} 秒")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(1)
```

---

## 7. 性能优化技巧

### 7.1 批量操作优化

```python
# ❌ 逐条插入（慢）
for stock in stocks:
    cursor.execute("INSERT INTO table VALUES (?, ?)", (stock.code, stock.name))

# ✅ 批量插入（快）
data = [(s.code, s.name) for s in stocks]
cursor.executemany("INSERT INTO table VALUES (?, ?)", data)
```

### 7.2 数据库索引优化

```python
# 为常用查询字段创建索引
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_table_date 
    ON table_name(date(record_date))
""")

# 复合索引
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_table_code_date 
    ON table_name(stock_code, date(record_date))
""")
```

### 7.3 内存优化

```python
# ❌ 一次性加载所有数据（内存消耗大）
all_data = load_all_data()

# ✅ 分批处理（内存友好）
for batch in get_batches(data, batch_size=1000):
    process_batch(batch)
```

### 7.4 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stock_info_cached(stock_code: str) -> dict:
    """缓存股票信息查询结果"""
    return tq.get_stock_info(stock_code)

# 使用缓存版本
info = get_stock_info_cached("600000")
```

### 7.5 异步处理

```python
import asyncio
import concurrent.futures

async def async_select_formula(selector, stock_list, formula_name):
    """异步执行选股"""
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            selector.select_by_formula,
            stock_list,
            formula_name
        )
    return result
```

---

## 附录

### A. 常用代码片段

```python
# 安全的数据库操作模板
def safe_db_operation(self, operation_func, *args, **kwargs):
    """安全的数据库操作模板"""
    conn = sqlite3.connect(str(self.db_path))
    try:
        cursor = conn.cursor()
        result = operation_func(cursor, *args, **kwargs)
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        conn.close()
```

### B. 测试数据生成

```python
def generate_test_stocks(count: int = 100) -> List[str]:
    """生成测试用股票代码"""
    prefixes = ['600', '601', '000', '002', '300']
    stocks = []
    for i in range(count):
        prefix = prefixes[i % len(prefixes)]
        code = f"{prefix}{i+1:03d}"
        stocks.append(code)
    return stocks
```

### C. 常见错误排查

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `TQ 初始化失败` | 通达信未启动或路径错误 | 检查客户端状态和配置路径 |
| `选股结果为0` | 公式名称错误或无符合条件股票 | 验证公式名，检查数据 |
| `database is locked` | 数据库被其他进程占用 | 关闭其他程序，重启服务 |
| `Connection refused` | TQ 连接数超限 | 等待或重启 TQ |
