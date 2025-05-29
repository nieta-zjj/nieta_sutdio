# 代码质量检查使用指南

本文档提供了如何使用项目中代码质量检查工具的详细指南。

## 快速开始

### 1. 安装依赖

```bash
# 安装项目依赖
pnpm install
```

### 2. 基础检查命令

```bash
# 运行所有质量检查
pnpm check

# 仅检查ESLint问题
pnpm check:eslint

# 仅检查TypeScript类型
pnpm check:types

# 仅检查代码格式
pnpm check:format

# 仅检查依赖问题
pnpm check:deps
```

### 3. 生成报告

```bash
# 生成所有报告
pnpm report

# 生成ESLint报告
pnpm report:eslint

# 生成格式检查报告
pnpm report:format

# 生成依赖分析报告
pnpm report:deps
```

## 详细使用说明

### ESLint检查

#### 基础检查

```bash
# 检查所有文件（不修复）
pnpm lint:check

# 严格模式检查（不允许警告）
pnpm lint:strict

# 检查特定文件
npx eslint src/components/Button.tsx
```

#### 检查结果解读

```
src/components/Button.tsx
  15:5   warning  Function has a complexity of 16  sonarjs/cognitive-complexity
  23:10  error    'user' is possibly null           @typescript-eslint/no-unsafe-member-access
  45:1   warning  Unexpected console statement      no-console
```

结果说明：

- **文件路径**: `src/components/Button.tsx`
- **位置**: `15:5` (第15行第5列)
- **级别**: `warning`/`error`
- **描述**: 问题描述
- **规则**: 触发的ESLint规则

#### 常见问题修复

**认知复杂度过高**

```typescript
// ❌ 问题：复杂度过高
function processData(data: any[]) {
  if (data) {
    if (data.length > 0) {
      for (const item of data) {
        if (item.type === "user") {
          if (item.active) {
            if (item.permissions) {
              // 复杂逻辑...
            }
          }
        }
      }
    }
  }
}

// ✅ 修复：拆分函数
function processData(data: any[]) {
  if (!data?.length) return;

  const users = data.filter((item) => item.type === "user");
  users.forEach(processUser);
}

function processUser(user: any) {
  if (!user.active || !user.permissions) return;
  // 处理用户逻辑...
}
```

**安全问题**

```typescript
// ❌ 问题：对象注入
function getValue(obj: any, key: string) {
  return obj[key]; // 不安全的属性访问
}

// ✅ 修复：安全的属性访问
function getValue<T>(obj: T, key: keyof T): T[keyof T] {
  return obj[key];
}

// 或者使用运行时检查
function getValue(obj: any, key: string) {
  if (Object.prototype.hasOwnProperty.call(obj, key)) {
    return obj[key];
  }
  return undefined;
}
```

### TypeScript检查

#### 基础检查

```bash
# 检查所有类型错误
pnpm type-check

# 监听模式
npx tsc --noEmit --watch

# 详细输出
npx tsc --noEmit --listFiles
```

#### 检查结果解读

```
src/components/Button.tsx(15,5): error TS2322: Type 'string | null' is not assignable to type 'string'.
  Type 'null' is not assignable to type 'string'.
```

结果说明：

- **文件**: `src/components/Button.tsx`
- **位置**: `(15,5)` (第15行第5列)
- **错误码**: `TS2322`
- **描述**: 类型不匹配的详细说明

#### 常见问题修复

**空值检查**

```typescript
// ❌ 问题：可能为null
function getName(user: User | null) {
  return user.name; // Error: user可能为null
}

// ✅ 修复：空值检查
function getName(user: User | null) {
  return user?.name ?? "Unknown";
}
```

**类型断言**

```typescript
// ❌ 问题：类型不明确
const data = JSON.parse(response) as any;

// ✅ 修复：明确类型
interface ApiResponse {
  data: User[];
  status: string;
}

const data = JSON.parse(response) as ApiResponse;
```

### Prettier格式检查

#### 基础检查

```bash
# 检查格式问题
pnpm format:check

# 修复格式问题
pnpm format:write

# 检查特定文件
npx prettier --check src/components/Button.tsx
```

#### 检查结果解读

```
Checking formatting...
src/components/Button.tsx
src/utils/helper.ts
Code style issues found in the above file(s). Forgot to run Prettier?
```

#### 修复格式问题

```bash
# 自动修复所有格式问题
pnpm format:write

# 修复特定文件
npx prettier --write src/components/Button.tsx
```

### 依赖检查

#### 基础检查

```bash
# 检查依赖问题
pnpm check:deps

# 详细输出
npx npm-check
```

#### 检查结果解读

```
❤️  Your modules look amazing. Keep up the great work.

? Choose which packages to update.

 Major Update Potentially breaking API changes. Use caution.
❯◯ react 17.0.2 → 18.2.0 https://github.com/facebook/react

 Minor Update New backwards-compatible features.
❯◯ typescript 4.9.5 → 5.0.2 https://github.com/Microsoft/TypeScript

 Patch Update Backwards-compatible bug fixes.
❯◯ eslint 8.36.0 → 8.39.0 https://github.com/eslint/eslint

 Unused Dependencies
❯◯ lodash 4.17.21 https://github.com/lodash/lodash
```

#### 依赖问题处理

**更新依赖**

```bash
# 更新特定包
pnpm update react

# 更新所有包到最新版本
pnpm update

# 更新到指定版本
pnpm add react@18.2.0
```

**移除未使用的依赖**

```bash
# 移除未使用的包
pnpm remove lodash

# 检查确认
pnpm check:deps
```

## 报告分析

### ESLint报告

生成的报告位于 `reports/eslint-report.html`，包含：

1. **总体统计**: 错误和警告数量
2. **文件列表**: 每个有问题的文件
3. **问题详情**: 具体的错误和警告
4. **规则说明**: 触发的ESLint规则

### 依赖报告

生成的报告位于 `reports/deps-report.txt`，包含：

1. **过时依赖**: 可以更新的包
2. **未使用依赖**: 可以移除的包
3. **安全漏洞**: 有安全问题的包
4. **更新建议**: 推荐的更新操作

## 工作流程建议

### 开发时

1. **实时检查**: 配置IDE实时显示ESLint和TypeScript错误
2. **保存时格式化**: 配置IDE保存时自动运行Prettier
3. **定期检查**: 每天运行一次 `pnpm check`

### 提交前

```bash
# 1. 运行所有检查
pnpm check

# 2. 如果有格式问题，修复格式
pnpm format:write

# 3. 手动修复其他问题

# 4. 再次检查确认
pnpm check

# 5. 提交代码
git add .
git commit -m "feat: add new feature"
```

### 代码审查时

```bash
# 生成详细报告
pnpm report

# 查看HTML报告
open reports/eslint-report.html
```

## 自动化集成

### Git Hooks

虽然项目不使用自动修复，但可以添加检查钩子：

```bash
# .git/hooks/pre-commit
#!/bin/sh
echo "Running code quality checks..."
pnpm check

if [ $? -ne 0 ]; then
  echo "Code quality checks failed. Please fix the issues before committing."
  exit 1
fi
```

### CI/CD集成

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: npm install -g pnpm
      - run: pnpm install
      - run: pnpm check
      - run: pnpm build
```

## 故障排除

### 常见问题

**1. ESLint配置错误**

```bash
# 检查配置文件
npx eslint --print-config src/components/Button.tsx

# 验证配置
npx eslint --debug src/components/Button.tsx
```

**2. TypeScript配置问题**

```bash
# 检查配置
npx tsc --showConfig

# 清理缓存
rm -rf .next
rm tsconfig.tsbuildinfo
```

**3. Prettier不工作**

```bash
# 检查配置
npx prettier --find-config-path src/components/Button.tsx

# 检查文件是否被忽略
npx prettier --get-file-info src/components/Button.tsx
```

**4. 依赖安装问题**

```bash
# 清理依赖
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install
```

### 性能优化

**1. 加速ESLint**

- 使用 `.eslintignore` 排除不必要的文件
- 只检查修改的文件：`npx eslint $(git diff --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx)$')`

**2. 加速TypeScript**

- 使用增量编译：`tsc --incremental`
- 使用项目引用分割大型项目

**3. 加速Prettier**

- 使用 `.prettierignore` 排除大文件
- 只格式化修改的文件

## 最佳实践

### 1. 渐进式修复

对于大型项目：

1. 先修复所有错误（error）
2. 再修复警告（warning）
3. 分模块逐步修复
4. 设置里程碑目标

### 2. 团队协作

1. **统一工具版本**: 确保团队使用相同版本的工具
2. **共享配置**: 将配置文件纳入版本控制
3. **定期更新**: 定期更新工具和规则
4. **知识分享**: 分享常见问题的解决方案

### 3. 持续改进

1. **监控指标**: 跟踪代码质量指标的变化
2. **定期审查**: 定期审查和更新规则配置
3. **反馈循环**: 收集团队反馈，优化工具配置
4. **学习新规则**: 关注工具更新，学习新的最佳实践
