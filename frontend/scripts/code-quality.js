#!/usr/bin/env node

/**
 * 代码质量检查脚本 - 仅检查不自动修复
 *
 * 这个脚本用于运行各种代码质量检查工具，包括：
 * - ESLint (代码质量和风格检查)
 * - TypeScript 类型检查
 * - Prettier 格式检查
 * - 依赖检查
 *
 * 重要：此脚本仅进行检查，不会自动修复任何问题
 * 所有修复都需要开发者手动处理
 *
 * 使用方法:
 * - 检查所有项目: node scripts/code-quality.js
 * - 检查特定文件: node scripts/code-quality.js --files="app/components/*.tsx"
 * - 仅运行特定检查: node scripts/code-quality.js --only=eslint,types
 */

const { execSync } = require("child_process");

// 解析命令行参数
const args = process.argv.slice(2);
const params = {};
args.forEach((arg) => {
  if (arg.startsWith("--")) {
    const [key, value] = arg.slice(2).split("=");
    params[key] = value || true;
  }
});

// 默认检查所有文件，排除 example 目录
const files = params.files
  ? params.files.split(",")
  : ["app", "components", "lib", "utils", "types", "config", "*.{ts,tsx,js,jsx}"];
// 默认运行所有检查
const onlyRun = params.only ? params.only.split(",") : ["eslint", "types", "format", "deps"];

// 颜色输出
const colors = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
};

// 打印带颜色的消息
function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 运行命令并处理错误 - 仅检查不修复
function runCommand(command, errorMessage) {
  try {
    log(`运行检查: ${command}`, "cyan");
    execSync(command, { stdio: "inherit" });
    return true;
  } catch (error) {
    log(`${errorMessage}: 发现问题需要手动修复`, "red");
    return false;
  }
}

// 检查结果
const results = {
  eslint: null,
  types: null,
  format: null,
  deps: null,
};

// 运行 ESLint 检查（仅检查不修复）
if (onlyRun.includes("eslint")) {
  log("\n🔍 运行 ESLint 代码质量检查...", "blue");
  log("⚠️  注意：仅检查代码问题，不会自动修复", "yellow");
  const filePattern = files.join(" ");
  results.eslint = runCommand(
    `npx eslint ${filePattern} --ext .ts,.tsx,.js,.jsx -c eslint.config.mjs --ignore-pattern "example/**"`,
    "ESLint 检查发现问题"
  );
}

// 运行 TypeScript 类型检查
if (onlyRun.includes("types")) {
  log("\n🔍 运行 TypeScript 类型检查...", "blue");
  results.types = runCommand("npx tsc --noEmit --skipLibCheck", "TypeScript 类型检查发现问题");
}

// 运行 Prettier 格式检查（仅检查不修复）
if (onlyRun.includes("format")) {
  log("\n🔍 运行 Prettier 格式检查...", "blue");
  log("⚠️  注意：仅检查格式问题，不会自动修复", "yellow");
  results.format = runCommand(
    'npx prettier --check "**/*.{ts,tsx,js,jsx,json,md}" --ignore-path .prettierignore',
    "Prettier 格式检查发现问题"
  );
}

// 检查依赖项
if (onlyRun.includes("deps")) {
  log("\n🔍 检查依赖项...", "blue");
  try {
    log("运行检查: npx npm-check", "cyan");
    execSync("npx npm-check", { stdio: "inherit" });
    log(
      "\n⚠️ 依赖项检查完成，未使用的依赖和缺失的依赖只会产生警告，不会阻止构建或提交。",
      "yellow"
    );
    // 依赖项检查不应该导致整个检查失败，所以返回 true
    results.deps = true;
  } catch (error) {
    log(
      "\n⚠️ 依赖项检查完成，未使用的依赖和缺失的依赖只会产生警告，不会阻止构建或提交。",
      "yellow"
    );
    // 依赖项检查不应该导致整个检查失败，所以返回 true
    results.deps = true;
  }
}

// 输出总结
log("\n📊 检查结果摘要:", "magenta");
Object.entries(results).forEach(([check, passed]) => {
  if (passed === null) return; // 跳过未运行的检查
  const status = passed ? `${colors.green}通过✅` : `${colors.red}需要修复❌`;
  log(`${check}: ${status}`, "reset");
});

// 确定退出代码
const allPassed = Object.values(results).every((result) => result === true || result === null);
if (!allPassed) {
  log("\n❌ 代码质量检查发现问题。请手动修复上述问题后再提交代码。", "red");
  log("\n💡 修复建议:", "yellow");
  if (results.eslint === false) {
    log("   - ESLint问题: 运行 pnpm lint:check 查看详细问题，然后手动修复", "yellow");
  }
  if (results.types === false) {
    log("   - TypeScript问题: 运行 pnpm type-check 查看详细问题，然后手动修复", "yellow");
  }
  if (results.format === false) {
    log(
      "   - 格式问题: 运行 pnpm format:check 查看详细问题，然后运行 pnpm format:write 修复",
      "yellow"
    );
  }
  process.exit(1);
} else {
  log("\n✅ 所有代码质量检查通过！", "green");
}
