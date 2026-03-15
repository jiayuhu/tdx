# Python 命名规范详表

## 速查表

| 类别 | 风格 | 正确示例 | 错误示例 |
|------|------|---------|---------|
| 模块 | `snake_case` | `database.py`, `stock_selector.py` | `Database.py`, `stockSelector.py` |
| 包 | `lowercase` | `utils`, `models` | `Utils`, `my_package` (避免下划线) |
| 类 | `PascalCase` | `BlockManager`, `StockSelector` | `block_manager`, `stockSelector` |
| 异常 | `PascalCase + Error` | `ConfigError`, `ValidationError` | `config_error`, `Bad_Input` |
| 函数 | `snake_case` | `get_stocks_by_date()` | `getStocksByDate()`, `GetStocks()` |
| 方法 | `snake_case` | `process_block()` | `processBlock()` |
| 变量 | `snake_case` | `stock_code`, `record_date` | `stockCode`, `RecordDate` |
| 常量 | `UPPER_SNAKE_CASE` | `BATCH_SIZE`, `DB_PATH` | `batchSize`, `Db_Path` |
| 私有成员 | `_snake_case` | `_tq_instance`, `_config` | `__private` (避免双下划线) |
| 受保护成员 | `_snake_case` | `_internal_cache` | `protected_cache` |
| 布尔变量 | `is_/has_/can_/should_` | `is_valid`, `has_data` | `valid`, `data_exists` |
| 全局内部 | `_snake_case` | `_TABLE_NAME_RE` | `TABLE_NAME_RE` (模块内部应加前缀) |

## 详细规则

### 1. 变量命名

```python
# 正确：描述性 snake_case
stock_code = "600001"
record_date = "2026-03-10"
selected_stocks = []
retry_count = 3

# 错误
sc = "600001"          # 过于简短，含义不明
stockCode = "600001"   # Java 风格驼峰
```

**循环变量例外**：单字符可用于简短循环
```python
for i in range(10):        # OK - 索引
for k, v in data.items():  # OK - 字典遍历
for row in rows:           # 更佳 - 描述性名称
```

### 2. 函数命名

```python
# 正确：动词开头 + snake_case
def get_recent_dates(table_name: str, limit: int) -> list:
def save_stocks(table_name: str, stocks: list) -> None:
def validate_table_name(name: str) -> bool:
def _utc_now() -> str:  # 私有辅助函数

# 错误
def recentDates():     # 驼峰
def data():            # 缺少动词
def do_stuff():        # 含义不明
```

**命名动词约定**：
| 动词 | 场景 |
|------|------|
| `get_` | 获取/查询数据 |
| `set_` | 设置值 |
| `save_` | 持久化数据 |
| `delete_/remove_` | 删除数据 |
| `validate_/check_` | 校验 |
| `parse_` | 解析输入 |
| `create_/build_` | 构建对象 |
| `is_/has_/can_` | 返回布尔值 |

### 3. 类命名

```python
# 正确：PascalCase，名词或名词短语
class StockDatabase:
class BlockManager:
class ConfigError(Exception):

# 错误
class stock_database:   # snake_case
class Mgr:              # 缩写不明
```

### 4. 常量命名

```python
# 正确：UPPER_SNAKE_CASE，定义在模块顶层
DB_PATH = Path(__file__).parent / "data" / "quant.db"
BATCH_SIZE = 100
MAX_RETRY_COUNT = 3
DEFAULT_KEEP_DAYS = 10

# 错误
dbPath = "..."         # 驼峰
Db_Path = "..."        # 混合风格
```

### 5. 缩写处理

```python
# 两/三字母缩写：全大写用于常量，其他场景与普通单词一样
HTTP_TIMEOUT = 30          # 常量中全大写
http_client = HttpClient() # 变量中小写
class HttpClient:          # 类名中首字母大写
db_connection = None       # 常见缩写（db, id, url）可直接使用

# 避免自创缩写
blk_mgr = BlockManager()  # 错误：blk, mgr 不直观
block_manager = BlockManager()  # 正确
```

### 6. 双下划线（name mangling）

```python
# 避免使用双下划线前缀，除非确实需要避免子类命名冲突
class Base:
    def _internal(self):     # 正确：单下划线表示内部
        pass

    def __mangled(self):     # 避免：除非有明确的 name mangling 需求
        pass
```

### 7. 模块级别的特殊名称

```python
# __all__ 控制模块导出
__all__ = ['BlockManager', 'StockDatabase']

# __version__ 模块版本
__version__ = '1.0.0'
```
