"""
应用入口模块

提供FastAPI应用实例和路由配置
"""
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from backend.api.responses import JSONResponse

from backend.api.routes import api_router
from backend.core import initialize_app, shutdown_app, settings
from backend.api.errors import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from backend.api.middleware import LoggingMiddleware, DatabaseMiddleware

print(settings.TEST_DB_HOST)

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 改为INFO级别，减少调试日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 关闭peewee的debug日志以提高性能
logging.getLogger('peewee').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在初始化应用...")
    db = initialize_app()
    logger.info("应用初始化完成")

    yield

    # 关闭时执行
    logger.info("正在关闭应用...")
    shutdown_app()
    logger.info("应用关闭完成")

# 创建FastAPI应用
app = FastAPI(
    title="Backend API",
    description="Backend API服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nietest.talesofai.cn",
        "https://nietestbackend.talesofai.cn",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8001",  # 添加8001端口支持
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8001"  # 添加8001端口支持
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 添加全局OPTIONS处理器
@app.options("/{full_path:path}")
async def options_handler(request: Request):
    """处理所有OPTIONS预检请求"""
    # 获取请求的origin
    origin = request.headers.get("origin")

    # 允许的域名列表
    allowed_origins = [
        "https://nietest.talesofai.cn",
        "https://nietestbackend.talesofai.cn",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8001"
    ]

    # 如果origin在允许列表中，则设置为该origin，否则设置为第一个允许的origin
    allow_origin = origin if origin in allowed_origins else allowed_origins[0]

    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        }
    )

# 添加数据库中间件（必须在日志中间件之前添加，确保数据库连接在记录日志之前初始化）
app.add_middleware(DatabaseMiddleware)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 添加API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径"""
    return JSONResponse(content={"message": "Backend API服务"})

@app.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse(content={"status": "healthy"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8001, reload=True)
