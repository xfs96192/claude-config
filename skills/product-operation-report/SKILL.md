---
name: product-operation-report
description: 为投资经理生成标准化的产品运作说明与“近期波动解释”文字。支持根据产品代码/名称与指定日期生成运作快照（年化收益率/久期/杠杆/权益仓位/权益风格分布），并在提供阶段表现数据与市场表现信息时，按固定模板输出近期净值波动解释段落；支持使用用户提供的最新持仓盈亏表覆盖默认取数。
---

# 产品运作报告生成

## 功能说明

自动生成标准化的产品运作说明文字（运作快照），以及用于解释近期产品波动的模板化文字（近期波动解释）。

### 1) 运作快照（单句）

```
截止X月X日，[产品名称]当前组合成立以来年化收益率为X.XX%，组合有效久期约X.XX年，杠杆XXX%，权益仓位X.X%左右，权益持仓风格分布为[风格1]XX%、[风格2]XX%、[风格3]XX%。
```

### 2) 近期波动解释（按模板多段）

```
截止X月X日，[产品名称]当前组合成立以来年化收益率为X.XX%，组合有效久期约X.XX年，杠杆XXX%，权益仓位X.X%左右，权益持仓风格分布为……
自YYYY年M月D日至YYYY年M月D日，产品净值累计下跌/上涨XXbp。近1周净值下跌/上涨XXbp，近1月净值下跌/上涨XXbp，主要受到……的影响。
期间，沪深300指数……；债券方面，万得短期纯债型基金指数……。
随着……，产品净值已得到一定修复。
```

## 使用方法

### 基本用法

执行 `scripts/generate_report.py` 脚本，传入产品标识和日期：

```bash
python scripts/generate_report.py <产品代码或产品名称> <日期YYYYMMDD>
```

示例：
```bash
python scripts/generate_report.py "丰利逸动6个月最短持有期日开1号增强型" "20260115"
python scripts/generate_report.py "9K706010" "20260115"
```

> 说明：以上为兼容旧用法，等价于 `snapshot` 模式。

### 运作快照（推荐显式用法）

```bash
python scripts/generate_report.py snapshot <产品代码或产品名称> <日期YYYYMMDD>
```

### 近期波动解释

```bash
python scripts/generate_report.py volatility <产品代码或产品名称> <日期YYYYMMDD> \
  --period-start <YYYYMMDD或YYYY-MM-DD> --period-end <YYYYMMDD或YYYY-MM-DD> \
  --market-text "<市场表现一句话>"
```

如果你提供了“阶段表现数据表”，脚本可自动提取区间/近1周/近1月的 bp：

```bash
python scripts/generate_report.py volatility 9K706010 20260115 \
  --stages-file /path/to/stages.xlsx \
  --period-start 20250129 --period-end 20260203 \
  --market-text "沪深300指数下跌3.42%，最大回撤6.52%；债券方面，万得短期纯债型基金指数微幅上涨3bp"
```

### 参数说明

- **产品标识**：可以使用产品代码（如 `9K706010`）或产品简称（如 `丰利逸动6个月最短持有期日开1号增强型`）
- **日期**：格式为 `YYYYMMDD` 或 `YYYY-MM-DD`

常用可选参数（两种模式都可用）：

- `--holding-file`：当你提供最新持仓盈亏表时，用它覆盖默认按日期查找的持仓数据
- `--classification-file`：指定基金分类数据文件；不传则默认取“基金分类标签”目录下最新一份
- `--equity-style-script`：权益风格占比计算脚本，已更新为 `generate_equity_style_report.py`
- `--asof-display`：只改变展示的“截止X月X日”，不影响取数（用于数据日期与话术日期不同的场景）

## 数据来源

脚本自动从以下数据源读取：

1. **产品运作概览数据**：`/Users/fanshengxia/Desktop/周报V2/数据/产品运作概览数据-母子产品/`
   - 提供年化收益率、组合久期、杠杆、权益仓位等指标

2. **持仓盈亏数据**：`/Users/fanshengxia/Desktop/周报V2/数据/周度更新数据/`
   - 提供持仓明细，用于计算权益持仓风格分布（可用 `--holding-file` 覆盖）

3. **基金分类数据**：`/Users/fanshengxia/Desktop/投资助理工作/基金分类标签/基金分类数据_2026-01.xlsx`
   - 提供基金风格分类标签（均衡、科技成长、价值、红利等）

## 输出指标

生成的报告包含以下指标：

- **成立以来年化收益率**：从产品成立至指定日期的年化收益率
- **组合有效久期**：组合的有效久期（年）
- **杠杆**：产品杠杆比例
- **权益仓位**：权益资产占比
- **权益持仓风格分布**：使用 `/Users/fanshengxia/Desktop/投资助理工作/基金分类标签/generate_equity_style_report.py` 的同口径逻辑计算（按占比从高到低排序）
- **近期波动解释所需区间表现**：可从你提供的“阶段表现数据表”提取，或手工传入 bp

## 工作流程

当用户请求生成产品运作说明时：

1. 确认用户提供的产品标识（代码或名称）和日期
2. 选择输出类型：
   - 只要快照：运行 `snapshot`
   - 解释近期波动：运行 `volatility`，并补齐 `--period-start/--period-end`、区间/近1周/近1月 bp、以及 `--market-text`
3. 执行 `generate_report.py` 脚本
4. 返回生成的文字（快照单句或波动解释多段）
4. 如果产品名称不匹配，协助用户查找正确的产品名称或代码

## 注意事项

- 产品名称需要与数据文件中的记录完全匹配（建议使用产品代码以避免名称匹配问题）
- 指定日期需要对应的数据文件存在
- 权益风格分布已切换为 `generate_equity_style_report.py` 的计算口径
- 如果找不到对应产品或日期的数据，脚本会返回错误提示

### 阶段表现数据表（可选，但用于自动提取 bp）

当使用 `--stages-file` 时，建议至少包含这些列（列名可略有差异，脚本会做常见兼容）：

- `产品代码`（可选）/ `产品简称`（至少其一）
- `阶段`（至少包含 `近1周`、`近1月`，以及与你的 `--period-start/--period-end` 对应的一行）
- `起始日期`、`截止日期`
- `净值变动bp`（或提供 `区间收益率`，脚本会换算成 bp）
