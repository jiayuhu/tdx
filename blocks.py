"""
通达信自定义板块查询模块

基于 TdxQuant API 实现自定义板块的查询、创建、删除、修改等功能。

使用示例:
    from blocks import BlockManager

    manager = BlockManager(tq)
    stocks = manager.get_block_stocks('X01')
    manager.create_block('TEST', '测试板块')
"""

import json
from typing import Any, Dict, List, Optional


class BlockManager:
    """自定义板块管理器"""

    DEFAULT_DELAY_MS = 100  # 默认延时 100 毫秒

    def __init__(self, tq, delay_ms: Optional[int] = None) -> None:
        """初始化板块管理器"""
        self.tq = tq
        self.delay_ms = delay_ms if delay_ms is not None else self.DEFAULT_DELAY_MS

    def _tq_delay(self) -> None:
        """板块操作后延时"""
        if self.delay_ms > 0:
            import time

            time.sleep(self.delay_ms / 1000.0)

    def get_user_blocks(self) -> List[Dict[str, Any]]:
        """获取用户自定义板块列表"""
        return self.tq.get_user_sector()

    def get_block_stocks(self, block_code: str, block_type: int = 1) -> List[str]:
        """获取板块成分股"""
        return self.tq.get_stock_list_in_sector(block_code, block_type)

    def create_block(self, block_code: str, block_name: str) -> Dict[str, Any]:
        """创建板块"""
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        if not block_name:
            return {"ErrorId": "-1", "Error": "板块名称不能为空"}
        result = self.tq.create_sector(block_code=block_code, block_name=block_name)
        self._tq_delay()
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "创建失败，返回为空"}

    def delete_block(self, block_code: str) -> Dict[str, Any]:
        """删除板块"""
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        result = self.tq.delete_sector(block_code=block_code)
        self._tq_delay()
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "删除失败，返回为空"}

    def rename_block(self, block_code: str, new_name: str) -> Dict[str, Any]:
        """重命名板块"""
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        if not new_name:
            return {"ErrorId": "-1", "Error": "新板块名称不能为空"}
        result = self.tq.rename_sector(block_code=block_code, block_name=new_name)
        self._tq_delay()
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "重命名失败，返回为空"}

    def clear_block_stocks(self, block_code: str) -> Dict[str, Any]:
        """清空板块成分股"""
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        result = self.tq.clear_sector(block_code=block_code)
        self._tq_delay()
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "清空失败，返回为空"}

    def add_stocks_to_block(
        self, block_code: str, stocks: List[str], show: bool = False
    ) -> Dict[str, Any]:
        """添加股票到板块"""
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        if not stocks:
            return {"ErrorId": "-1", "Error": "股票列表不能为空"}
        result = self.tq.send_user_block(block_code=block_code, stocks=stocks, show=show)
        self._tq_delay()
        return result

    def get_block_count(self, block_code: str) -> int:
        """获取板块成分股数量"""
        try:
            stocks = self.get_block_stocks(block_code, block_type=1)
            return len(stocks) if stocks else 0
        except Exception:
            return 0

    def prepare_target_block(self, block_code: str, block_name: str) -> bool:
        """准备目标板块（创建或清空）"""
        if not self.find_block_by_code(block_code):
            print(f"创建板块 '{block_code}' ({block_name})...")
            result = self.create_block(block_code, block_name)
            if result.get('ErrorId') == '0':
                print("板块创建成功")
                return True
            else:
                print(f"板块创建失败：{result.get('Error')}")
                return False
        else:
            print(f"清空板块 '{block_code}' 中的股票...")
            result = self.clear_block_stocks(block_code)
            if result.get('ErrorId') != '0':
                print(f"清空板块失败：{result.get('Error')}")
                return False
            return True

    def get_source_stocks(self, source_block: str) -> Optional[List[str]]:
        """获取源板块成分股"""
        stock_list = self.get_block_stocks(source_block, block_type=1)
        if not stock_list:
            stock_list = self.get_block_stocks(source_block, block_type=0)
        return stock_list if stock_list else None

    def update_target_block(self, target_block: str, stocks: List[str]) -> None:
        """更新目标板块（先清空再添加）"""
        self.clear_block_stocks(target_block)
        if stocks:
            self.add_stocks_to_block(target_block, stocks)

    def find_block_by_code(self, block_code: str) -> bool:
        """检查板块是否存在"""
        blocks = self.get_user_blocks()
        for block in blocks:
            code = block['Code'] if isinstance(block, dict) else block
            if code == block_code:
                return True
        return False
