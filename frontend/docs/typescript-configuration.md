# TypeScript 配置说明

本文档详细说明了项目中TypeScript的配置和最佳实践。

## 配置文件

- **主配置文件**: `tsconfig.json`
- **TypeScript版本**: 5.6.3

## 编译选项详解

### 基础配置

```json
{
  "compilerOptions": {
    "target": "es5", // 编译目标版本
    "lib": ["dom", "dom.iterable", "esnext"], // 包含的库文件
    "allowJs": true, // 允许编译JS文件
    "skipLibCheck": true, // 跳过库文件类型检查
    "strict": true, // 启用严格模式
    "forceConsistentCasingInFileNames": true, // 强制文件名大小写一致
    "noEmit": true, // 不生成输出文件
    "esModuleInterop": true, // ES模块互操作
    "module": "esnext", // 模块系统
    "moduleResolution": "node", // 模块解析策略
    "resolveJsonModule": true, // 允许导入JSON模块
    "isolatedModules": true, // 每个文件作为单独模块
    "jsx": "preserve", // JSX处理方式
    "incremental": true // 增量编译
  }
}
```

### 路径映射

```json
{
  "compilerOptions": {
    "paths": {
      "~/*": ["./*"] // 路径别名
    }
  }
}
```

### 包含和排除

```json
{
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules", "example/**/*"]
}
```

## 严格模式详解

### 1. 严格空值检查

```typescript
// ❌ 错误 - 可能为null或undefined
function getName(user: User | null) {
  return user.name; // 错误：user可能为null
}

// ✅ 正确 - 空值检查
function getName(user: User | null) {
  return user?.name ?? "Unknown";
}

// ✅ 正确 - 类型守卫
function getName(user: User | null) {
  if (user) {
    return user.name;
  }
  return "Unknown";
}
```

### 2. 严格函数类型

```typescript
// ❌ 错误 - 参数类型不兼容
type Handler = (event: MouseEvent) => void;
const handler: Handler = (event: Event) => {}; // 错误

// ✅ 正确 - 参数类型兼容
type Handler = (event: MouseEvent) => void;
const handler: Handler = (event: MouseEvent) => {};
```

### 3. 严格属性初始化

```typescript
// ❌ 错误 - 属性未初始化
class Component {
  private name: string; // 错误：未初始化
}

// ✅ 正确 - 属性初始化
class Component {
  private name: string = "";

  // 或者在构造函数中初始化
  constructor(name: string) {
    this.name = name;
  }
}
```

## 类型定义最佳实践

### 1. 接口定义

```typescript
// ✅ 推荐的接口定义
interface User {
  readonly id: string;
  name: string;
  email: string;
  age?: number;
  preferences: {
    theme: "light" | "dark";
    language: string;
  };
}

// ✅ 扩展接口
interface AdminUser extends User {
  permissions: string[];
  lastLogin: Date;
}
```

### 2. 类型别名

```typescript
// ✅ 基础类型别名
type Status = "pending" | "success" | "error";
type ID = string | number;

// ✅ 函数类型
type EventHandler<T = Event> = (event: T) => void;
type AsyncFunction<T> = () => Promise<T>;

// ✅ 条件类型
type NonNullable<T> = T extends null | undefined ? never : T;
```

### 3. 泛型使用

```typescript
// ✅ 泛型接口
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

// ✅ 泛型函数
function createArray<T>(length: number, value: T): T[] {
  return Array(length).fill(value);
}

// ✅ 约束泛型
interface Identifiable {
  id: string;
}

function updateEntity<T extends Identifiable>(entity: T, updates: Partial<T>): T {
  return { ...entity, ...updates };
}
```

### 4. 工具类型

```typescript
// ✅ 使用内置工具类型
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
}

// 创建用户时不需要id
type CreateUserData = Omit<User, "id">;

// 更新用户时所有字段都是可选的
type UpdateUserData = Partial<User>;

// 公开的用户信息（不包含密码）
type PublicUser = Omit<User, "password">;

// 只读用户信息
type ReadonlyUser = Readonly<User>;
```

## React组件类型

### 1. 函数组件

```typescript
// ✅ 基础函数组件
interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary'
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
};
```

### 2. 带泛型的组件

```typescript
// ✅ 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}
```

### 3. 事件处理

```typescript
// ✅ 事件处理类型
interface FormProps {
  onSubmit: (data: FormData) => void;
}

const Form: React.FC<FormProps> = ({ onSubmit }) => {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    onSubmit(formData);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log(event.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleInputChange} />
      <button type="submit">Submit</button>
    </form>
  );
};
```

### 4. Ref类型

```typescript
// ✅ Ref类型使用
const InputComponent: React.FC = () => {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return (
    <div>
      <input ref={inputRef} />
      <button onClick={focusInput}>Focus Input</button>
    </div>
  );
};
```

## Hooks类型

### 1. useState

```typescript
// ✅ useState类型推断
const [count, setCount] = useState(0); // 自动推断为number

// ✅ 显式类型
const [user, setUser] = useState<User | null>(null);

// ✅ 复杂状态类型
interface AppState {
  loading: boolean;
  error: string | null;
  data: any[];
}

const [state, setState] = useState<AppState>({
  loading: false,
  error: null,
  data: [],
});
```

### 2. useEffect

```typescript
// ✅ useEffect类型
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await fetch("/api/data");
      const data: ApiResponse<User[]> = await response.json();
      setUsers(data.data);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
  };

  fetchData();
}, []);
```

### 3. 自定义Hooks

```typescript
// ✅ 自定义Hook类型
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url);
      const result: T = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
```

## 常见类型问题解决

### 1. 对象属性访问

```typescript
// ❌ 错误 - 动态属性访问
const getValue = (obj: any, key: string) => {
  return obj[key]; // 不安全
};

// ✅ 正确 - 类型安全的属性访问
const getValue = <T, K extends keyof T>(obj: T, key: K): T[K] => {
  return obj[key];
};

// ✅ 或者使用类型守卫
const hasProperty = <T, K extends string>(obj: T, key: K): obj is T & Record<K, unknown> => {
  return key in obj;
};
```

### 2. 数组类型

```typescript
// ✅ 数组类型定义
const numbers: number[] = [1, 2, 3];
const users: Array<User> = [];

// ✅ 只读数组
const readonlyNumbers: readonly number[] = [1, 2, 3];

// ✅ 元组类型
const coordinate: [number, number] = [10, 20];
const userInfo: [string, number, boolean] = ["John", 25, true];
```

### 3. 联合类型和交叉类型

```typescript
// ✅ 联合类型
type Status = "loading" | "success" | "error";
type StringOrNumber = string | number;

// ✅ 交叉类型
type UserWithPermissions = User & {
  permissions: string[];
};

// ✅ 类型守卫
const isString = (value: StringOrNumber): value is string => {
  return typeof value === "string";
};
```

## 类型声明文件

### 1. 全局类型声明

```typescript
// types/global.d.ts
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }

  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_API_URL: string;
      DATABASE_URL: string;
    }
  }
}

export {};
```

### 2. 模块声明

```typescript
// types/modules.d.ts
declare module "*.svg" {
  const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
  export default content;
}

declare module "*.css" {
  const classes: { [key: string]: string };
  export default classes;
}
```

## 性能优化

### 1. 类型推断优化

```typescript
// ✅ 让TypeScript推断简单类型
const name = "John"; // 推断为string
const age = 25; // 推断为number

// ✅ 显式声明复杂类型
const config: AppConfig = {
  apiUrl: process.env.API_URL,
  timeout: 5000,
};
```

### 2. 避免过度类型化

```typescript
// ❌ 过度类型化
const handleClick: React.MouseEventHandler<HTMLButtonElement> = (event) => {
  // 简单的点击处理
};

// ✅ 简化类型
const handleClick = (event: React.MouseEvent) => {
  // 简单的点击处理
};
```

## 调试技巧

### 1. 类型检查命令

```bash
# 检查所有类型错误
pnpm type-check

# 监听模式
npx tsc --noEmit --watch

# 详细输出
npx tsc --noEmit --listFiles
```

### 2. IDE配置

推荐的VSCode设置：

```json
{
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "typescript.suggest.autoImports": true,
  "typescript.updateImportsOnFileMove.enabled": "always"
}
```

## 常见错误和解决方案

### 1. 类型"xxx"上不存在属性"yyy"

```typescript
// 问题：访问不存在的属性
// 解决：使用可选链或类型守卫
const value = obj?.property ?? defaultValue;
```

### 2. 不能将类型"xxx"分配给类型"yyy"

```typescript
// 问题：类型不匹配
// 解决：检查类型定义，使用类型断言或修改类型
const value = data as ExpectedType;
```

### 3. 参数"xxx"隐式具有"any"类型

```typescript
// 问题：参数缺少类型注解
// 解决：添加明确的类型注解
function process(data: unknown) {
  // 处理逻辑
}
```
