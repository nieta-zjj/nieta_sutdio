# 用户管理脚本使用指南

本目录包含了完整的用户管理脚本，可以创建新用户并指定用户权限。

## 📁 文件说明

- `user_management.py` - 主要的用户管理脚本，提供完整的命令行接口
- `create_user_example.py` - 简化的用户创建示例脚本，提供交互式界面
- `USER_MANAGEMENT_README.md` - 本说明文档

## 🚀 快速开始

### 方法一：使用示例脚本（推荐新手）

```bash
# 运行交互式用户创建工具
python scripts/create_user_example.py
```

这个脚本提供了友好的交互界面，可以：
1. 创建预设的示例用户
2. 交互式创建自定义用户
3. 查看可用角色和权限

### 方法二：使用命令行脚本（推荐高级用户）

```bash
# 查看帮助
python scripts/user_management.py --help

# 查看可用角色和权限
python scripts/user_management.py roles
```

## 📋 用户角色系统

系统采用分层权限模型，角色之间有继承关系：

### 角色层级（从低到高）
1. **guest** - 访客
2. **user** - 普通用户
3. **pro_user** - 高级用户
4. **manager** - 管理员
5. **admin** - 超级管理员

### 权限继承
- 高级角色自动继承低级角色的所有权限
- 用户可以同时拥有多个角色
- 最终权限是所有角色权限的并集

### 权限类别
- **TEST** - 测试相关权限
- **DATA** - 数据管理相关权限
- **TRAIN** - 训练相关权限
- **GLOBAL** - 全局权限

## 🛠️ 详细使用方法

### 1. 创建用户

```bash
# 创建普通用户
python scripts/user_management.py create --username john --password john123 --roles user

# 创建管理员
python scripts/user_management.py create --username admin --password admin123 --roles admin

# 创建多角色用户
python scripts/user_management.py create --username poweruser --password power123 --roles user pro_user
```

### 2. 查看用户信息

```bash
# 查看特定用户信息和权限
python scripts/user_management.py info --username john

# 列出所有用户
python scripts/user_management.py list
```

### 3. 更新用户角色

```bash
# 更新用户角色
python scripts/user_management.py update --username john --roles pro_user manager
```

### 4. 用户状态管理

```bash
# 激活用户
python scripts/user_management.py activate --username john

# 停用用户
python scripts/user_management.py deactivate --username john
```

### 5. 查看角色和权限

```bash
# 查看所有可用角色和对应权限
python scripts/user_management.py roles
```

## 📊 示例用户

运行示例脚本会创建以下测试用户：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | admin | 超级管理员 |
| manager | manager123 | manager | 管理员 |
| pro_user | prouser123 | pro_user | 高级用户 |
| normal_user | user123 | user | 普通用户 |
| guest_user | guest123 | guest | 访客用户 |
| multi_role_user | multi123 | user, pro_user | 多角色用户 |

## 🔒 权限详情

### GUEST 权限
- `test:view_results` - 查看测试结果
- `data:view_collection` - 查看指定集合的图片
- `data:change_tags_viewable` - 更改可查看图片的标签

### USER 权限（包含GUEST所有权限）
- `test:create_low_priority` - 创建低优先级任务
- `test:delete_own` - 删除自己的任务
- `data:view_all` - 查看所有图片
- `data:upload` - 上传数据
- `data:change_tags_any` - 更改任何图片的标签
- `train:start` - 启动训练任务
- `train:stop` - 停止训练任务

### PRO_USER 权限（包含USER所有权限）
- `test:create_high_priority` - 创建高优先级任务
- `test:delete_any` - 删除任何任务
- `data:auto_annotate` - 执行自动标注任务
- `train:batch_start` - 批量启动训练任务

### MANAGER 权限（包含PRO_USER所有权限）
- `data:delete` - 删除数据

### ADMIN 权限（包含MANAGER所有权限）
- `global:create_user` - 创建用户
- `global:assign_permissions` - 分配权限

## ⚠️ 注意事项

1. **数据库连接**：脚本会自动连接到配置的数据库，确保数据库服务正在运行
2. **密码安全**：密码会自动使用bcrypt进行哈希加密存储
3. **角色验证**：创建用户时会验证角色的有效性
4. **用户名唯一性**：用户名必须唯一，不能重复
5. **权限继承**：理解角色继承关系，避免分配冗余权限

## 🐛 故障排除

### 常见错误

1. **数据库连接失败**
   ```
   ❌ 数据库连接失败: connection refused
   ```
   - 检查数据库服务是否启动
   - 验证数据库配置信息

2. **用户名已存在**
   ```
   ❌ 用户名 'john' 已存在
   ```
   - 使用不同的用户名
   - 或者更新现有用户的角色

3. **无效角色**
   ```
   ❌ 无效的角色: ['invalid_role']
   ```
   - 使用 `python scripts/user_management.py roles` 查看可用角色
   - 检查角色名称拼写

### 获取帮助

```bash
# 查看主脚本帮助
python scripts/user_management.py --help

# 查看特定命令帮助
python scripts/user_management.py create --help
```

## 🔧 开发说明

如需扩展用户管理功能：

1. **添加新角色**：在 `backend/models/db/user.py` 中的 `Role` 枚举添加新角色
2. **添加新权限**：在 `Permission` 枚举中添加新权限
3. **配置权限映射**：在 `ROLE_ADDITIONAL_PERMISSIONS` 中配置角色权限关系
4. **更新继承关系**：在 `ROLE_HIERARCHY` 中配置角色继承关系

## 📝 更新日志

- v1.0.0 - 初始版本，支持基本的用户CRUD操作
- 支持角色权限系统
- 提供命令行和交互式两种使用方式