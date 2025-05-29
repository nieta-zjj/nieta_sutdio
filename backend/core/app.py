"""
应用初始化模块

负责初始化应用的各个组件
"""
import logging
from backend.db.initialization import initialize_test_db, close_test_db

# 配置日志
logger = logging.getLogger(__name__)

def initialize_app():
    """
    初始化应用

    初始化数据库连接和其他组件
    """
    logger.debug("正在初始化应用...")

    # 初始化测试数据库连接
    db = initialize_test_db()
    logger.debug(f"已初始化测试数据库连接: {db}")

    # 确保所有模型都使用这个数据库连接
    # 注意：由于我们已经在 BaseModel 中设置了 database = test_db_proxy，
    # 所以这里不需要额外的初始化代码

    logger.debug("应用初始化完成")

    return db

def shutdown_app():
    """
    关闭应用

    关闭数据库连接和其他组件
    """
    logger.debug("正在关闭应用...")

    # 关闭测试数据库连接
    close_test_db()
    logger.debug("已关闭测试数据库连接")

    logger.debug("应用关闭完成")
