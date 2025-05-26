#!/usr/bin/env python3
"""
Dramatiq 进程管理器主程序
"""
import sys
import time
import signal
import argparse
from pathlib import Path
from loguru import logger
from config import config
from redis_monitor import RedisMonitor
from process_manager import ProcessManager
from auto_scaler import AutoScaler

class DramatiqProcessManager:
    """Dramatiq 进程管理器主类"""

    def __init__(self):
        """初始化管理器"""
        self.redis_monitor = None
        self.process_manager = None
        self.auto_scaler = None
        self.running = False

        # 配置日志
        self._setup_logging()

        logger.info("Dramatiq 进程管理器启动")
        logger.info(f"配置信息:")
        logger.info(f"  - Redis: {config.redis_host}:{config.redis_port}")
        logger.info(f"  - 队列名称: {config.dramatiq_queue_name}")
        logger.info(f"  - 最小进程数: {config.min_processes}")
        logger.info(f"  - 最大进程数: {config.max_processes}")
        logger.info(f"  - 检查间隔: {config.check_interval} 秒")

    def _setup_logging(self):
        """配置日志"""
        # 移除默认的日志处理器
        logger.remove()

        # 添加控制台日志
        logger.add(
            sys.stdout,
            level=config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )

        # 添加文件日志
        logger.add(
            config.log_file,
            level=config.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )

    def initialize(self):
        """初始化所有组件"""
        try:
            logger.info("初始化组件...")

            # 初始化 Redis 监控器
            self.redis_monitor = RedisMonitor()

            # 初始化进程管理器
            self.process_manager = ProcessManager()

            # 初始化自动扩缩容器
            self.auto_scaler = AutoScaler(self.process_manager, self.redis_monitor)

            logger.info("所有组件初始化完成")
            return True

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False

    def start(self, initial_processes: int = None):
        """启动管理器"""
        if not self.initialize():
            logger.error("初始化失败，无法启动")
            return False

        try:
            self.running = True

            # 启动初始进程
            if initial_processes is None:
                initial_processes = config.min_processes

            logger.info(f"启动 {initial_processes} 个初始进程...")
            added_count = self.process_manager.scale_up(initial_processes)
            if added_count < initial_processes:
                logger.warning(f"只成功启动了 {added_count} 个进程，预期 {initial_processes} 个")

            # 启动自动扩缩容监控
            self.auto_scaler.start_monitoring()

            logger.info("进程管理器启动完成")
            return True

        except Exception as e:
            logger.error(f"启动失败: {e}")
            self.running = False
            return False

    def stop(self):
        """停止管理器"""
        if not self.running:
            return

        logger.info("正在停止进程管理器...")
        self.running = False

        try:
            # 停止自动扩缩容监控
            if self.auto_scaler:
                self.auto_scaler.stop_monitoring()

            # 关闭所有进程
            if self.process_manager:
                self.process_manager.shutdown_all()

            # 关闭 Redis 连接
            if self.redis_monitor:
                self.redis_monitor.close()

            logger.info("进程管理器已停止")

        except Exception as e:
            logger.error(f"停止过程中发生异常: {e}")

    def run_forever(self):
        """运行直到收到停止信号"""
        if not self.running:
            logger.error("管理器未启动")
            return

        try:
            logger.info("进程管理器正在运行，按 Ctrl+C 停止")

            while self.running and not self.process_manager.is_shutdown_requested():
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        finally:
            self.stop()

    def status(self):
        """显示当前状态"""
        if not self.auto_scaler:
            logger.error("管理器未初始化")
            return

        try:
            status_info = self.auto_scaler.get_scaling_status()

            print("\n=== Dramatiq 进程管理器状态 ===")
            print(f"队列任务数: {status_info.get('queue_length', 'N/A')}")
            print(f"当前进程数: {status_info.get('current_processes', 'N/A')}")
            print(f"进程数范围: {status_info.get('min_processes', 'N/A')} - {status_info.get('max_processes', 'N/A')}")
            print(f"扩容阈值: {status_info.get('scale_up_threshold', 'N/A')}")
            print(f"缩容阈值: {status_info.get('scale_down_threshold', 'N/A')}")
            print(f"监控状态: {'运行中' if status_info.get('monitoring_active') else '已停止'}")

            process_list = status_info.get('process_list', [])
            if process_list:
                print(f"\n运行中的进程:")
                for proc in process_list:
                    print(f"  PID: {proc['pid']}, 启动时间: {proc['start_time']}, 状态: {proc['status']}")
            else:
                print("\n当前没有运行中的进程")

            print("=" * 35)

        except Exception as e:
            logger.error(f"获取状态失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Dramatiq 进程管理器")
    parser.add_argument(
        "command",
        choices=["start", "status", "scale-up", "scale-down"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="初始进程数或扩缩容进程数"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="以守护进程模式运行"
    )

    args = parser.parse_args()

    manager = DramatiqProcessManager()

    if args.command == "start":
        if manager.start(args.processes):
            if args.daemon:
                # TODO: 实现守护进程模式
                logger.warning("守护进程模式尚未实现，使用前台模式")
            manager.run_forever()
        else:
            sys.exit(1)

    elif args.command == "status":
        if manager.initialize():
            manager.status()
        else:
            sys.exit(1)

    elif args.command == "scale-up":
        if manager.initialize():
            count = args.processes or 1
            added = manager.auto_scaler.manual_scale_up(count)
            print(f"成功增加 {added} 个进程")
        else:
            sys.exit(1)

    elif args.command == "scale-down":
        if manager.initialize():
            count = args.processes or 1
            removed = manager.auto_scaler.manual_scale_down(count)
            print(f"成功减少 {removed} 个进程")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()