"""
Dramatiq 进程管理器

一个用于自动管理 Dramatiq worker 进程的独立服务，支持基于队列长度的自动扩缩容。
"""

__version__ = "1.0.0"
__author__ = "Process Manager Team"
__description__ = "Dramatiq Worker Process Manager with Auto-scaling"

from .config import config
from .redis_monitor import RedisMonitor
from .process_manager import ProcessManager
from .auto_scaler import AutoScaler

__all__ = [
    "config",
    "RedisMonitor",
    "ProcessManager",
    "AutoScaler"
]