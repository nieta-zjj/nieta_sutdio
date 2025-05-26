# Dramatiq 进程管理器

一个用于自动管理 Dramatiq worker 进程的独立服务，支持基于队列长度的自动扩缩容。

## 功能特性

- 🚀 **自动扩缩容**: 根据 Redis 队列长度自动调整 worker 进程数量
- 📊 **实时监控**: 每3分钟检测队列状态，智能决策扩缩容
- 🛡️ **优雅关闭**: 支持进程的优雅启动和关闭
- 📝 **详细日志**: 完整的操作日志记录
- 🎛️ **手动控制**: 支持手动扩缩容操作
- ⚙️ **灵活配置**: 通过环境变量或配置文件自定义所有参数

## 扩缩容策略

- **扩容条件**: 当队列任务数 > 当前进程数 × 5 时，增加1个进程
- **缩容条件**: 当队列任务数 < 当前进程数 × 2.5 时，减少1个进程
- **最小进程数**: 始终保持至少1个进程运行
- **最大进程数**: 默认最多10个进程（可配置）

## 安装

1. 创建虚拟环境（推荐）:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖:
```bash
cd process_manager
pip install -r requirements.txt
```

## 配置

### 环境变量配置

在项目根目录的 `.env` 文件中添加以下配置（如果不存在则创建）:

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Dramatiq 配置
DRAMATIQ_QUEUE_NAME=nietest_subtask
DRAMATIQ_COMMAND=python -m dramatiq --processes 1 --threads 5 --verbose backend.dramatiq_app.workers.subtask

# 进程管理配置
MIN_PROCESSES=1
MAX_PROCESSES=10
CHECK_INTERVAL=180  # 检查间隔（秒）
SCALE_UP_THRESHOLD_MULTIPLIER=5
SCALE_DOWN_THRESHOLD_MULTIPLIER=2.5

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=process_manager.log

# 进程管理器配置
GRACEFUL_SHUTDOWN_TIMEOUT=30
PROCESS_STARTUP_DELAY=5
```

### 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `REDIS_HOST` | localhost | Redis 服务器地址 |
| `REDIS_PORT` | 6379 | Redis 端口 |
| `REDIS_DB` | 0 | Redis 数据库编号 |
| `DRAMATIQ_QUEUE_NAME` | nietest_subtask | 监控的队列名称 |
| `DRAMATIQ_COMMAND` | python -m dramatiq... | 启动 worker 的完整命令 |
| `MIN_PROCESSES` | 1 | 最小进程数 |
| `MAX_PROCESSES` | 10 | 最大进程数 |
| `CHECK_INTERVAL` | 180 | 检查间隔（秒） |
| `SCALE_UP_THRESHOLD_MULTIPLIER` | 5 | 扩容阈值倍数 |
| `SCALE_DOWN_THRESHOLD_MULTIPLIER` | 2.5 | 缩容阈值倍数 |

## 使用方法

### 启动进程管理器

```bash
# 启动管理器（使用默认最小进程数）
python main.py start

# 启动管理器并指定初始进程数
python main.py start --processes 3

# 以守护进程模式运行（开发中）
python main.py start --daemon
```

### 查看状态

```bash
python main.py status
```

输出示例:
```
=== Dramatiq 进程管理器状态 ===
队列任务数: 12
当前进程数: 3
进程数范围: 1 - 10
扩容阈值: 15
缩容阈值: 7.5
监控状态: 运行中

运行中的进程:
  PID: 12345, 启动时间: 2024-01-01T10:00:00, 状态: running
  PID: 12346, 启动时间: 2024-01-01T10:05:00, 状态: running
  PID: 12347, 启动时间: 2024-01-01T10:10:00, 状态: running
===================================
```

### 手动扩缩容

```bash
# 手动增加1个进程
python main.py scale-up

# 手动增加3个进程
python main.py scale-up --processes 3

# 手动减少1个进程
python main.py scale-down

# 手动减少2个进程
python main.py scale-down --processes 2
```

### 停止管理器

在运行的管理器中按 `Ctrl+C` 即可优雅停止所有进程。

## 工作原理

### 监控循环

1. 每隔 `CHECK_INTERVAL` 秒（默认3分钟）检查一次队列状态
2. 获取 Redis 中指定队列的任务数量
3. 根据当前进程数计算扩缩容阈值
4. 根据队列长度决定是否需要扩缩容

### 扩容逻辑

```
if 队列任务数 > 当前进程数 × SCALE_UP_THRESHOLD_MULTIPLIER:
    增加1个进程
```

### 缩容逻辑

```
if 队列任务数 < 当前进程数 × SCALE_DOWN_THRESHOLD_MULTIPLIER:
    减少1个进程（但不少于最小进程数）
```

### 进程管理

- **启动**: 使用 `subprocess.Popen` 启动新的 Dramatiq worker 进程
- **监控**: 定期检查进程状态，自动清理死亡进程
- **停止**: 优先使用 `SIGTERM` 优雅关闭，超时后使用 `SIGKILL` 强制终止

## 日志

管理器会生成详细的日志，包括:

- 进程启动/停止事件
- 扩缩容决策和执行结果
- Redis 连接状态
- 错误和异常信息

日志同时输出到控制台和文件（默认 `process_manager.log`）。

## 故障排除

### 常见问题

1. **Redis 连接失败**
   - 检查 Redis 服务是否运行
   - 验证 Redis 连接配置
   - 检查网络连接

2. **进程启动失败**
   - 检查 `DRAMATIQ_COMMAND` 配置是否正确
   - 确保工作目录正确
   - 检查 Python 环境和依赖

3. **权限问题**
   - 确保有足够权限启动和停止进程
   - 检查日志文件写入权限

### 调试模式

设置环境变量 `LOG_LEVEL=DEBUG` 可以获得更详细的调试信息。

## 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main.py       │    │  AutoScaler     │    │ ProcessManager  │
│   (主程序入口)   │────│  (自动扩缩容)   │────│  (进程管理)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Config        │    │  RedisMonitor   │    │  Dramatiq       │
│   (配置管理)     │    │  (队列监控)     │    │  Worker         │
└─────────────────┘    └─────────────────┘    │  Processes      │
                                              └─────────────────┘
```

## 扩展功能

### 自定义扩缩容策略

可以通过修改 `AutoScaler` 类中的 `_scale_up_decision` 和 `_scale_down_decision` 方法来实现自定义的扩缩容策略。

### 监控集成

可以集成 Prometheus、Grafana 等监控系统，通过暴露指标接口来监控进程管理器的状态。

### Web 管理界面

可以开发 Web 界面来可视化管理进程状态和配置。

## 许可证

本项目采用 MIT 许可证。