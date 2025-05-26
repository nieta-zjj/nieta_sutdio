"""
自动扩缩容模块
"""
import time
import threading
from typing import Optional
from loguru import logger
from config import config
from redis_monitor import RedisMonitor
from process_manager import ProcessManager

class AutoScaler:
    """自动扩缩容器"""

    def __init__(self, process_manager: ProcessManager, redis_monitor: RedisMonitor):
        """
        初始化自动扩缩容器

        Args:
            process_manager: 进程管理器实例
            redis_monitor: Redis 监控器实例
        """
        self.process_manager = process_manager
        self.redis_monitor = redis_monitor
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        logger.info("自动扩缩容器初始化完成")

    def start_monitoring(self) -> None:
        """开始监控和自动扩缩容"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("监控线程已在运行")
            return

        logger.info("启动自动扩缩容监控")
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name="AutoScaler-Monitor",
            daemon=True
        )
        self.monitoring_thread.start()

    def stop_monitoring(self) -> None:
        """停止监控"""
        logger.info("停止自动扩缩容监控")
        self.stop_event.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
            if self.monitoring_thread.is_alive():
                logger.warning("监控线程未能在超时时间内停止")

    def _monitoring_loop(self) -> None:
        """监控循环"""
        logger.info(f"开始监控循环，检查间隔: {config.check_interval} 秒")

        while not self.stop_event.is_set():
            try:
                # 检查是否需要扩缩容
                self._check_and_scale()

                # 等待下一次检查
                if self.stop_event.wait(timeout=config.check_interval):
                    break  # 收到停止信号

            except Exception as e:
                logger.error(f"监控循环中发生异常: {e}")
                # 发生异常时等待一段时间再继续
                if self.stop_event.wait(timeout=30):
                    break

        logger.info("监控循环已停止")

    def _check_and_scale(self) -> None:
        """检查队列状态并执行扩缩容"""
        try:
            # 获取当前队列长度
            queue_length = self.redis_monitor.get_queue_length()
            current_processes = self.process_manager.get_process_count()

            logger.info(f"当前状态 - 队列任务数: {queue_length}, 运行进程数: {current_processes}")

            # 计算扩容和缩容阈值
            scale_up_threshold = current_processes * config.scale_up_threshold_multiplier
            scale_down_threshold = current_processes * config.scale_down_threshold_multiplier

            logger.debug(f"扩容阈值: {scale_up_threshold}, 缩容阈值: {scale_down_threshold}")

            # 判断是否需要扩容
            if queue_length > scale_up_threshold:
                self._scale_up_decision(queue_length, current_processes)
            # 判断是否需要缩容
            elif queue_length < scale_down_threshold:
                self._scale_down_decision(queue_length, current_processes)
            else:
                logger.debug("队列长度在正常范围内，无需扩缩容")

        except Exception as e:
            logger.error(f"检查和扩缩容过程中发生异常: {e}")

    def _scale_up_decision(self, queue_length: int, current_processes: int) -> None:
        """扩容决策"""
        if current_processes >= config.max_processes:
            logger.warning(f"已达到最大进程数限制 {config.max_processes}，无法扩容")
            return

        # 计算需要增加的进程数
        # 简单策略：每次增加1个进程
        scale_count = 1

        logger.info(f"队列任务数 {queue_length} 超过扩容阈值，准备增加 {scale_count} 个进程")

        added_count = self.process_manager.scale_up(scale_count)
        if added_count > 0:
            logger.info(f"扩容成功，增加了 {added_count} 个进程")
        else:
            logger.error("扩容失败")

    def _scale_down_decision(self, queue_length: int, current_processes: int) -> None:
        """缩容决策"""
        if current_processes <= config.min_processes:
            logger.debug(f"已达到最小进程数限制 {config.min_processes}，无法缩容")
            return

        # 计算需要减少的进程数
        # 简单策略：每次减少1个进程
        scale_count = 1

        logger.info(f"队列任务数 {queue_length} 低于缩容阈值，准备减少 {scale_count} 个进程")

        removed_count = self.process_manager.scale_down(scale_count)
        if removed_count > 0:
            logger.info(f"缩容成功，减少了 {removed_count} 个进程")
        else:
            logger.warning("缩容失败或无需缩容")

    def get_scaling_status(self) -> dict:
        """获取扩缩容状态信息"""
        try:
            queue_length = self.redis_monitor.get_queue_length()
            current_processes = self.process_manager.get_process_count()
            process_list = self.process_manager.get_process_list()

            scale_up_threshold = current_processes * config.scale_up_threshold_multiplier
            scale_down_threshold = current_processes * config.scale_down_threshold_multiplier

            return {
                "queue_length": queue_length,
                "current_processes": current_processes,
                "min_processes": config.min_processes,
                "max_processes": config.max_processes,
                "scale_up_threshold": scale_up_threshold,
                "scale_down_threshold": scale_down_threshold,
                "monitoring_active": self.monitoring_thread and self.monitoring_thread.is_alive(),
                "process_list": [
                    {
                        "pid": p.pid,
                        "start_time": p.start_time.isoformat(),
                        "status": p.status
                    }
                    for p in process_list
                ]
            }
        except Exception as e:
            logger.error(f"获取扩缩容状态时发生异常: {e}")
            return {"error": str(e)}

    def manual_scale_up(self, count: int = 1) -> int:
        """手动扩容"""
        logger.info(f"手动扩容请求，增加 {count} 个进程")
        return self.process_manager.scale_up(count)

    def manual_scale_down(self, count: int = 1) -> int:
        """手动缩容"""
        logger.info(f"手动缩容请求，减少 {count} 个进程")
        return self.process_manager.scale_down(count)