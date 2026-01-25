---
name: market-review
description: 生成市场指数复盘报告。自动执行Wind数据获取、Excel生成、JSON转换、前端展示和截图保存的完整流程。当用户要求"生成市场复盘"、"市场回顾"、"生成截止某日期的市场复盘"、"市场数据更新"时使用此技能。
---

# 市场指数复盘

自动化生成多资产市场复盘仪表板，包括权益、债券、汇率、商品四大类资产的行情数据和分位数分析。

## 前置条件

1. **Wind终端已登录** - 必须确保 Wind 金融终端已安装并登录
2. **Python环境就绪** - 需要 pandas, numpy, openpyxl, WindPy
3. **前端依赖已安装** - dashboard 目录需要已运行过 `npm install` 或 `pnpm install`

## 执行流程

### 步骤 1: 解析用户请求的日期

从用户输入中提取截止日期。如果未指定，使用当天日期。

日期格式: `YYYY-MM-DD`

**日期范围说明**: 近一月走势包含完整31天。例如截止日期为2026-01-24，则起始日期为2025-12-24。

### 步骤 2: 生成 Wind 数据

```bash
cd /Users/fanshengxia/Desktop/市场观点美化/data
python generate_tables_from_wind.py --date YYYY-MM-DD
```

生成文件:
- `指标值.xlsx` - 37个指标的当前值、历史统计和分位数
- `近1月净值走势.xlsx` - 完整31天的日度行情数据

### 步骤 3: 转换 Excel 为 JSON

```bash
cd /Users/fanshengxia/Desktop/市场观点美化/data
python excel_to_json_converter.py
```

输出文件:
- `data/asset_data.json` - 数据备份
- `asset-analysis-real-data/asset-analysis-dashboard/src/assets/asset_data.json` - 前端数据

### 步骤 4: 启动前端服务

**重要**: 使用 `./node_modules/.bin/vite` 而不是 `pnpm dev`，避免环境变量问题。

```bash
cd /Users/fanshengxia/Desktop/市场观点美化/asset-analysis-real-data/asset-analysis-dashboard
./node_modules/.bin/vite
```

后台运行时使用 `run_in_background: true` 参数。

前端服务启动后访问: http://localhost:5173

### 步骤 5: 截图保存

等待前端完全加载后（约5秒），使用 puppeteer 进行截图：

```bash
cd /tmp && npm install puppeteer --no-save 2>/dev/null
```

```javascript
// /tmp/screenshot.js
const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0', timeout: 30000 });
    await new Promise(resolve => setTimeout(resolve, 2000));
    await page.screenshot({
        path: '/Users/fanshengxia/Desktop/市场观点美化/市场复盘_YYYY-MM-DD.png',
        fullPage: true
    });
    await browser.close();
})();
```

截图保存路径: `/Users/fanshengxia/Desktop/市场观点美化/市场复盘_YYYY-MM-DD.png`

### 步骤 6: 关闭前端服务

使用 `TaskStop` 工具停止后台运行的前端服务。

## 项目路径

| 路径 | 说明 |
|------|------|
| `/Users/fanshengxia/Desktop/市场观点美化` | 项目根目录 |
| `data/` | 数据脚本和生成的文件 |
| `data/generate_tables_from_wind.py` | Wind 数据生成脚本 (v2.2) |
| `data/excel_to_json_converter.py` | Excel 转 JSON 脚本 |
| `asset-analysis-real-data/asset-analysis-dashboard/` | React 前端项目 |

## 示例用法

用户: "生成截止2026年1月24日的市场复盘"

响应流程:
1. 提取日期: 2026-01-24
2. 运行 Wind 数据生成: `python generate_tables_from_wind.py --date 2026-01-24`
   - 数据范围: 2025-12-24 至 2026-01-24（完整31天）
3. 运行 JSON 转换: `python excel_to_json_converter.py`
4. 启动前端: `./node_modules/.bin/vite`（后台运行）
5. 等待5秒后使用 puppeteer 截图
6. 截图保存为: `市场复盘_2026-01-24.png`
7. 停止前端服务

## 错误处理

| 错误 | 解决方案 |
|------|----------|
| Wind未连接 | 确保 Wind 终端已登录，重新启动 Wind |
| EDB代码错误 | 检查 Wind 代码是否有效 |
| pnpm 未找到 | 使用 `./node_modules/.bin/vite` 替代 |
| 前端启动失败 | 运行 `npm install` 安装依赖 |
| puppeteer 未安装 | 运行 `cd /tmp && npm install puppeteer --no-save` |
| 截图失败 | 手动在浏览器中截图保存 |

## 辅助脚本

提供一键执行脚本（不含截图）:

```bash
/Users/fanshengxia/.claude/skills/market-review/scripts/run_market_review.sh 2026-01-24
```
