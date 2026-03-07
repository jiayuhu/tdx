"""
选股程序总入口
依次运行所有选股程序

执行顺序:
1. xg_below240w.py      : AAA → X01 (低于五年周线)
2. xg_small_goodfund.py : X01 → X02 (微盘股且基本面良好)
3. xg_buy_small_goodfund.py : X02 → B00/B01/B02 (KDJ 买入信号)
4. xg_buy_aaa_kdj.py    : AAA → BA1/BA2 (AAA 板块 KDJ)

使用示例:
    python xg.py
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from datetime import datetime
import re

# ============================================================================
# 配置
# ============================================================================
PROJECT_ROOT = Path(__file__).parent

# 选股程序列表（按执行顺序）
XG_PROGRAMS = [
    {
        "name": "xg_below240w.py",
        "desc": "低于五年周线 (AAA → X01)",
        "source": "AAA",
        "targets": ["X01"],
    },
    {
        "name": "xg_small_goodfund.py",
        "desc": "微盘股且基本面良好 (X01 → X02)",
        "source": "X01",
        "targets": ["X02"],
    },
    {
        "name": "xg_buy_small_goodfund.py",
        "desc": "KDJ 买入信号 (X02 → B00/B01/B02)",
        "source": "X02",
        "targets": ["B00", "B01", "B02"],
    },
    {
        "name": "xg_buy_aaa_kdj.py",
        "desc": "AAA 板块 KDJ (AAA → BA1/BA2)",
        "source": "AAA",
        "targets": ["BA1", "BA2"],
    },
]


# ============================================================================
# 辅助函数
# ============================================================================

def parse_output(output: str, program_name: str) -> dict:
    """
    解析选股程序输出，提取结果信息
    
    Returns:
        dict: 包含选股结果的字典
    """
    result = {
        "program": program_name,
        "source_block": "",
        "source_count": 0,
        "results": [],
    }
    
    # 提取源板块和数量
    source_match = re.search(r"源板块 [：:]\s*(\w+)\s*\((\d+)\s*只", output)
    if source_match:
        result["source_block"] = source_match.group(1)
        result["source_count"] = int(source_match.group(2))
    
    # 提取目标板块和数量（多种格式）
    # 格式 1: "选中股票：XX 只"
    select_match = re.search(r"选中股票 [：:]\s*(\d+)\s*只", output)
    
    # 格式 2: "最终选中：XX 只"
    final_match = re.search(r"最终选中 [：:]\s*(\d+)\s*只", output)
    
    # 格式 3: "输出股票数：XX 只" (多步骤)
    output_matches = re.findall(r"输出股票数 [：:]\s*(\d+)\s*只", output)
    
    # 格式 4: 板块汇总 "X01 (低于五年周线): XX 只"
    block_matches = re.findall(r"(\w+)\s*\([^)]+\)[：:]\s*(\d+)\s*只股票", output)
    
    if block_matches:
        for block_code, count in block_matches:
            result["results"].append({
                "target_block": block_code,
                "count": int(count),
            })
    elif select_match or final_match:
        count = int(select_match.group(1) if select_match else final_match.group(1))
        result["results"].append({
            "target_block": "N/A",
            "count": count,
        })
    elif output_matches:
        for i, count in enumerate(output_matches):
            result["results"].append({
                "target_block": f"Step{i+1}",
                "count": int(count),
            })
    
    return result


def run_program(program_name: str, desc: str, index: int, total: int) -> tuple:
    """
    运行单个选股程序
    
    Returns:
        tuple: (是否成功，输出内容，解析结果)
    """
    print()
    print("=" * 70)
    print(f"步骤 {index}/{total}: {desc}")
    print(f"程序：{program_name}")
    print("=" * 70)
    print()
    
    program_path = PROJECT_ROOT / program_name
    
    if not program_path.exists():
        print(f"错误：程序 {program_name} 不存在")
        return False, "", None
    
    try:
        # 运行程序
        result = subprocess.run(
            [sys.executable, str(program_path)],
            cwd=str(PROJECT_ROOT),
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        output = result.stdout + result.stderr
        
        # 打印输出
        print(output)
        
        # 解析结果
        parsed = parse_output(output, program_name)
        
        if result.returncode == 0:
            print()
            print(f"[OK] {program_name} 执行成功")
            return True, output, parsed
        else:
            print()
            print(f"[FAIL] {program_name} 执行失败 (返回码：{result.returncode})")
            return False, output, parsed
            
    except Exception as e:
        print()
        print(f"[ERROR] {program_name} 执行异常：{e}")
        return False, "", None


def print_header():
    """打印程序头部信息"""
    print()
    print("=" * 70)
    print("通达信选股程序总入口")
    print("=" * 70)
    print()
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("执行顺序:")
    for i, prog in enumerate(XG_PROGRAMS, 1):
        print(f"  {i}. {prog['name']}: {prog['desc']}")
    print()
    print("=" * 70)
    print()


def print_footer(success_count: int, total: int):
    """打印程序尾部信息"""
    print()
    print("=" * 70)
    print("选股任务完成")
    print("=" * 70)
    print()
    print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"执行结果：{success_count}/{total} 程序成功")
    print()
    
    if success_count == total:
        print("[OK] 所有选股程序执行成功！")
    else:
        print(f"[WARN] 有 {total - success_count} 个程序执行失败，请检查日志")
    
    print()
    print("=" * 70)


def print_summary(all_results: list):
    """打印选股结果汇总"""
    print()
    print("=" * 70)
    print("选股结果汇总")
    print("=" * 70)
    print()
    
    print("选股流程:")
    print("-" * 70)
    print()
    
    # 打印每个程序的结果
    for result in all_results:
        if not result:
            continue
        
        program = result.get("program", "Unknown")
        source = result.get("source_block", "N/A")
        source_count = result.get("source_count", 0)
        targets = result.get("results", [])
        
        print(f"程序：{program}")
        print(f"  源板块：{source} ({source_count} 只)")
        
        if targets:
            print(f"  目标板块:")
            for t in targets:
                block = t.get("target_block", "N/A")
                count = t.get("count", 0)
                print(f"    - {block}: {count} 只")
        print()
    
    print("-" * 70)
    print()
    
    # 打印最终板块统计
    print("最终板块持股统计:")
    print("-" * 70)
    print()
    print(f"{'板块代码':<10} {'来源程序':<25} {'股票数量':>10}")
    print("-" * 50)
    
    # 收集所有目标板块
    all_blocks = {}
    for result in all_results:
        if not result:
            continue
        program = result.get("program", "Unknown")
        for t in result.get("results", []):
            block = t.get("target_block", "N/A")
            count = t.get("count", 0)
            # 跳过无效板块名
            if block in ["N/A", "Step1", "Step2", "Step3"]:
                continue
            # 更新板块信息（保留最新值）
            all_blocks[block] = {
                "count": count,
                "program": program,
            }
    
    # 打印板块统计
    for block, info in sorted(all_blocks.items()):
        print(f"{block:<10} {info['program']:<25} {info['count']:>10}")
    
    print("-" * 70)
    print()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数：依次运行所有选股程序"""
    print_header()
    
    success_count = 0
    total = len(XG_PROGRAMS)
    all_results = []
    
    for i, prog in enumerate(XG_PROGRAMS, 1):
        success, output, parsed = run_program(
            program_name=prog["name"],
            desc=prog["desc"],
            index=i,
            total=total
        )
        
        all_results.append(parsed)
        
        if success:
            success_count += 1
    
    # 打印汇总
    print_summary(all_results)
    
    print_footer(success_count, total)
    
    # 返回退出码
    sys.exit(0 if success_count == total else 1)


if __name__ == "__main__":
    main()
