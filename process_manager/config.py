"""
进程管理器配置模块
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ProcessManagerConfig(BaseSettings):
    """进程管理器配置"""

    # Redis 配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Dramatiq 配置
    dramatiq_queue_name: str = Field(default="nietest_subtask", env="DRAMATIQ_QUEUE_NAME")
    dramatiq_command: str = Field(
        default="python -m dramatiq --processes 1 --threads 5 --verbose backend.dramatiq_app.workers.subtask",
        env="DRAMATIQ_COMMAND"
    )

    # 进程管理配置
    min_processes: int = Field(default=1, env="MIN_PROCESSES")
    max_processes: int = Field(default=10, env="MAX_PROCESSES")
    check_interval: int = Field(default=180, env="CHECK_INTERVAL")  # 3分钟
    scale_up_threshold_multiplier: int = Field(default=5, env="SCALE_UP_THRESHOLD_MULTIPLIER")
    scale_down_threshold_multiplier: float = Field(default=2.5, env="SCALE_DOWN_THRESHOLD_MULTIPLIER")

    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="process_manager.log", env="LOG_FILE")

    # 进程管理器配置
    graceful_shutdown_timeout: int = Field(default=30, env="GRACEFUL_SHUTDOWN_TIMEOUT")
    process_startup_delay: int = Field(default=5, env="PROCESS_STARTUP_DELAY")

    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
config = ProcessManagerConfig()