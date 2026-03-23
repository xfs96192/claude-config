---
name: portfolio-backtest skill 路径与使用说明
description: 记录个人基金持仓回测分析skill的位置、触发方式和输出路径
type: reference
---

## Skill 位置

`/Users/fanshengxia/.claude/skills/portfolio-backtest/`
- `SKILL.md` — 主流程指令
- `scripts/generate_outputs.py` — 输出生成脚本（图表、Excel、Markdown）

## 触发词

"帮我分析持仓"、"更新持仓回测"、"我更新了持仓"、"帮我做组合回测"，或用户提供基金E账户Excel文件时

## 输入

基金E账户App 导出的 Excel 文件，格式固定（Sheet="持有信息"，第5行为表头）

## 输出目录

`/Users/fanshengxia/Desktop/个人事项/资产/portfolio_analysis/`
- `portfolio_analysis_chart.png` — 综合图表
- `portfolio_analysis_report.xlsx` — Excel底表（4个Sheet）
- `portfolio_analysis_report.md` — Markdown报告
- `nav_data/` — 各基金复权净值CSV
- `holdings_classified.csv` — 含分类的持仓底表

## 上次运行记录

- 持仓日期：2026-03-18
- 基金数量：46只（合并同代码不同账户后）
- 总市值：¥430,767 元
- 回测结果：年化8.18%，最大回撤-13.64%，夏普0.73

## 资产分类规则

已编码在 SKILL.md 中，大类：货币基金、纯债、固收+、权益-A股、权益-港股、权益-美股
