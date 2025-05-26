#!/bin/bash

# Dramatiq Worker 一键启动脚本
# 启动配置：主任务1进程50线程，子任务1进程5线程

echo "=== 启动 Dramatiq Workers ==="
echo "配置："
echo "- 主任务: 1进程 x 50线程"
echo "- 子任务: 1进程 x 5线程"
echo "================================"

# 检查是否已有worker在运行
if pgrep -f "dramatiq" > /dev/null; then
    echo "警告: 检测到已有dramatiq进程在运行"
    echo "当前运行的进程："
    ps aux | grep dramatiq | grep -v grep
    echo ""
    read -p "是否要停止现有进程并重新启动? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止现有dramatiq进程..."
        pkill -f dramatiq
        sleep 3
    else
        echo "取消启动"
        exit 1
    fi
fi

# 启动主任务worker (后台运行)
echo "启动主任务worker..."
nohup python backend/dramatiq_app/start_dramatiq.py master --processes 1 --threads 50 > master_worker.log 2>&1 &
MASTER_PID=$!
echo "主任务worker已启动 (PID: $MASTER_PID)"

# 等待一下再启动下一个
sleep 3

# 启动子任务worker (后台运行)
echo "启动子任务worker..."
nohup python backend/dramatiq_app/start_dramatiq.py subtask --processes 1 --threads 5 > subtask_worker.log 2>&1 &
SUBTASK_PID=$!
echo "子任务worker已启动 (PID: $SUBTASK_PID)"

echo ""
echo "所有worker已启动完成！"
echo ""
echo "进程信息："
echo "- 主任务worker PID: $MASTER_PID"
echo "- 子任务worker PID: $SUBTASK_PID"
echo ""
echo "日志文件："
echo "- 主任务日志: master_worker.log"
echo "- 子任务日志: subtask_worker.log"
echo ""
echo "监控命令："
echo "- 查看进程状态: ps aux | grep dramatiq"
echo "- 查看主任务日志: tail -f master_worker.log"
echo "- 查看子任务日志: tail -f subtask_worker.log"
echo "- 停止所有worker: pkill -f dramatiq"
echo ""
echo "Workers正在后台运行..."