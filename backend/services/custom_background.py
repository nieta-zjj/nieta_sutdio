"""
自定义后台任务服务模块

提供一个简单的接口，用于将任务发送到Dramatiq队列，
替代直接调用dramatiq.send()方法
"""
import typing
import logging
from dramatiq.brokers.redis import RedisBroker
from dramatiq import Message

from backend.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class CustomBackgroundService:
    """自定义后台任务服务，封装Dramatiq消息队列操作"""

    def __init__(self) -> None:
        """初始化自定义后台任务服务"""
        # 使用配置中的Redis URL
        self.broker_url = settings.BROKER_REDIS_URL
        logger.info(f"初始化自定义后台任务服务，使用Redis: {self.broker_url}")

        # 创建Redis代理
        self.broker = RedisBroker(url=self.broker_url)

    def enqueue(self, actor_name: str, kwargs: dict, queue_name: str = "default", delay: int = None) -> None:
        """
        将任务发送到Dramatiq队列

        Args:
            actor_name: Actor名称
            kwargs: 任务参数
            queue_name: 队列名称，默认为default
            delay: 延迟执行时间（毫秒），默认为None（立即执行）
        """
        # 创建消息（不在options中包含delay）
        msg = Message(
            queue_name=queue_name,
            actor_name=actor_name,
            args=(),
            kwargs=kwargs,
            options={},  # 延迟参数不放在options中
        )

        # 发送消息到队列，将delay作为关键字参数传递给enqueue方法
        if delay is not None:
            logger.debug(f"发送延迟任务到队列: {queue_name}, Actor: {actor_name}, 参数: {kwargs}, 延迟: {delay}毫秒")
            self.broker.enqueue(msg, delay=delay)
        else:
            logger.debug(f"发送立即任务到队列: {queue_name}, Actor: {actor_name}, 参数: {kwargs}")
            self.broker.enqueue(msg)

        logger.debug(f"任务已发送到队列: {queue_name}")


# 单例模式
_custom_background_service_instance: typing.Optional[CustomBackgroundService] = None


def get_background_service() -> CustomBackgroundService:
    """
    获取自定义后台任务服务实例（单例模式）

    Returns:
        自定义后台任务服务实例
    """
    global _custom_background_service_instance
    if _custom_background_service_instance is None:
        _custom_background_service_instance = CustomBackgroundService()
    return _custom_background_service_instance
