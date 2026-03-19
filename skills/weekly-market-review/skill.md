---
name: weekly-market-review
description: 端到端自动生成周度市场复盘报告。完整流程：(1)读取market_summary.txt用户材料（若为空则调用gangtise-kb获取近一周债券/权益/策略/转债研报），(2)运行iChoice EMQuantAPI脚本获取债券收益率bp变动、权益指数及申万行业周度涨跌幅、转债指数数据，输出market_data.json，(3)基于数据和材料由Claude直接撰写与output文件夹风格完全一致的周报，(4)保存至output/weekly_review_YYYY-MM-DD.md。当用户说「周度市场总结」「市场复盘」「生成本周市场回顾」「市场回顾」「周报」「复盘」时触发。
---

# 周度市场复盘

## 工作目录

`/Users/fanshengxia/Desktop/市场复盘/周报市场复盘`

## 执行流程

### 步骤 1：确定报告日期

使用今日日期（`YYYY-MM-DD`）作为报告日期和输出文件名。

### 步骤 2：读取市场材料

读取 `market_summary.txt`：

- **有内容** → 直接使用
- **为空或不存在** → 运行 gangtise-kb 查询近一周研报（资源类型 10=券商研报, 40=首席观点）：

```bash
cd /Users/fanshengxia/.claude/skills/gangtise-kb
python3 scripts/query_kb.py "债券市场 利率债 信用债" --type 10,40 --days 7 --top 5
python3 scripts/query_kb.py "权益市场 A股 行业轮动" --type 10,40 --days 7 --top 5
python3 scripts/query_kb.py "可转债市场" --type 10,40 --days 7 --top 3
python3 scripts/query_kb.py "宏观策略 货币政策 资金面 债市展望" --type 10,40 --days 7 --top 3
```

### 步骤 3：获取市场数据（iChoice）

运行数据获取脚本（**必须设置 timeout=300000**，首次登录耗时2-3分钟）：

```bash
python3 /Users/fanshengxia/.claude/skills/weekly-market-review/scripts/fetch_market_data.py
```

脚本输出：`market_data.json`（在工作目录）。

**若部分债券代码报错（ErrorCode != 0）**：
1. 读取 `/Users/fanshengxia/Desktop/ichoice_data/ichoice/数据指标.xlsx` 查找正确代码
2. 更新脚本中 `BOND_EDB` 字典的对应代码
3. 重新运行脚本

脚本末尾会打印各指标的值和行业涨跌幅排名，可用于验证数据。

### 步骤 4：撰写周报

读取 `market_data.json` 和市场材料，按 [references/output_format.md](references/output_format.md) 的格式撰写三大板块。

**数据准确性要求（严格执行）：**
- 所有数值必须来自 `market_data.json`，不得估算或编造
- 若某指标数据缺失，用"数据暂缺"代替，不可使用假设值
- 债券 bp 变动：保留两位小数，加符号（如 `-3.10bp`）
- 权益涨跌幅：保留两位小数，加符号和百分号（如 `+1.13%`）
- 行业只列名称不列具体涨跌幅数字

### 步骤 5：保存输出

保存至工作目录下：
```
output/weekly_review_YYYY-MM-DD.md
```
