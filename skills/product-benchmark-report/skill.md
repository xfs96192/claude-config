---
name: product-benchmark-report
description: 生成单产品净值走势与业绩基准对比报告。输出文件夹包含：Markdown报告(含走势图+业绩指标表)、Excel净值对比数据、计算脚本。当用户说"生成XX产品的业绩评价"、"统计XX的净值和基准对比"、"帮我做XX的业绩报告"时触发。
---

# 单产品业绩基准对比报告生成技能

## 概述

生成指定产品的净值走势 vs 业绩基准对比分析报告，最终输出一个以
`{产品代码}_{产品名称}_{截止日期}` 命名的文件夹，内含：
- `{产品名称}_业绩评价_{日期}.md`  —— 主报告（含图表 + 业绩指标表）
- `{产品名称}_净值对比图_{日期}.png` —— 走势对比图
- `{产品名称}_净值对比数据_{日期}.xlsx` —— 净值原始数据（不写入Markdown）
- `calculate_{产品代码}.py` —— 计算脚本副本

---

## 触发条件

用户发来以下类型的消息：
- "帮我生成 9K717120 的业绩评价"
- "统计资源优势3M 的净值和基准对比"
- 同时附带或提到一个净值数据xlsx文件（可选）

---

## 执行步骤

### Step 1：确认产品代码

从用户消息中提取**产品代码**（如 `9K717120`）。

如果用户只说产品简称（如"资源优势3M"），则：
1. 读取 `/Users/fanshengxia/Desktop/周报V2/数据/指数业绩基准数据.xlsx` Sheet1
2. 在 `产品简称` 列中模糊匹配，确认产品代码
3. 若匹配到多个，列出让用户确认

---

### Step 2：确认净值数据来源

**优先级（从高到低）：**

1. **用户在当前对话中提供了净值文件** → 使用该文件路径
   - 文件要求：xlsx，第一个Sheet含两列：日期、单位净值

2. **用户未提供文件** → 使用 parquet 缓存 + 最新周度文件自动拼接
   - 缓存路径：`/Users/fanshengxia/Desktop/周报V2/数据/.nav_cache/nav_master_data.parquet`
   - 最新周度路径：`/Users/fanshengxia/Desktop/周报V2/数据/产品净值数据/产品运作情况表-补充精简*.xlsx`

---

### Step 3：运行生成脚本

```bash
python3 /Users/fanshengxia/.claude/skills/product-benchmark-report/scripts/generate_report.py \
  <产品代码> [净值文件路径]
```

**示例（有文件）：**
```bash
python3 /Users/fanshengxia/.claude/skills/product-benchmark-report/scripts/generate_report.py \
  9K717120 /Users/fanshengxia/Downloads/净值走势图2026-03-04.xlsx
```

**示例（无文件，使用缓存）：**
```bash
python3 /Users/fanshengxia/.claude/skills/product-benchmark-report/scripts/generate_report.py \
  9K717120
```

脚本会自动：
- 加载净值数据
- 从 `指数业绩基准数据.xlsx` 读取业绩基准配置
- 通过 Wind（系统Python `python3`）获取指数数据
- 计算各期间年化收益率和最大回撤
- 生成图表、Excel、Markdown

---

### Step 4：验证输出

脚本执行后，确认以下文件存在：
```
/Users/fanshengxia/Desktop/业绩评价/单个产品及业绩基准对比表现/
└── {产品代码}_{产品名称}_{日期}/
    ├── {产品名称}_业绩评价_{日期}.md       ← 主报告
    ├── {产品名称}_净值对比图_{日期}.png
    ├── {产品名称}_净值对比数据_{日期}.xlsx
    └── calculate_{产品代码}.py
```

---

### Step 5：向用户汇报结果

向用户展示：
1. 输出文件夹路径
2. 各期业绩指标摘要（直接列在回复中）：

| 指标 | 本产品 | 业绩基准 |
|------|--------|---------|
| 近3月年化收益率 | X.XX% | X.XX% |
| 近6月年化收益率 | X.XX% | X.XX% |
| 近1年年化收益率 | X.XX% | X.XX% |
| 成立以来年化收益率 | X.XX% | X.XX% |
| 超额年化收益 | X.XX% | — |
| 最大回撤 | X.XX% | — |

---

## 关键业绩计算规则

### 年化收益率公式

```
年化收益率 = (期末净值 / 期初净值 - 1) / 运作天数 × 365
```

**运作天数取法（与PAS/周报系统口径一致，固定自然日）：**
- 近1月：`end_date - Timedelta(days=30)`  → 30 天
- 近3月：`end_date - Timedelta(days=90)`  → 90 天
- 近6月：`end_date - Timedelta(days=180)` → 180 天
- 近1年：`end_date - Timedelta(days=365)` → 365 天
- 今年以来：自上一年 12-31 起至 end_date
- 成立以来：**总净值观测行数**（非日历天数，差1天）

> 注：早期版本曾用 `DateOffset(months=N)`（月对齐），会导致 30/31 天波动，已统一改为固定 N 自然日，与 utils.py:37 的 PAS 周报口径对齐。

### 业绩基准构建

1. 从 `指数业绩基准数据.xlsx` 读取各指数Wind代码和权重
2. 活期存款年化利率默认 **1.35%**
3. 基准净值初始值 = 产品第一天单位净值（通常为1.0）
4. 日收益率 = Σ(指数日收益率 × 权重) + 活期日利率 × 活期权重

### 超额收益

```
超额年化收益 = 产品成立以来年化 - 基准成立以来年化
```

---

## 错误处理

| 问题 | 处理方式 |
|------|---------|
| 产品代码在基准配置中找不到 | 提示用户检查产品代码，列出基准配置文件中所有产品 |
| Wind 未连接 | 提示用户启动 Wind 客户端 |
| 缓存中无该产品净值 | 提示用户提供净值文件 |
| 净值数据过短（无法计算某期指标） | 对应字段显示 N/A |

---

## 文件结构参考

```
技能脚本:
/Users/fanshengxia/.claude/skills/product-benchmark-report/
├── skill.md
└── scripts/
    └── generate_report.py

输出位置:
/Users/fanshengxia/Desktop/业绩评价/单个产品及业绩基准对比表现/
└── {product_code}_{product_name}_{YYYYMMDD}/
```
