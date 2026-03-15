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

from logging_config import logger, log_exceptions, suppress_tq_errors


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
        with suppress_tq_errors():
            try:
                result = self.tq.get_user_sector()
                return result if result else []
            except Exception as e:
                logger.warning(f"获取用户板块列表失败: {e}")
                return []

    def get_block_stocks(self, block_code: str, block_type: int = 1) -> List[str]:
        """获取板块成分股"""
        # 先检查板块是否存在，避免对不存在的板块调用 API
        if not self.find_block_by_code(block_code):
            logger.debug(f"板块 '{block_code}' 不存在")
            return []
            
        # 使用上下文管理器抑制 TQ API 的错误输出
        with suppress_tq_errors():
            try:
                result = self.tq.get_stock_list_in_sector(block_code, block_type)
                if result is None or len(result) == 0:
                    logger.debug(f"板块 '{block_code}' 无成分股")
                    return []
                return result
            except Exception as e:
                logger.warning(f"获取板块 '{block_code}' 成分股失败: {e}")
                return []

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
            logger.debug(f"股票列表为空，跳过添加到板块 '{block_code}'")
            return {"ErrorId": "0", "Error": "无股票需要添加"}
        result = self.tq.send_user_block(block_code=block_code, stocks=stocks, show=show)
        self._tq_delay()
        return result

    def get_block_count(self, block_code: str) -> int:
        """获取板块成分股数量"""
        try:
            stocks = self.get_block_stocks(block_code, block_type=1)
            count = len(stocks) if stocks else 0
            logger.debug(f"板块 {block_code} 成分股数量: {count}")
            return count
        except Exception as e:
            logger.warning(f"获取板块 {block_code} 成分股数量失败: {e}")
            return 0

    def recreate_block(self, block_code: str, block_name: str) -> bool:
        """重建板块（先删除再创建）"""
        if not block_code or not block_name:
            logger.warning("板块简称或名称不能为空")
            return False
            
        # 先删除板块（如果存在）
        if self.find_block_by_code(block_code):
            logger.debug(f"删除现有板块 '{block_code}'")
            delete_result = self.delete_block(block_code)
            if delete_result.get('ErrorId') != '0':
                logger.error(f"删除板块 '{block_code}' 失败: {delete_result.get('Error')}")
                return False
        
        # 再创建新板块
        logger.debug(f"创建新板块 '{block_code}' ({block_name})")
        create_result = self.create_block(block_code, block_name)
        if create_result.get('ErrorId') == '0':
            logger.info(f"板块 '{block_code}' 重建成功")
            return True
        else:
            logger.error(f"创建板块 '{block_code}' 失败: {create_result.get('Error')}")
            return False

    def prepare_target_block(self, block_code: str, block_name: str) -> bool:
        """准备目标板块（重建方式）"""
        return self.recreate_block(block_code, block_name)

    def get_source_stocks(self, source_block: str) -> Optional[List[str]]:
        """获取源板块成分股"""
        # 使用抑制器包装所有 get_block_stocks 调用
        with suppress_tq_errors():
            stock_list = self.get_block_stocks(source_block, block_type=1)
            if not stock_list:
                stock_list = self.get_block_stocks(source_block, block_type=0)
        return stock_list if stock_list else None

    def update_target_block_with_recreate(self, target_block: str, block_name: str, stocks: List[str]) -> None:
        """更新目标板块（重建方式：先删除再创建同名板块，然后添加股票）"""
        if self.recreate_block(target_block, block_name) and stocks:
            self.add_stocks_to_block(target_block, stocks)

    def update_target_block(self, target_block: str, stocks: List[str]) -> None:
        """更新目标板块（清空方式：先清空再添加）"""
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
