"""
选股程序：X02-X05 微盘股基本面选股
描述：依次调用 4 个选股公式，从 P001 筛选到 P002

前置条件:
1. 通达信客户端已启动并登录
2. 已在客户端中创建以下选股公式:
   - X02_LTSZ100Y: 流通市值小于 100 亿
   - X03_MG_GOOD: 净利润基本面良好
   - X04_MG_GR_Q4: 净利润同比增长且已出四季报/年报
   - X05_GX_BT0: 潜在股息大于 0

使用示例:
    python xg_small_goodfund.py
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# ============================================================================
# 读取配置文件
# ============================================================================
PROJECT_ROOT = Path(__file__).parent

try:
    with open(PROJECT_ROOT / "config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("错误：配置文件 config.yaml 不存在")
    sys.exit(1)
except Exception as e:
    print(f"读取配置文件失败：{e}")
    sys.exit(1)

# ============================================================================
# 初始化通达信
# ============================================================================
TDX_ROOT = config.get("tdx_root", r"D:\App\new_tdx64")
PLUGIN_PATH = os.path.join(TDX_ROOT, "PYPlugins", "user")
sys.path.insert(0, PLUGIN_PATH)

from tqcenter import tq

# 初始化连接
tq.initialize(__file__)

# ============================================================================
# 导入板块管理功能
# ============================================================================
sys.path.insert(0, str(PROJECT_ROOT))
from blocks import (
    get_block_stocks,
    create_block,
    clear_block_stocks,
    add_stocks_to_block,
    get_user_blocks,
)

# ============================================================================
# 固定配置（写死在程序中）
# ============================================================================
BATCH_SIZE = 200
DIVIDEND_TYPE = 1  # 前复权
FILTER_ST = True   # 过滤 ST 股票
STOCK_PERIOD = '1d'
DATA_COUNT = -1    # 获取所有数据

# 选股公式序列
FORMULAS = [
    'X02_LTSZ100Y',   # 流通市值小于 100 亿
    'X03_MG_GOOD',    # 净利润基本面良好
    'X04_MG_GR_Q4',   # 净利润同比增长且已出四季报/年报
    'X05_GX_BT0',     # 潜在股息大于 0
]

# ============================================================================
# 从配置文件读取
# ============================================================================
xg_config = config.get("xg_small_goodfund", {})
SOURCE_BLOCK = xg_config.get("source_block", "P001")
TARGET_BLOCK = xg_config.get("target_block", "P002")
TARGET_BLOCK_NAME = xg_config.get("target_block_name", "P002_微盘股且基本面良好")


# ============================================================================
# 辅助函数
# ============================================================================

def is_st_stock(stock_code: str) -> bool:
    """
    检查股票是否为 ST 股票
    """
    try:
        info = tq.get_stock_info(stock_code, field_list=['Name'])
        if not info:
            return False
        
        name = info.get('Name', '')
        st_markers = ['ST', '*ST', '退', '退市']
        for marker in st_markers:
            if marker in name.upper():
                return True
        
        return False
    except Exception:
        return False


def get_stock_name(stock_code: str) -> str:
    """
    获取股票名称
    """
    try:
        info = tq.get_stock_info(stock_code, field_list=['Name'])
        if info:
            return info.get('Name', '')
        return ''
    except Exception:
        return ''


def select_by_formula(stock_list: list, formula_name: str) -> list:
    """
    使用通达信公式引擎批量选股
    """
    selected = []
    total = len(stock_list)
    
    # 过滤 ST 股票
    non_st_list = [s for s in stock_list if not is_st_stock(s)]
    st_count = len(stock_list) - len(non_st_list)
    
    # 分批处理
    batches = [non_st_list[i:i+BATCH_SIZE] for i in range(0, len(non_st_list), BATCH_SIZE)]
    
    for batch_idx, batch in enumerate(batches, 1):
        batch_selected_count = 0
        
        try:
            result = tq.formula_process_mul_xg(
                formula_name=formula_name,
                formula_arg='',
                return_count=1,
                return_date=False,
                stock_list=batch,
                stock_period=STOCK_PERIOD,
                count=DATA_COUNT,
                dividend_type=DIVIDEND_TYPE
            )
            
            if result and isinstance(result, dict):
                for stock_code, stock_data in result.items():
                    if stock_code == 'ErrorId':
                        continue
                    
                    if isinstance(stock_data, dict):
                        for key, value in stock_data.items():
                            if key in ['XG', 'SELECT', 'BUY', 'OUTPUT', 'OUTPUT1'] and value:
                                if isinstance(value, list) and len(value) > 0:
                                    if str(value[-1]) == '1':
                                        selected.append(stock_code)
                                        batch_selected_count += 1
                                elif str(value) == '1':
                                    selected.append(stock_code)
                                    batch_selected_count += 1
                                    
        except Exception as e:
            pass
    
    return selected


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数：依次调用 4 个选股公式"""
    source_block = SOURCE_BLOCK
    target_block = TARGET_BLOCK
    target_block_name = TARGET_BLOCK_NAME
    
    print()
    print("=" * 70)
    print(f"选股任务：微盘股基本面选股")
    print(f"从板块 {source_block} 筛选到 {target_block}")
    print("=" * 70)
    print()
    
    # 1. 确保目标板块存在
    if not find_block_by_code(target_block):
        print(f"创建板块 '{target_block}' ({target_block_name})...")
        result = create_block(target_block, target_block_name)
        if result.get('ErrorId') == '0':
            print(f"板块创建成功")
        else:
            print(f"板块创建失败：{result.get('Error')}")
            return
    else:
        print(f"板块 '{target_block}' 已存在")
    
    print()
    
    # 2. 获取源板块的成分股
    print(f"获取板块 '{source_block}' 的成分股...")
    
    stock_list = get_block_stocks(source_block, block_type=1)
    
    if not stock_list:
        print(f"板块 '{source_block}' 无成分股或不存在")
        return
    
    print(f"板块 '{source_block}' 共有 {len(stock_list)} 只股票")
    print()
    
    # 3. 依次调用选股公式
    current_stocks = stock_list
    
    for i, formula_name in enumerate(FORMULAS, 1):
        print("=" * 70)
        print(f"步骤 {i}/{len(FORMULAS)}: 调用公式 {formula_name}")
        print("=" * 70)
        
        if not current_stocks:
            print("当前股票池为空，停止选股")
            break
        
        print(f"输入股票数：{len(current_stocks)} 只")
        
        # 执行选股
        selected_stocks = select_by_formula(current_stocks, formula_name)
        
        print(f"输出股票数：{len(selected_stocks)} 只")
        print(f"剔除股票数：{len(current_stocks) - len(selected_stocks)} 只")
        print(f"留存率：{len(selected_stocks)*100//len(current_stocks) if current_stocks else 0}%")
        print()
        
        # 更新股票池
        current_stocks = selected_stocks
    
    # 4. 清空目标板块并添加最终选中的股票
    if current_stocks:
        print("=" * 70)
        print("保存结果")
        print("=" * 70)
        print(f"清空板块 '{target_block}' 中的股票...")
        clear_block_stocks(target_block)
        print(f"添加 {len(current_stocks)} 只股票到板块 '{target_block}'...")
        result = add_stocks_to_block(target_block, current_stocks)
        print(f"操作完成")
        print()
        
        # 显示选中的股票列表（前 20 只）
        print("选中的股票 (前 20 只):")
        print("-" * 70)
        print(f"{'序号':<5} {'股票代码':<12} {'股票名称':<15}")
        print("-" * 70)
        for i, stock in enumerate(current_stocks[:20], 1):
            stock_name = get_stock_name(stock)
            print(f"{i:<5} {stock:<12} {stock_name:<15}")
        if len(current_stocks) > 20:
            print(f"  ... 还有 {len(current_stocks) - 20} 只")
        print("-" * 70)
    else:
        print("未选中任何股票")
    
    # 5. 显示最终结果
    print()
    print("=" * 70)
    print("任务完成")
    print("=" * 70)
    print(f"源板块：{source_block} ({len(stock_list)} 只股票)")
    print(f"最终选中：{len(current_stocks)} 只股票")
    print(f"总留存率：{len(current_stocks)*100//len(stock_list) if stock_list else 0}%")
    if current_stocks:
        print(f"结果已保存到板块 '{target_block}'")
        print(f"可以使用 'python blocks.py info {target_block}' 查看结果")
    print("=" * 70)
    print()


def find_block_by_code(block_code: str) -> bool:
    """检查板块是否存在"""
    blocks = get_user_blocks()
    for block in blocks:
        code = block['Code'] if isinstance(block, dict) else block
        if code == block_code:
            return True
    return False


if __name__ == "__main__":
    main()
