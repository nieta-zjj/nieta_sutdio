# Dramatiq Worker 启动命令

## 方式1: 使用现有的 start_dramatiq.py

### 启动主任务worker (1进程50线程)
```bash
python backend/dramatiq_app/start_dramatiq.py master --processes 1 --threads 50
```

### 启动子任务worker (1进程5线程)
```bash
python backend/dramatiq_app/start_dramatiq.py subtask --processes 1 --threads 5
```

## 方式2: 直接使用 dramatiq 命令

### 启动主任务worker (1进程50线程)
```bash
python -m dramatiq backend.dramatiq_app.workers.master --processes 1 --threads 50 --queues nietest_master nietest_master_ops
```

### 启动子任务worker (1进程5线程)
```bash
python -m dramatiq backend.dramatiq_app.workers.subtask --processes 1 --threads 5 --queues nietest_subtask
```

## 方式3: 后台运行 (推荐生产环境)

### 启动主任务worker (后台运行)
```bash
nohup python backend/dramatiq_app/start_dramatiq.py master --processes 1 --threads 50 > master_worker.log 2>&1 &
```

### 启动子任务worker (后台运行)
```bash
nohup python backend/dramatiq_app/start_dramatiq.py subtask --processes 1 --threads 5 > subtask_worker.log 2>&1 &
```

## 方式4: 使用 screen 或 tmux (推荐开发环境)

### 使用 screen
```bash
# 启动主任务worker
screen -S master_worker -d -m python backend/dramatiq_app/start_dramatiq.py master --processes 1 --threads 50

# 启动子任务worker
screen -S subtask_worker -d -m python backend/dramatiq_app/start_dramatiq.py subtask --processes 1 --threads 5

# 查看运行的screen会话
screen -ls

# 连接到会话查看日志
screen -r master_worker
screen -r subtask_worker
```

### 使用 tmux
```bash
# 启动主任务worker
tmux new-session -d -s master_worker 'python backend/dramatiq_app/start_dramatiq.py master --processes 1 --threads 50'

# 启动子任务worker
tmux new-session -d -s subtask_worker 'python backend/dramatiq_app/start_dramatiq.py subtask --processes 1 --threads 5'

# 查看运行的tmux会话
tmux list-sessions

# 连接到会话查看日志
tmux attach-session -t master_worker
tmux attach-session -t subtask_worker
```

## 停止worker

### 查找进程
```bash
ps aux | grep dramatiq
```

### 停止特定进程
```bash
kill -TERM <进程ID>
```

### 停止所有dramatiq进程
```bash
pkill -f dramatiq
```

## 监控worker状态

### 查看日志 (如果使用nohup)
```bash
tail -f master_worker.log
tail -f subtask_worker.log
```

### 查看进程状态
```bash
ps aux | grep "start_dramatiq\|dramatiq"
```