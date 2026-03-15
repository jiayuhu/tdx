"""
选股器模块 - 股票筛选和公式执行

提供选股功能：
- ST 股票检测
- 股票名称获取
- 批量选股公式执行

使用示例:
    from selector import StockSelector

    selector = StockSelector()
    selected = selector.select_by_formula(stock_list, 'MY_FORMULA')
"""

from typing import List, Optional

from base import (
    BATCH_SIZE,
    DATA_COUNT,
    DEFAULT_PERIOD,
    DIVIDEND_TYPE,
    get_tq,
)
from logging_config import logger, log_exceptions, suppress_tq_errors


class StockSelector:
    """选股器 - 提供选股功能"""

    def __init__(self) -> None:
        """初始化选股器"""
        self.tq = get_tq()

    def is_st_stock(self, stock_code: str) -> bool:
        """检查股票是否为 ST 股票"""
        try:
            info = self.tq.get_stock_info(stock_code, field_list=['Name'])
            if not info:
                logger.debug(f"股票 {stock_code} 无基本信息")
                return False
            name = info.get('Name', '')
            st_markers = ['ST', '*ST', '退', '退市']
            is_st = any(marker in name.upper() for marker in st_markers)
            if is_st:
                logger.debug(f"股票 {stock_code} 是ST股: {name}")
            return is_st
        except Exception as e:
            logger.warning(f"检查股票 {stock_code} 是否为ST股失败: {e}")
            return False

    def get_stock_name(self, stock_code: str) -> str:
        """获取股票名称"""
        try:
            info = self.tq.get_stock_info(stock_code, field_list=['Name'])
            name = info.get('Name', '') if info else ''
            logger.debug(f"获取股票 {stock_code} 名称: {name}")
            return name
        except Exception as e:
            logger.warning(f"获取股票 {stock_code} 名称失败: {e}")
            return ''

    def select_by_formula(
        self,
        stock_list: List[str],
        formula_name: str,
        stock_period: Optional[str] = None,
        filter_st: bool = True,
    ) -> List[str]:
        """使用通达信公式引擎批量选股"""
        logger.info(f"开始执行选股公式: {formula_name}, 股票数量: {len(stock_list)}, 过滤ST: {filter_st}")
        selected: List[str] = []

        non_st_list = (
            [s for s in stock_list if not self.is_st_stock(s)]
            if filter_st
            else stock_list
        )
        
        if filter_st:
            logger.info(f"过滤ST股后剩余 {len(non_st_list)} 只股票")

        if stock_period is None:
            stock_period = DEFAULT_PERIOD

        batches = [
            non_st_list[i : i + BATCH_SIZE]
            for i in range(0, len(non_st_list), BATCH_SIZE)
        ]

        for i, batch in enumerate(batches):
            try:
                logger.debug(f"处理第 {i+1}/{len(batches)} 批次，包含 {len(batch)} 只股票")
                # 为 formula_process_mul_xg 增加错误抑制
                with suppress_tq_errors():
                    result = self.tq.formula_process_mul_xg(
                        formula_name=formula_name,
                        formula_arg='',
                        return_count=1,
                        return_date=False,
                        stock_list=batch,
                        stock_period=stock_period,
                        count=DATA_COUNT,
                        dividend_type=DIVIDEND_TYPE,
                    )

                if result and isinstance(result, dict):
                    for stock_code, stock_data in result.items():
                        if stock_code == 'ErrorId':
                            continue

                        if isinstance(stock_data, dict):
                            for key, value in stock_data.items():
                                if key not in ['XG', 'SELECT', 'BUY', 'OUTPUT', 'OUTPUT1'] or value is None:
                                    continue
                                matched = False
                                if isinstance(value, list) and len(value) > 0:
                                    if '1' in [str(v).strip() for v in value]:
                                        matched = True
                                elif str(value).strip() == '1':
                                    matched = True
                                if matched:
                                    selected.append(stock_code)
                                    break

            except Exception as e:
                logger.error(f"选股异常：{formula_name} - 第{i+1}批次处理失败: {e}")

        logger.info(f"选股完成: 公式 {formula_name} 共选出 {len(selected)} 只股票")
        return selected
