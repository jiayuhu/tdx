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
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from base import init_tq_context, close_tq_context, get_tq, get_config
from selector import StockSelector
from blocks import BlockManager
from executor import execute_strategy

_BJT_OFFSET = timedelta(hours=8)


def _beijing_now() -> str:
    """返回当前北京时间字符串 (UTC+8)"""
    return (datetime.now(timezone.utc) + _BJT_OFFSET).strftime('%Y-%m-%d %H:%M:%S')


# ============================================================================
# 辅助函数
# ============================================================================

def print_header():
    """打印程序头部信息"""
    print("\n" + "=" * 50)
    print("通达信选股程序")
    print("=" * 50)
    print(f"开始：{_beijing_now()}")


def print_footer(success_count: int, total: int):
    """打印程序尾部信息"""
    print("=" * 50)
    print(f"完成：{success_count}/{total} 成功")
    print(f"结束：{_beijing_now()}")

    if success_count == total:
        print("[OK] 所有程序执行成功！")
    else:
        print(f"[WARN] {total - success_count} 个程序失败，请检查日志")
    print("=" * 50)


def print_summary(block_manager: BlockManager, strategies: List[Dict]) -> None:
    """
    打印最终板块持股统计
    直接查询通达信板块数据
    
    Args:
        block_manager: BlockManager 实例
        strategies: 策略配置列表（从 config.yaml 读取，当前未使用）
    """
    print("\n最终板块持股统计:")
    print("=" * 70)
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
                print("  [FAIL] 执行失败")
                print()
                print("=" * 50)
                print(f"[错误] 步骤 {i}/{total} 执行失败，选股流程终止")
                print("=" * 50)
                break

            results.append(result)
            success_count += 1

            # 显示执行结果数量
            result_type = result.get('type')
            if result_type == 'parallel':
                target_counts = ", ".join([
                    f"{r['target_block']}: {r['count']} 支"
                    for r in result.get('results', [])
                ])
                print("  [OK] 执行成功 (" + target_counts + ")")
            elif result_type == 'single':
                print("  [OK] 执行成功 (" + result['target_block'] + ": " + str(result['selected_count']) + " 支)")
            elif result_type == 'multi':
                print("  [OK] 执行成功 (" + result['target_block'] + ": " + str(result['selected_count']) + " 支)")
            elif result_type == 'db_update':
                updates_list = result.get('updates', [])
                if updates_list:
                    info_parts = []
                    for u in updates_list:
                        code = u.get('block_code', 'N/A')
                        target = u.get('target_block', 'N/A')
                        action = u.get('delta_action', 'unknown')
                        added = u.get('added', 0)
                        info_parts.append(code + "->" + target + ": " + action + "(" + str(added) + ")")
                    update_info = ", ".join(info_parts)
                else:
                    update_info = "无更新数据"
                print("  [OK] 执行成功 (" + update_info + ")")
            else:
                # 未知类型也显示结果
                print("  [OK] 执行成功 (result=" + str(result) + ")")

        # 打印最终板块持股统计
        if results:
            print_summary(block_manager, selected_programs)

        print_footer(success_count, total)

        # 返回退出码
        sys.exit(0)

    finally:
        # 关闭 TQ
        close_tq_context()


if __name__ == "__main__":
    main()
