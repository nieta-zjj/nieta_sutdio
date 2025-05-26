"""
Redis 队列监控模块
"""
import redis
from typing import Optional
from loguru import logger
from config import config

class RedisMonitor:
    """Redis 队列监控器"""

    def __init__(self):
        """初始化 Redis 连接"""
        self.redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self) -> None:
        """连接到 Redis"""
        try:
            self.redis_client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.redis_client.ping()
            logger.info(f"成功连接到 Redis: {config.redis_host}:{config.redis_port}")
        except Exception as e:
            logger.error(f"连接 Redis 失败: {e}")
            self.redis_client = None
            raise

    def get_queue_length(self, queue_name: str = None) -> int:
        """
        获取指定队列的任务数量

        Args:
            queue_name: 队列名称，默认使用配置中的队列名

        Returns:
            队列中的任务数量
        """
        if not self.redis_client:
            logger.warning("Redis 连接不可用，尝试重新连接")
            self._connect()

        if not queue_name:
            queue_name = config.dramatiq_queue_name

        try:
            # Dramatiq 使用的队列键格式
            queue_key = f"dramatiq:queue:{queue_name}"
            length = self.redis_client.llen(queue_key)
            logger.debug(f"队列 {queue_name} 当前任务数: {length}")
            return length
        except Exception as e:
            logger.error(f"获取队列长度失败: {e}")
            return 0

    def get_all_queue_info(self) -> dict:
        """
        获取所有 Dramatiq 相关队列的信息

        Returns:
            包含队列信息的字典
        """
        if not self.redis_client:
            self._connect()

        try:
            # 获取所有 dramatiq 相关的键
            pattern = "dramatiq:*"
            keys = self.redis_client.keys(pattern)

            queue_info = {}
            for key in keys:
                if key.startswith("dramatiq:queue:"):
                    queue_name = key.replace("dramatiq:queue:", "")
                    length = self.redis_client.llen(key)
                    queue_info[queue_name] = length

            logger.debug(f"所有队列信息: {queue_info}")
            return queue_info
        except Exception as e:
            logger.error(f"获取队列信息失败: {e}")
            return {}

    def is_connected(self) -> bool:
        """检查 Redis 连接状态"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception:
            pass
        return False

    def close(self) -> None:
        """关闭 Redis 连接"""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("Redis 连接已关闭")
            except Exception as e:
                logger.error(f"关闭 Redis 连接失败: {e}")
            finally:
                self.redis_client = None