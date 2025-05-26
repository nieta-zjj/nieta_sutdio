#!/usr/bin/env python3
"""
简单的Dramatiq Worker启动脚本

使用现有的start_dramatiq.py来启动workers
- 主进程：1个进程，50个线程
- subtask：1个进程，5个线程
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """主函数"""
    print("=== Dramatiq Worker 启动器 (使用start_dramatiq.py) ===")
    print("配置:")
    print("- 主任务: 1进程 x 50线程")
    print("- 子任务: 1进程 x 5线程")
    print("=" * 50)

    project_root = Path(__file__).parent

    processes = []

    try:
        # 启动主任务worker
        print("启动主任务worker...")
        master_cmd = [
            sys.executable,
            "backend/dramatiq_app/start_dramatiq.py",
            "master",
            "--processes", "1",
            "--threads", "50"
        ]
        # python -m backend.dramatiq_app.start_dramatiq master --processes 1 --threads 50 --watch
        # python -m dramatiq backend.dramatiq_app.workers.master --processes 1 --threads 50 --watch
        master_process = subprocess.Popen(master_cmd, cwd=project_root)
        processes.append(("主任务Worker", master_process))
        time.sleep(3)  # 等待主任务worker启动

        # 启动子任务worker
        print("启动子任务worker...")
        subtask_cmd = [
            sys.executable,
            "backend/dramatiq_app/start_dramatiq.py",
            "subtask",
            "--processes", "1",
            "--threads", "5"
        ]
        subtask_process = subprocess.Popen(subtask_cmd, cwd=project_root)
        processes.append(("子任务Worker", subtask_process))

        print("\n所有worker已启动，按Ctrl+C停止...")

        # 监控进程状态
        while True:
            time.sleep(5)
            for name, process in processes:
                if process.poll() is not None:
                    print(f"警告: {name} 进程已退出 (返回码: {process.returncode})")

    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭所有worker...")

        # 优雅地停止所有进程
        for name, process in processes:
            if process.poll() is None:
                print(f"停止 {name}...")
                process.terminate()

        # 等待进程退出
        for name, process in processes:
            try:
                process.wait(timeout=15)
                print(f"{name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"强制杀死 {name}...")
                process.kill()
                process.wait()

        print("所有worker已停止")

if __name__ == "__main__":
    main()