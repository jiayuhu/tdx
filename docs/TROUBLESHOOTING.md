# TDX 故障排除手册 (TROUBLESHOOTING.md)

## 目录
1. [通用排查方法](#1-通用排查方法)
2. [TQ 相关问题](#2-tq-相关问题)
3. [数据库问题](#3-数据库问题)
4. [选股逻辑问题](#4-选股逻辑问题)
5. [性能问题](#5-性能问题)
6. [部署问题](#6-部署问题)
7. [Web 界面问题](#7-web-界面问题)

---

## 1. 通用排查方法

### 1.1 启用调试模式

```bash
# 增加日志级别
set LOG_LEVEL=DEBUG
uv run python xg.py --strategy test_strategy

# 或在代码中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 1.2 查看错误日志

```bash
# 实时查看日志
Get-Content xg.log -Wait

# 搜索错误信息
Select-String -Path xg.log -Pattern "ERROR" -Context 3

# 按时间过滤
Get-Content xg.log | Select-String "2026-03-11"
```

### 1.3 环境检查脚本

```python
# diagnose.py
def check_environment():
    import sys
    import os
    from base import get_config, get_tq
    
    print("=== 环境诊断 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查配置
    try:
        config = get_config()
        print("✓ 配置文件加载成功")
        print(f"  TDX路径: {config.get('tdx_root')}")
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
    
    # 检查TQ连接
    try:
        tq = get_tq()
        if tq:
            print("✓ TQ连接正常")
        else:
            print("✗ TQ未初始化")
    except Exception as e:
        print(f"✗ TQ连接失败: {e}")

if __name__ == "__main__":
    check_environment()
```

---

## 2. TQ 相关问题

### 2.1 TQ 初始化失败

**错误信息**:
```
TQ 数据接口初始化失败
```

**可能原因**:
1. 通达信客户端未启动
2. 配置路径错误
3. TQ DLL 文件缺失
4. 权限不足

**解决方案**:
```bash
# 1. 检查通达信状态
tasklist | findstr tdx

# 2. 验证配置路径
uv run python -c "from base import init_tq_context, get_config; init_tq_context('xg.py'); print(get_config()['tdx_root'])"

# 3. 手动测试 TQ 导入
uv run python -c "import sys; sys.path.insert(0, 'D:/通达信路径/PYPlugins/user'); from tqcenter import tq; print('TQ导入成功')"

# 4. 以管理员身份运行
```

### 2.2 公式执行异常

**错误信息**:
```
选股异常：FORMULA_NAME - 具体错误信息
```

**排查步骤**:
1. **验证公式存在性**
   ```python
   # 在通达信中手动测试公式
   # 公式管理器 → 条件选股 → 选择对应公式 → 测试
   ```

2. **检查公式名称**
   ```yaml
   # config.yaml 中的名称必须与通达信中完全一致
   formula_name: "精确的公式名称"
   ```

3. **验证股票代码格式**
   ```python
   # TQ 要求 6 位数字代码
   # 错误: "SH600000"  正确: "600000"
   ```

### 2.3 板块操作失败

**错误信息**:
```json
{"ErrorId": "1", "ErrorMsg": "错误描述"}
```

**常见错误码**:
- `ErrorId: "1"` - 板块不存在
- `ErrorId: "2"` - 权限不足
- `ErrorId: "3"` - 参数错误

**解决方案**:
```python
# 检查板块是否存在
uv run python blocks.py list

# 手动创建板块
uv run python blocks.py create X99 "测试板块"

# 增加操作延时
# config.yaml
tq_delay_ms: 200  # 从 100 增加到 200
```

---

## 3. 数据库问题

### 3.1 数据库锁定

**错误信息**:
```
database is locked
```

**原因分析**:
- 多个进程同时写入数据库
- 未正确关闭数据库连接
- 长时间事务未提交

**解决方案**:
```bash
# 1. 查找占用进程
tasklist | findstr python

# 2. 检查数据库连接
sqlite3 data/quant.db ".database"

# 3. 强制解锁（谨慎使用）
cp data/quant.db data/quant.db.backup
sqlite3 data/quant.db "PRAGMA wal_checkpoint(TRUNCATE);"

# 4. 代码层面改进
# 使用上下文管理器确保连接关闭
with sqlite3.connect(db_path) as conn:
    # 数据库操作
    conn.commit()  # 显式提交
```

### 3.2 数据查询异常

**症状**: 查询结果为空或不正确

**排查方法**:
```sql
-- 1. 检查表结构
.schema b01

-- 2. 验证数据存在性
SELECT COUNT(*) FROM b01 WHERE date(record_date) = '2026-03-10';

-- 3. 检查日期格式
SELECT DISTINCT date(record_date) FROM b01 ORDER BY date(record_date) DESC LIMIT 5;

-- 4. 使用 dbview.py 交互查询
uv run python dbview.py
```

### 3.3 磁盘空间不足

**错误信息**:
```
database or disk is full
```

**解决方案**:
```bash
# 1. 检查磁盘空间
df -h  # Linux
Get-PSDrive C  # Windows

# 2. 清理旧数据
uv run python dbclear.py --days 30

# 3. 压缩数据库
sqlite3 data/quant.db "VACUUM;"
```

---

## 4. 选股逻辑问题

### 4.1 选股结果为 0

**排查步骤**:

1. **验证源数据**
   ```bash
   # 检查源板块是否有股票
   uv run python blocks.py info AAA
   ```

2. **手动测试公式**
   ```python
   # 在通达信中验证公式逻辑
   # K线图 → 公式管理器 → 选择公式 → 应用到图表
   ```

3. **检查 ST 过滤**
   ```python
   # 临时禁用 ST 过滤测试
   selector.select_by_formula(stocks, formula, filter_st=False)
   ```

4. **验证参数设置**
   ```yaml
   # 检查 K线周期是否正确
   stock_period: "1d"  # 日线
   stock_period: "1w"  # 周线
   ```

### 4.2 增量计算异常

**症状**: 新增股票数量异常

**调试方法**:
```python
# 1. 查看历史数据
uv run python dbview.py --search b01 "date(record_date) BETWEEN '2026-03-08' AND '2026-03-10'"

# 2. 手动计算增量
uv run python -c "
from database import StockDatabase
db = StockDatabase('./data/quant.db')
curr = db.get_stocks_by_date('b01', '2026-03-10')
prev = db.get_stocks_by_date('b01', '2026-03-09')
added, removed = db.calculate_delta(curr, prev)
print(f'新增: {len(added)}, 移除: {len(removed)}')
"

# 3. 验证时间一致性
# 确保所有记录使用相同的 UTC 时间标准
```

### 4.3 买点计算偏差

**症状**: EMA(C,2) 计算结果与预期不符

**验证方法**:
```python
# 1. 手动计算验证
python -c "
import numpy as np
prices = [10.0, 10.5, 11.0]  # 示例价格序列
ema = prices[-1] * (2/3) + prices[-2] * (1/3)
print(f'计算结果: {ema}')
"

# 2. 与通达信对比
# 通达信公式: EMA(C,2)
# 确认复权方式一致（前复权）
```

---

## 5. 性能问题

### 5.1 执行速度慢

**性能分析工具**:
```python
import time
import cProfile
import pstats

def profile_function():
    # 要分析的函数
    pass

# 性能分析
cProfile.run('profile_function()', 'profile.stats')

# 查看结果
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative').print_stats(10)
```

**常见性能瓶颈**:

1. **TQ API 调用**
   ```python
   # 优化：减少 API 调用次数
   # 批量获取股票信息而不是逐个查询
   ```

2. **数据库操作**
   ```sql
   -- 添加索引优化查询
   CREATE INDEX IF NOT EXISTS idx_table_date ON table_name(date(record_date));
   ```

3. **内存使用**
   ```python
   # 分批处理大数据集
   def process_in_batches(data, batch_size=1000):
       for i in range(0, len(data), batch_size):
           batch = data[i:i+batch_size]
           process_batch(batch)
   ```

### 5.2 内存泄漏

**检测方法**:
```python
import tracemalloc

tracemalloc.start()

# 执行可能泄漏的代码
function_that_might_leak()

# 查看内存分配
current, peak = tracemalloc.get_traced_memory()
print(f"当前内存: {current / 1024 / 1024:.1f} MB")
print(f"峰值内存: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

**常见泄漏点**:
- 未关闭的数据库连接
- 全局变量累积
- 缓存未清理

---

## 6. 部署问题

### 6.1 依赖安装失败

**错误信息**:
```
Could not find a version that satisfies the requirement
```

**解决方案**:
```bash
# 1. 更新 pip 和 uv
uv run python -m pip install --upgrade pip
pip install uv --upgrade

# 2. 使用国内镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 检查 Python 版本兼容性
python --version  # 确保 >= 3.14
```

### 6.2 路径问题

**Windows 路径错误**:
```python
# 错误
path = "D:\App\new_tdx64"  # \n 被解释为换行符

# 正确
path = r"D:\App\new_tdx64"  # 原始字符串
# 或
path = "D:\\App\\new_tdx64"  # 双反斜杠
```

### 6.3 权限问题

```bash
# 以管理员身份运行 PowerShell
Start-Process PowerShell -Verb RunAs

# 或修改文件权限
icacls data /grant Users:F
```

---

## 7. Web 界面问题

### 7.1 服务无法启动

**错误信息**:
```
Address already in use
```

**解决方案**:
```bash
# 1. 查找占用端口的进程
netstat -ano | findstr :5000

# 2. 结束占用进程
taskkill /PID <进程ID> /F

# 3. 更改端口
# start_web.bat
dotnet run --project web --urls "http://localhost:5001"
```

### 7.2 页面加载缓慢

**优化建议**:
```csharp
// 1. 使用 IMemoryCache 缓存热点查询
// 2. 在 Razor Pages 中进行分页查询，限制单次返回记录数
```

### 7.3 API 接口错误

**调试方法**:
```javascript
// 前端调试
fetch('/api/stocks')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// 后端日志
// 查看 dotnet 运行日志输出
```

---

## 附录

### A. 快速诊断脚本

```bash
#!/bin/bash
# quick_diagnose.sh

echo "=== TDX 系统诊断 ==="
date

echo "1. 检查进程..."
pgrep -f "python.*xg" && echo "✓ 选股服务运行中" || echo "✗ 选股服务未运行"

echo "2. 检查数据库..."
sqlite3 data/quant.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" && echo "✓ 数据库连接正常" || echo "✗ 数据库连接失败"

echo "3. 检查磁盘空间..."
df -h . | awk 'NR==2 {print "可用空间:", $4}'

echo "4. 检查最近错误..."
tail -10 xg.log | grep ERROR

echo "诊断完成"
```

### B. 应急联系清单

- **技术支持**: support@example.com
- **紧急电话**: 400-xxx-xxxx
- **备用方案**: 手动在通达信客户端执行选股

### C. 版本兼容性矩阵

| TDX版本 | Python版本 | uv版本 | 兼容性 |
|---------|------------|---------|--------|
| 1.0.0   | 3.14+      | 0.1.0+  | ✓ 完全兼容 |
| 0.9.x   | 3.12-3.13  | 0.1.0+  | ⚠ 部分功能受限 |
