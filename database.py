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

import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from base import EMA_LONG_WEIGHT, EMA_SHORT_WEIGHT, get_tq
from logging_config import logger, log_exceptions, suppress_tq_errors

_TABLE_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _utc_now() -> str:
    """返回当前 UTC 时间字符串 (YYYY-MM-DD HH:MM:SS)"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _utc_today() -> str:
    """返回当前 UTC 日期字符串 (YYYY-MM-DD)"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def _safe_table_name(name: str) -> str:
    """校验并返回安全的表名，不合法则抛出 ValueError"""
    if not _TABLE_NAME_RE.match(name):
        raise ValueError(f"非法表名: {name!r}")
    return name


class StockDatabase:
    """选股数据库管理器"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.touch(exist_ok=True)

    def init(self, blocks: List[Dict[str, Any]]) -> None:
        """初始化数据库表结构"""
        logger.info(f"初始化数据库，共 {len(blocks)} 个板块")
        self.db_path.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()

            for block_config in blocks:
                block_code = block_config.get('code')
                try:
                    table_name = _safe_table_name(block_code.lower())
                    delta_table = _safe_table_name(f"{block_code.lower()}_delta")
                except ValueError as e:
                    print(f"跳过板块 '{block_code}'：{e}")
                    continue

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
        finally:
            conn.close()

    def fetch_stocks(
        self,
        block_code: str,
        block_manager,
        block_type: int = 1,
    ) -> Optional[Dict[str, str]]:
        """获取板块股票及名称"""
        try:
            stocks = block_manager.get_block_stocks(block_code, block_type=block_type)
            if not stocks:
                logger.debug(f"板块 '{block_code}' 无成分股")
                return None

            tq = get_tq()
            stock_data: Dict[str, str] = {}
            for stock in stocks:
                try:
                    info = tq.get_stock_info(stock, field_list=['Name'])
                    stock_data[stock] = info.get('Name', '') if info else ''
                except Exception as e:
                    logger.warning(f"获取股票 {stock} 信息失败: {e}")
                    stock_data[stock] = ''
            return stock_data
        except Exception as e:
            logger.error(f"获取板块 '{block_code}' 股票数据失败: {e}")
            return None

    def save_stocks(self, table_name: str, stock_data: Dict[str, str], record_date: str) -> None:
        """保存股票数据到数据库（record_date 为 UTC datetime 字符串）"""
        logger.info(f"保存股票数据到表 {table_name}，共 {len(stock_data)} 只股票")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE date(record_date) = date(?)", (record_date,))
            cursor.executemany(
                f"INSERT INTO {table_name} (stock_code, stock_name, record_date) VALUES (?, ?, ?)",
                [(s[0], s[1], record_date) for s in stock_data.items()],
            )
            conn.commit()
            logger.info(f"成功保存 {len(stock_data)} 只股票到 {table_name}")
        except Exception as e:
            logger.error(f"保存股票数据到 {table_name} 失败: {e}")
            raise
        finally:
            conn.close()

    def get_recent_dates(self, table_name: str, limit: int = 2) -> List[str]:
        """获取最近 N 个交易日期（返回 UTC 日期字符串 YYYY-MM-DD）"""
        logger.debug(f"获取表 {table_name} 的最近 {limit} 个交易日日期")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT DISTINCT date(record_date) as d FROM {table_name} ORDER BY d DESC LIMIT ?",
                (limit,),
            )
            dates = [row[0] for row in cursor.fetchall()]
            logger.debug(f"从 {table_name} 获取到 {len(dates)} 个日期: {dates}")
            return dates
        except Exception as e:
            logger.error(f"获取 {table_name} 最近日期失败: {e}")
            raise
        finally:
            conn.close()

    def get_stocks_by_date(self, table_name: str, record_day: str) -> Dict[str, str]:
        """获取指定日期的股票数据（record_day 为 YYYY-MM-DD）"""
        logger.debug(f"获取表 {table_name} 在 {record_day} 的股票数据")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT stock_code, stock_name FROM {table_name} WHERE date(record_date) = ?", (record_day,))
            result = {row[0]: row[1] for row in cursor.fetchall()}
            logger.debug(f"从 {table_name} 获取到 {len(result)} 只股票")
            return result
        except Exception as e:
            logger.error(f"获取 {table_name} 在 {record_day} 的股票数据失败: {e}")
            raise
        finally:
            conn.close()

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
        """保存增量股票到数据库（record_date 为 UTC datetime 字符串）"""
        logger.info(f"保存增量数据到表 {delta_table}，新增 {len(added)} 只股票")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            tq = get_tq()

            for stock in added:
                try:
                    cursor.execute(
                        f"SELECT id FROM {delta_table} WHERE stock_code = ? AND date(record_date) = date(?)",
                        (stock, record_date),
                    )
                    if cursor.fetchone():
                        continue
                    buy_point = self.calculate_buy_point(tq, stock)
                    cursor.execute(
                        f"INSERT INTO {delta_table} (stock_code, stock_name, entry_date, buy_point, record_date) VALUES (?, ?, ?, ?, ?)",
                        (stock, curr_db.get(stock, ''), record_date, buy_point, record_date),
                    )
                except Exception as e:
                    logger.warning(f"处理股票 {stock} 失败：{e}")
                    continue
            conn.commit()
            logger.info(f"成功保存 {len(added)} 只增量股票到 {delta_table}")
        except Exception as e:
            logger.error(f"保存增量数据到 {delta_table} 失败: {e}")
            raise
        finally:
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
                logger.debug(f"股票 {stock_code} 无行情数据")
                return 0.0
            close_series = result['Close'][stock_code]
            if len(close_series) < 2:
                return float(close_series.iloc[-1]) if len(close_series) > 0 else 0.0
            close_prices = close_series.values
            return float(close_prices[-1] * EMA_SHORT_WEIGHT + close_prices[-2] * EMA_LONG_WEIGHT)
        except Exception as e:
            logger.warning(f"计算股票 {stock_code} 买点失败: {e}")
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
        logger.info(f"保存更新日志: 板块 {block_code}, 新增 {added}, 减少 {removed}")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            now = _utc_now()
            cursor.execute(
                """INSERT INTO update_log (update_date, block_code, prev_count, curr_count, added_count, removed_count) VALUES (?, ?, ?, ?, ?, ?)""",
                (now, block_code, prev_count, curr_count, added, removed),
            )
            conn.commit()
            logger.debug(f"成功保存更新日志: {block_code}")
        except Exception as e:
            logger.error(f"保存更新日志失败: {e}")
            raise
        finally:
            conn.close()

    def cleanup(self, table_name: str, delta_table: str, keep_days: int) -> None:
        """清理旧数据"""
        logger.info(f"清理表 {table_name} 和 {delta_table} 中 {keep_days} 天前的数据")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=keep_days)).strftime('%Y-%m-%d')
            cursor.execute(f"DELETE FROM {table_name} WHERE date(record_date) < ?", (cutoff_date,))
            deleted_main = cursor.rowcount
            cursor.execute(f"DELETE FROM {delta_table} WHERE date(record_date) < ?", (cutoff_date,))
            deleted_delta = cursor.rowcount
            conn.commit()
            logger.info(f"清理完成: {table_name} 删除 {deleted_main} 条, {delta_table} 删除 {deleted_delta} 条")
        except Exception as e:
            logger.error(f"清理数据失败: {e}")
            raise
        finally:
            conn.close()

    def update_block(self, target_block: str, target_block_name: str, stocks: List[str], block_manager) -> None:
        """更新目标板块（重建方式）"""
        if not stocks:
            logger.debug(f"无新增股票，跳过更新板块 '{target_block}'")
            return
        block_manager.update_target_block_with_recreate(target_block, target_block_name, stocks)

    def clear_delta_block(self, target_block: str, target_block_name: str, block_manager) -> None:
        """清空 delta 板块（当无新增股票时）"""
        logger.info(f"无新增股票，清空 delta 板块 '{target_block}'")
        # 如果板块不存在，先创建
        if not block_manager.find_block_by_code(target_block):
            logger.info(f"板块 '{target_block}' 不存在，创建新板块")
            block_manager.create_block(target_block, target_block_name)
        # 清空板块内容
        block_manager.clear_block_stocks(target_block)

    def process_block(
        self,
        block_config: Dict[str, Any],
        block_manager,
        keep_days: int,
    ) -> Dict[str, Any]:
        """处理单个板块的数据库更新"""
        block_code = block_config.get('code')
        target_block = block_config.get('target_block')
        target_block_name = block_config.get('target_block_name')

        # 检查源板块是否存在
        if not block_manager.find_block_by_code(block_code):
            logger.info(f"源板块 '{block_code}' 不存在，跳过处理")
            return {
                'block_code': block_code,
                'target_block': target_block,
                'error': '板块不存在',
                'skipped': True,
                'delta_action': '跳过'
            }

        try:
            table_name = _safe_table_name(block_code.lower())
            delta_table = _safe_table_name(f"{block_code.lower()}_delta")
        except ValueError as e:
            logger.error(f"板块 '{block_code}' 表名校验失败：{e}")
            return {'block_code': block_code, 'target_block': target_block, 'error': str(e), 'delta_action': '错误'}

        now = _utc_now()
        # 抑制 TQ API 的错误输出
        with suppress_tq_errors():
            stock_data = self.fetch_stocks(block_code, block_manager, block_type=1)

        if not stock_data:
            logger.info(f"板块 '{block_code}' 无成分股，跳过处理")
            # 无成分股时清空delta板块
            self.clear_delta_block(target_block, target_block_name, block_manager)
            return {
                'block_code': block_code,
                'target_block': target_block,
                'error': '无成分股',
                'skipped': True,
                'curr_count': 0,
                'added': 0,
                'removed': 0,
                'delta_action': '已清空'
            }

        self.save_stocks(table_name, stock_data, now)
        dates = self.get_recent_dates(table_name, limit=2)

        if len(dates) < 1:
            # 首日记录时，也需要清空 delta 板块（确保干净）
            self.clear_delta_block(target_block, target_block_name, block_manager)
            return {
                'block_code': block_code,
                'target_block': target_block,
                'curr_count': len(stock_data),
                'added': 0,
                'removed': 0,
                'delta_action': '首日记录'
            }

        curr_db = self.get_stocks_by_date(table_name, dates[0])
        prev_db = self.get_stocks_by_date(table_name, dates[1]) if len(dates) > 1 else {}

        added, removed = self.calculate_delta(curr_db, prev_db)
        self.save_delta(delta_table, added, curr_db, now)
        self.save_log(block_code, len(prev_db), len(curr_db), len(added), len(removed))
        self.cleanup(table_name, delta_table, keep_days)

        if added:
            self.update_block(target_block, target_block_name, list(added), block_manager)
            delta_action = f'更新({len(added)}只)'
        else:
            # 无新增股票时，清空 delta 板块
            self.clear_delta_block(target_block, target_block_name, block_manager)
            delta_action = '已清空'

        return {
            'block_code': block_code,
            'target_block': target_block,
            'curr_count': len(stock_data),
            'added': len(added),
            'removed': len(removed),
            'delta_action': delta_action,
        }
