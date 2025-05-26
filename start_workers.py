#!/usr/bin/env python3
"""
Dramatiq Worker启动脚本

启动配置：
- 主进程：1个进程，50个线程 (处理 nietest_master 和 nietest_master_ops 队列)
- subtask：1个进程，5个线程 (处理 nietest_subtask 队列)
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_master_worker():
    """启动主任务worker"""
    print("启动主任务worker: 1个进程，50个线程")
    cmd = [
        sys.executable, "-m", "dramatiq",
        "backend.dramatiq_app.workers.master",
        "--processes", "1",
        "--threads", "50",
        "--queues", "nietest_master", "nietest_master_ops"
    ]
    return subprocess.Popen(cmd, cwd=project_root)

def start_subtask_worker():
    """启动子任务worker"""
    print("启动子任务worker: 1个进程，5个线程")
    cmd = [
        sys.executable, "-m", "dramatiq",
        "backend.dramatiq_app.workers.subtask",
        "--processes", "1",
        "--threads", "5",
        "--queues", "nietest_subtask"
    ]
    return subprocess.Popen(cmd, cwd=project_root)

def main():
    """主函数"""
    print("=== Dramatiq Worker 启动器 ===")
    print("配置:")
    print("- 主任务: 1进程 x 50线程 (nietest_master, nietest_master_ops)")
    print("- 子任务: 1进程 x 5线程 (nietest_subtask)")
    print("=" * 40)

    processes = []

    try:
        # 启动主任务worker
        master_process = start_master_worker()
        processes.append(("主任务Worker", master_process))
        time.sleep(2)  # 等待一下再启动下一个

        # 启动子任务worker
        subtask_process = start_subtask_worker()
        processes.append(("子任务Worker", subtask_process))

        print("\n所有worker已启动，按Ctrl+C停止...")

        # 等待进程
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    print(f"警告: {name} 进程已退出 (返回码: {process.returncode})")

    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭所有worker...")

        # 优雅地停止所有进程
        for name, process in processes:
            if process.poll() is None:  # 进程还在运行
                print(f"停止 {name}...")
                process.terminate()

        # 等待进程退出
        for name, process in processes:
            try:
                process.wait(timeout=10)
                print(f"{name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"强制杀死 {name}...")
                process.kill()
                process.wait()

        print("所有worker已停止")

if __name__ == "__main__":
    main()