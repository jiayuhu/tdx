# 通达信 TdxQuant 选股系统

基于通达信 TdxQuant API 的自动化选股系统，支持多策略组合选股。

## 系统架构

```
AAA (1054 支)
 │
 ├─ [1] below240w        : AAA → X01 (低于五年周线)
 │
 ├─ [2] small_goodfund   : X01 → X02 (微盘股基本面选股)
 │    ├─ X02_LTSZ100Y    : 流通市值 < 100 亿
 │    ├─ X03_MG_GOOD     : 净利润基本面良好
 │    ├─ X04_MG_GR_Q4    : 净利润同比增长且已出四季报/年报
 │    └─ X05_GX_BT0      : 潜在股息 > 0
 │
 ├─ [3] buy_kdj_small    : X02 → B00/B01/B02 (KDJ 买入信号)
 │    ├─ B00_KDJ5W       : KDJ 五周线
 │    ├─ B01_KDJ_DJC     : KDJ 低金叉
 │    └─ B02_KDJ_GJC     : KDJ 高金叉
 │
 ├─ [4] buy_kdj_aaa      : AAA → BA1/BA2 (AAA 板块 KDJ)
 │    ├─ B01_KDJ_DJC     : KDJ 低金叉
 │    └─ B02_KDJ_GJC     : KDJ 高金叉
 │
 └─ [5] db_update        : 数据库更新 (记录每日增量)
      ├─ B01 → B01_delta
      ├─ B02 → B02_delta
      ├─ BA1 → BA1_delta
      └─ BA2 → BA2_delta
```

## 快速开始

### 执行全部选股策略

```bash
uv run python xg.py
```

### 执行单个策略

```bash
# 低于五年周线
uv run python xg.py --strategy below240w

# 微盘股基本面选股
uv run python xg.py --strategy small_goodfund

# KDJ 买入信号（微盘股）
uv run python xg.py --strategy buy_kdj_small

# KDJ 买入信号（AAA 板块）
uv run python xg.py --strategy buy_kdj_aaa

# 数据库更新
uv run python xg.py --strategy db_update
```

### 执行多个策略

```bash
uv run python xg.py --strategy below240w small_goodfund
```

### 查看策略列表

```bash
uv run python xg.py --list
```

### 查看策略详情

```bash
uv run python xg.py --info below240w
uv run python xg.py --info small_goodfund
uv run python xg.py --info buy_kdj_small
```

### 板块管理

```bash
# 列出所有板块
uv run python blocks.py list

# 查看板块详情
uv run python blocks.py info X01
uv run python blocks.py info B00
```

### 数据库管理

```bash
# 查看数据库表
uv run python dbview.py --tables

# 查看表结构
uv run python dbview.py --schema b01

# 查看表数据
uv run python dbview.py --data b01 -n 20

# 清空数据库
uv run python dbclear.py
```

## 选股策略

### 1. below240w - 低于五年周线

**选股条件**：
- 收盘价低于 240 周均线（约 5 年）
- 前复权数据
- 自动过滤 ST 股票

**配置**：
- 源板块：AAA
- 目标板块：X01
- 选股公式：X01_BELOW240W
- K 线周期：周线 (1w)

### 2. small_goodfund - 微盘股基本面选股

**选股流程**（4 步筛选）：
1. X02_LTSZ100Y: 流通市值 < 100 亿
2. X03_MG_GOOD: 净利润基本面良好
3. X04_MG_GR_Q4: 净利润同比增长且已出四季报/年报
4. X05_GX_BT0: 潜在股息 > 0

**配置**：
- 源板块：X01
- 目标板块：X02

### 3. buy_kdj_small - KDJ 买入信号（微盘股）

**选股公式**（3 个独立输出）：
- B00_KDJ5W: KDJ 五周线（周线）
- B01_KDJ_DJC: KDJ 低金叉（日线）
- B02_KDJ_GJC: KDJ 高金叉（日线）

**配置**：
- 源板块：X02
- 目标板块：B00, B01, B02

### 4. buy_kdj_aaa - KDJ 买入信号（AAA 板块）

**选股公式**（2 个独立输出）：
- B01_KDJ_DJC: KDJ 低金叉（日线）
- B02_KDJ_GJC: KDJ 高金叉（日线）

**配置**：
- 源板块：AAA
- 目标板块：BA1, BA2

### 5. db_update - 数据库更新

**功能**：
- 从通达信获取当前板块数据并保存到数据库
- 比较最近两天的数据计算增量
- 长线选股板块 (B01, B02) 的增量股票加入 B01_delta/B02_delta
- 短线选股板块 (BA1, BA2) 的增量股票加入 BA1_delta/BA2_delta
- 记录买点 (EMA(C,2)) 和入选日期

**配置**：
- 长线板块：B01, B02
- 短线板块：BA1, BA2
- 数据保留：10 天

## 配置文件

编辑 `config.yaml` 修改参数：

```yaml
# 通达信根目录
tdx_root: "D:\\App\\new_tdx64"

# 选股程序执行列表
xg_programs:
  - name: "below240w"
    desc: "低于五年周线 (AAA → X01)"
    type: "single"
    source_block: "AAA"
    target_block: "X01"
    target_block_name: "X01_低于五年周线"
    formula_name: "X01_BELOW240W"
    stock_period: "1w"

  - name: "small_goodfund"
    desc: "微盘股基本面选股 (X01 → X02)"
    type: "multi"
    source_block: "X01"
    target_block: "X02"
    target_block_name: "X02_微盘股且基本面良好"
    formulas:
      - "X02_LTSZ100Y"
      - "X03_MG_GOOD"
      - "X04_MG_GR_Q4"
      - "X05_GX_BT0"

  - name: "buy_kdj_small"
    desc: "KDJ 买入信号 (X02 → B00/B01/B02)"
    type: "parallel"
    source_block: "X02"
    formulas:
      - formula_name: "B00_KDJ5W"
        target_block: "B00"
        target_block_name: "B00_KDJ5W"
        stock_period: "1w"
      - formula_name: "B01_KDJ_DJC"
        target_block: "B01"
        target_block_name: "B01_KDJ_低金叉"
        stock_period: "1d"

  - name: "buy_kdj_aaa"
    desc: "AAA 板块 KDJ (AAA → BA1/BA2)"
    type: "parallel"
    source_block: "AAA"
    formulas:
      - formula_name: "B01_KDJ_DJC"
        target_block: "BA1"
        target_block_name: "BA1_KDJ_低金叉"
        stock_period: "1d"
      - formula_name: "B02_KDJ_GJC"
        target_block: "BA2"
        target_block_name: "BA2_KDJ_高金叉"
        stock_period: "1d"

  - name: "db_update"
    desc: "数据库更新 (记录增量股票)"
    type: "db_update"
    long_term_blocks:
      - code: "B01"
        target_block: "B01_delta"
    short_term_blocks:
      - code: "BA1"
        target_block: "BA1_delta"
    keep_days: 10
```

## 策略类型说明

| 类型 | 说明 | 配置项 |
|------|------|--------|
| `single` | 单公式选股 | `source_block`, `target_block`, `formula_name`, `stock_period` |
| `multi` | 多公式串行选股 | `source_block`, `target_block`, `formulas` (公式列表) |
| `parallel` | 多公式并行选股 | `source_block`, `formulas` (每项包含 `formula_name`, `target_block`, `stock_period`) |
| `db_update` | 数据库更新 | `long_term_blocks`, `short_term_blocks`, `keep_days` |

## 项目结构

```
tdx/
├── config.yaml              # 配置文件（唯一定义选股逻辑）
├── xg.py                    # 选股总入口（支持命令行参数）
├── xg_base.py               # 公共模块（TQ 单例管理、选股引擎）
├── blocks.py                # 板块管理工具
├── dbview.py                # 数据库查看工具
├── dbclear.py               # 清空数据库工具
├── pyproject.toml           # Python 项目配置
└── README.md                # 项目说明
```

## 输出示例

```
==================================================
通达信选股程序
==================================================
开始：2026-03-10 14:00:00
执行顺序:
  1. 低于五年周线 (AAA → X01)
  2. 微盘股基本面选股 (X01 → X02)
  3. KDJ 买入信号 (X02 → B00/B01/B02)
  4. AAA 板块 KDJ (AAA → BA1/BA2)
  5. 数据库更新 (记录增量股票)
==================================================

[步骤 1/5] 低于五年周线 (AAA → X01)
  策略：below240w
板块 'X01' 已存在，清空板块中的股票...
获取板块 'AAA' 的成分股...
源板块：AAA (1054 支)
  [OK] 执行成功 (X01: 83 支)

[步骤 2/5] 微盘股基本面选股 (X01 → X02)
  策略：small_goodfund
板块 'X02' 已存在，清空板块中的股票...
获取板块 'X01' 的成分股...
源板块：X01 (84 支)
步骤 1/4: X02_LTSZ100Y → 62 支 (73%)
步骤 2/4: X03_MG_GOOD → 57 支 (91%)
步骤 3/4: X04_MG_GR_Q4 → 31 支 (54%)
步骤 4/4: X05_GX_BT0 → 31 支 (100%)
  [OK] 执行成功 (X02: 31 支)

[步骤 3/5] KDJ 买入信号 (X02 → B00/B01/B02)
  策略：buy_kdj_small
获取板块 'X02' 的成分股...
源板块：X02 (31 支)
板块 'B00' 已存在，清空板块中的股票...
B00 (B00_KDJ5W): 10 支 (1w)
板块 'B01' 已存在，清空板块中的股票...
B01 (B01_KDJ_低金叉): 1 支 (1d)
板块 'B02' 已存在，清空板块中的股票...
B02 (B02_KDJ_高金叉): 1 支 (1d)
  [OK] 执行成功 (B00: 10 支，B01: 1 支，B02: 1 支)

[步骤 4/5] AAA 板块 KDJ (AAA → BA1/BA2)
  策略：buy_kdj_aaa
获取板块 'AAA' 的成分股...
源板块：AAA (1054 支)
板块 'BA1' 已存在，清空板块中的股票...
BA1 (BA1_KDJ_低金叉): 9 支 (1d)
板块 'BA2' 已存在，清空板块中的股票...
BA2 (BA2_KDJ_高金叉): 16 支 (1d)
  [OK] 执行成功 (BA1: 9 支，BA2: 16 支)

[步骤 5/5] 数据库更新 (记录增量股票)
  策略：db_update
  [OK] 执行成功 (B01: 1 新增，B02: 1 新增，BA1: 9 新增，BA2: 16 新增)

选股结果汇总:
======================================================================

策略：below240w
  源板块：AAA (1054 支)
  → X01 (X01_低于五年周线): 84 支

策略：small_goodfund
  源板块：X01 (84 支)
  → X02 (X02_微盘股且基本面良好): 31 支

策略：buy_kdj_small
  源板块：X02 (31 支)
  → B00 (B00_KDJ5W): 10 支
  → B01 (B01_KDJ_低金叉): 1 支
  → B02 (B02_KDJ_高金叉): 1 支

策略：buy_kdj_aaa
  源板块：AAA (1054 支)
  → BA1 (BA1_KDJ_低金叉): 9 支
  → BA2 (BA2_KDJ_高金叉): 16 支

======================================================================
最终板块持股统计:
----------------------------------------------------------------------
板块         板块名称               数量
----------------------------------------------------------------------
X01        X01_低于五年周线           84
X02        X02_微盘股且基本面良好        31
B00        B00_KDJ5W               10
B01        B01_KDJ_低金叉            1
B02        B02_KDJ_高金叉            1
BA1        BA1_KDJ_低金叉            9
BA2        BA2_KDJ_高金叉           16
----------------------------------------------------------------------
======================================================================
==================================================
完成：5/5 成功
结束：2026-03-10 14:05:00
[OK] 所有程序执行成功！
==================================================
```

## 前置条件

1. **通达信客户端**：已安装并登录
2. **选股公式**：已在通达信客户端中创建以下公式：
   - X01_BELOW240W: 收盘价低于 240 周均线
   - X02_LTSZ100Y: 流通市值小于 100 亿
   - X03_MG_GOOD: 净利润基本面良好
   - X04_MG_GR_Q4: 净利润同比增长且已出四季报/年报
   - X05_GX_BT0: 潜在股息大于 0
   - B00_KDJ5W: KDJ 五周线
   - B01_KDJ_DJC: KDJ 低金叉
   - B02_KDJ_GJC: KDJ 高金叉

## 注意事项

1. **数据刷新**：运行选股前建议在通达信客户端中刷新盘后数据
2. **公式创建**：所有选股公式需要在通达信客户端中预先创建
3. **ST 过滤**：程序会自动过滤 ST 股票
4. **复权设置**：默认使用前复权数据
5. **执行时间**：完整流程约需 5-10 分钟（取决于股票数量和网络状况）
6. **TQ 管理**：系统使用单一 TQ 实例，由 `xg.py` 统一管理

## 常见问题

**Q: 提示"TQ 数据接口初始化失败"**
A: 请确保通达信客户端已启动并登录，且没有其他 Python 脚本正在使用 TQ 接口。

**Q: 选股结果为 0**
A: 检查通达信客户端中是否已创建对应的选股公式，公式名称是否正确。

**Q: 如何修改选股参数**
A: 编辑 `config.yaml` 文件，修改对应策略的配置参数。

**Q: 如何添加新的选股策略**
A: 在 `config.yaml` 的 `xg_programs` 列表中添加新的策略配置，无需修改代码。

## 许可证

MIT License
