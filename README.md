# 通达信 TdxQuant 选股系统

基于通达信 TdxQuant API 的自动化选股系统，支持多策略组合选股。

## 系统架构

```
AAA (1054 只)
 │
 ├─ [1] xg_below240w.py
 │   └─→ X01 (低于五年周线)
 │        │
 │        └─ [2] xg_small_goodfund.py
 │             └─→ X02 (微盘股且基本面良好)
 │                  │
 │                  └─ [3] xg_buy_small_goodfund.py
 │                       ├─→ B00 (KDJ5W)
 │                       ├─→ B01 (KDJ 低金叉)
 │                       └─→ B02 (KDJ 高金叉)
 │
 └─ [4] xg_buy_aaa_kdj.py (独立)
      ├─→ BA1 (KDJ 低金叉)
      └─→ BA2 (KDJ 高金叉)
```

## 快速开始

### 一键运行全部选股程序

```bash
# 方式 1：使用总入口
uv run python xg.py

# 方式 2：使用 main.py
uv run python main.py --run
```

### 查看板块统计

```bash
uv run python main.py --status
```

### 查看帮助

```bash
uv run python main.py --help
```

## 选股策略

### 1. 低于五年周线 (`xg_below240w.py`)

**选股条件**：
- 收盘价低于 240 周均线（约 5 年）
- 前复权数据
- 自动过滤 ST 股票

**配置**：
- 源板块：AAA
- 目标板块：X01

```bash
uv run python xg_below240w.py
```

### 2. 微盘股基本面筛选 (`xg_small_goodfund.py`)

**选股流程**（4 步筛选）：
1. X02_LTSZ100Y: 流通市值 < 100 亿
2. X03_MG_GOOD: 净利润基本面良好
3. X04_MG_GR_Q4: 净利润同比增长且已出四季报/年报
4. X05_GX_BT0: 潜在股息 > 0

**配置**：
- 源板块：X01
- 目标板块：X02

```bash
uv run python xg_small_goodfund.py
```

### 3. KDJ 买入信号 - 微盘股 (`xg_buy_small_goodfund.py`)

**选股公式**（3 个独立输出）：
- B00_KDJ5W: KDJ 五周线（周线）
- B01_KDJ_DJC: KDJ 低金叉（日线）
- B02_KDJ_GJC: KDJ 高金叉（日线）

**配置**：
- 源板块：X02
- 目标板块：B00, B01, B02

```bash
uv run python xg_buy_small_goodfund.py
```

### 4. KDJ 买入信号 - AAA 直选 (`xg_buy_aaa_kdj.py`)

**选股公式**（2 个独立输出）：
- B01_KDJ_DJC: KDJ 低金叉（日线）
- B02_KDJ_GJC: KDJ 高金叉（日线）

**配置**：
- 源板块：AAA
- 目标板块：BA1, BA2

```bash
uv run python xg_buy_aaa_kdj.py
```

## 配置文件

编辑 `config.yaml` 修改参数：

```yaml
# 通达信根目录
tdx_root: "D:\\App\\new_tdx64"

# 各选股程序的配置
xg_below240w:
  source_block: "AAA"
  target_block: "X01"
  target_block_name: "X01_低于五年周线"

xg_small_goodfund:
  source_block: "X01"
  target_block: "X02"
  target_block_name: "X02_微盘股且基本面良好"

xg_buy_small_goodfund:
  formulas:
    - formula_name: "B00_KDJ5W"
      source_block: "X02"
      target_block: "B00"
      stock_period: "1w"
    # ... 更多配置

xg_buy_aaa_kdj:
  formulas:
    - formula_name: "B01_KDJ_DJC"
      source_block: "AAA"
      target_block: "BA1"
      stock_period: "1d"
    # ... 更多配置
```

## 板块管理

```bash
# 列出所有板块
uv run python blocks.py list

# 查看板块详情
uv run python blocks.py info X01
uv run python blocks.py info X02
uv run python blocks.py info B00
uv run python blocks.py info B01
uv run python blocks.py info B02
uv run python blocks.py info BA1
uv run python blocks.py info BA2
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

## 项目结构

```
tdx/
├── config.yaml              # 配置文件
├── xg.py                    # 选股总入口（一键运行全部）
├── main.py                  # 主程序（菜单 + 快捷命令）
├── blocks.py                # 板块管理工具
├── xg_below240w.py          # 选股 1：低于五年周线
├── xg_small_goodfund.py     # 选股 2：微盘股基本面
├── xg_buy_small_goodfund.py # 选股 3：KDJ 买入 (X02)
├── xg_buy_aaa_kdj.py        # 选股 4：KDJ 买入 (AAA)
├── pyproject.toml           # Python 项目配置
└── README.md                # 项目说明
```

## 输出示例

```
======================================================================
选股结果汇总
======================================================================

选股流程:
----------------------------------------------------------------------

程序：xg_below240w.py
  源板块：AAA (89 只)
  目标板块:
    - X01: 89 只

程序：xg_small_goodfund.py
  源板块：X01 (89 只)
  目标板块:
    - X02: 30 只

程序：xg_buy_small_goodfund.py
  源板块：X02 (30 只)
  目标板块:
    - B00: 8 只
    - B01: 2 只
    - B02: 1 只

程序：xg_buy_aaa_kdj.py
  源板块：AAA (1054 只)
  目标板块:
    - BA1: 35 只
    - BA2: 22 只

----------------------------------------------------------------------

最终板块持股统计:
----------------------------------------------------------------------

板块代码       来源程序                            股票数量
--------------------------------------------------
B00        xg_buy_small_goodfund.py           8
B01        xg_buy_small_goodfund.py           2
B02        xg_buy_small_goodfund.py           1
BA1        xg_buy_aaa_kdj.py                 35
BA2        xg_buy_aaa_kdj.py                 22
X01        xg_below240w.py                   89
X02        xg_small_goodfund.py              30
----------------------------------------------------------------------
```

## 注意事项

1. **数据刷新**：运行选股前建议在通达信客户端中刷新盘后数据
2. **公式创建**：所有选股公式需要在通达信客户端中预先创建
3. **ST 过滤**：程序会自动过滤 ST 股票
4. **复权设置**：默认使用前复权数据
5. **执行时间**：完整流程约需 5-10 分钟（取决于股票数量和网络状况）

## 常见问题

**Q: 提示"TQ 数据接口初始化失败"**
A: 请确保通达信客户端已启动并登录，且没有其他 Python 脚本正在使用 TQ 接口。

**Q: 选股结果为 0**
A: 检查通达信客户端中是否已创建对应的选股公式，公式名称是否正确。

**Q: 如何修改选股参数**
A: 编辑 `config.yaml` 文件，修改对应程序的配置参数。

## 许可证

MIT License
