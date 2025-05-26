#!/bin/bash

# Dramatiq 进程管理器启动脚本

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查 Python 环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python 未找到，请安装 Python 3.7+"
        exit 1
    fi

    log_info "使用 Python: $PYTHON_CMD"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi

    # 检查是否在虚拟环境中
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warn "建议在虚拟环境中运行"
    else
        log_info "检测到虚拟环境: $VIRTUAL_ENV"
    fi

    # 尝试导入关键模块
    $PYTHON_CMD -c "import redis, psutil, loguru, pydantic" 2>/dev/null || {
        log_error "缺少必要的依赖，请运行: pip install -r requirements.txt"
        exit 1
    }

    log_info "依赖检查通过"
}

# 检查环境配置
check_environment() {
    log_info "检查环境配置..."

    # 检查 .env 文件
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warn ".env 文件不存在，将使用默认配置"

        # 可选：创建示例 .env 文件
        if [ -f "$PROJECT_ROOT/env.example" ]; then
            log_info "发现 env.example，可以复制为 .env 文件"
            echo "cp $PROJECT_ROOT/env.example $PROJECT_ROOT/.env"
        fi
    else
        log_info "找到 .env 配置文件"
    fi
}

# 检查 Redis 连接
check_redis() {
    log_info "检查 Redis 连接..."

    # 从环境变量或默认值获取 Redis 配置
    REDIS_HOST=${REDIS_HOST:-localhost}
    REDIS_PORT=${REDIS_PORT:-6379}

    # 使用 Python 检查 Redis 连接
    $PYTHON_CMD -c "
import redis
import sys
try:
    r = redis.Redis(host='$REDIS_HOST', port=$REDIS_PORT, socket_connect_timeout=5)
    r.ping()
    print('Redis 连接成功')
except Exception as e:
    print(f'Redis 连接失败: {e}')
    sys.exit(1)
" || {
        log_error "Redis 连接失败，请检查 Redis 服务是否运行"
        log_info "Redis 配置: $REDIS_HOST:$REDIS_PORT"
        exit 1
    }
}

# 显示帮助信息
show_help() {
    echo "Dramatiq 进程管理器启动脚本"
    echo ""
    echo "用法: $0 [选项] [命令]"
    echo ""
    echo "命令:"
    echo "  start [--processes N]  启动进程管理器"
    echo "  status                 查看状态"
    echo "  scale-up [--processes N]   手动扩容"
    echo "  scale-down [--processes N] 手动缩容"
    echo "  stop                   停止所有进程"
    echo ""
    echo "选项:"
    echo "  --processes N          指定进程数量"
    echo "  --daemon              以守护进程模式运行"
    echo "  --check-only          只检查环境，不启动服务"
    echo "  --skip-checks         跳过环境检查"
    echo "  --help                显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start                    # 启动管理器"
    echo "  $0 start --processes 3      # 启动3个初始进程"
    echo "  $0 status                   # 查看状态"
    echo "  $0 scale-up --processes 2   # 增加2个进程"
    echo ""
}

# 主函数
main() {
    local command=""
    local processes=""
    local daemon_mode=false
    local check_only=false
    local skip_checks=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|status|scale-up|scale-down|stop)
                command="$1"
                shift
                ;;
            --processes)
                processes="$2"
                shift 2
                ;;
            --daemon)
                daemon_mode=true
                shift
                ;;
            --check-only)
                check_only=true
                shift
                ;;
            --skip-checks)
                skip_checks=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 如果没有指定命令，显示帮助
    if [ -z "$command" ] && [ "$check_only" = false ]; then
        show_help
        exit 1
    fi

    log_info "Dramatiq 进程管理器启动脚本"
    log_info "工作目录: $SCRIPT_DIR"
    log_info "项目根目录: $PROJECT_ROOT"

    # 环境检查
    if [ "$skip_checks" = false ]; then
        check_python
        check_dependencies
        check_environment
        check_redis
        log_info "环境检查完成"
    fi

    # 如果只是检查环境，则退出
    if [ "$check_only" = true ]; then
        log_info "环境检查完成，退出"
        exit 0
    fi

    # 切换到脚本目录
    cd "$SCRIPT_DIR"

    # 构建命令参数
    local cmd_args=()
    cmd_args+=("$command")

    if [ -n "$processes" ]; then
        cmd_args+=("--processes" "$processes")
    fi

    if [ "$daemon_mode" = true ]; then
        cmd_args+=("--daemon")
    fi

    # 执行命令
    log_info "执行命令: $PYTHON_CMD main.py ${cmd_args[*]}"

    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

    # 运行主程序
    exec "$PYTHON_CMD" main.py "${cmd_args[@]}"
}

# 信号处理
trap 'log_info "收到中断信号，正在退出..."; exit 130' INT TERM

# 运行主函数
main "$@"