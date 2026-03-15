"""
数据库查看工具

功能:
1. 查看数据表和数据表结构
2. 查看数据库中的数据

使用示例:
    python dbview.py              # 交互模式
    python dbview.py --tables     # 列出所有表
    python dbview.py --schema b01 # 查看 b01 表结构
    python dbview.py --data b01 -n 10  # 查看 b01 表前 10 条数据
"""

import re
import sqlite3
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

_BJT_OFFSET = timedelta(hours=8)


def _to_beijing(utc_str: str) -> str:
    """将 UTC 时间字符串转换为北京时间 (UTC+8) 显示"""
    try:
        dt = datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S')
        bjt = dt + _BJT_OFFSET
        return bjt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return utc_str

DB_PATH = Path(__file__).parent / "data" / "quant.db"

_TABLE_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_table_name(name: str) -> bool:
    """校验表名是否只含字母、数字和下划线"""
    return bool(_TABLE_NAME_RE.match(name))


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"数据库文件不存在：{DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn: sqlite3.Connection) -> None:
    """列出所有表"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite%'
        ORDER BY name
    """)
    tables = [row['name'] for row in cursor.fetchall()]

    print(f"\n数据库：{DB_PATH}")
    print(f"表数量：{len(tables)}")
    print()
    print(f"{'表名':<20} {'记录数':>10}")
    print("-" * 35)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"{table:<20} {count:>10}")

    print()


def show_table_schema(conn: sqlite3.Connection, table_name: str) -> None:
    """显示表结构"""
    if not _validate_table_name(table_name):
        print(f"错误：表名 '{table_name}' 含有非法字符")
        return

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))

    if not cursor.fetchone():
        print(f"错误：表 '{table_name}' 不存在")
        return

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()

    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    count = cursor.fetchone()['count']

    print(f"\n表：{table_name}")
    print(f"记录数：{count}")
    print()
    print("列信息:")
    print(f"{'ID':<5} {'列名':<20} {'类型':<15} {'非空':<6} {'默认值':<15} {'主键':<6}")
    print("-" * 70)

    for col in columns:
        dflt_val = str(col['dflt_value']) if col['dflt_value'] is not None else 'NULL'
        notnull_str = '是' if col['notnull'] else '否'
        pk_str = '是' if col['pk'] else '否'
        print(f"{col['cid']:<5} {col['name']:<20} {col['type']:<15} "
              f"{notnull_str:<6} {dflt_val:<15} {pk_str:<6}")

    if indexes:
        print()
        print("索引:")
        for idx in indexes:
            cursor.execute(f"PRAGMA index_info({idx['name']})")
            idx_cols = cursor.fetchall()
            col_names = ', '.join([col['name'] for col in idx_cols])
            print(f"  {idx['name']}: {col_names}")

    print()


def show_table_data(conn: sqlite3.Connection, table_name: str, 
                    limit: int = 10, where: Optional[str] = None) -> None:
    """显示表数据"""
    if not _validate_table_name(table_name):
        print(f"错误：表名 '{table_name}' 含有非法字符")
        return

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))

    if not cursor.fetchone():
        print(f"错误：表 '{table_name}' 不存在")
        return

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    col_names = [col['name'] for col in columns]
    # 识别 DATETIME/TIMESTAMP 列，用于 UTC→北京时间转换
    datetime_cols = {
        col['name'] for col in columns
        if col['type'].upper() in ('DATETIME', 'TIMESTAMP')
    }

    query = f"SELECT * FROM {table_name}"
    params = []
    
    if where:
        # 简单的 WHERE 条件验证：只支持 column = 'value' 格式
        import re
        match = re.match(r"^(\w+)\s*=\s*[\"'](.+?)[\"']\s*$", where.strip())
        if match:
            col_name, value = match.groups()
            # 验证列名是否存在于表中
            if col_name in col_names:
                query += f" WHERE {col_name} = ?"
                params.append(value)
            else:
                print(f"错误：列名 '{col_name}' 不存在")
                return
        else:
            print("错误：WHERE 条件格式不支持（仅支持 column = 'value'）")
            return
    
    query += f" ORDER BY id DESC LIMIT {int(limit)}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()

    print(f"\n表：{table_name}")
    print(f"查询：{query}")
    print(f"返回 {len(rows)} 条记录")
    print()

    if rows:
        col_widths = []
        for i, col_name in enumerate(col_names):
            max_width = len(col_name)
            for row in rows:
                val = str(row[i]) if row[i] is not None else 'NULL'
                if col_name in datetime_cols:
                    val = _to_beijing(val)
                max_width = max(max_width, len(val))
            col_widths.append(min(max_width, 30))

        header = " | ".join([col_name.ljust(col_widths[i])
                            for i, col_name in enumerate(col_names)])
        print(header)
        print("-" * len(header))

        for row in rows:
            values = []
            for i, val in enumerate(row):
                val_str = str(val) if val is not None else 'NULL'
                if col_names[i] in datetime_cols and val is not None:
                    val_str = _to_beijing(val_str)
                if len(val_str) > col_widths[i]:
                    val_str = val_str[:col_widths[i]-3] + '...'
                values.append(val_str.ljust(col_widths[i]))
            print(" | ".join(values))
    else:
        print("(无数据)")

    print()


def interactive_mode(conn: sqlite3.Connection) -> None:
    """交互模式"""
    print("\n" + "=" * 70)
    print("数据库查看工具 - 交互模式")
    print("=" * 70)
    print()
    print("可用命令:")
    print("  tables              - 列出所有表")
    print("  schema <表名>       - 查看表结构")
    print("  data <表名> [n]     - 查看表数据 (默认前 10 条)")
    print("  search <表名> <条件> - 搜索数据 (WHERE 条件)")
    print("  help                - 显示帮助")
    print("  quit/exit           - 退出程序")
    print()

    while True:
        try:
            cmd = input("dbview> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        parts = cmd.split()
        command = parts[0].lower()

        if command in ('quit', 'exit', 'q'):
            break
        elif command == 'help':
            print("\n可用命令:")
            print("  tables              - 列出所有表")
            print("  schema <表名>       - 查看表结构")
            print("  data <表名> [n]     - 查看表数据 (默认前 10 条)")
            print("  search <表名> <条件> - 搜索数据 (WHERE 条件)")
            print("  help                - 显示帮助")
            print("  quit/exit           - 退出程序")
            print()
        elif command == 'tables':
            list_tables(conn)
        elif command == 'schema':
            if len(parts) < 2:
                print("用法：schema <表名>")
            else:
                table_name = parts[1]
                if not _validate_table_name(table_name):
                    print(f"错误：表名 '{table_name}' 含有非法字符")
                else:
                    show_table_schema(conn, table_name)
        elif command == 'data':
            if len(parts) < 2:
                print("用法：data <表名> [记录数]")
            else:
                table_name = parts[1]
                if not _validate_table_name(table_name):
                    print(f"错误：表名 '{table_name}' 含有非法字符")
                else:
                    limit = int(parts[2]) if len(parts) > 2 else 10
                    show_table_data(conn, table_name, limit)
        elif command == 'search':
            if len(parts) < 3:
                print("用法：search <表名> <WHERE 条件>")
                print("示例：search b01 record_date = '2026-03-08'")
            else:
                table_name = parts[1]
                if not _validate_table_name(table_name):
                    print(f"错误：表名 '{table_name}' 含有非法字符")
                else:
                    where = ' '.join(parts[2:])
                    show_table_data(conn, table_name, limit=50, where=where)
        else:
            print(f"未知命令：{command}")
            print("输入 'help' 查看可用命令")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='数据库查看工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python dbview.py                    # 交互模式
  python dbview.py --tables           # 列出所有表
  python dbview.py --schema b01       # 查看 b01 表结构
  python dbview.py --data b01         # 查看 b01 表前 10 条数据
  python dbview.py --data b01 -n 20   # 查看 b01 表前 20 条数据
  python dbview.py --search b01 "record_date = '2026-03-08'"  # 搜索数据
        """
    )

    parser.add_argument('--tables', action='store_true', help='列出所有表')
    parser.add_argument('--schema', metavar='TABLE', help='查看表结构')
    parser.add_argument('--data', metavar='TABLE', help='查看表数据')
    parser.add_argument('-n', '--limit', type=int, default=10, help='显示记录数 (默认 10)')
    parser.add_argument('--search', nargs=2, metavar=('TABLE', 'WHERE'), help='搜索数据')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        args.interactive = True

    try:
        conn = get_connection()
    except FileNotFoundError as e:
        print(f"错误：{e}")
        return 1

    try:
        if args.interactive:
            interactive_mode(conn)
        elif args.tables:
            list_tables(conn)
        elif args.schema:
            show_table_schema(conn, args.schema)
        elif args.data:
            show_table_data(conn, args.data, args.limit)
        elif args.search:
            show_table_data(conn, args.search[0], limit=50, where=args.search[1])
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    exit(main())
