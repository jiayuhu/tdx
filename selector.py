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
                return False
            name = info.get('Name', '')
            st_markers = ['ST', '*ST', '退', '退市']
            return any(marker in name.upper() for marker in st_markers)
        except Exception:
            return False

    def get_stock_name(self, stock_code: str) -> str:
        """获取股票名称"""
        try:
            info = self.tq.get_stock_info(stock_code, field_list=['Name'])
            return info.get('Name', '') if info else ''
        except Exception:
            return ''

    def select_by_formula(
        self,
        stock_list: List[str],
        formula_name: str,
        stock_period: Optional[str] = None,
        filter_st: bool = True,
    ) -> List[str]:
        """使用通达信公式引擎批量选股"""
        selected: List[str] = []

        non_st_list = (
            [s for s in stock_list if not self.is_st_stock(s)]
            if filter_st
            else stock_list
        )

        if stock_period is None:
            stock_period = DEFAULT_PERIOD

        batches = [
            non_st_list[i : i + BATCH_SIZE]
            for i in range(0, len(non_st_list), BATCH_SIZE)
        ]

        for batch in batches:
            try:
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
                print(f"选股异常：{formula_name} - {e}")

        return selected
