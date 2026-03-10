"""
基础模块 - TQ 单例管理和配置

提供基础功能：
- TQ 单例管理
- 配置读取
- 项目根目录获取
- 常量定义

使用示例:
    from base import init_tq_context, close_tq_context, get_tq, get_config

    init_tq_context(__file__)
    config = get_config()
    tq = get_tq()
    close_tq_context()
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

# ============================================================================
# 常量定义
# ============================================================================

STRATEGY_TYPE_SINGLE = 'single'
STRATEGY_TYPE_MULTI = 'multi'
STRATEGY_TYPE_PARALLEL = 'parallel'
STRATEGY_TYPE_DB_UPDATE = 'db_update'

BATCH_SIZE = 200
DIVIDEND_TYPE = 1
DATA_COUNT = -1
DEFAULT_PERIOD = '1d'

EMA_SHORT_WEIGHT = 2 / 3
EMA_LONG_WEIGHT = 1 / 3

# ============================================================================
# TQ 单例管理
# ============================================================================

_tq_instance: Optional[Any] = None
_config: Optional[dict] = None
PROJECT_ROOT: Optional[Path] = None


def init_tq_context(script_path: str) -> None:
    """初始化 TQ 上下文"""
    global _tq_instance, _config, PROJECT_ROOT

    if _tq_instance is not None:
        return

    PROJECT_ROOT = Path(script_path).parent

    try:
        with open(PROJECT_ROOT / "config.yaml", "r", encoding="utf-8") as f:
            _config = yaml.safe_load(f)
    except FileNotFoundError:
        print("错误：配置文件 config.yaml 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"读取配置文件失败：{e}")
        sys.exit(1)

    TDX_ROOT = _config.get("tdx_root", r"D:\App\new_tdx64")
    PLUGIN_PATH = os.path.join(TDX_ROOT, "PYPlugins", "user")
    sys.path.insert(0, PLUGIN_PATH)

    from tqcenter import tq

    tq.initialize(script_path)
    _tq_instance = tq


def close_tq_context() -> None:
    """关闭 TQ 上下文"""
    global _tq_instance, _config, PROJECT_ROOT

    if _tq_instance:
        try:
            _tq_instance.close()
        except Exception:
            pass
        _tq_instance = None
        _config = None
        PROJECT_ROOT = None


def get_tq() -> Any:
    """获取 TQ 实例"""
    if _tq_instance is None:
        raise RuntimeError("TQ 未初始化，请先调用 init_tq_context()")
    return _tq_instance


def get_config() -> Optional[dict]:
    """获取配置"""
    if _config is None:
        raise RuntimeError("TQ 未初始化，请先调用 init_tq_context()")
    return _config


def get_project_root() -> Path:
    """获取项目根目录"""
    if PROJECT_ROOT is None:
        raise RuntimeError("TQ 未初始化，请先调用 init_tq_context()")
    return PROJECT_ROOT
