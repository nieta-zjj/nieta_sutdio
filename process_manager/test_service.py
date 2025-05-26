#!/usr/bin/env python3
"""
进程管理器测试脚本
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from process_manager.config import config
from process_manager.redis_monitor import RedisMonitor
from process_manager.process_manager import ProcessManager
from process_manager.auto_scaler import AutoScaler

def test_config():
    """测试配置模块"""
    logger.info("测试配置模块...")

    print(f"Redis 配置: {config.redis_host}:{config.redis_port}")
    print(f"队列名称: {config.dramatiq_queue_name}")
    print(f"进程数范围: {config.min_processes} - {config.max_processes}")
    print(f"检查间隔: {config.check_interval} 秒")
    print(f"Dramatiq 命令: {config.dramatiq_command}")

    logger.info("配置模块测试通过")
    return True

def test_redis_monitor():
    """测试 Redis 监控器"""
    logger.info("测试 Redis 监控器...")

    try:
        monitor = RedisMonitor()

        # 测试连接
        if not monitor.is_connected():
            logger.error("Redis 连接失败")
            return False

        # 测试获取队列长度
        queue_length = monitor.get_queue_length()
        logger.info(f"当前队列长度: {queue_length}")

        # 测试获取所有队列信息
        queue_info = monitor.get_all_queue_info()
        logger.info(f"所有队列信息: {queue_info}")

        monitor.close()
        logger.info("Redis 监控器测试通过")
        return True

    except Exception as e:
        logger.error(f"Redis 监控器测试失败: {e}")
        return False

def test_process_manager():
    """测试进程管理器"""
    logger.info("测试进程管理器...")

    try:
        manager = ProcessManager()

        # 测试获取进程数
        count = manager.get_process_count()
        logger.info(f"当前进程数: {count}")

        # 测试获取进程列表
        processes = manager.get_process_list()
        logger.info(f"进程列表: {len(processes)} 个进程")

        logger.info("进程管理器测试通过")
        return True

    except Exception as e:
        logger.error(f"进程管理器测试失败: {e}")
        return False

def test_auto_scaler():
    """测试自动扩缩容器"""
    logger.info("测试自动扩缩容器...")

    try:
        redis_monitor = RedisMonitor()
        process_manager = ProcessManager()
        scaler = AutoScaler(process_manager, redis_monitor)

        # 测试获取状态
        status = scaler.get_scaling_status()
        logger.info(f"扩缩容状态: {status}")

        redis_monitor.close()
        logger.info("自动扩缩容器测试通过")
        return True

    except Exception as e:
        logger.error(f"自动扩缩容器测试失败: {e}")
        return False

def test_integration():
    """集成测试"""
    logger.info("开始集成测试...")

    try:
        # 初始化所有组件
        redis_monitor = RedisMonitor()
        process_manager = ProcessManager()
        auto_scaler = AutoScaler(process_manager, redis_monitor)

        # 获取初始状态
        initial_status = auto_scaler.get_scaling_status()
        logger.info(f"初始状态: {initial_status}")

        # 模拟启动一个进程（仅测试，不实际启动）
        logger.info("模拟进程管理操作...")

        # 清理
        redis_monitor.close()

        logger.info("集成测试通过")
        return True

    except Exception as e:
        logger.error(f"集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始进程管理器测试")

    tests = [
        ("配置模块", test_config),
        ("Redis 监控器", test_redis_monitor),
        ("进程管理器", test_process_manager),
        ("自动扩缩容器", test_auto_scaler),
        ("集成测试", test_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"运行测试: {test_name}")
        logger.info(f"{'='*50}")

        try:
            if test_func():
                logger.success(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} 测试失败")
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {e}")
            failed += 1

    logger.info(f"\n{'='*50}")
    logger.info(f"测试结果汇总")
    logger.info(f"{'='*50}")
    logger.info(f"通过: {passed}")
    logger.info(f"失败: {failed}")
    logger.info(f"总计: {passed + failed}")

    if failed == 0:
        logger.success("🎉 所有测试通过！")
        return 0
    else:
        logger.error(f"💥 有 {failed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())