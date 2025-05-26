"""
进程管理器核心模块
"""
import os
import signal
import subprocess
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import psutil
from loguru import logger
from config import config

@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    process: subprocess.Popen
    start_time: datetime
    command: str
    status: str = "running"

class ProcessManager:
    """Dramatiq 进程管理器"""

    def __init__(self):
        """初始化进程管理器"""
        self.processes: Dict[int, ProcessInfo] = {}
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("进程管理器初始化完成")

    def _signal_handler(self, signum: int, frame) -> None:
        """信号处理器"""
        logger.info(f"收到信号 {signum}，开始优雅关闭")
        self.shutdown_event.set()

    def start_process(self) -> Optional[int]:
        """
        启动一个新的 Dramatiq worker 进程

        Returns:
            新进程的 PID，如果启动失败返回 None
        """
        with self.lock:
            current_count = len(self.processes)
            if current_count >= config.max_processes:
                logger.warning(f"已达到最大进程数限制 {config.max_processes}")
                return None

            try:
                # 启动新进程
                logger.info(f"启动新的 Dramatiq worker 进程...")
                logger.debug(f"执行命令: {config.dramatiq_command}")

                process = subprocess.Popen(
                    config.dramatiq_command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid if os.name != 'nt' else None,
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 回到项目根目录
                )

                # 等待一小段时间确保进程启动
                time.sleep(1)

                # 检查进程是否成功启动
                if process.poll() is None:
                    process_info = ProcessInfo(
                        pid=process.pid,
                        process=process,
                        start_time=datetime.now(),
                        command=config.dramatiq_command
                    )
                    self.processes[process.pid] = process_info

                    logger.info(f"成功启动 Dramatiq worker 进程，PID: {process.pid}")
                    logger.info(f"当前运行进程数: {len(self.processes)}")
                    return process.pid
                else:
                    # 进程启动失败
                    stdout, stderr = process.communicate()
                    logger.error(f"进程启动失败")
                    logger.error(f"stdout: {stdout.decode() if stdout else 'None'}")
                    logger.error(f"stderr: {stderr.decode() if stderr else 'None'}")
                    return None

            except Exception as e:
                logger.error(f"启动进程时发生异常: {e}")
                return None

    def stop_process(self, pid: int, graceful: bool = True) -> bool:
        """
        停止指定的进程

        Args:
            pid: 进程 PID
            graceful: 是否优雅关闭

        Returns:
            是否成功停止
        """
        with self.lock:
            if pid not in self.processes:
                logger.warning(f"进程 {pid} 不在管理列表中")
                return False

            process_info = self.processes[pid]
            process = process_info.process

            try:
                logger.info(f"正在停止进程 {pid}...")

                if graceful:
                    # 优雅关闭：发送 SIGTERM
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()

                    # 等待进程结束
                    try:
                        process.wait(timeout=config.graceful_shutdown_timeout)
                        logger.info(f"进程 {pid} 已优雅关闭")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"进程 {pid} 优雅关闭超时，强制终止")
                        if os.name != 'nt':
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        else:
                            process.kill()
                        process.wait()
                else:
                    # 强制关闭：发送 SIGKILL
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait()
                    logger.info(f"进程 {pid} 已强制终止")

                # 从管理列表中移除
                del self.processes[pid]
                logger.info(f"当前运行进程数: {len(self.processes)}")
                return True

            except Exception as e:
                logger.error(f"停止进程 {pid} 时发生异常: {e}")
                # 尝试从列表中移除（可能进程已经死亡）
                if pid in self.processes:
                    del self.processes[pid]
                return False

    def get_process_count(self) -> int:
        """获取当前运行的进程数"""
        with self.lock:
            # 清理已死亡的进程
            self._cleanup_dead_processes()
            return len(self.processes)

    def get_process_list(self) -> List[ProcessInfo]:
        """获取所有进程信息"""
        with self.lock:
            self._cleanup_dead_processes()
            return list(self.processes.values())

    def _cleanup_dead_processes(self) -> None:
        """清理已死亡的进程"""
        dead_pids = []
        for pid, process_info in self.processes.items():
            if process_info.process.poll() is not None:
                dead_pids.append(pid)
                logger.warning(f"检测到进程 {pid} 已死亡，从管理列表中移除")

        for pid in dead_pids:
            del self.processes[pid]

    def scale_up(self, count: int = 1) -> int:
        """
        扩容：增加指定数量的进程

        Args:
            count: 要增加的进程数

        Returns:
            实际增加的进程数
        """
        logger.info(f"开始扩容，计划增加 {count} 个进程")

        added_count = 0
        for i in range(count):
            if self.get_process_count() >= config.max_processes:
                logger.warning("已达到最大进程数限制，停止扩容")
                break

            pid = self.start_process()
            if pid:
                added_count += 1
                # 进程启动间隔
                if i < count - 1:
                    time.sleep(config.process_startup_delay)
            else:
                logger.error(f"第 {i+1} 个进程启动失败")
                break

        logger.info(f"扩容完成，实际增加了 {added_count} 个进程")
        return added_count

    def scale_down(self, count: int = 1) -> int:
        """
        缩容：减少指定数量的进程

        Args:
            count: 要减少的进程数

        Returns:
            实际减少的进程数
        """
        logger.info(f"开始缩容，计划减少 {count} 个进程")

        with self.lock:
            current_count = len(self.processes)
            if current_count <= config.min_processes:
                logger.warning(f"已达到最小进程数限制 {config.min_processes}")
                return 0

            # 计算实际可以停止的进程数
            actual_count = min(count, current_count - config.min_processes)

            # 选择要停止的进程（选择最新启动的进程）
            process_list = sorted(
                self.processes.values(),
                key=lambda x: x.start_time,
                reverse=True
            )

            stopped_count = 0
            for i in range(actual_count):
                process_info = process_list[i]
                if self.stop_process(process_info.pid):
                    stopped_count += 1

        logger.info(f"缩容完成，实际减少了 {stopped_count} 个进程")
        return stopped_count

    def shutdown_all(self) -> None:
        """关闭所有进程"""
        logger.info("开始关闭所有进程...")

        with self.lock:
            process_list = list(self.processes.keys())

        for pid in process_list:
            self.stop_process(pid, graceful=True)

        logger.info("所有进程已关闭")

    def is_shutdown_requested(self) -> bool:
        """检查是否请求关闭"""
        return self.shutdown_event.is_set()