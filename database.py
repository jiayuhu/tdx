"""
选股数据库模块 - 数据存储和管理

负责选股数据的存储和管理：
- 数据库初始化
- 股票数据保存
- 增量计算
- 日志记录
- 数据清理

使用示例:
    from database import StockDatabase

    db = StockDatabase(DB_PATH)
    db.init(blocks)
    result = db.process_block(block_config, block_manager, keep_days)
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from base import EMA_LONG_WEIGHT, EMA_SHORT_WEIGHT, get_tq


class StockDatabase:
    """选股数据库管理器"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init(self, blocks: List[Dict[str, Any]]) -> None:
        """初始化数据库表结构"""
        self.db_path.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        for block_config in blocks:
            block_code = block_config.get('code')
            table_name = f"{block_code.lower()}"

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    record_date DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name}(record_date)")

            delta_table = f"{block_code.lower()}_delta"
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {delta_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    entry_date DATETIME NOT NULL,
                    buy_point REAL,
                    record_date DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stock_code, record_date)
                )
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{delta_table}_date ON {delta_table}(record_date)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_date DATETIME NOT NULL,
                block_code TEXT NOT NULL,
                prev_count INTEGER,
                curr_count INTEGER,
                added_count INTEGER,
                removed_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def fetch_stocks(
        self,
        block_code: str,
        block_manager,
        block_type: int = 1,
    ) -> Optional[Dict[str, str]]:
        """获取板块股票及名称"""
        stocks = block_manager.get_block_stocks(block_code, block_type=block_type)
        if not stocks:
            return None

        tq = get_tq()
        stock_data: Dict[str, str] = {}
        for stock in stocks:
            try:
                info = tq.get_stock_info(stock, field_list=['Name'])
                stock_data[stock] = info.get('Name', '') if info else ''
            except Exception:
                stock_data[stock] = ''
        return stock_data

    def save_stocks(self, table_name: str, stock_data: Dict[str, str], record_date: str) -> None:
        """保存股票数据到数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE date(record_date) = date(?)", (record_date,))
        cursor.executemany(
            f"INSERT INTO {table_name} (stock_code, stock_name, record_date) VALUES (?, ?, ?)",
            [(s[0], s[1], record_date) for s in stock_data.items()],
        )
        conn.commit()
        conn.close()

    def get_recent_dates(self, table_name: str, limit: int = 2) -> List[str]:
        """获取最近 N 个交易日期"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT DISTINCT date(record_date) as record_day FROM {table_name} ORDER BY record_day DESC LIMIT ?",
            (limit,),
        )
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates

    def get_stocks_by_date(self, table_name: str, date: str) -> Dict[str, str]:
        """获取指定日期的股票数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(f"SELECT stock_code, stock_name FROM {table_name} WHERE date(record_date) = ?", (date,))
        result = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return result

    @staticmethod
    def calculate_delta(
        curr_db: Dict[str, str],
        prev_db: Dict[str, str],
    ) -> Tuple[set, set]:
        """计算增量和减少"""
        curr_set = set(curr_db.keys())
        prev_set = set(prev_db.keys())
        return curr_set - prev_set, prev_set - curr_set

    def save_delta(
        self,
        delta_table: str,
        added: set,
        curr_db: Dict[str, str],
        record_date: str,
    ) -> None:
        """保存增量股票到数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        utc_now = datetime.now(timezone.utc).isoformat()
        tq = get_tq()

        for stock in added:
            cursor.execute(
                f"SELECT id FROM {delta_table} WHERE stock_code = ? AND date(record_date) = date(?)",
                (stock, record_date),
            )
            if cursor.fetchone():
                continue
            buy_point = self.calculate_buy_point(tq, stock)
            cursor.execute(
                f"INSERT INTO {delta_table} (stock_code, stock_name, entry_date, buy_point, record_date) VALUES (?, ?, ?, ?, ?)",
                (stock, curr_db.get(stock, ''), utc_now, buy_point, utc_now),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def calculate_buy_point(tq, stock_code: str) -> float:
        """计算买点 EMA(C,2)"""
        try:
            result = tq.get_market_data(
                field_list=['Close'],
                stock_list=[stock_code],
                period='1d',
                count=10,
                dividend_type='front',
            )
            if not result or 'Close' not in result:
                return 0.0
            close_series = result['Close'][stock_code]
            if len(close_series) < 2:
                return float(close_series.iloc[-1]) if len(close_series) > 0 else 0.0
            close_prices = close_series.values
            return float(close_prices[-1] * EMA_SHORT_WEIGHT + close_prices[-2] * EMA_LONG_WEIGHT)
        except Exception:
            return 0.0

    def save_log(
        self,
        block_code: str,
        prev_count: int,
        curr_count: int,
        added: int,
        removed: int,
    ) -> None:
        """保存更新日志"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        today = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """INSERT INTO update_log (update_date, block_code, prev_count, curr_count, added_count, removed_count) VALUES (?, ?, ?, ?, ?, ?)""",
            (today, block_code, prev_count, curr_count, added, removed),
        )
        conn.commit()
        conn.close()

    def cleanup(self, table_name: str, delta_table: str, keep_days: int) -> None:
        """清理旧数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=keep_days)).isoformat()
        cursor.execute(f"DELETE FROM {table_name} WHERE date(record_date) < date(?)", (cutoff_date,))
        cursor.execute(f"DELETE FROM {delta_table} WHERE date(record_date) < date(?)", (cutoff_date,))
        conn.commit()
        conn.close()

    def update_block(self, target_block: str, stocks: List[str], block_manager) -> None:
        """更新目标板块"""
        block_manager.update_target_block(target_block, stocks)

    def process_block(
        self,
        block_config: Dict[str, Any],
        block_manager,
        keep_days: int,
    ) -> Dict[str, Any]:
        """处理单个板块的数据库更新"""
        block_code = block_config.get('code')
        target_block = block_config.get('target_block')
        table_name = block_code.lower()
        delta_table = f"{block_code.lower()}_delta"

        today = datetime.now(timezone.utc).isoformat()
        stock_data = self.fetch_stocks(block_code, block_manager, block_type=1)

        if not stock_data:
            return {'block_code': block_code, 'error': '无数据'}

        self.save_stocks(table_name, stock_data, today)
        dates = self.get_recent_dates(table_name, limit=2)

        if len(dates) < 1:
            return {'block_code': block_code, 'curr_count': len(stock_data), 'added': 0, 'removed': 0}

        curr_db = self.get_stocks_by_date(table_name, dates[0])
        prev_db = self.get_stocks_by_date(table_name, dates[1]) if len(dates) > 1 else {}

        added, removed = self.calculate_delta(curr_db, prev_db)
        self.save_delta(delta_table, added, curr_db, dates[0])
        self.save_log(block_code, len(prev_db), len(curr_db), len(added), len(removed))
        self.cleanup(table_name, delta_table, keep_days)

        if added:
            self.update_block(target_block, list(added), block_manager)

        return {
            'block_code': block_code,
            'curr_count': len(stock_data),
            'added': len(added),
            'removed': len(removed),
        }
