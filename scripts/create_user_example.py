#!/usr/bin/env python3
"""
快速创建用户示例脚本

这个脚本提供了一些预设的用户创建示例，方便快速测试和使用。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入修复后的用户管理模块
try:
    from scripts.user_management import UserManager
except ImportError as e:
    print(f"❌ 导入用户管理模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


def create_sample_users():
    """创建示例用户"""
    user_manager = UserManager()

    # 示例用户配置
    sample_users = [
        {
            "username": "admin",
            "password": "admin123",
            "roles": ["admin"],
            "description": "超级管理员 - 拥有所有权限"
        },
        {
            "username": "manager",
            "password": "manager123",
            "roles": ["manager"],
            "description": "管理员 - 拥有管理权限"
        },
        {
            "username": "pro_user",
            "password": "prouser123",
            "roles": ["pro_user"],
            "description": "高级用户 - 拥有高级功能权限"
        },
        {
            "username": "normal_user",
            "password": "user123",
            "roles": ["user"],
            "description": "普通用户 - 基础功能权限"
        },
        {
            "username": "guest_user",
            "password": "guest123",
            "roles": ["guest"],
            "description": "访客用户 - 只读权限"
        },
        {
            "username": "multi_role_user",
            "password": "multi123",
            "roles": ["user", "pro_user"],
            "description": "多角色用户 - 同时拥有多个角色"
        }
    ]

    print("🚀 开始创建示例用户...")
    print("=" * 60)

    for user_config in sample_users:
        print(f"\n📝 创建用户: {user_config['username']}")
        print(f"   描述: {user_config['description']}")
        print(f"   角色: {', '.join(user_config['roles'])}")

        success = user_manager.create_user(
            username=user_config["username"],
            password=user_config["password"],
            roles=user_config["roles"]
        )

        if success:
            print("   ✅ 创建成功")
        else:
            print("   ❌ 创建失败")

        print("-" * 40)

    print("\n🎉 示例用户创建完成！")
    print("\n📋 用户登录信息:")
    print("=" * 60)
    for user_config in sample_users:
        print(f"用户名: {user_config['username']:<15} 密码: {user_config['password']:<12} 角色: {', '.join(user_config['roles'])}")


def interactive_create_user():
    """交互式创建用户"""
    user_manager = UserManager()

    print("🔧 交互式用户创建")
    print("=" * 40)

    # 显示可用角色
    print("\n📋 可用角色:")
    roles_info = {
        "guest": "访客 - 只读权限",
        "user": "普通用户 - 基础功能",
        "pro_user": "高级用户 - 高级功能",
        "manager": "管理员 - 管理权限",
        "admin": "超级管理员 - 所有权限"
    }

    for role, desc in roles_info.items():
        print(f"  {role}: {desc}")

    print("\n" + "=" * 40)

    try:
        # 获取用户输入
        username = input("请输入用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return

        password = input("请输入密码: ").strip()
        if not password:
            print("❌ 密码不能为空")
            return

        roles_input = input("请输入角色 (多个角色用空格分隔，默认为 user): ").strip()
        if not roles_input:
            roles = ["user"]
        else:
            roles = roles_input.split()

        # 创建用户
        print(f"\n🚀 正在创建用户 '{username}'...")
        success = user_manager.create_user(username, password, roles)

        if success:
            print(f"\n🎉 用户 '{username}' 创建成功！")
        else:
            print(f"\n❌ 用户 '{username}' 创建失败")

    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    print("👋 欢迎使用用户创建工具")
    print("=" * 50)
    print("1. 创建示例用户 (预设的测试用户)")
    print("2. 交互式创建用户")
    print("3. 查看可用角色和权限")
    print("4. 退出")
    print("=" * 50)

    try:
        choice = input("请选择操作 (1-4): ").strip()

        if choice == "1":
            create_sample_users()
        elif choice == "2":
            interactive_create_user()
        elif choice == "3":
            user_manager = UserManager()
            user_manager.show_available_roles()
        elif choice == "4":
            print("👋 再见！")
        else:
            print("❌ 无效的选择")

    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()