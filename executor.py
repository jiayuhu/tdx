"""
选股策略执行器模块

负责执行各种选股策略：
- 单公式选股
- 多公式串行选股
- 多公式并行选股
- 数据库更新

使用示例:
    from executor import execute_strategy

    result = execute_strategy(config, selector, block_manager)
"""

from typing import Any, Dict, List, Optional

from base import (
    DEFAULT_PERIOD,
    STRATEGY_TYPE_DB_UPDATE,
    STRATEGY_TYPE_MULTI,
    STRATEGY_TYPE_PARALLEL,
    STRATEGY_TYPE_SINGLE,
    get_project_root,
)
from database import StockDatabase


def execute_single_strategy(
    config: Dict[str, Any],
    selector,
    block_manager,
) -> Optional[Dict[str, Any]]:
    """执行单公式选股策略"""
    target_block = config.get('target_block')
    target_block_name = config.get('target_block_name')

    if not block_manager.prepare_target_block(target_block, target_block_name):
        return None

    source_block = config.get('source_block')
    stock_list = block_manager.get_source_stocks(source_block)
    if not stock_list:
        return None

    print(f"源板块：{source_block} ({len(stock_list)} 支)")

    formula_name = config.get('formula_name')
    stock_period = config.get('stock_period', DEFAULT_PERIOD)
    selected_stocks = selector.select_by_formula(stock_list, formula_name, stock_period=stock_period)

    if selected_stocks:
        block_manager.add_stocks_to_block(target_block, selected_stocks)

    return {
        'name': config.get('name'),
        'type': STRATEGY_TYPE_SINGLE,
        'source_block': source_block,
        'source_count': len(stock_list),
        'target_block': target_block,
        'selected_count': len(selected_stocks),
    }


def execute_multi_strategy(
    config: Dict[str, Any],
    selector,
    block_manager,
) -> Optional[Dict[str, Any]]:
    """执行多公式串行选股策略（逐步筛选）"""
    target_block = config.get('target_block')
    target_block_name = config.get('target_block_name')

    if not block_manager.prepare_target_block(target_block, target_block_name):
        return None

    source_block = config.get('source_block')
    stock_list = block_manager.get_source_stocks(source_block)
    if not stock_list:
        return None

    formulas: List[str] = config.get('formulas', [])
    current_stocks = stock_list
    initial_count = len(stock_list)

    for i, formula_name in enumerate(formulas, 1):
        if not current_stocks:
            print("当前股票池为空，停止选股")
            break

        selected_stocks = selector.select_by_formula(current_stocks, formula_name)
        output_count = len(selected_stocks)
        input_count = len(current_stocks)
        pct = output_count * 100 // input_count if input_count else 0

        print(f"步骤 {i}/{len(formulas)}: {formula_name} → {output_count} 支 ({pct}%)")
        current_stocks = selected_stocks

    if current_stocks:
        block_manager.add_stocks_to_block(target_block, current_stocks)

    total_pct = len(current_stocks) * 100 // initial_count if initial_count else 0

    return {
        'name': config.get('name'),
        'type': STRATEGY_TYPE_MULTI,
        'source_block': source_block,
        'source_count': initial_count,
        'target_block': target_block,
        'selected_count': len(current_stocks),
        'pct': total_pct,
    }


def execute_parallel_strategy(
    config: Dict[str, Any],
    selector,
    block_manager,
) -> Optional[Dict[str, Any]]:
    """执行多公式并行选股策略（独立输出到不同板块）"""
    source_block = config.get('source_block')
    formulas: List[Dict[str, Any]] = config.get('formulas', [])

    stock_list = block_manager.get_source_stocks(source_block)
    if not stock_list:
        return None

    results: List[Dict[str, Any]] = []

    for formula_config in formulas:
        formula_name = formula_config.get('formula_name')
        target_block = formula_config.get('target_block')
        target_block_name = formula_config.get('target_block_name')
        stock_period = formula_config.get('stock_period', DEFAULT_PERIOD)

        if not block_manager.prepare_target_block(target_block, target_block_name):
            continue

        selector.select_by_formula(stock_list, formula_name, stock_period=stock_period)
        actual_count = block_manager.get_block_count(target_block)

        results.append({
            'target_block': target_block,
            'target_block_name': target_block_name,
            'count': actual_count,
            'period': stock_period,
        })

        print(f"{target_block} ({target_block_name}): {actual_count} 支 ({stock_period})")

    return {
        'name': config.get('name'),
        'type': STRATEGY_TYPE_PARALLEL,
        'source_block': source_block,
        'source_count': len(stock_list),
        'results': results,
    }


def execute_db_update(
    config: Dict[str, Any],
    block_manager,
) -> Optional[Dict[str, Any]]:
    """执行数据库更新"""
    PROJECT_ROOT = get_project_root()
    DB_PATH = PROJECT_ROOT / "data" / "quant.db"

    long_term_blocks: List[Dict[str, Any]] = config.get('long_term_blocks', [])
    short_term_blocks: List[Dict[str, Any]] = config.get('short_term_blocks', [])
    keep_days: int = config.get('keep_days', 10)

    db = StockDatabase(DB_PATH)
    db.init(long_term_blocks + short_term_blocks)

    updates: List[Dict[str, Any]] = []
    for block_config in long_term_blocks + short_term_blocks:
        result = db.process_block(block_config, block_manager, keep_days)
        if result:
            updates.append(result)

    return {
        'name': config.get('name'),
        'type': STRATEGY_TYPE_DB_UPDATE,
        'updates': updates,
        'keep_days': keep_days,
    }


def execute_strategy(
    config: Dict[str, Any],
    selector,
    block_manager,
) -> Optional[Dict[str, Any]]:
    """执行选股策略（根据类型自动分发）"""
    strategy_type = config.get('type', STRATEGY_TYPE_SINGLE)

    if strategy_type == STRATEGY_TYPE_DB_UPDATE:
        return execute_db_update(config, block_manager)

    handlers = {
        STRATEGY_TYPE_SINGLE: execute_single_strategy,
        STRATEGY_TYPE_MULTI: execute_multi_strategy,
        STRATEGY_TYPE_PARALLEL: execute_parallel_strategy,
    }

    handler = handlers.get(strategy_type)
    if handler is None:
        print(f"未知策略类型：{strategy_type}")
        return None

    return handler(config, selector, block_manager)
