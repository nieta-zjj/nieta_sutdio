# Prettier 配置说明

本文档详细说明了项目中Prettier的配置和代码格式化规范。

## 配置文件

- **主配置文件**: `.prettierrc`
- **忽略文件**: `.prettierignore`
- **Prettier版本**: 3.5.3

## 配置选项详解

### 基础配置

```json
{
  "semi": true, // 使用分号
  "singleQuote": false, // 使用双引号
  "tabWidth": 2, // 缩进宽度为2个空格
  "printWidth": 100, // 最大行宽100字符
  "trailingComma": "es5", // ES5兼容的尾随逗号
  "bracketSpacing": true, // 对象括号内空格
  "arrowParens": "always", // 箭头函数参数括号
  "endOfLine": "auto" // 行尾符自动检测
}
```

### 配置选项说明

#### 1. 分号 (semi)

```javascript
// semi: true (推荐)
const message = "Hello World";
const numbers = [1, 2, 3];

// semi: false
const message = "Hello World";
const numbers = [1, 2, 3];
```

#### 2. 引号 (singleQuote)

```javascript
// singleQuote: false (项目配置)
const message = "Hello World";
const template = `Hello ${name}`;

// singleQuote: true
const message = "Hello World";
const template = `Hello ${name}`;
```

#### 3. 缩进宽度 (tabWidth)

```javascript
// tabWidth: 2 (项目配置)
function example() {
  if (condition) {
    return true;
  }
}

// tabWidth: 4
function example() {
  if (condition) {
    return true;
  }
}
```

#### 4. 行宽 (printWidth)

```javascript
// printWidth: 100 (项目配置)
const longVariableName = someFunction(parameter1, parameter2, parameter3, parameter4);

// 超过100字符会换行
const veryLongVariableName = someFunction(
  parameter1,
  parameter2,
  parameter3,
  parameter4,
  parameter5
);
```

#### 5. 尾随逗号 (trailingComma)

```javascript
// trailingComma: "es5" (项目配置)
const obj = {
  name: "John",
  age: 30, // ✅ 对象和数组有尾随逗号
};

const arr = [
  "apple",
  "banana", // ✅ 数组有尾随逗号
];

// 函数参数不会有尾随逗号（ES5兼容）
function example(a, b, c) {
  return a + b + c;
}
```

#### 6. 括号间距 (bracketSpacing)

```javascript
// bracketSpacing: true (项目配置)
const obj = { name: "John", age: 30 };

// bracketSpacing: false
const obj = { name: "John", age: 30 };
```

#### 7. 箭头函数参数 (arrowParens)

```javascript
// arrowParens: "always" (项目配置)
const single = (x) => x * 2;
const multiple = (x, y) => x + y;

// arrowParens: "avoid"
const single = (x) => x * 2;
const multiple = (x, y) => x + y;
```

## 忽略文件配置

### .prettierignore 内容

```
# 依赖目录
node_modules/
pnpm-lock.yaml

# 构建输出
.next/
out/
dist/
build/

# 环境文件
.env*

# IDE文件
.vscode/
.idea/

# 操作系统文件
.DS_Store
Thumbs.db

# 示例目录
example/

# 生成文件
*.tsbuildinfo
coverage/

# 公共资源
public/

# 不应格式化的配置文件
*.config.js
*.config.mjs
*.config.ts
```

### 忽略规则说明

1. **依赖目录**: 第三方代码不需要格式化
2. **构建输出**: 生成的代码不需要格式化
3. **配置文件**: 某些配置文件有特殊格式要求
4. **二进制文件**: 图片、字体等文件不需要格式化

## 格式化示例

### JavaScript/TypeScript

#### 对象格式化

```javascript
// 格式化前
const user = {
  name: "John Doe",
  age: 30,
  email: "john@example.com",
  preferences: { theme: "dark", language: "en" },
};

// 格式化后
const user = {
  name: "John Doe",
  age: 30,
  email: "john@example.com",
  preferences: {
    theme: "dark",
    language: "en",
  },
};
```

#### 数组格式化

```javascript
// 格式化前
const colors = ["red", "green", "blue", "yellow", "orange", "purple"];

// 格式化后
const colors = ["red", "green", "blue", "yellow", "orange", "purple"];
```

#### 函数格式化

```javascript
// 格式化前
function calculateTotal(items, taxRate, discount) {
  return items.reduce((total, item) => total + item.price, 0) * (1 + taxRate) * (1 - discount);
}

// 格式化后
function calculateTotal(items, taxRate, discount) {
  return items.reduce((total, item) => total + item.price, 0) * (1 + taxRate) * (1 - discount);
}
```

#### 条件语句格式化

```javascript
// 格式化前
if ((condition1 && condition2) || condition3) {
  doSomething();
  doSomethingElse();
} else {
  doAlternative();
}

// 格式化后
if ((condition1 && condition2) || condition3) {
  doSomething();
  doSomethingElse();
} else {
  doAlternative();
}
```

### React/JSX

#### 组件格式化

```jsx
// 格式化前
const Button = ({ children, onClick, disabled, variant = "primary", ...props }) => (
  <button className={`btn btn-${variant}`} onClick={onClick} disabled={disabled} {...props}>
    {children}
  </button>
);

// 格式化后
const Button = ({ children, onClick, disabled, variant = "primary", ...props }) => (
  <button className={`btn btn-${variant}`} disabled={disabled} onClick={onClick} {...props}>
    {children}
  </button>
);
```

#### JSX属性格式化

```jsx
// 格式化前
<Component prop1="value1" prop2="value2" prop3="value3" prop4="value4" prop5="value5" onEvent={handler}/>

// 格式化后
<Component
  prop1="value1"
  prop2="value2"
  prop3="value3"
  prop4="value4"
  prop5="value5"
  onEvent={handler}
/>
```

### CSS/SCSS

#### CSS格式化

```css
/* 格式化前 */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  margin: 0 auto;
  max-width: 1200px;
}

/* 格式化后 */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  margin: 0 auto;
  max-width: 1200px;
}
```

### JSON

#### JSON格式化

```json
// 格式化前
{"name":"John","age":30,"hobbies":["reading","coding","gaming"],"address":{"street":"123 Main St","city":"New York","country":"USA"}}

// 格式化后
{
  "name": "John",
  "age": 30,
  "hobbies": ["reading", "coding", "gaming"],
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "country": "USA"
  }
}
```

### Markdown

#### Markdown格式化

```markdown
<!-- 格式化前 -->

#Title
##Subtitle
This is a paragraph with some**bold**text and*italic*text.
-Item 1
-Item 2
-Item 3

<!-- 格式化后 -->

# Title

## Subtitle

This is a paragraph with some **bold** text and _italic_ text.

- Item 1
- Item 2
- Item 3
```

## 命令行使用

### 检查格式

```bash
# 检查所有文件格式
pnpm format:check

# 检查特定文件
npx prettier --check "src/**/*.{ts,tsx}"

# 检查单个文件
npx prettier --check src/components/Button.tsx
```

### 格式化文件

```bash
# 格式化所有文件
pnpm format:write

# 格式化特定目录
npx prettier --write "src/**/*.{ts,tsx}"

# 格式化单个文件
npx prettier --write src/components/Button.tsx
```

### 其他有用命令

```bash
# 列出会被格式化的文件
npx prettier --list-different "**/*.{ts,tsx,js,jsx,json,md}"

# 调试配置
npx prettier --find-config-path src/components/Button.tsx

# 检查文件是否被忽略
npx prettier --get-file-info src/components/Button.tsx
```

## IDE集成

### VSCode配置

#### 设置文件 (settings.json)

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[markdown]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

#### 推荐扩展

- Prettier - Code formatter
- ESLint
- TypeScript Importer

### WebStorm配置

1. 打开 Settings → Languages & Frameworks → JavaScript → Prettier
2. 勾选 "On code reformat" 和 "On save"
3. 设置 Prettier package 路径
4. 配置文件模式匹配

## 与ESLint集成

### 配置说明

项目中Prettier通过ESLint插件集成：

```javascript
// eslint.config.mjs
plugins: {
  prettier: fixupPluginRules(prettier),
},

rules: {
  "prettier/prettier": "warn",
}
```

### 冲突解决

当ESLint和Prettier规则冲突时：

1. **优先级**: Prettier规则优先于ESLint格式规则
2. **配置**: 使用`eslint-config-prettier`禁用冲突的ESLint规则
3. **检查**: 运行`pnpm check`同时检查两者

## 自定义配置

### 项目特定配置

如需修改配置，编辑`.prettierrc`文件：

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "printWidth": 120, // 增加行宽
  "trailingComma": "all", // 所有地方都使用尾随逗号
  "bracketSpacing": true,
  "arrowParens": "avoid", // 单参数箭头函数不使用括号
  "endOfLine": "lf" // 强制使用LF行尾
}
```

### 文件特定配置

使用注释覆盖特定文件的配置：

```javascript
// prettier-ignore
const uglyCode = {
    a:1,b:2,c:3
};

/* prettier-ignore */
const matrix = [
  [1, 0, 0],
  [0, 1, 0],
  [0, 0, 1]
];
```

## 常见问题

### 1. 格式化后代码变丑了？

Prettier优先考虑一致性而非美观。如果觉得某些格式不好看，可以：

- 调整`printWidth`设置
- 重构代码结构
- 使用`prettier-ignore`注释

### 2. 与团队成员格式不一致？

确保所有人使用相同的：

- Prettier版本
- 配置文件
- IDE设置

### 3. 格式化很慢？

优化建议：

- 使用`.prettierignore`排除不必要的文件
- 在IDE中只对修改的文件格式化
- 使用增量格式化工具

### 4. 某些文件不应该格式化？

添加到`.prettierignore`文件或使用`prettier-ignore`注释。
