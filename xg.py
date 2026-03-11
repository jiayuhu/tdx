"""
选股程序总入口
支持配置驱动的选股策略执行

使用示例:
    # 执行全部策略
    python xg.py
    
    # 执行单个策略
    python xg.py --strategy below240w
    python xg.py --strategy small_goodfund
    python xg.py --strategy buy_kdj_small
    python xg.py --strategy buy_kdj_aaa
    python xg.py --strategy db_update
    
    # 执行多个策略
    python xg.py --strategy below240w --strategy small_goodfund
    
    # 列出所有策略
    python xg.py --list
    
    # 查看策略详情
    python xg.py --info below240w
"""

import sys
import argparse
from datetime import datetime
from typing import List, Dict

from base import init_tq_context, close_tq_context, get_tq, get_config
from selector import StockSelector
from blocks import BlockManager
from executor import execute_strategy


# ============================================================================
# 辅助函数
# ============================================================================

def print_header():
    """打印程序头部信息"""
    print("\n" + "=" * 50)
    print("通达信选股程序")
    print("=" * 50)
    print(f"开始：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def print_footer(success_count: int, total: int):
    """打印程序尾部信息"""
    print("=" * 50)
    print(f"完成：{success_count}/{total} 成功")
    print(f"结束：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success_count == total:
        print("[OK] 所有程序执行成功！")
    else:
        print(f"[WARN] {total - success_count} 个程序失败，请检查日志")
    print("=" * 50)


def print_summary(block_manager: BlockManager, strategies: List[Dict]) -> None:
    """
    打印选股结果汇总
    直接查询通达信板块数据
    
    Args:
        block_manager: BlockManager 实例
        strategies: 策略配置列表（从 config.yaml 读取）
    """
    print("\n选股结果汇总:")
    print("=" * 70)

    # 从策略配置中提取源板块和目标板块
    strategy_blocks = []
    for strategy in strategies:
        strategy_type = strategy.get('type', 'single')
        
        if strategy_type in ('single', 'multi'):
            source = strategy.get('source_block')
            target = strategy.get('target_block')
            target_name = strategy.get('target_block_name', '')
            if source and target:
                strategy_blocks.append({
                    'name': strategy.get('name', ''),
                    'source': source,
                    'targets': [(target, target_name)]
                })
        elif strategy_type == 'parallel':
            source = strategy.get('source_block')
            targets = []
            for formula in strategy.get('formulas', []):
                target = formula.get('target_block')
                target_name = formula.get('target_block_name', '')
                if target:
                    targets.append((target, target_name))
            if source and targets:
                strategy_blocks.append({
                    'name': strategy.get('name', ''),
                    'source': source,
                    'targets': targets
                })

    # 打印每个策略的结果
    print()
    for strategy in strategy_blocks:
        name = strategy["name"]
        source = strategy["source"]
        targets = strategy["targets"]

        print(f"策略：{name}")

        # 查询源板块
        source_count = block_manager.get_block_count(source)
        print(f"  源板块：{source} ({source_count} 支)")

        # 查询目标板块
        for block_code, block_name in targets:
            count = block_manager.get_block_count(block_code)
            print(f"  → {block_code} ({block_name}): {count} 支")

        print()

    # 打印最终板块统计
    print("=" * 70)
    print("最终板块持股统计:")
    print("-" * 70)
    print(f"{'板块':<10} {'板块名称':<20} {'数量':>8}")
    print("-" * 70)

    # 添加固定板块
    fixed_blocks = [
        ("X01", "X01_低于五年周线"),
        ("X02", "X02_微盘股且基本面良好"),
        ("B00", "B00_KDJ5W"),
        ("B01", "B01_KDJ_低金叉"),
        ("B02", "B02_KDJ_高金叉"),
        ("BA1", "BA1_KDJ_低金叉"),
        ("BA2", "BA2_KDJ_高金叉"),
    ]

    for block_code, block_name in fixed_blocks:
        count = block_manager.get_block_count(block_code)
        print(f"{block_code:<10} {block_name:<20} {count:>8}")

    print("-" * 70)
    print("=" * 70)


def list_strategies(config):
    """列出所有策略"""
    programs = config.get('xg_programs', [])
    
    print("\n可用策略列表:")
    print("=" * 70)
    print(f"{'序号':<5} {'策略名称':<20} {'描述':<40}")
    print("-" * 70)
    
    for i, prog in enumerate(programs, 1):
        name = prog.get('name', 'Unknown')
        desc = prog.get('desc', '')
        print(f"{i:<5} {name:<20} {desc:<40}")
    
    print("=" * 70)
    print()
    print("使用示例:")
    print("  python xg.py --strategy below240w           # 执行单个策略")
    print("  python xg.py --strategy below240w small_goodfund  # 执行多个策略")
    print("  python xg.py                                # 执行全部策略")
    print()


def show_strategy_info(config, strategy_name):
    """显示策略详情"""
    programs = config.get('xg_programs', [])
    
    strategy = None
    for prog in programs:
        if prog.get('name') == strategy_name:
            strategy = prog
            break
    
    if not strategy:
        print(f"错误：策略 '{strategy_name}' 不存在")
        print("使用 'python xg.py --list' 查看所有可用策略")
        return
    
    print(f"\n策略详情：{strategy_name}")
    print("=" * 70)
    print(f"描述：{strategy.get('desc', '')}")
    print(f"类型：{strategy.get('type', 'single')}")
    
    strategy_type = strategy.get('type', 'single')
    
    if strategy_type == 'single':
        print(f"源板块：{strategy.get('source_block')}")
        print(f"目标板块：{strategy.get('target_block')} ({strategy.get('target_block_name')})")
        print(f"选股公式：{strategy.get('formula_name')}")
        print(f"K 线周期：{strategy.get('stock_period', '1d')}")
    
    elif strategy_type == 'multi':
        print(f"源板块：{strategy.get('source_block')}")
        print(f"目标板块：{strategy.get('target_block')} ({strategy.get('target_block_name')})")
        print("选股公式序列:")
        for i, formula in enumerate(strategy.get('formulas', []), 1):
            print(f"  {i}. {formula}")
    
    elif strategy_type == 'parallel':
        print(f"源板块：{strategy.get('source_block')}")
        print("选股公式（并行输出）:")
        for formula in strategy.get('formulas', []):
            formula_name = formula.get('formula_name')
            target_block = formula.get('target_block')
            target_block_name = formula.get('target_block_name')
            stock_period = formula.get('stock_period', '1d')
            print(f"  - {formula_name} → {target_block} ({target_block_name}) [{stock_period}]")
    
    elif strategy_type == 'db_update':
        print("长线板块:")
        for block in strategy.get('long_term_blocks', []):
            print(f"  - {block.get('code')} → {block.get('target_block')}")
        print("短线板块:")
        for block in strategy.get('short_term_blocks', []):
            print(f"  - {block.get('code')} → {block.get('target_block')}")
        print(f"数据保留：{strategy.get('keep_days', 10)} 天")
    
    print("=" * 70)
    print()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='通达信选股程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python xg.py                              # 执行全部策略
  python xg.py --strategy below240w         # 执行单个策略
  python xg.py --strategy below240w small_goodfund  # 执行多个策略
  python xg.py --list                       # 列出所有策略
  python xg.py --info below240w             # 查看策略详情
        """
    )
    
    parser.add_argument(
        '--strategy', '-s',
        nargs='+',
        metavar='STRATEGY',
        help='执行指定的策略（可指定多个）'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有策略'
    )
    
    parser.add_argument(
        '--info', '-i',
        metavar='STRATEGY',
        help='查看指定策略的详情'
    )
    
    args = parser.parse_args()
    
    # 初始化 TQ
    init_tq_context(__file__)
    
    try:
        config = get_config()
        
        # 列出所有策略
        if args.list:
            list_strategies(config)
            return
        
        # 查看策略详情
        if args.info:
            show_strategy_info(config, args.info)
            return
        
        # 执行策略
        programs = config.get('xg_programs', [])
        
        # 确定要执行的策略
        if args.strategy:
            # 执行指定的策略
            selected_programs = [
                p for p in programs if p.get('name') in args.strategy
            ]
            if not selected_programs:
                print(f"错误：未找到指定的策略：{args.strategy}")
                print("使用 'python xg.py --list' 查看所有可用策略")
                return
        else:
            # 执行全部策略
            selected_programs = programs
        
        print_header()
        print(f"执行顺序:")
        for i, prog in enumerate(selected_programs, 1):
            print(f"  {i}. {prog.get('desc', prog.get('name'))}")
        print("=" * 50)

        # 创建选股器和板块管理器
        selector = StockSelector()
        block_manager = BlockManager(get_tq())

        success_count = 0
        total = len(selected_programs)
        results = []

        # 执行选股程序
        for i, prog in enumerate(selected_programs, 1):
            name = prog.get('name', '')
            desc = prog.get('desc', '')

            print(f"\n[步骤 {i}/{total}] {desc}")
            print(f"  策略：{name}")

            # 执行策略
            result = execute_strategy(prog, selector, block_manager)

            # 检查结果
            if result is None:
                print(f"  [FAIL] 执行失败")
                print()
                print("=" * 50)
                print(f"[错误] 步骤 {i}/{total} 执行失败，选股流程终止")
                print("=" * 50)
                break

            results.append(result)
            success_count += 1

            # 显示执行结果数量
            if result.get('type') == 'parallel':
                target_counts = ", ".join([
                    f"{r['target_block']}: {r['count']} 支"
                    for r in result.get('results', [])
                ])
                print(f"  [OK] 执行成功 ({target_counts})")
            elif result.get('type') == 'single':
                print(f"  [OK] 执行成功 ({result['target_block']}: {result['selected_count']} 支)")
            elif result.get('type') == 'multi':
                print(f"  [OK] 执行成功 ({result['target_block']}: {result['selected_count']} 支)")
            elif result.get('type') == 'db_update':
                update_info = ", ".join([
                    f"{u['block_code']}: {u.get('added', 0)} 新增"
                    for u in result.get('updates', []) if 'error' not in u
                ])
                print(f"  [OK] 执行成功 ({update_info})")
            else:
                print(f"  [OK] 执行成功")

        # 打印汇总（直接查询板块数据，在 TQ 关闭前）
        if results:
            print_summary(block_manager, selected_programs)

        print_footer(success_count, total)

        # 返回退出码
        sys.exit(0 if success_count == total else 1)

    finally:
        # 关闭 TQ
        close_tq_context()


if __name__ == "__main__":
    main()
