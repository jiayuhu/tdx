"""
数据库清空工具

清空数据库中所有表的数据。

使用示例:
    python dbclear.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "quant.db"


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
        conn.close()
        return 0

    # 清空所有表
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"已清空 {table}")

    conn.commit()

    # 显示结果
    print("\n清空完成！")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")

    conn.close()
    return len(tables)


if __name__ == "__main__":
    clear_database(DB_PATH)
