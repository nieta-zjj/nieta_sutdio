# ESLint 配置说明

本文档详细说明了项目中ESLint的配置和规则。

## 配置文件

- **主配置文件**: `eslint.config.mjs`
- **配置格式**: ESLint 9.x 扁平配置格式

## 插件和扩展

### 核心插件

1. **react**: React特定规则
2. **unused-imports**: 未使用导入检测
3. **import**: 导入顺序和规范
4. **@typescript-eslint**: TypeScript特定规则
5. **jsx-a11y**: 可访问性规则
6. **prettier**: 代码格式化集成
7. **security**: 安全漏洞检测
8. **sonarjs**: 代码质量和复杂度检测

### 扩展配置

- `plugin:react/recommended`: React推荐规则
- `plugin:prettier/recommended`: Prettier集成
- `plugin:react-hooks/recommended`: React Hooks规则
- `plugin:jsx-a11y/recommended`: 可访问性推荐规则
- `plugin:@next/next/recommended`: Next.js推荐规则

## 安全规则详解

### 对象注入检测

```javascript
// ❌ 错误 - 可能的对象注入
const key = userInput;
const value = obj[key];

// ✅ 正确 - 使用安全的属性访问
const value = Object.prototype.hasOwnProperty.call(obj, key) ? obj[key] : undefined;
```

### 正则表达式安全

```javascript
// ❌ 错误 - 动态正则表达式
const pattern = userInput;
const regex = new RegExp(pattern);

// ✅ 正确 - 字面量正则表达式
const regex = /^[a-zA-Z0-9]+$/;
```

### 文件系统安全

```javascript
// ❌ 错误 - 动态文件路径
const filename = userInput;
fs.readFile(filename, callback);

// ✅ 正确 - 验证文件路径
const allowedFiles = ["config.json", "data.txt"];
if (allowedFiles.includes(filename)) {
  fs.readFile(path.join(__dirname, filename), callback);
}
```

## 代码复杂度规则详解

### 认知复杂度

- **限制**: 15
- **说明**: 衡量函数理解难度的指标
- **修复**: 拆分复杂函数，减少嵌套

### 重复字符串

- **限制**: 5次重复
- **说明**: 避免硬编码重复字符串
- **修复**: 提取为常量

### 相同函数

- **说明**: 检测完全相同的函数实现
- **修复**: 提取为共用函数

### 可折叠的if语句

```javascript
// ❌ 错误 - 可折叠的if
if (condition1) {
  if (condition2) {
    doSomething();
  }
}

// ✅ 正确 - 合并条件
if (condition1 && condition2) {
  doSomething();
}
```

### 重复的分支

```javascript
// ❌ 错误 - 重复分支
if (condition) {
  doSomething();
  return result;
} else {
  doSomething();
  return result;
}

// ✅ 正确 - 提取公共逻辑
doSomething();
return result;
```

## React特定规则

### Props排序

```javascript
// ✅ 正确的props排序
<Component
  key="unique"
  ref={ref}
  className="example"
  disabled
  value={value}
  onChange={handleChange}
  onClick={handleClick}
/>
```

排序规则：

1. 保留字段（key, ref等）
2. 布尔属性（简写形式）
3. 其他属性（按字母顺序）
4. 回调函数（最后）

### 自闭合组件

```javascript
// ❌ 错误
<Component></Component>

// ✅ 正确
<Component />
```

### Hooks依赖

```javascript
// ❌ 错误 - 缺少依赖
useEffect(() => {
  fetchData(id);
}, []); // 缺少id依赖

// ✅ 正确 - 包含所有依赖
useEffect(() => {
  fetchData(id);
}, [id]);
```

## TypeScript规则

### 未使用变量

```javascript
// ❌ 错误 - 未使用的变量
const unusedVariable = "value";

// ✅ 正确 - 使用下划线前缀表示有意忽略
const _intentionallyUnused = "value";
```

### 函数参数

```javascript
// ❌ 错误 - 未使用的参数
function handler(event, unusedParam) {
  console.log(event);
}

// ✅ 正确 - 使用下划线前缀
function handler(event, _unusedParam) {
  console.log(event);
}

// ✅ 或者省略参数名
function handler(event) {
  console.log(event);
}
```

## 导入顺序规则

```javascript
// ✅ 正确的导入顺序
import type { ComponentType } from 'react';

import { readFileSync } from 'fs';
import path from 'path';

import React from 'react';
import { Button } from '@heroui/react';

import { apiClient } from '~/utils/apiClient';
import { formatDate } from '~/utils/dateUtils';

import { Header } from '../Header';
import { Footer } from '../Footer';

import { LocalComponent } from './LocalComponent';

import './styles.css';
```

## 代码间距规则

```javascript
// ✅ 正确的代码间距
const API_URL = "https://api.example.com";
const MAX_RETRIES = 3;

function fetchData() {
  const url = `${API_URL}/data`;
  const options = { method: "GET" };

  return fetch(url, options);
}

function processData(data) {
  const processed = data.map((item) => item.value);

  return processed.filter((value) => value > 0);
}
```

规则说明：

- 变量声明后需要空行
- return语句前需要空行
- 连续的变量声明之间不需要空行

## 忽略规则

### 文件级忽略

```javascript
/* eslint-disable security/detect-object-injection */
// 整个文件忽略特定规则
```

### 行级忽略

```javascript
// eslint-disable-next-line sonarjs/cognitive-complexity
function complexFunction() {
  // 复杂逻辑...
}
```

### 块级忽略

```javascript
/* eslint-disable react-hooks/exhaustive-deps */
useEffect(() => {
  // 特殊情况下的effect
}, []);
/* eslint-enable react-hooks/exhaustive-deps */
```

## 自定义规则配置

如需修改规则配置，请在`eslint.config.mjs`中调整：

```javascript
rules: {
  // 调整认知复杂度限制
  "sonarjs/cognitive-complexity": ["warn", 20],

  // 禁用特定规则
  "no-console": "off",

  // 将警告改为错误
  "react-hooks/exhaustive-deps": "error",
}
```

## 常见问题

### 1. 如何处理第三方库的类型问题？

使用类型断言或创建类型声明文件。

### 2. 如何处理动态属性访问？

使用`Object.prototype.hasOwnProperty.call()`或`Map`数据结构。

### 3. 如何处理复杂的业务逻辑？

将复杂逻辑拆分为多个小函数，每个函数职责单一。

### 4. 如何处理必要的console.log？

在开发环境中可以临时忽略，生产环境应该移除或使用专门的日志库。
