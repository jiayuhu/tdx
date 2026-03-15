"""
数据库清空工具

清空数据库中所有表的数据。

使用示例:
    python dbclear.py
"""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "quant.db"


def _validate_table_name(table_name: str) -> bool:
    """验证表名安全性，防止SQL注入"""
    # 只允许字母、数字和下划线
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name))


def clear_database(db_path: Path) -> int:
    """
    清空数据库所有表的数据

    Args:
        db_path: 数据库文件路径

    Returns:
        int: 清空的表数量
    """
    if not db_path.exists():
        print("数据库文件不存在")
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite%'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"发现 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table}")

        confirm = input("\n确定要清空所有表的数据吗？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return 0

        # 清空所有表
        for table in tables:
            # 验证表名安全性
            if not _validate_table_name(table):
                print(f"跳过非法表名: {table}")
                continue
            cursor.execute(f"DELETE FROM {table}")
            print(f"已清空 {table}")

        conn.commit()

        # 显示结果
        print("\n清空完成！")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")

        return len(tables)
    finally:
        conn.close()


if __name__ == "__main__":
    clear_database(DB_PATH)
