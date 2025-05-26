#!/usr/bin/env python3
"""
用户管理脚本

功能：
1. 创建新用户并指定角色
2. 更新用户角色
3. 查看用户信息和权限
4. 列出所有用户
5. 激活/停用用户

使用方法：
python scripts/user_management.py create --username <用户名> --password <密码> --roles <角色列表>
python scripts/user_management.py update --username <用户名> --roles <角色列表>
python scripts/user_management.py info --username <用户名>
python scripts/user_management.py list
python scripts/user_management.py activate --username <用户名>
python scripts/user_management.py deactivate --username <用户名>

环境配置：
请确保项目根目录有.env文件，包含以下数据库配置：
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=your_database
TEST_DB_USER=your_username
TEST_DB_PASSWORD=your_password
"""

import argparse
import sys
import os
from typing import List, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 直接导入需要的模块，避免循环导入
from playhouse.pool import PooledPostgresqlDatabase
from backend.db.database import test_db_proxy
from backend.models.db.user import User, Role, Permission, ROLE_ADDITIONAL_PERMISSIONS, ROLE_HIERARCHY
from backend.crud.user import user_crud
from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def check_env_file():
    """检查环境配置文件"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        print("⚠️ 警告：未找到.env文件")
        print(f"请在项目根目录创建.env文件，参考env.example")
        print("或者设置以下环境变量：")
        print("- TEST_DB_HOST")
        print("- TEST_DB_PORT")
        print("- TEST_DB_NAME")
        print("- TEST_DB_USER")
        print("- TEST_DB_PASSWORD")
        return False
    return True

def get_db_config():
    """获取数据库配置"""
    # 从环境变量读取配置
    from pathlib import Path
    from dotenv import load_dotenv

    # 加载环境变量
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    # 数据库配置
    db_config = {
        'database': os.getenv('TEST_DB_NAME', 'test_db'),
        'user': os.getenv('TEST_DB_USER', 'postgres'),
        'password': os.getenv('TEST_DB_PASSWORD', ''),
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': int(os.getenv('TEST_DB_PORT', '5432')),
        'max_connections': int(os.getenv('TEST_DB_MAX_CONNECTIONS', '20')),
        'stale_timeout': int(os.getenv('TEST_DB_STALE_TIMEOUT', '600'))
    }

    return db_config

def initialize_database():
    """初始化数据库连接"""
    db_config = get_db_config()

    # 检查必要的配置
    if not all([db_config['database'], db_config['user'], db_config['host']]):
        raise ValueError("数据库配置不完整，请检查环境变量或.env文件")

    test_db = PooledPostgresqlDatabase(
        db_config['database'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port'],
        max_connections=max(db_config['max_connections'], 20),
        stale_timeout=max(db_config['stale_timeout'], 600),
        timeout=30,
        autorollback=True,
        autoconnect=True
    )

    test_db_proxy.initialize(test_db)
    return test_db

def close_database():
    """关闭数据库连接"""
    try:
        if not test_db_proxy.is_closed():
            test_db_proxy.close()
    except Exception:
        pass


class UserManager:
    """用户管理器"""

    def __init__(self, skip_db_init=False):
        """初始化数据库连接"""
        if skip_db_init:
            return

        try:
            initialize_database()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            print("\n💡 解决方案：")
            print("1. 确保数据库服务正在运行")
            print("2. 检查.env文件中的数据库配置")
            print("3. 验证数据库连接参数")
            sys.exit(1)

    def __del__(self):
        """清理数据库连接"""
        try:
            close_database()
        except:
            pass

    def create_user(self, username: str, password: str, roles: List[str]) -> bool:
        """
        创建新用户

        Args:
            username: 用户名
            password: 密码
            roles: 角色列表

        Returns:
            是否创建成功
        """
        try:
            # 检查用户名是否已存在
            existing_user = user_crud.get_by_username(username=username)
            if existing_user:
                print(f"❌ 用户名 '{username}' 已存在")
                return False

            # 验证角色
            valid_roles = [role.value for role in Role]
            invalid_roles = [role for role in roles if role not in valid_roles]
            if invalid_roles:
                print(f"❌ 无效的角色: {invalid_roles}")
                print(f"可用角色: {valid_roles}")
                return False

            # 创建用户数据
            user_data = {
                "username": username,
                "hashed_password": get_password_hash(password),
                "roles": roles,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 创建用户
            user = user_crud.create(obj_in=user_data)
            print(f"✅ 用户 '{username}' 创建成功")
            print(f"   用户ID: {user.id}")
            print(f"   角色: {', '.join(roles)}")

            # 显示用户权限
            self._show_user_permissions(user)

            return True

        except Exception as e:
            print(f"❌ 创建用户失败: {e}")
            return False

    def update_user_roles(self, username: str, roles: List[str]) -> bool:
        """
        更新用户角色

        Args:
            username: 用户名
            roles: 新的角色列表

        Returns:
            是否更新成功
        """
        try:
            # 查找用户
            user = user_crud.get_by_username(username=username)
            if not user:
                print(f"❌ 用户 '{username}' 不存在")
                return False

            # 验证角色
            valid_roles = [role.value for role in Role]
            invalid_roles = [role for role in roles if role not in valid_roles]
            if invalid_roles:
                print(f"❌ 无效的角色: {invalid_roles}")
                print(f"可用角色: {valid_roles}")
                return False

            # 更新角色
            old_roles = user.roles.copy()
            updated_user = user_crud.update_roles(user_id=user.id, roles=roles)

            if updated_user:
                print(f"✅ 用户 '{username}' 角色更新成功")
                print(f"   旧角色: {', '.join(old_roles)}")
                print(f"   新角色: {', '.join(roles)}")

                # 显示更新后的权限
                self._show_user_permissions(updated_user)
                return True
            else:
                print(f"❌ 更新用户角色失败")
                return False

        except Exception as e:
            print(f"❌ 更新用户角色失败: {e}")
            return False

    def show_user_info(self, username: str) -> bool:
        """
        显示用户信息

        Args:
            username: 用户名

        Returns:
            是否成功
        """
        try:
            user = user_crud.get_by_username(username=username)
            if not user:
                print(f"❌ 用户 '{username}' 不存在")
                return False

            print(f"📋 用户信息: {username}")
            print(f"   用户ID: {user.id}")
            print(f"   角色: {', '.join(user.roles)}")
            print(f"   状态: {'激活' if user.is_active else '停用'}")
            print(f"   创建时间: {user.created_at}")
            print(f"   更新时间: {user.updated_at}")

            # 显示权限
            self._show_user_permissions(user)

            return True

        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
            return False

    def list_users(self) -> bool:
        """
        列出所有用户

        Returns:
            是否成功
        """
        try:
            users = User.select()

            if not users:
                print("📋 没有找到任何用户")
                return True

            print("📋 用户列表:")
            print(f"{'用户名':<20} {'角色':<30} {'状态':<10} {'创建时间'}")
            print("-" * 80)

            for user in users:
                status = "激活" if user.is_active else "停用"
                roles_str = ", ".join(user.roles)
                created_str = user.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"{user.username:<20} {roles_str:<30} {status:<10} {created_str}")

            return True

        except Exception as e:
            print(f"❌ 获取用户列表失败: {e}")
            return False

    def activate_user(self, username: str) -> bool:
        """
        激活用户

        Args:
            username: 用户名

        Returns:
            是否成功
        """
        return self._set_user_status(username, True)

    def deactivate_user(self, username: str) -> bool:
        """
        停用用户

        Args:
            username: 用户名

        Returns:
            是否成功
        """
        return self._set_user_status(username, False)

    def _set_user_status(self, username: str, is_active: bool) -> bool:
        """
        设置用户状态

        Args:
            username: 用户名
            is_active: 是否激活

        Returns:
            是否成功
        """
        try:
            user = user_crud.get_by_username(username=username)
            if not user:
                print(f"❌ 用户 '{username}' 不存在")
                return False

            if user.is_active == is_active:
                status_text = "激活" if is_active else "停用"
                print(f"ℹ️ 用户 '{username}' 已经是{status_text}状态")
                return True

            # 更新状态
            user.is_active = is_active
            user.updated_at = datetime.now()
            user.save()

            status_text = "激活" if is_active else "停用"
            print(f"✅ 用户 '{username}' 已{status_text}")

            return True

        except Exception as e:
            status_text = "激活" if is_active else "停用"
            print(f"❌ {status_text}用户失败: {e}")
            return False

    def _show_user_permissions(self, user: User):
        """
        显示用户权限

        Args:
            user: 用户对象
        """
        permissions = user.get_permissions()

        print(f"   权限数量: {len(permissions)}")

        if permissions:
            # 按类别分组显示权限
            permission_groups = {}
            for perm in permissions:
                category = perm.value.split(':')[0]
                if category not in permission_groups:
                    permission_groups[category] = []
                permission_groups[category].append(perm.value)

            for category, perms in permission_groups.items():
                print(f"   {category.upper()}:")
                for perm in sorted(perms):
                    print(f"     - {perm}")

    def show_available_roles(self):
        """显示可用角色和权限"""
        print("📋 可用角色和权限:")
        print()

        for role in Role:
            print(f"🔹 {role.value.upper()}")

            # 获取该角色的所有权限（包括继承的）
            all_permissions = set()
            roles_to_process = [role.value]
            processed_roles = set()

            while roles_to_process:
                current_role = roles_to_process.pop(0)
                if current_role in processed_roles:
                    continue
                processed_roles.add(current_role)

                # 添加当前角色的权限
                if current_role in ROLE_ADDITIONAL_PERMISSIONS:
                    all_permissions.update(ROLE_ADDITIONAL_PERMISSIONS[current_role])

                # 添加父角色
                parent_roles = ROLE_HIERARCHY.get(current_role, [])
                roles_to_process.extend(parent_roles)

            if all_permissions:
                # 按类别分组
                permission_groups = {}
                for perm in all_permissions:
                    category = perm.value.split(':')[0]
                    if category not in permission_groups:
                        permission_groups[category] = []
                    permission_groups[category].append(perm.value)

                for category, perms in permission_groups.items():
                    print(f"   {category.upper()}:")
                    for perm in sorted(perms):
                        print(f"     - {perm}")
            else:
                print("   无特殊权限")
            print()


def show_roles_without_db():
    """不连接数据库显示角色信息"""
    print("📋 可用角色和权限:")
    print()

    # 角色描述
    role_descriptions = {
        "guest": "访客 - 只读权限",
        "user": "普通用户 - 基础功能",
        "pro_user": "高级用户 - 高级功能",
        "manager": "管理员 - 管理权限",
        "admin": "超级管理员 - 所有权限"
    }

    for role_name, description in role_descriptions.items():
        print(f"🔹 {role_name.upper()}")
        print(f"   {description}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="用户管理脚本")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 创建用户命令
    create_parser = subparsers.add_parser("create", help="创建新用户")
    create_parser.add_argument("--username", required=True, help="用户名")
    create_parser.add_argument("--password", required=True, help="密码")
    create_parser.add_argument("--roles", nargs="+", default=["user"], help="角色列表")

    # 更新用户角色命令
    update_parser = subparsers.add_parser("update", help="更新用户角色")
    update_parser.add_argument("--username", required=True, help="用户名")
    update_parser.add_argument("--roles", nargs="+", required=True, help="新的角色列表")

    # 查看用户信息命令
    info_parser = subparsers.add_parser("info", help="查看用户信息")
    info_parser.add_argument("--username", required=True, help="用户名")

    # 列出用户命令
    subparsers.add_parser("list", help="列出所有用户")

    # 激活用户命令
    activate_parser = subparsers.add_parser("activate", help="激活用户")
    activate_parser.add_argument("--username", required=True, help="用户名")

    # 停用用户命令
    deactivate_parser = subparsers.add_parser("deactivate", help="停用用户")
    deactivate_parser.add_argument("--username", required=True, help="用户名")

    # 显示角色命令
    subparsers.add_parser("roles", help="显示可用角色和权限")

    # 配置检查命令
    subparsers.add_parser("check-config", help="检查配置")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 对于不需要数据库的命令，直接处理
    if args.command == "roles":
        try:
            # 尝试显示详细权限信息
            user_manager = UserManager(skip_db_init=True)
            user_manager.show_available_roles()
        except:
            # 如果失败，显示简化版本
            show_roles_without_db()
        sys.exit(0)

    if args.command == "check-config":
        print("🔍 检查配置...")
        env_ok = check_env_file()
        if env_ok:
            print("✅ 环境配置文件存在")

        try:
            initialize_database()
            print("✅ 数据库连接测试成功")
            close_database()
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
        sys.exit(0)

    # 其他命令需要数据库连接
    check_env_file()
    user_manager = UserManager()

    try:
        if args.command == "create":
            success = user_manager.create_user(args.username, args.password, args.roles)
            sys.exit(0 if success else 1)

        elif args.command == "update":
            success = user_manager.update_user_roles(args.username, args.roles)
            sys.exit(0 if success else 1)

        elif args.command == "info":
            success = user_manager.show_user_info(args.username)
            sys.exit(0 if success else 1)

        elif args.command == "list":
            success = user_manager.list_users()
            sys.exit(0 if success else 1)

        elif args.command == "activate":
            success = user_manager.activate_user(args.username)
            sys.exit(0 if success else 1)

        elif args.command == "deactivate":
            success = user_manager.deactivate_user(args.username)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()