# SQLite 最佳实践

## 1. 参数化查询（必须）

```python
# 正确：使用 ? 占位符
cursor.execute(
    "SELECT * FROM stocks WHERE stock_code = ? AND date(record_date) = ?",
    (stock_code, record_day)
)

# 正确：INSERT 同理
cursor.execute(
    "INSERT INTO stocks (stock_code, record_date) VALUES (?, ?)",
    (code, _utc_now())
)

# 错误：字符串拼接 — SQL 注入风险
cursor.execute(f"SELECT * FROM stocks WHERE stock_code = '{stock_code}'")
```

## 2. 表名安全（动态表名必须校验）

```python
import re

_TABLE_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

def _safe_table_name(name: str) -> str:
    """校验并返回安全的表名，不合法时抛出 ValueError"""
    if not _TABLE_NAME_RE.match(name):
        raise ValueError(f"非法表名：{name}")
    return name

# 使用：在 f-string 中嵌入表名前必须校验
table = _safe_table_name(table_name)
cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
```

## 3. 连接管理

```python
# 推荐：上下文管理器自动提交/回滚
import sqlite3

def save_data(db_path: str, data: list) -> None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO stocks (code, date) VALUES (?, ?)",
            data
        )
        # with 块结束时自动 commit；异常时自动 rollback

# 只读查询也推荐使用 with
def query_data(db_path: str) -> list:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stocks")
        return cursor.fetchall()
```

## 4. 批量操作

```python
# 正确：executemany 批量插入
records = [(code, _utc_now()) for code in stock_codes]
cursor.executemany(
    "INSERT INTO stocks (stock_code, record_date) VALUES (?, ?)",
    records
)

# 大批量时使用事务包裹
conn.execute("BEGIN TRANSACTION")
try:
    for batch in chunks(records, 500):
        cursor.executemany(sql, batch)
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

## 5. 日期时间处理

```python
from datetime import datetime, timezone, timedelta

def _utc_now() -> str:
    """返回当前 UTC 时间字符串"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# 存储：始终使用 UTC
cursor.execute(
    "INSERT INTO logs (message, created_at) VALUES (?, ?)",
    (msg, _utc_now())
)

# 查询：使用 date() 函数做日级别匹配
# date() 兼容 'YYYY-MM-DD' 和 'YYYY-MM-DD HH:MM:SS' 两种格式
cursor.execute(
    "SELECT * FROM stocks WHERE date(record_date) = ?",
    (target_day,)  # target_day 为 'YYYY-MM-DD' 格式
)

# 去重日期查询
cursor.execute(
    "SELECT DISTINCT date(record_date) as d FROM stocks ORDER BY d DESC LIMIT ?",
    (limit,)
)

# 显示时转换为北京时间 (UTC+8)
_BJT_OFFSET = timedelta(hours=8)

def _to_beijing(utc_str: str) -> str:
    try:
        dt = datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S')
        return (dt + _BJT_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return utc_str
```

## 6. 表结构与索引

```python
# 建表时指定类型，便于工具识别
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT NOT NULL,
        record_date DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# 为常用查询字段建索引
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_stocks_date
    ON stocks (record_date)
""")
```
