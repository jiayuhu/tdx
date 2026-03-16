# TDX 项目规范说明书 (SPEC.md)

## 1. 项目概述

### 1.1 项目目标
构建一个基于通达信 TdxQuant API 的自动化选股系统，通过配置驱动的方式支持多种选股策略的组合执行，实现从数据获取、策略执行到结果存储和展示的全流程自动化。

### 1.2 项目组成
本项目由两个独立程序组成，通过共享 SQLite 数据库协作：

1. **Python 选股程序**（根目录）
   - 调用通达信 TdxQuant API 执行选股策略
   - 管理通达信自定义板块
   - 将选股结果写入 SQLite 数据库
   - 技术栈：Python 3.14 + SQLite

2. **ASP.NET Core Web 展示程序**（`web/` 目录）
   - 读取共享数据库展示每日选股结果
   - 提供长线/短线板块数据浏览
   - 技术栈：ASP.NET Core 10 + Razor Pages + EF Core + SQLite

### 1.3 项目范围
- **包含**: 股票筛选、板块管理、数据存储、增量跟踪、Web 界面展示
- **不包含**: 实盘交易、风控管理、资金管理、回测系统

### 1.4 核心价值
- **配置驱动**: 通过 YAML 配置文件定义策略，无需修改代码
- **模块化设计**: 各功能模块职责清晰，易于扩展
- **数据可追溯**: 完整记录选股历史和增量变化
- **多策略支持**: 支持单公式、多公式串行、多公式并行等多种策略类型

---

## 2. 架构设计决策

### 2.1 配置驱动架构

**决策**: 使用 YAML 配置文件作为策略定义的唯一真实源

**理由**:
- 业务策略频繁调整，代码修改成本高
- 非技术人员可通过修改配置参与策略调整
- 便于版本控制和回滚

**约束**:
- 所有策略逻辑必须能在配置中表达
- 配置变更需经过测试验证

### 2.2 单例模式管理 TQ 连接

**决策**: 全局单例管理 TdxQuant API 连接

**理由**:
- TQ API 限制同时只能有一个实例
- 避免重复初始化带来的性能损耗
- 简化资源管理和生命周期控制

**实现**:
```python
# base.py
_tq_instance: Optional[Any] = None

def init_tq_context(script_path: str) -> None:
    global _tq_instance
    if _tq_instance is not None:
        return  # 避免重复初始化
    # 初始化逻辑...
```

### 2.3 UTC 时间存储 + 北京时间显示

**决策**: 数据库存储使用 UTC 时间，界面显示转换为北京时间

**理由**:
- UTC 作为标准时间，避免时区混淆
- 北京时间符合用户习惯
- 便于跨时区部署

**实现**:
```python
# database.py
def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# dbview.py
def _to_beijing(utc_str: str) -> str:
    dt = datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S')
    return (dt + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
```

### 2.4 SQLite 作为数据存储

**决策**: 使用 SQLite 本地数据库存储选股结果

**理由**:
- 轻量级，无需独立数据库服务器
- 支持复杂查询和索引
- 便于部署和备份
- 满足当前数据量需求

**约束**:
- 不支持高并发写入
- 单文件存储，注意备份
- 数据库路径固定为 `data/quant.db`，`data/` 目录由程序运行时自动创建且不纳入 Git

---

## 3. 核心算法规范

### 3.1 增量计算算法

**目的**: 跟踪每日选股结果的变化，识别新增和移除的股票

**算法描述**:
```
输入: 当前日期成分股集合 Curr, 前一日成分股集合 Prev
输出: 新增股票集合 Added, 移除股票集合 Removed

Added = Curr - Prev  (今日有但昨日无)
Removed = Prev - Curr  (昨日有但今日无)
```

**实现**:
```python
@staticmethod
def calculate_delta(
    curr_db: Dict[str, str],  # {股票代码: 股票名称}
    prev_db: Dict[str, str],
) -> Tuple[set, set]:
    curr_set = set(curr_db.keys())
    prev_set = set(prev_db.keys())
    added = curr_set - prev_set
    removed = prev_set - curr_set
    return added, removed
```

### 3.2 EMA 买点计算

**目的**: 为新增股票计算买入参考价格

**算法描述**:
```
EMA(C,2) = Close[-1] × (2/3) + Close[-2] × (1/3)

其中:
- Close[-1]: 最新收盘价
- Close[-2]: 前一交易日收盘价
```

**实现**:
```python
@staticmethod
def calculate_buy_point(tq, stock_code: str) -> float:
    result = tq.get_market_data(
        field_list=['Close'],
        stock_list=[stock_code],
        period='1d',
        count=10,
        dividend_type='front',
    )
    close_prices = result['Close'][stock_code].values
    return float(close_prices[-1] * EMA_SHORT_WEIGHT + close_prices[-2] * EMA_LONG_WEIGHT)
```

---

## 4. 配置文件规范

### 4.1 配置结构

```yaml
# 顶层配置
tdx_root: string              # 通达信安装路径
tq_delay_ms: integer          # TQ 操作延时(ms)
xg_programs: list             # 选股策略列表

# 策略配置项
- name: string               # 策略名称（唯一标识）
  desc: string               # 策略描述
  type: enum[single|multi|parallel|db_update]  # 策略类型
  source_block: string       # 源板块代码
  target_block: string       # 目标板块代码
  target_block_name: string  # 目标板块名称
  formula_name: string       # 选股公式名称
  stock_period: enum[1d|1w|1m]  # K线周期
  formulas: list             # 多公式策略的公式列表
  long_term_blocks: list     # 长线板块配置
  short_term_blocks: list    # 短线板块配置
  keep_days: integer         # 数据保留天数
```

### 4.2 配置验证规则

| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|----------|
| name | string | 是 | 非空，唯一 |
| type | enum | 是 | 必须是 single/multi/parallel/db_update |
| source_block | string | 条件 | single/multi/parallel 必填 |
| target_block | string | 条件 | single/multi 必填 |
| formulas | list | 条件 | multi/parallel 必填，至少1项 |
| keep_days | integer | 条件 | db_update 必填，≥1 |

---

## 5. 错误处理规范

### 5.1 异常分类

```python
class SelectionError(Exception):
    """选股相关错误"""
    pass

class DatabaseError(Exception):
    """数据库操作错误"""
    pass

class BlockOperationError(Exception):
    """板块操作错误"""
    pass

class ConfigurationError(Exception):
    """配置错误"""
    pass
```

### 5.2 错误处理原则

1. **具体异常捕获**: 避免使用 bare `except:`
2. **错误日志记录**: 所有异常必须记录到日志
3. **用户友好提示**: 向用户显示清晰的错误信息
4. **优雅降级**: 非致命错误不应终止整个流程

### 5.3 重试机制

```python
def execute_with_retry(func, max_retries=3, delay=1.0):
    """带重试的执行器"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"执行失败，已重试 {max_retries} 次: {e}")
                raise
            logger.warning(f"执行失败，{delay}s 后重试 ({attempt + 1}/{max_retries}): {e}")
            time.sleep(delay)
```

---

## 6. 性能基准

### 6.1 关键性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 单次选股耗时 | ≤ 300ms | 200支股票批量选股 |
| 完整流程耗时 | ≤ 10分钟 | 5个策略全部执行 |
| 数据库写入速度 | ≥ 1000条/秒 | INSERT 操作 |
| 内存使用峰值 | ≤ 500MB | 执行期间监控 |

### 6.2 性能优化策略

1. **批量处理**: TQ API 调用按 200 支股票分批
2. **连接复用**: 数据库连接在单次操作中复用
3. **索引优化**: 为 `record_date` 字段建立索引
4. **延迟加载**: 非必要数据按需加载

---

## 7. 安全规范

### 7.1 数据安全

- **SQL 注入防护**: 所有数据库查询必须参数化
- **输入验证**: 所有外部输入必须验证合法性
- **敏感信息**: 配置文件中的路径信息视为敏感

### 7.2 访问控制

- **文件权限**: `data/quant.db` 设置适当权限（`data/` 目录由程序自动创建）
- **日志过滤**: 错误日志中不输出敏感信息
- **API 限流**: TQ API 调用间保持适当延时

---

## 8. 测试规范

### 8.1 测试覆盖要求

| 模块 | 测试类型 | 覆盖率目标 |
|------|----------|------------|
| base.py | 单元测试 | 80% |
| selector.py | 单元测试 | 75% |
| database.py | 单元测试 + 集成测试 | 85% |
| executor.py | 集成测试 | 90% |
| blocks.py | 单元测试 | 70% |

### 8.2 测试数据管理

- 使用独立的测试数据库
- 提供模拟的 TQ API 响应数据
- 测试前后清理数据

---

## 9. 部署规范

### 9.1 环境要求

**生产环境**:
- Windows Server 2019+
- Python 3.14+
- 通达信客户端稳定运行
- 4GB RAM, 10GB 磁盘空间

**开发环境**:
- Windows 10/11
- Python 3.14+
- 通达信客户端
- IDE 支持 (VS Code/PyCharm)

### 9.2 部署流程

1. 代码拉取/打包
2. 依赖安装 (`pip install -r requirements.txt`)
3. 配置文件检查
4. 数据库初始化
5. 服务启动
6. 健康检查

---

## 10. 维护规范

### 10.1 日常维护任务

| 任务 | 频率 | 负责人 |
|------|------|--------|
| 数据库备份 | 每日 | 运维 |
| 日志轮转 | 每周 | 系统 |
| 性能监控 | 实时 | 系统 |
| 策略效果评估 | 每月 | 业务 |

### 10.2 版本升级流程

1. 功能分支开发
2. 代码审查
3. 测试环境验证
4. 生产环境灰度发布
5. 全量上线
6. 回滚预案准备

---

## 11. 变更历史

| 版本 | 日期 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 1.0.0 | 2026-03-11 | 初始版本 | Qoder |
| 1.1.0 | TBD | 添加 Web 界面 | TBD |
