@echo off
REM Dramatiq 进程管理器启动脚本 (Windows)

setlocal enabledelayedexpansion

REM 获取脚本目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM 颜色定义 (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %GREEN%[INFO]%NC% %~1
goto :eof

:log_warn
echo %YELLOW%[WARN]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:log_debug
echo %BLUE%[DEBUG]%NC% %~1
goto :eof

REM 检查 Python 环境
:check_python
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    call :log_info "使用 Python: python3"
    goto :eof
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    call :log_info "使用 Python: python"
    goto :eof
)

call :log_error "Python 未找到，请安装 Python 3.7+"
exit /b 1

REM 检查依赖
:check_dependencies
call :log_info "检查依赖..."

if not exist "%SCRIPT_DIR%requirements.txt" (
    call :log_error "requirements.txt 文件不存在"
    exit /b 1
)

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    call :log_info "检测到虚拟环境: %VIRTUAL_ENV%"
) else (
    call :log_warn "建议在虚拟环境中运行"
)

REM 尝试导入关键模块
%PYTHON_CMD% -c "import redis, psutil, loguru, pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "缺少必要的依赖，请运行: pip install -r requirements.txt"
    exit /b 1
)

call :log_info "依赖检查通过"
goto :eof

REM 检查环境配置
:check_environment
call :log_info "检查环境配置..."

if not exist "%PROJECT_ROOT%\.env" (
    call :log_warn ".env 文件不存在，将使用默认配置"

    if exist "%PROJECT_ROOT%\env.example" (
        call :log_info "发现 env.example，可以复制为 .env 文件"
        echo copy "%PROJECT_ROOT%\env.example" "%PROJECT_ROOT%\.env"
    )
) else (
    call :log_info "找到 .env 配置文件"
)
goto :eof

REM 检查 Redis 连接
:check_redis
call :log_info "检查 Redis 连接..."

REM 从环境变量或默认值获取 Redis 配置
if not defined REDIS_HOST set "REDIS_HOST=localhost"
if not defined REDIS_PORT set "REDIS_PORT=6379"

REM 使用 Python 检查 Redis 连接
%PYTHON_CMD% -c "import redis; import sys; r = redis.Redis(host='%REDIS_HOST%', port=%REDIS_PORT%, socket_connect_timeout=5); r.ping(); print('Redis 连接成功')" >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Redis 连接失败，请检查 Redis 服务是否运行"
    call :log_info "Redis 配置: %REDIS_HOST%:%REDIS_PORT%"
    exit /b 1
)
goto :eof

REM 显示帮助信息
:show_help
echo Dramatiq 进程管理器启动脚本
echo.
echo 用法: %~nx0 [选项] [命令]
echo.
echo 命令:
echo   start [--processes N]      启动进程管理器
echo   status                     查看状态
echo   scale-up [--processes N]   手动扩容
echo   scale-down [--processes N] 手动缩容
echo   stop                       停止所有进程
echo.
echo 选项:
echo   --processes N              指定进程数量
echo   --daemon                   以守护进程模式运行
echo   --check-only               只检查环境，不启动服务
echo   --skip-checks              跳过环境检查
echo   --help                     显示此帮助信息
echo.
echo 示例:
echo   %~nx0 start                    # 启动管理器
echo   %~nx0 start --processes 3      # 启动3个初始进程
echo   %~nx0 status                   # 查看状态
echo   %~nx0 scale-up --processes 2   # 增加2个进程
echo.
goto :eof

REM 主函数
:main
set "command="
set "processes="
set "daemon_mode=false"
set "check_only=false"
set "skip_checks=false"

REM 解析参数
:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="start" (
    set "command=start"
    shift
    goto :parse_args
)
if "%~1"=="status" (
    set "command=status"
    shift
    goto :parse_args
)
if "%~1"=="scale-up" (
    set "command=scale-up"
    shift
    goto :parse_args
)
if "%~1"=="scale-down" (
    set "command=scale-down"
    shift
    goto :parse_args
)
if "%~1"=="stop" (
    set "command=stop"
    shift
    goto :parse_args
)
if "%~1"=="--processes" (
    set "processes=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--daemon" (
    set "daemon_mode=true"
    shift
    goto :parse_args
)
if "%~1"=="--check-only" (
    set "check_only=true"
    shift
    goto :parse_args
)
if "%~1"=="--skip-checks" (
    set "skip_checks=true"
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    call :show_help
    exit /b 0
)
if "%~1"=="-h" (
    call :show_help
    exit /b 0
)
call :log_error "未知参数: %~1"
call :show_help
exit /b 1

:args_done
REM 如果没有指定命令，显示帮助
if "%command%"=="" if "%check_only%"=="false" (
    call :show_help
    exit /b 1
)

call :log_info "Dramatiq 进程管理器启动脚本"
call :log_info "工作目录: %SCRIPT_DIR%"
call :log_info "项目根目录: %PROJECT_ROOT%"

REM 环境检查
if "%skip_checks%"=="false" (
    call :check_python
    if %errorlevel% neq 0 exit /b %errorlevel%

    call :check_dependencies
    if %errorlevel% neq 0 exit /b %errorlevel%

    call :check_environment
    if %errorlevel% neq 0 exit /b %errorlevel%

    call :check_redis
    if %errorlevel% neq 0 exit /b %errorlevel%

    call :log_info "环境检查完成"
)

REM 如果只是检查环境，则退出
if "%check_only%"=="true" (
    call :log_info "环境检查完成，退出"
    exit /b 0
)

REM 切换到脚本目录
cd /d "%SCRIPT_DIR%"

REM 构建命令参数
set "cmd_args=%command%"

if not "%processes%"=="" (
    set "cmd_args=%cmd_args% --processes %processes%"
)

if "%daemon_mode%"=="true" (
    set "cmd_args=%cmd_args% --daemon"
)

REM 执行命令
call :log_info "执行命令: %PYTHON_CMD% main.py %cmd_args%"

REM 设置环境变量
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM 运行主程序
%PYTHON_CMD% main.py %cmd_args%
exit /b %errorlevel%

REM 调用主函数
call :main %*