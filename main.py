"""
通达信 TdxQuant 主程序

功能:
- 显示程序信息和帮助
- 快速启动选股程序
- 查看板块信息

使用示例:
    python main.py          # 显示主菜单
    python main.py --run    # 运行全部选股程序
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from datetime import datetime

# ============================================================================
# 配置
# ============================================================================
PROJECT_ROOT = Path(__file__).parent

# 选股程序配置
XG_PROGRAMS = [
    {"file": "xg.py", "desc": "运行全部选股程序"},
    {"file": "xg_below240w.py", "desc": "低于五年周线 (AAA → X01)"},
    {"file": "xg_small_goodfund.py", "desc": "微盘股基本面 (X01 → X02)"},
    {"file": "xg_buy_small_goodfund.py", "desc": "KDJ 买入 (X02 → B00/B01/B02)"},
    {"file": "xg_buy_aaa_kdj.py", "desc": "AAA 板块 KDJ (AAA → BA1/BA2)"},
]

# 板块管理命令
BLOCK_COMMANDS = [
    {"cmd": "list", "desc": "列出所有板块"},
    {"cmd": "info X01", "desc": "查看 X01 板块详情"},
    {"cmd": "info X02", "desc": "查看 X02 板块详情"},
    {"cmd": "info B00", "desc": "查看 B00 板块详情"},
    {"cmd": "info B01", "desc": "查看 B01 板块详情"},
    {"cmd": "info B02", "desc": "查看 B02 板块详情"},
    {"cmd": "info BA1", "desc": "查看 BA1 板块详情"},
    {"cmd": "info BA2", "desc": "查看 BA2 板块详情"},
]


# ============================================================================
# 辅助函数
# ============================================================================

def load_config():
    """加载配置文件"""
    config_path = PROJECT_ROOT / "config.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("错误：配置文件 config.yaml 不存在")
        return None
    except Exception as e:
        print(f"读取配置文件失败：{e}")
        return None


def run_program(program_file: str) -> int:
    """
    运行选股程序
    
    Returns:
        int: 程序返回码
    """
    program_path = PROJECT_ROOT / program_file
    
    if not program_path.exists():
        print(f"错误：程序 {program_file} 不存在")
        return 1
    
    result = subprocess.run(
        [sys.executable, str(program_path)],
        cwd=str(PROJECT_ROOT),
        check=False
    )
    
    return result.returncode


def print_header():
    """打印头部信息"""
    print()
    print("=" * 70)
    print("通达信 TdxQuant 选股系统")
    print("=" * 70)
    print()


def print_menu(config: dict):
    """打印主菜单"""
    print("主菜单:")
    print("-" * 70)
    print()
    
    # 选股程序
    print("选股程序:")
    for i, prog in enumerate(XG_PROGRAMS, 1):
        print(f"  {i}. python {prog['file']}")
        print(f"     {prog['desc']}")
    print()
    
    # 板块命令
    print("板块查询:")
    for cmd in BLOCK_COMMANDS:
        print(f"  python blocks.py {cmd['cmd']}")
        print(f"     {cmd['desc']}")
    print()
    
    # 快捷操作
    print("快捷操作:")
    print("  python main.py --run     # 运行全部选股程序")
    print("  python main.py --status  # 查看板块统计")
    print()
    print("-" * 70)


def print_status(config: dict):
    """打印板块统计信息"""
    print()
    print("=" * 70)
    print("板块统计")
    print("=" * 70)
    print()
    
    # 初始化通达信
    TDX_ROOT = config.get("tdx_root", r"D:\App\new_tdx64")
    PLUGIN_PATH = os.path.join(TDX_ROOT, 'PYPlugins', 'user')
    sys.path.insert(0, PLUGIN_PATH)
    
    try:
        from tqcenter import tq
        tq.initialize(__file__)
        sys.path.insert(0, str(PROJECT_ROOT))
        from blocks import get_block_stocks
    except Exception as e:
        print(f"初始化失败：{e}")
        return
    
    # 板块列表
    blocks_info = [
        ("X01", "低于五年周线"),
        ("X02", "微盘股且基本面良好"),
        ("B00", "KDJ5W"),
        ("B01", "KDJ 低金叉 (X02)"),
        ("B02", "KDJ 高金叉 (X02)"),
        ("BA1", "KDJ 低金叉 (AAA)"),
        ("BA2", "KDJ 高金叉 (AAA)"),
    ]
    
    print(f"{'板块代码':<10} {'板块名称':<20} {'股票数量':>10}")
    print("-" * 40)
    
    for block_code, block_name in blocks_info:
        try:
            stocks = get_block_stocks(block_code, block_type=1)
            count = len(stocks) if stocks else 0
            print(f"{block_code:<10} {block_name:<20} {count:>10}")
        except:
            print(f"{block_code:<10} {block_name:<20} {'N/A':>10}")
    
    print("-" * 40)
    print()


def print_help():
    """打印帮助信息"""
    print()
    print("使用帮助:")
    print("-" * 70)
    print()
    print("1. 直接运行主程序:")
    print("   python main.py")
    print("   显示主菜单和使用说明")
    print()
    print("2. 运行全部选股程序:")
    print("   python main.py --run")
    print("   或")
    print("   python xg.py")
    print()
    print("3. 查看板块统计:")
    print("   python main.py --status")
    print()
    print("4. 运行单个选股程序:")
    print("   python xg_below240w.py         # 低于五年周线")
    print("   python xg_small_goodfund.py    # 微盘股基本面")
    print("   python xg_buy_small_goodfund.py # KDJ 买入 (X02)")
    print("   python xg_buy_aaa_kdj.py       # KDJ 买入 (AAA)")
    print()
    print("5. 查看板块信息:")
    print("   python blocks.py list          # 列出所有板块")
    print("   python blocks.py info X01      # 查看 X01 详情")
    print()
    print("-" * 70)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    args = sys.argv[1:]
    
    # 加载配置
    config = load_config()
    if not config:
        sys.exit(1)
    
    # 处理命令行参数
    if "--run" in args:
        # 运行全部选股程序
        print_header()
        print("开始运行全部选股程序...")
        print()
        returncode = run_program("xg.py")
        sys.exit(returncode)
    
    elif "--status" in args:
        # 查看板块统计
        print_header()
        print_status(config)
        sys.exit(0)
    
    elif "--help" in args or "-h" in args:
        # 显示帮助
        print_help()
        sys.exit(0)
    
    else:
        # 显示主菜单
        print_header()
        
        # 显示配置信息
        tdx_root = config.get("tdx_root", r"D:\App\new_tdx64")
        print(f"通达信根目录：{tdx_root}")
        print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 显示菜单
        print_menu(config)
        
        # 显示板块统计
        print_status(config)
        
        print()
        print("=" * 70)
        print("提示：使用 --help 查看完整帮助")
        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
