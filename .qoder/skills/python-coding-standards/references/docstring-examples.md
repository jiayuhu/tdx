# Python 文档字符串模板 (Google 风格)

## 1. 模块文档字符串

```python
"""
股票数据库管理模块

功能:
1. 持久化选股结果到 SQLite
2. 计算每日股票增量变化
3. 记录执行日志

使用示例:
    from database import StockDatabase

    db = StockDatabase()
    db.save_stocks('b01', ['600001', '600002'])
    dates = db.get_recent_dates('b01', limit=5)
"""
```

## 2. 类文档字符串

```python
class BlockManager:
    """通达信自定义板块管理器

    管理自定义板块的创建、查询、修改和删除操作。
    通过 TdxQuant API 与通达信客户端交互。

    Attributes:
        tq: TdxQuant 客户端实例
        block_path: 板块文件存储路径
    """
```

简单类可以用一行：
```python
class ConfigError(Exception):
    """配置文件解析错误"""
```

## 3. 函数文档字符串

### 完整格式（复杂函数）

```python
def save_stocks(table_name: str, stocks: List[str],
                record_date: Optional[str] = None) -> int:
    """保存选股结果到数据库

    将股票代码列表存入指定表，同一日期的旧数据会被覆盖。
    日期以 UTC 格式存储。

    Args:
        table_name: 目标数据表名（如 'b01'）
        stocks: 股票代码列表（如 ['600001', '000002']）
        record_date: 记录日期，默认为当前 UTC 时间

    Returns:
        实际写入的记录数

    Raises:
        ValueError: 表名含有非法字符时
        sqlite3.OperationalError: 数据库操作失败时
    """
```

### 简洁格式（简单函数）

```python
def _utc_now() -> str:
    """返回当前 UTC 时间字符串 (YYYY-MM-DD HH:MM:SS)"""

def _validate_table_name(name: str) -> bool:
    """校验表名是否只含字母、数字和下划线"""

def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
```

### 含示例的格式

```python
def get_stocks_by_date(table_name: str, record_day: str) -> List[str]:
    """查询指定日期的选股结果

    Args:
        table_name: 数据表名
        record_day: 日期字符串 (YYYY-MM-DD)

    Returns:
        股票代码列表

    Example:
        >>> db = StockDatabase()
        >>> stocks = db.get_stocks_by_date('b01', '2026-03-10')
        >>> print(stocks)
        ['600001', '000002', '300100']
    """
```

## 4. 属性/Property 文档字符串

```python
class StockDatabase:
    @property
    def db_path(self) -> Path:
        """数据库文件路径（只读）"""
        return self._db_path
```

## 5. 文档字符串要点

| 规则 | 说明 |
|------|------|
| 首行 | 一行简短描述，以句号结尾（中文省略句号亦可） |
| 空行 | 首行与详细描述之间空一行 |
| Args | 每个参数一行：`参数名: 描述` |
| Returns | 描述返回值的类型和含义 |
| Raises | 列出可能抛出的异常 |
| 缩进 | 与首行 `"""` 对齐 |
| 私有函数 | 一行描述即可，不需要 Args/Returns |
| 三引号 | 使用双引号 `"""` 而非单引号 `'''` |
