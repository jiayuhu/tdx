# Python 常见反模式

## 1. 可变默认参数

```python
# 错误：列表在函数定义时创建一次，后续调用共享同一对象
def add_item(item, items=[]):
    items.append(item)
    return items

# 正确：使用 None 作为哨兵值
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## 2. 裸 except 捕获

```python
# 错误：捕获所有异常，包括 KeyboardInterrupt、SystemExit
try:
    process()
except:
    pass

# 错误：捕获 Exception 但静默忽略
try:
    process()
except Exception:
    pass

# 正确：捕获具体异常
try:
    process()
except (ValueError, FileNotFoundError) as e:
    logger.error(f"处理失败：{e}")

# 如果确实需要捕获所有异常，必须加注释
try:
    cleanup()
except Exception:
    pass  # 清理操作失败可以忽略，不影响主流程
```

## 3. 使用 == 比较 None

```python
# 错误
if x == None:
if x != None:

# 正确：使用 is / is not
if x is None:
if x is not None:
```

## 4. 使用 type() 做类型检查

```python
# 错误：不支持继承
if type(obj) == dict:

# 正确：支持继承
if isinstance(obj, dict):
```

## 5. import * 污染命名空间

```python
# 错误：不清楚导入了什么，可能覆盖已有名称
from os.path import *
from utils import *

# 正确：显式导入
from os.path import join, exists
from utils import validate_config
```

## 6. 循环中拼接字符串

```python
# 错误：每次拼接创建新字符串对象，O(n^2)
result = ""
for item in items:
    result += str(item) + ", "

# 正确：使用 join
result = ", ".join(str(item) for item in items)
```

## 7. 忘记关闭资源

```python
# 错误：异常时文件不会关闭
f = open("data.txt")
data = f.read()
f.close()

# 正确：with 语句保证关闭
with open("data.txt") as f:
    data = f.read()

# 数据库连接同理
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    # ...
```

## 8. 过度使用全局变量

```python
# 错误：全局可变状态，难以测试和调试
config = {}
db = None

def init():
    global config, db
    config = load_config()
    db = connect()

# 正确：封装为类或使用依赖注入
class AppContext:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.db = connect(self.config['db_path'])
```

## 9. 不检查函数返回值

```python
# 错误：忽略可能返回 None 的函数
stocks = get_selected_stocks()
for s in stocks:  # stocks 可能是 None → TypeError
    print(s)

# 正确：检查返回值
stocks = get_selected_stocks()
if stocks:
    for s in stocks:
        print(s)
```

## 10. 在循环中频繁查询数据库

```python
# 错误：N+1 查询问题
for code in stock_codes:
    cursor.execute("SELECT name FROM stocks WHERE code = ?", (code,))
    name = cursor.fetchone()

# 正确：批量查询
placeholders = ",".join("?" * len(stock_codes))
cursor.execute(
    f"SELECT code, name FROM stocks WHERE code IN ({placeholders})",
    stock_codes
)
results = {row[0]: row[1] for row in cursor.fetchall()}
```

## 11. 用 assert 做运行时校验

```python
# 错误：assert 在 -O 模式下会被移除
def withdraw(amount):
    assert amount > 0, "金额必须为正"

# 正确：使用显式校验
def withdraw(amount):
    if amount <= 0:
        raise ValueError("金额必须为正")
```

## 12. 硬编码魔法数字

```python
# 错误：含义不明
if len(stocks) > 500:
    time.sleep(3)

# 正确：定义为常量
BATCH_SIZE = 500
API_COOLDOWN_SECONDS = 3

if len(stocks) > BATCH_SIZE:
    time.sleep(API_COOLDOWN_SECONDS)
```
