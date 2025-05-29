#!/usr/bin/env node

/**
 * 代码质量报告生成工具
 *
 * 这个脚本用于生成代码质量报告，包括：
 * - ESLint 报告
 * - Prettier 格式检查报告
 * - 代码复杂度报告
 * - 依赖分析报告
 *
 * 使用方法:
 * - 生成所有报告: node scripts/generate-report.js
 * - 生成特定报告: node scripts/generate-report.js --type=eslint,format
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// 解析命令行参数
const args = process.argv.slice(2);
const params = {};
args.forEach((arg) => {
  if (arg.startsWith("--")) {
    const [key, value] = arg.slice(2).split("=");
    params[key] = value || true;
  }
});

// 默认生成所有报告
const reportTypes = params.type
  ? params.type.split(",")
  : ["eslint", "format", "complexity", "deps"];

// 创建报告目录
const reportsDir = path.join(__dirname, "..", "reports");
if (!fs.existsSync(reportsDir)) {
  fs.mkdirSync(reportsDir, { recursive: true });
}

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

// 运行命令并处理错误
function runCommand(command, errorMessage) {
  try {
    log(`运行: ${command}`, "cyan");
    return execSync(command, { encoding: "utf8" });
  } catch (error) {
    log(`${errorMessage}: ${error.message}`, "red");
    return null;
  }
}

// 生成 ESLint 报告
if (reportTypes.includes("eslint")) {
  log("\n📊 生成 ESLint 报告...", "blue");

  try {
    const eslintReport = runCommand(
      'npx eslint . --ext .ts,.tsx,.js,.jsx -c eslint.config.mjs -f json --ignore-pattern "example/**"',
      "ESLint 报告生成失败"
    );

    if (eslintReport) {
      const reportPath = path.join(reportsDir, "eslint-report.json");
      fs.writeFileSync(reportPath, eslintReport);

      // 生成 HTML 报告
      const htmlReportPath = path.join(reportsDir, "eslint-report.html");
      const htmlReport = `
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>ESLint 代码质量报告</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
            .summary { margin-bottom: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .summary-item { display: inline-block; margin-right: 20px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #007acc; }
            .file { margin-bottom: 20px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
            .file-header { background: #f5f5f5; padding: 15px; font-weight: bold; border-bottom: 1px solid #ddd; }
            .file-path { color: #666; font-size: 0.9em; margin-top: 5px; }
            .messages { padding: 0; }
            .message { padding: 15px; border-top: 1px solid #eee; display: flex; align-items: flex-start; }
            .message:nth-child(odd) { background: #fafafa; }
            .severity { width: 80px; font-weight: bold; }
            .error { color: #d73a49; }
            .warning { color: #e36209; }
            .message-content { flex: 1; margin-left: 15px; }
            .rule { color: #6f42c1; font-family: monospace; background: #f1f3f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
            .location { color: #666; font-size: 0.9em; margin-top: 5px; }
            .no-issues { text-align: center; padding: 40px; color: #28a745; font-size: 1.2em; }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>ESLint 代码质量报告</h1>
            <div class="summary">
              <p><strong>生成时间:</strong> ${new Date().toLocaleString()}</p>
              <p><strong>报告路径:</strong> ${reportPath}</p>
              <div id="summary-stats"></div>
            </div>
            <div id="report"></div>
          </div>

          <script>
            const report = ${eslintReport};
            const reportElement = document.getElementById('report');
            const summaryStats = document.getElementById('summary-stats');

            // 统计错误和警告数量
            let errorCount = 0;
            let warningCount = 0;
            let fileCount = 0;

            report.forEach(file => {
              if (file.messages.length > 0) {
                fileCount++;
                errorCount += file.errorCount;
                warningCount += file.warningCount;
              }
            });

            // 显示统计信息
            summaryStats.innerHTML = \`
              <div class="summary-item">
                <strong>文件数:</strong> \${fileCount}
              </div>
              <div class="summary-item">
                <strong>错误:</strong> <span style="color: #d73a49;">\${errorCount}</span>
              </div>
              <div class="summary-item">
                <strong>警告:</strong> <span style="color: #e36209;">\${warningCount}</span>
              </div>
            \`;

            if (errorCount === 0 && warningCount === 0) {
              reportElement.innerHTML = '<div class="no-issues">🎉 恭喜！没有发现代码质量问题</div>';
            } else {
              report.forEach(file => {
                if (file.messages.length === 0) return;

                const fileElement = document.createElement('div');
                fileElement.className = 'file';

                const fileHeader = document.createElement('div');
                fileHeader.className = 'file-header';
                fileHeader.innerHTML = \`
                  <div>\${file.filePath.replace(process.cwd(), '').replace(/\\\\/g, '/')}</div>
                  <div class="file-path">错误: \${file.errorCount}, 警告: \${file.warningCount}</div>
                \`;

                const messagesElement = document.createElement('div');
                messagesElement.className = 'messages';

                file.messages.forEach(message => {
                  const messageElement = document.createElement('div');
                  messageElement.className = 'message';

                  const severityClass = message.severity === 2 ? 'error' : 'warning';
                  const severityText = message.severity === 2 ? '错误' : '警告';

                  messageElement.innerHTML = \`
                    <div class="severity \${severityClass}">\${severityText}</div>
                    <div class="message-content">
                      <div>\${message.message}</div>
                      <div class="rule">\${message.ruleId || '未知规则'}</div>
                      <div class="location">行 \${message.line}, 列 \${message.column}</div>
                    </div>
                  \`;

                  messagesElement.appendChild(messageElement);
                });

                fileElement.appendChild(fileHeader);
                fileElement.appendChild(messagesElement);
                reportElement.appendChild(fileElement);
              });
            }
          </script>
        </body>
        </html>
      `;

      fs.writeFileSync(htmlReportPath, htmlReport);
      log(`✅ ESLint 报告已生成: ${reportPath}`, "green");
      log(`✅ ESLint HTML 报告已生成: ${htmlReportPath}`, "green");
    }
  } catch (error) {
    log(`❌ ESLint 报告生成失败: ${error.message}`, "red");
  }
}

// 生成 Prettier 格式检查报告
if (reportTypes.includes("format")) {
  log("\n📊 生成 Prettier 格式检查报告...", "blue");

  try {
    const formatReport = runCommand(
      'npx prettier --check "**/*.{ts,tsx,js,jsx,json,md}" --ignore-path .prettierignore',
      "Prettier 格式检查报告生成失败"
    );

    const reportPath = path.join(reportsDir, "prettier-report.txt");
    const timestamp = new Date().toLocaleString();

    if (formatReport === null) {
      // 有格式问题
      fs.writeFileSync(
        reportPath,
        `Prettier 格式检查报告\n生成时间: ${timestamp}\n\n发现格式问题，请运行 pnpm format:write 修复\n`
      );
      log(`✅ Prettier 报告已生成: ${reportPath}`, "green");
    } else {
      // 没有格式问题
      fs.writeFileSync(
        reportPath,
        `Prettier 格式检查报告\n生成时间: ${timestamp}\n\n✅ 所有文件格式正确\n`
      );
      log(`✅ Prettier 报告已生成: ${reportPath}`, "green");
    }
  } catch (error) {
    log(`❌ Prettier 报告生成失败: ${error.message}`, "red");
  }
}

// 生成代码复杂度报告
if (reportTypes.includes("complexity")) {
  log("\n📊 生成代码复杂度报告...", "blue");

  try {
    // 使用 ESLint 的 sonarjs 插件生成复杂度报告
    const complexityReport = runCommand(
      'npx eslint . --ext .ts,.tsx -c eslint.config.mjs -f json --ignore-pattern "example/**" --no-eslintrc',
      "代码复杂度报告生成失败"
    );

    if (complexityReport) {
      const reportPath = path.join(reportsDir, "complexity-report.json");
      fs.writeFileSync(reportPath, complexityReport);
      log(`✅ 代码复杂度报告已生成: ${reportPath}`, "green");
    }
  } catch (error) {
    log(`❌ 代码复杂度报告生成失败: ${error.message}`, "red");
    log("提示: 复杂度信息包含在 ESLint 报告中", "yellow");
  }
}

// 生成依赖分析报告
if (reportTypes.includes("deps")) {
  log("\n📊 生成依赖分析报告...", "blue");

  try {
    const depsReport = runCommand("npx npm-check --json", "依赖分析报告生成失败");

    if (depsReport) {
      const reportPath = path.join(reportsDir, "deps-report.json");
      fs.writeFileSync(reportPath, depsReport);

      // 生成可读的依赖报告
      const depsData = JSON.parse(depsReport);
      const readableReportPath = path.join(reportsDir, "deps-report.txt");
      let readableReport = `依赖分析报告\n生成时间: ${new Date().toLocaleString()}\n\n`;

      if (depsData.length === 0) {
        readableReport += "✅ 所有依赖都是最新的且被使用\n";
      } else {
        readableReport += `发现 ${depsData.length} 个依赖问题:\n\n`;
        depsData.forEach((dep, index) => {
          readableReport += `${index + 1}. ${dep.moduleName}\n`;
          readableReport += `   当前版本: ${dep.installed}\n`;
          if (dep.latest) readableReport += `   最新版本: ${dep.latest}\n`;
          if (dep.unused) readableReport += `   状态: 未使用\n`;
          if (dep.bump) readableReport += `   建议: 可更新\n`;
          readableReport += "\n";
        });
      }

      fs.writeFileSync(readableReportPath, readableReport);
      log(`✅ 依赖分析报告已生成: ${reportPath}`, "green");
      log(`✅ 依赖分析可读报告已生成: ${readableReportPath}`, "green");
    }
  } catch (error) {
    log(`❌ 依赖分析报告生成失败: ${error.message}`, "red");
  }
}

log("\n✅ 报告生成完成！所有报告都保存在 reports/ 目录中。", "green");
log("\n📁 报告文件说明:", "cyan");
log("   - eslint-report.json: ESLint 检查结果 (JSON格式)", "cyan");
log("   - eslint-report.html: ESLint 检查结果 (HTML格式，可在浏览器中查看)", "cyan");
log("   - prettier-report.txt: Prettier 格式检查结果", "cyan");
log("   - complexity-report.json: 代码复杂度分析结果", "cyan");
log("   - deps-report.json: 依赖分析结果 (JSON格式)", "cyan");
log("   - deps-report.txt: 依赖分析结果 (可读格式)", "cyan");
