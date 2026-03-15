---
name: python-coding-standards
description: 'Use when: 编写、审查或重构 Python 代码时。确保遵循 PEP 8/PEP 257 编码规范和最佳实践。适用于代码生成、代码审查、Bug 修复、重构等所有 Python 开发场景。关键词: Python, PEP8, 编码规范, 代码风格, 命名规范, 文档字符串, 类型注解, 异常处理, SQLite'
---

# Python 编码规范

本规范适用于所有 Python 项目的代码编写、审查和重构。基于 PEP 8、PEP 257 及社区最佳实践。

---

## 1. 命名规范

| 类别 | 风格 | 示例 |
|------|------|------|
| 模块 | `snake_case` | `database.py`, `stock_selector.py` |
| 包 | `lowercase` | `utils`, `models` |
| 类/异常 | `PascalCase` | `BlockManager`, `ConfigError` |
| 函数/方法 | `snake_case` | `get_stocks_by_date()` |
| 变量 | `snake_case` | `stock_code`, `record_date` |
| 常量 | `UPPER_SNAKE_CASE` | `BATCH_SIZE`, `DB_PATH` |
| 私有成员 | `_leading_underscore` | `_config`, `_utc_now()` |
| 布尔变量 | `is_/has_/can_/should_` | `is_valid`, `has_data` |

**核心原则**：
- 名称应描述含义，避免缩写（`block_manager` 而非 `blk_mgr`）
- 常见缩写可接受：`db`, `id`, `url`, `http`, `api`
- 避免双下划线前缀（name mangling），除非确需避免子类冲突
- 函数名以动词开头：`get_`, `save_`, `validate_`, `parse_`, `create_`

详细命名对照表见 [naming-conventions.md](./references/naming-conventions.md)

---

## 2. 代码格式化

### 缩进与行宽
- 缩进：4 个空格，禁用 Tab
- 行宽：代码最长 120 字符，文档字符串最长 72 字符
- 续行缩进：对齐到开括号，或悬挂缩进 4 空格

### 空行
- 顶级定义（函数、类）之间：2 个空行
- 类内方法之间：1 个空行
- 逻辑分组之间：1 个空行

### import 组织
```python
# 第一组：标准库
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# 第二组：第三方库
import yaml

# 第三组：本地模块
from base import init_tq_context, get_config
from database import StockDatabase
```

**规则**：
- 三组之间用空行分隔
- 每组内按字母排序
- 优先 `from module import name`，避免 `import *`
- 避免循环导入

### 字符串
- 优先单引号 `'text'`
- 多行/文档字符串使用双引号 `"""text"""`
- 优先 f-string 格式化：`f"共 {count} 条记录"`

### 末尾逗号
```python
# 多行结构加末尾逗号，便于 diff
config = {
    'name': 'test',
    'value': 42,  # <- 末尾逗号
}
```

---

## 3. 文档字符串 (Google 风格)

### 模块文档字符串（必须）
```python
"""
数据库管理模块

功能:
1. 持久化选股结果到 SQLite
2. 计算每日股票增量变化

使用示例:
    db = StockDatabase()
    db.save_stocks('b01', ['600001', '600002'])
"""
```

### 函数文档字符串
```python
def save_stocks(table_name: str, stocks: List[str]) -> int:
    """保存选股结果到数据库

    将股票代码列表存入指定表，同一日期的旧数据会被覆盖。

    Args:
        table_name: 目标数据表名
        stocks: 股票代码列表

    Returns:
        实际写入的记录数

    Raises:
        ValueError: 表名含有非法字符时
    """
```

**规则**：
- 公有函数/方法：必须有文档字符串
- 私有函数（`_` 前缀）：一行描述即可
- 使用 `"""` 双引号三引号
- 首行为简短描述，与详细内容之间空一行

完整模板见 [docstring-examples.md](./references/docstring-examples.md)

---

## 4. 类型注解

### 基本规则
```python
# 公有函数必须有完整类型注解
def get_stocks_by_date(table_name: str, record_day: str) -> List[str]:
    ...

# 返回 None 显式标注
def save_log(message: str) -> None:
    ...

# Optional 用于可能为 None 的参数
def query(table: str, limit: Optional[int] = None) -> List[Dict]:
    ...
```

### 常用类型
```python
from typing import List, Dict, Optional, Tuple, Any, Callable, Union

# 容器类型
stocks: List[str]
config: Dict[str, Any]
pair: Tuple[str, int]

# 可选与联合
name: Optional[str]           # 等价于 Union[str, None]
value: Union[int, float]

# 回调
handler: Callable[[str, int], bool]
```

### Python 3.10+ 简写
```python
# 可以使用内置类型替代 typing
stocks: list[str]
config: dict[str, Any]
name: str | None              # 替代 Optional[str]
```

**规则**：
- 公有 API 必须有类型注解
- 私有函数建议有，但不强制
- 变量注解：仅在类型不明显时添加
- 避免过度使用 `Any`

---

## 5. 异常处理

### 捕获具体异常
```python
# 正确：捕获具体异常
try:
    config = load_yaml(path)
except FileNotFoundError:
    print(f"配置文件不存在：{path}")
except yaml.YAMLError as e:
    print(f"配置文件格式错误：{e}")

# 错误：裸 except 或过宽的 Exception
try:
    process()
except:          # 禁止
    pass
```

### 上下文管理器
```python
# 文件、数据库连接、锁等资源必须使用 with
with open(path) as f:
    data = f.read()

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    ...
```

### Guard Clause（提前返回）
```python
# 正确：条件不满足时提前退出
def process_block(block_code: str) -> Optional[dict]:
    if not block_code:
        return None
    if not validate_code(block_code):
        raise ValueError(f"非法板块代码：{block_code}")
    # 主逻辑
    ...

# 错误：过深嵌套
def process_block(block_code: str):
    if block_code:
        if validate_code(block_code):
            # 主逻辑嵌套太深
            ...
```

### 自定义异常
```python
class ConfigError(Exception):
    """配置文件相关错误"""

# 使用异常链
try:
    data = parse(raw)
except ValueError as e:
    raise ConfigError(f"解析失败：{raw}") from e
```

---

## 6. SQLite 最佳实践

| 规则 | 说明 |
|------|------|
| 参数化查询 | 始终使用 `?` 占位符，禁止字符串拼接 SQL 值 |
| 表名校验 | 动态表名必须通过正则 `^[a-zA-Z_][a-zA-Z0-9_]*$` 校验 |
| 连接管理 | 使用 `with sqlite3.connect()` 上下文管理器 |
| 日期时间 | 存储用 UTC (`YYYY-MM-DD HH:MM:SS`)，显示转北京时间 |
| 批量操作 | 使用 `executemany` 而非循环 `execute` |
| 事务 | 大批量写入用显式事务包裹 |

```python
# 日级别匹配用 date() 函数（兼容纯日期和完整时间戳）
cursor.execute(
    f"SELECT * FROM {table} WHERE date(record_date) = ?",
    (target_day,)
)
```

详细模式见 [sqlite-patterns.md](./references/sqlite-patterns.md)

---

## 7. 项目结构

```
project/
├── main.py              # 入口文件
├── config.yaml          # 外部配置
├── base.py              # 基础模块：初始化、常量、配置读取
├── database.py          # 数据层：数据库操作
├── executor.py          # 业务层：策略执行
├── selector.py          # 业务层：选股逻辑
├── blocks.py            # 业务层：板块管理
├── data/                # 数据文件目录
└── tests/               # 测试目录
```

**规则**：
- 每个模块职责单一
- 入口文件使用 `if __name__ == "__main__":` 守卫
- 配置外部化到 YAML/JSON，不硬编码
- 共享常量集中定义在 base 模块

---

## 8. 日志与错误报告

```python
import logging

logger = logging.getLogger(__name__)

# 日志级别使用
logger.debug("查询参数：table=%s, date=%s", table, date)   # 调试信息
logger.info("保存 %d 条记录到 %s", count, table)            # 正常流程
logger.warning("表 %s 数据为空，跳过", table)                # 可恢复的问题
logger.error("数据库操作失败：%s", e)                        # 错误
```

**规则**：
- 优先使用 `logging` 模块而非 `print()`
- 面向用户的信息使用中文
- 日志中使用 `%s` 占位符（延迟求值），不用 f-string
- 敏感信息（密码、密钥）不输出到日志

---

## 9. 常见反模式

| 反模式 | 正确做法 |
|--------|---------|
| `def f(x=[])` 可变默认参数 | `def f(x=None)` + 内部初始化 |
| 裸 `except:` | 捕获具体异常 |
| `x == None` | `x is None` |
| `type(x) == dict` | `isinstance(x, dict)` |
| `from module import *` | 显式导入具体名称 |
| 循环内字符串 `+=` | `"".join(...)` |
| 忘记关闭资源 | 使用 `with` 语句 |
| 循环内逐条数据库查询 | 批量查询 |
| `assert` 做运行时校验 | 显式 `if` + `raise` |
| 硬编码魔法数字 | 定义为命名常量 |

详细说明及代码对比见 [anti-patterns.md](./references/anti-patterns.md)
