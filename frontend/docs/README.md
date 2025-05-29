# 前端代码质量检查体系

本目录包含了前端项目代码质量检查体系的完整文档。

## 📋 概述

本项目实现了一套**仅检查不自动修复**的代码质量检查体系，确保所有代码修复都由开发者手动完成，以提高代码质量和开发者技能。

### 🎯 设计原则

- **仅检查不修复**: 所有工具只进行检查，不会自动修复问题
- **全面覆盖**: 涵盖代码质量、类型安全、格式规范、安全性等多个方面
- **详细报告**: 提供详细的问题报告和修复建议
- **渐进式改进**: 支持分步骤修复，适合大型项目

### 🛠️ 工具链

| 工具           | 版本   | 用途         | 配置文件            |
| -------------- | ------ | ------------ | ------------------- |
| **ESLint**     | 9.25.1 | 代码质量检查 | `eslint.config.mjs` |
| **TypeScript** | 5.6.3  | 类型检查     | `tsconfig.json`     |
| **Prettier**   | 3.5.3  | 代码格式检查 | `.prettierrc`       |
| **npm-check**  | 6.0.1  | 依赖分析     | -                   |

### 🔍 检查范围

- ✅ **代码质量**: 复杂度、重复代码、最佳实践
- ✅ **安全性**: 潜在安全漏洞检测
- ✅ **类型安全**: TypeScript类型检查
- ✅ **代码格式**: 统一的代码风格
- ✅ **依赖管理**: 未使用和过时的依赖
- ✅ **可访问性**: React组件可访问性

## 📚 文档目录

### 核心文档

1. **[代码质量指南](./code-quality-guidelines.md)** 📖

   - 完整的代码质量要求和规范
   - 手动修复指南和最佳实践
   - 提交前检查清单

2. **[使用指南](./usage-guide.md)** 🚀
   - 快速开始和基础命令
   - 详细的使用说明和故障排除
   - 工作流程建议

### 配置文档

3. **[ESLint配置说明](./eslint-configuration.md)** ⚙️

   - ESLint规则详解
   - 安全和复杂度检查规则
   - 自定义配置指南

4. **[TypeScript配置说明](./typescript-configuration.md)** 📝

   - TypeScript配置详解
   - 类型定义最佳实践
   - 常见问题解决方案

5. **[Prettier配置说明](./prettier-configuration.md)** 🎨
   - 代码格式化规则
   - IDE集成配置
   - 自定义格式化选项

## 🚀 快速开始

### 1. 安装依赖

```bash
pnpm install
```

### 2. 运行检查

```bash
# 运行所有质量检查
pnpm check

# 运行特定检查
pnpm check:eslint    # ESLint检查
pnpm check:types     # TypeScript检查
pnpm check:format    # 格式检查
pnpm check:deps      # 依赖检查
```

### 3. 生成报告

```bash
# 生成所有报告
pnpm report

# 查看HTML报告
open reports/eslint-report.html
```

### 4. 修复问题

```bash
# 仅修复格式问题（唯一的自动修复）
pnpm format:write

# 其他问题需要手动修复
# 参考各配置文档中的修复指南
```

## 📊 可用命令

### 检查命令

| 命令                | 描述             | 输出   |
| ------------------- | ---------------- | ------ |
| `pnpm check`        | 运行所有质量检查 | 控制台 |
| `pnpm check:eslint` | 仅ESLint检查     | 控制台 |
| `pnpm check:types`  | 仅TypeScript检查 | 控制台 |
| `pnpm check:format` | 仅格式检查       | 控制台 |
| `pnpm check:deps`   | 仅依赖检查       | 控制台 |

### 报告命令

| 命令                 | 描述           | 输出位置                      |
| -------------------- | -------------- | ----------------------------- |
| `pnpm report`        | 生成所有报告   | `reports/`                    |
| `pnpm report:eslint` | 生成ESLint报告 | `reports/eslint-report.*`     |
| `pnpm report:format` | 生成格式报告   | `reports/prettier-report.txt` |
| `pnpm report:deps`   | 生成依赖报告   | `reports/deps-report.*`       |

### 格式化命令

| 命令                | 描述         | 说明               |
| ------------------- | ------------ | ------------------ |
| `pnpm format:check` | 检查格式问题 | 仅检查不修复       |
| `pnpm format:write` | 修复格式问题 | 唯一的自动修复命令 |

### 其他命令

| 命令               | 描述                 |
| ------------------ | -------------------- |
| `pnpm lint:check`  | ESLint检查（不修复） |
| `pnpm lint:strict` | 严格模式ESLint检查   |
| `pnpm type-check`  | TypeScript类型检查   |

## 📁 项目结构

```
frontend/
├── frontenddocs/                 # 📚 文档目录
│   ├── README.md                # 📖 本文档
│   ├── code-quality-guidelines.md  # 📋 质量指南
│   ├── usage-guide.md           # 🚀 使用指南
│   ├── eslint-configuration.md  # ⚙️ ESLint配置
│   ├── typescript-configuration.md # 📝 TypeScript配置
│   └── prettier-configuration.md   # 🎨 Prettier配置
├── scripts/                     # 🔧 脚本目录
│   ├── code-quality.js         # 质量检查脚本
│   └── generate-report.js      # 报告生成脚本
├── reports/                     # 📊 报告输出目录
│   ├── eslint-report.html      # ESLint HTML报告
│   ├── eslint-report.json      # ESLint JSON报告
│   ├── prettier-report.txt     # Prettier报告
│   └── deps-report.*           # 依赖分析报告
├── .prettierrc                 # Prettier配置
├── .prettierignore             # Prettier忽略文件
├── eslint.config.mjs           # ESLint配置
├── tsconfig.json               # TypeScript配置
└── package.json                # 项目配置
```

## 🎯 工作流程

### 开发时

1. 配置IDE实时显示错误和警告
2. 保存时自动格式化（Prettier）
3. 定期运行 `pnpm check` 检查问题

### 提交前

1. 运行 `pnpm check` 检查所有问题
2. 运行 `pnpm format:write` 修复格式
3. 手动修复其他问题
4. 再次运行 `pnpm check` 确认
5. 提交代码

### 代码审查时

1. 运行 `pnpm report` 生成报告
2. 查看HTML报告分析问题
3. 提供修复建议

## 🔧 自定义配置

### 修改检查规则

1. **ESLint规则**: 编辑 `eslint.config.mjs`
2. **TypeScript配置**: 编辑 `tsconfig.json`
3. **Prettier格式**: 编辑 `.prettierrc`

### 添加忽略文件

1. **ESLint**: 在 `eslint.config.mjs` 中配置 `globalIgnores`
2. **Prettier**: 编辑 `.prettierignore`
3. **TypeScript**: 在 `tsconfig.json` 中配置 `exclude`

## 🆘 故障排除

### 常见问题

1. **工具版本不匹配**: 确保使用项目指定的工具版本
2. **配置文件错误**: 检查配置文件语法
3. **依赖问题**: 删除 `node_modules` 重新安装
4. **缓存问题**: 清理 `.next` 和 `tsconfig.tsbuildinfo`

### 获取帮助

1. 查看相关配置文档
2. 运行带 `--help` 参数的命令
3. 检查工具官方文档
4. 联系项目维护者

## 📈 质量指标

### 目标指标

- ✅ ESLint错误: 0
- ✅ ESLint警告: < 10
- ✅ TypeScript错误: 0
- ✅ 格式问题: 0
- ✅ 安全漏洞: 0
- ✅ 认知复杂度: < 15

### 监控方式

1. 定期运行 `pnpm report` 生成报告
2. 跟踪问题数量变化趋势
3. 在CI/CD中集成质量检查
4. 设置质量门禁

## 🤝 贡献指南

### 改进建议

1. 提交Issue描述问题或建议
2. 提供具体的配置改进方案
3. 更新相关文档
4. 测试配置变更的影响

### 文档更新

1. 保持文档与配置同步
2. 添加新的最佳实践示例
3. 更新故障排除指南
4. 完善使用说明

---

## 📞 联系方式

如有问题或建议，请：

1. 查看相关文档
2. 搜索已知问题
3. 提交Issue或联系维护者

**记住：代码质量是团队的共同责任！** 🚀
