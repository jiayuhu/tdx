"""
通达信自定义板块查询模块

基于 TdxQuant API 实现自定义板块的查询、创建、删除、修改等功能。

使用前请确保:
1. 已启动通达信客户端并登录
2. 通达信安装在配置文件中指定的路径
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional

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

# 初始化通达信插件环境
sys.path.insert(0, PLUGIN_PATH)
from tqcenter import tq

# 初始化连接
tq.initialize(__file__)


# ============================================================================
# 板块查询功能
# ============================================================================

class BlockManager:
    """
    自定义板块管理器
    
    提供自定义板块的完整管理功能，包括查询、创建、删除、修改等操作。
    
    使用示例:
        >>> # 获取所有自定义板块
        >>> blocks = BlockManager.get_user_blocks()
        >>> print(blocks)
        
        >>> # 创建新板块
        >>> result = BlockManager.create_block('MYBK', '我的板块')
        >>> print(result)
        
        >>> # 获取板块成分股
        >>> stocks = BlockManager.get_block_stocks('MYBK')
        >>> print(stocks)
    """

    @staticmethod
    def get_user_blocks() -> List[Dict]:
        """
        获取用户自定义板块列表

        Returns:
            List[Dict]: 自定义板块列表，每个元素包含：
                       - Code: 板块代码
                       - Name: 板块名称
            
        示例:
            >>> blocks = BlockManager.get_user_blocks()
            >>> for block in blocks:
            ...     print(f"  - {block['Code']}: {block['Name']}")
        """
        return tq.get_user_sector()

    @staticmethod
    def get_block_stocks(block_code: str, block_type: int = 1) -> List[str]:
        """
        获取指定板块的成分股列表

        Args:
            block_code: 板块代码或名称
                       - 系统板块：如 '880081.SH' 或 '钛金属'
                       - 自定义板块：如 'MYBK'
            block_type: 板块类型，默认 1
                       - 0: 板块代码/名称（系统板块）
                       - 1: 自定义板块简称

        Returns:
            List[str]: 成分股代码列表，格式如 ['600000.SH', '000001.SZ']

        示例:
            >>> # 通过板块代码获取
            >>> stocks = BlockManager.get_block_stocks('880081.SH')

            >>> # 通过板块名称获取
            >>> stocks = BlockManager.get_block_stocks('钛金属')

            >>> # 通过自定义板块简称获取（默认 block_type=1）
            >>> stocks = BlockManager.get_block_stocks('MYBK')
        """
        return tq.get_stock_list_in_sector(block_code, block_type)

    @staticmethod
    def create_block(block_code: str, block_name: str) -> Dict:
        """
        创建自定义板块

        Args:
            block_code: 板块简称，如 'MYBK'（不能为空）
            block_name: 板块名称，如 '我的板块'（不能为空）

        Returns:
            Dict: 操作结果，包含 ErrorId 和 Error 信息
                  - ErrorId='0' 表示成功
                  - ErrorId!='0' 表示失败，Error 字段包含错误信息
            
        示例:
            >>> result = BlockManager.create_block('MYBK', '我的板块')
            >>> if result.get('ErrorId') == '0':
            ...     print("创建成功")
            ... else:
            ...     print(f"创建失败：{result.get('Error')}")
        """
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        if not block_name:
            return {"ErrorId": "-1", "Error": "板块名称不能为空"}
        result = tq.create_sector(block_code=block_code, block_name=block_name)
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "创建失败，返回为空"}

    @staticmethod
    def delete_block(block_code: str) -> Dict:
        """
        删除自定义板块

        Args:
            block_code: 板块简称（不能为空）

        Returns:
            Dict: 操作结果
            
        示例:
            >>> result = BlockManager.delete_block('MYBK')
            >>> if result.get('ErrorId') == '0':
            ...     print("删除成功")
        """
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        result = tq.delete_sector(block_code=block_code)
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "删除失败，返回为空"}

    @staticmethod
    def rename_block(block_code: str, new_name: str) -> Dict:
        """
        重命名自定义板块（仅修改板块名称，不改变板块简称）

        Args:
            block_code: 板块简称（不能为空）
            new_name: 新的板块名称（不能为空）

        Returns:
            Dict: 操作结果
            
        示例:
            >>> result = BlockManager.rename_block('MYBK', '新名称')
            >>> if result.get('ErrorId') == '0':
            ...     print("重命名成功")
        """
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        if not new_name:
            return {"ErrorId": "-1", "Error": "新板块名称不能为空"}
        result = tq.rename_sector(block_code=block_code, block_name=new_name)
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "重命名失败，返回为空"}

    @staticmethod
    def clear_block_stocks(block_code: str) -> Dict:
        """
        清空自定义板块的所有成分股

        Args:
            block_code: 板块简称（不能为空）

        Returns:
            Dict: 操作结果
            
        示例:
            >>> result = BlockManager.clear_block_stocks('MYBK')
            >>> if result.get('ErrorId') == '0':
            ...     print("清空成功")
        """
        if not block_code:
            return {"ErrorId": "-1", "Error": "板块简称不能为空"}
        result = tq.clear_sector(block_code=block_code)
        return json.loads(result) if result else {"ErrorId": "-1", "Error": "清空失败，返回为空"}

    @staticmethod
    def add_stocks_to_block(block_code: str, stocks: List[str], show: bool = False) -> Dict:
        """
        添加股票到自定义板块

        Args:
            block_code: 板块简称
                       - 空字符串：添加到临时条件股
                       - 已有板块简称：添加到该板块
            stocks: 股票代码列表，格式如 ['600000.SH', '000001.SZ']
            show: 是否在客户端显示该自选股窗口，默认 False

        Returns:
            Dict: 操作结果
            
        示例:
            >>> # 添加到临时条件股
            >>> result = BlockManager.add_stocks_to_block(
            ...     block_code='', 
            ...     stocks=['600000.SH', '000001.SZ'],
            ...     show=True
            ... )
            
            >>> # 添加到自定义板块
            >>> result = BlockManager.add_stocks_to_block(
            ...     block_code='MYBK', 
            ...     stocks=['600000.SH', '000001.SZ']
            ... )
            
            >>> # 清空板块所有股票
            >>> result = BlockManager.add_stocks_to_block(block_code='MYBK', stocks=[])
        """
        return tq.send_user_block(block_code=block_code, stocks=stocks, show=show)

    @staticmethod
    def get_block_info(block_code: str, block_type: int = 1) -> Optional[Dict]:
        """
        获取板块详细信息

        Args:
            block_code: 板块代码或名称
            block_type: 板块类型，默认 1
                       - 0: 系统板块
                       - 1: 自定义板块

        Returns:
            Optional[Dict]: 板块信息字典，包含：
                           - block_code: 板块代码
                           - stock_count: 成分股数量
                           - stocks: 成分股列表
                           如果板块不存在则返回 None
                           
        示例:
            >>> info = BlockManager.get_block_info('880081.SH')
            >>> if info:
            ...     print(f"板块：{info['block_code']}")
            ...     print(f"成分股数量：{info['stock_count']}")
        """
        try:
            stocks = tq.get_stock_list_in_sector(block_code, block_type)
            if stocks is None:
                return None
            return {
                "block_code": block_code,
                "stock_count": len(stocks),
                "stocks": stocks
            }
        except Exception as e:
            return None

    @staticmethod
    def list_all_blocks() -> List[Dict]:
        """
        列出所有自定义板块及其基本信息

        Returns:
            List[Dict]: 板块信息列表，每个包含：
                       - block_code: 板块代码
                       - block_name: 板块名称
                       - stock_count: 成分股数量
                       
        示例:
            >>> blocks = BlockManager.list_all_blocks()
            >>> for block in blocks:
            ...     print(f"{block['block_code']}: {block['stock_count']} 只股票")
        """
        user_blocks = tq.get_user_sector()
        result = []
        for block in user_blocks:
            # block 可能是字典或字符串
            block_code = block['Code'] if isinstance(block, dict) else block
            block_name = block.get('Name', '') if isinstance(block, dict) else ''
            try:
                stocks = tq.get_stock_list_in_sector(block_code)
                result.append({
                    "block_code": block_code,
                    "block_name": block_name,
                    "stock_count": len(stocks) if stocks else 0
                })
            except Exception as e:
                result.append({
                    "block_code": block_code,
                    "block_name": block_name,
                    "stock_count": 0
                })
        return result

    @staticmethod
    def get_sector_list() -> List[str]:
        """
        获取所有板块列表（包含系统板块和自定义板块）

        Returns:
            List[str]: 板块代码列表
            
        示例:
            >>> sectors = BlockManager.get_sector_list()
            >>> print(f"共有 {len(sectors)} 个板块")
        """
        return tq.get_sector_list()


# ============================================================================
# 便捷函数（无需实例化类即可使用）
# ============================================================================

def get_user_blocks() -> List[str]:
    """获取用户自定义板块列表"""
    return BlockManager.get_user_blocks()


def get_block_stocks(block_code: str, block_type: int = 1) -> List[str]:
    """获取指定板块的成分股列表"""
    return BlockManager.get_block_stocks(block_code, block_type)


def create_block(block_code: str, block_name: str) -> Dict:
    """创建自定义板块"""
    return BlockManager.create_block(block_code, block_name)


def delete_block(block_code: str) -> Dict:
    """删除自定义板块"""
    return BlockManager.delete_block(block_code)


def rename_block(block_code: str, new_name: str) -> Dict:
    """重命名自定义板块"""
    return BlockManager.rename_block(block_code, new_name)


def clear_block_stocks(block_code: str) -> Dict:
    """清空板块成分股"""
    return BlockManager.clear_block_stocks(block_code)


def add_stocks_to_block(block_code: str, stocks: List[str], show: bool = False) -> Dict:
    """添加股票到板块"""
    return BlockManager.add_stocks_to_block(block_code, stocks, show)


def get_block_info(block_code: str, block_type: int = 1) -> Optional[Dict]:
    """获取板块详细信息"""
    return BlockManager.get_block_info(block_code, block_type)


def list_all_blocks() -> List[Dict]:
    """列出所有自定义板块"""
    return BlockManager.list_all_blocks()


def get_sector_list() -> List[str]:
    """获取所有板块列表"""
    return BlockManager.get_sector_list()


# ============================================================================
# 命令行接口
# ============================================================================

def _get_block_stocks_silent(block_code: str, block_type: int = 1) -> List[str]:
    """静默获取板块成分股（不输出错误信息）"""
    import io
    import contextlib
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            return get_block_stocks(block_code, block_type)
        except:
            return []


def cmd_list(args):
    """列出所有自定义板块"""
    blocks = get_user_blocks()
    if not blocks:
        print("暂无自定义板块")
        return
    
    print()
    print("=" * 70)
    print("自定义板块列表")
    print("=" * 70)
    print(f"{'序号':<5} {'板块代码':<18} {'板块名称':<22} {'成分股数量':>8}")
    print("-" * 70)
    
    total_stocks = 0
    for i, block in enumerate(blocks, 1):
        code = block['Code'] if isinstance(block, dict) else block
        name = block.get('Name', '') if isinstance(block, dict) else ''
        
        # 获取成分股数量（静默处理错误输出）
        import io
        import contextlib
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                stocks = get_block_stocks(code, block_type=1)
                stock_count = len(stocks) if stocks else 0
            except:
                stock_count = 0
        
        total_stocks += stock_count
        print(f"{i:<5} {code:<18} {name:<22} {stock_count:>8}")
    
    print("-" * 70)
    print(f"共 {len(blocks)} 个板块，总计 {total_stocks} 只成分股")
    print("=" * 70)
    print()


def cmd_info(args):
    """查看板块详细信息"""
    import io
    import contextlib
    
    # 获取板块成分股
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        stocks = get_block_stocks(args.block, block_type=args.type)
    
    if not stocks:
        print(f"板块 '{args.block}' 无成分股或不存在")
        return
    
    block_type_name = "系统板块" if args.type == 0 else "自定义板块"
    
    # 获取前 20 只成分股的名称
    preview_stocks = stocks[:20]
    stock_names = []
    for stock in preview_stocks:
        try:
            info = tq.get_stock_info(stock, field_list=['Name'])
            name = info.get('Name', '') if info else ''
            stock_names.append(name)
        except:
            stock_names.append('')
    
    print()
    print("=" * 70)
    print("板块详细信息")
    print("=" * 70)
    print(f"板块代码：{args.block}")
    print(f"板块类型：{block_type_name}")
    print(f"成分股数量：{len(stocks)}")
    print()
    
    # 显示前 20 只成分股详情
    if stocks:
        print("成分股预览 (前 20 只):")
        print("-" * 70)
        print(f"{'序号':<5} {'股票代码':<12} {'股票名称':<15}")
        print("-" * 70)
        
        for i, (stock, name) in enumerate(zip(preview_stocks, stock_names), 1):
            print(f"{i:<5} {stock:<12} {name:<15}")
        
        print("-" * 70)
        if len(stocks) > 20:
            print(f"... 还有 {len(stocks) - 20} 只股票")
    
    print()
    print("成分股分布统计:")
    print("-" * 70)
    
    # 统计市场分布
    sh_count = sum(1 for s in stocks if s.endswith('.SH'))
    sz_count = sum(1 for s in stocks if s.endswith('.SZ'))
    bj_count = sum(1 for s in stocks if s.endswith('.BJ'))
    
    print(f"  上海证券交易所 (SH): {sh_count:>6} 只 ({sh_count*100//len(stocks) if stocks else 0}%)")
    print(f"  深圳证券交易所 (SZ): {sz_count:>6} 只 ({sz_count*100//len(stocks) if stocks else 0}%)")
    print(f"  北京证券交易所 (BJ): {bj_count:>6} 只 ({bj_count*100//len(stocks) if stocks else 0}%)")
    
    print("=" * 70)
    print()


def cmd_create(args):
    """创建新板块"""
    print()
    print("=" * 70)
    print("创建新板块")
    print("=" * 70)
    result = create_block(args.code, args.name)
    if result.get('ErrorId') == '0':
        print(f"操作状态：成功")
        print(f"板块代码：{args.code}")
        print(f"板块名称：{args.name}")
        print(f"提示：可以使用 'python blocks.py info {args.code}' 查看板块详情")
    else:
        print(f"操作状态：失败")
        print(f"错误信息：{result.get('Error')}")
    print("=" * 70)
    print()


def cmd_delete(args):
    """删除板块"""
    print()
    print("=" * 70)
    print("删除板块")
    print("=" * 70)
    result = delete_block(args.block)
    if result.get('ErrorId') == '0':
        print(f"操作状态：成功")
        print(f"已删除板块：{args.block}")
    else:
        print(f"操作状态：失败")
        print(f"错误信息：{result.get('Error')}")
    print("=" * 70)
    print()


def cmd_rename(args):
    """重命名板块"""
    print()
    print("=" * 70)
    print("重命名板块")
    print("=" * 70)
    result = rename_block(args.block, args.new_name)
    if result.get('ErrorId') == '0':
        print(f"操作状态：成功")
        print(f"板块代码：{args.block}")
        print(f"原名称：{args.block}")
        print(f"新名称：{args.new_name}")
    else:
        print(f"操作状态：失败")
        print(f"错误信息：{result.get('Error')}")
    print("=" * 70)
    print()


def cmd_clear(args):
    """清空板块成分股"""
    print()
    print("=" * 70)
    print("清空板块成分股")
    print("=" * 70)
    result = clear_block_stocks(args.block)
    if result.get('ErrorId') == '0':
        print(f"操作状态：成功")
        print(f"已清空板块：{args.block}")
    else:
        print(f"操作状态：失败")
        print(f"错误信息：{result.get('Error')}")
    print("=" * 70)
    print()


def cmd_add(args):
    """添加股票到板块"""
    stocks = args.stocks.split(',')
    result = add_stocks_to_block(args.block, stocks)

    print()
    print("=" * 70)
    print("添加股票到板块")
    print("=" * 70)
    print(f"板块代码：{args.block}")
    print(f"添加股票：{len(stocks)} 只")
    print("-" * 70)
    for stock in stocks:
        print(f"  - {stock}")
    print("-" * 70)
    print(f"操作状态：完成")
    print(f"提示：可以使用 'python blocks.py info {args.block}' 查看成分股")
    print("=" * 70)
    print()


def main():
    """命令行入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='通达信自定义板块查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python blocks.py list                         # 列出所有自定义板块
  python blocks.py info AAA                     # 查看板块详细信息
  python blocks.py info 880081.SH -t 0          # 查看系统板块信息
  python blocks.py create TEST 测试板块          # 创建新板块
  python blocks.py delete TEST                  # 删除板块
  python blocks.py rename TEST 新名称            # 重命名板块
  python blocks.py clear TEST                   # 清空板块成分股
  python blocks.py add TEST 600000.SH,000001.SZ # 添加股票到板块
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有自定义板块')
    parser_list.set_defaults(func=cmd_list)

    # info 命令
    parser_info = subparsers.add_parser('info', help='查看板块详细信息')
    parser_info.add_argument('block', help='板块代码或名称')
    parser_info.add_argument('-t', '--type', type=int, default=1,
                            choices=[0, 1],
                            help='板块类型：0=系统板块，1=自定义板块（默认）')
    parser_info.set_defaults(func=cmd_info)

    # create 命令
    parser_create = subparsers.add_parser('create', help='创建新板块')
    parser_create.add_argument('code', help='板块代码')
    parser_create.add_argument('name', help='板块名称')
    parser_create.set_defaults(func=cmd_create)
    
    # delete 命令
    parser_delete = subparsers.add_parser('delete', help='删除板块')
    parser_delete.add_argument('block', help='板块代码')
    parser_delete.set_defaults(func=cmd_delete)
    
    # rename 命令
    parser_rename = subparsers.add_parser('rename', help='重命名板块')
    parser_rename.add_argument('block', help='板块代码')
    parser_rename.add_argument('new_name', help='新板块名称')
    parser_rename.set_defaults(func=cmd_rename)
    
    # clear 命令
    parser_clear = subparsers.add_parser('clear', help='清空板块成分股')
    parser_clear.add_argument('block', help='板块代码')
    parser_clear.set_defaults(func=cmd_clear)
    
    # add 命令
    parser_add = subparsers.add_parser('add', help='添加股票到板块')
    parser_add.add_argument('block', help='板块代码')
    parser_add.add_argument('stocks', help='股票代码列表，用逗号分隔')
    parser_add.set_defaults(func=cmd_add)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
