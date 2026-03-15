import logging
import os
import sys
from contextlib import contextmanager
from functools import wraps

# 配置日志
logger = logging.getLogger(__name__)


@contextmanager
def suppress_tq_errors():
    """临时抑制 TQ API 的 stdout/stderr 输出

    注意：TQ API 是 C/C++ 编译库，直接写入 OS 文件描述符，
    Python 层面的重定向无法完全抑制其错误输出。
    这里只做 Python 层面的重定向。
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

def setup_logging(level=logging.INFO):
    """配置日志系统"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('xg.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def log_exceptions(func):
    """异常日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"函数 {func.__name__} 执行失败: {e}")
            raise
    return wrapper