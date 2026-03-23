---
name: caifubu-equity-performance
description: 委外产品及持仓权益基金业绩分析工具。当用户要分析委外资管产品的净值走势、涨幅、最大回撤等业绩指标，或分析委外产品持仓的权益基金加权组合表现，并生成汇总Excel报告时立即使用此技能。触发关键词：委外产品分析、委外净值走势、委外业绩指标、权益基金持仓分析、持仓加权组合、委外涨幅回撤、持仓盈亏明细、委外分析excel。即使用户只说"帮我分析委外产品"或"计算一下持仓权益基金的组合表现"也应触发此技能。
---

# 委外产品及持仓权益基金业绩分析

## 功能概述

本技能完整实现以下分析流程：
1. 从净值走势 Excel 读取委外产品 NAV 序列，计算业绩和风险指标
2. 从持仓盈亏明细表筛选指定产品的权益基金持仓
3. 通过 iChoice API（ichoice-data skill）获取基金累计净值历史数据
4. 按日终市值加权构建组合净值序列，计算相同指标
5. 输出格式化 Excel 报告（汇总表 + 两个持仓明细表）

## 标准输入数据

| 文件 | 说明 |
|------|------|
| `委外分析-净值走势*.xlsx` | 委外产品净值时间序列，列为产品简称，行为日期，初始值通常为 1 |
| `持仓盈亏明细列表_YYYYMMDD.xlsx` | 产品全量持仓底表，包含 `产品代码`、`新版资产大类`、`新版资产小类`、`外部代码`、`日终市值(元)-产品法估值` 等字段 |

## 权益基金筛选条件

从持仓表中同时满足以下条件的行视为权益基金持仓：
- `新版资产大类` == `'公募基金'`
- `新版资产小类` in：`['被动指数型基金', '偏股混合型基金', '普通股票型基金', '国际(QDII)被动指数型股票基金']`

## 核心指标定义

所有涨幅和回撤均为**非年化**数据。

| 指标 | 计算方式 |
|------|---------|
| 成立以来涨幅 | `(最新净值 / 成立日净值) - 1`，截止最新数据日 |
| 2025年度涨幅 | `(2025-12-31净值 / 2024-12-31净值) - 1`；若产品在2025年内成立则以成立日为起点 |
| 今年以来涨幅 | `(最新净值 / 2025-12-31净值) - 1`；即2026年初至今 |
| 成立以来最大回撤 | 在全区间内：`min((净值_t - max净值_{0..t}) / max净值_{0..t})` |
| 2025年度最大回撤 | 同上，区间为2025年，以2024-12-31净值为起点 |
| 今年以来最大回撤 | 同上，区间为2026年初至最新，以2025-12-31净值为起点 |

## 加权组合构建方法

1. 以产品成立日为基准日，将每只基金 NAV rebase 到 1.0
2. 权重 = 该基金日终市值(元)-产品法估值 / 该产品全部权益基金总市值（从持仓底表当日数据获取）
3. 对于未能获取 NAV 的基金，重新归一化其余基金权重
4. 组合净值 = `∑(各基金rebase净值 × 归一化权重)`，按日期前向填充处理节假日缺失

## 执行流程

### Step 1：确认输入

向用户确认或从对话历史获取：
- 净值走势 Excel 文件路径
- 持仓盈亏明细 Excel 文件路径
- 需要分析权益基金组合的产品代码列表（如 `9K717120`、`9K717310`）
- 各产品成立日期（用于权益组合计算的起点）
- 输出 Excel 文件保存路径（默认与输入文件同目录）

### Step 2：读取委外产品净值并计算指标

```python
import pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore')

nav_df = pd.read_excel('<净值走势文件路径>', sheet_name=0)
nav_df['日期'] = pd.to_datetime(nav_df['日期'])
nav_df.set_index('日期', inplace=True)

def max_drawdown(arr):
    arr = np.array(arr, dtype=float)
    if len(arr) < 2: return np.nan
    peak = np.maximum.accumulate(arr)
    return ((arr - peak) / peak).min()

def calc_metrics(series, inception_date=None):
    s = series.copy()
    s = s[s != '--']
    s = pd.to_numeric(s, errors='coerce').dropna().sort_index()
    if inception_date:
        s = s[s.index >= pd.Timestamp(inception_date)]
    if len(s) < 2:
        return {k: np.nan for k in METRIC_COLS}

    v_first, v_last = s.iloc[0], s.iloc[-1]
    ret_inception = (v_last / v_first) - 1
    mdd_inception = max_drawdown(s.values)

    # 2025年度
    s_2024e = s[s.index < '2025-01-01']
    s_2025  = s[(s.index >= '2025-01-01') & (s.index <= '2025-12-31')]
    if len(s_2024e) > 0 and len(s_2025) > 0:
        ret_2025 = (s_2025.iloc[-1] / s_2024e.iloc[-1]) - 1
        mdd_2025 = max_drawdown(pd.concat([
            pd.Series([s_2024e.iloc[-1]], index=[s_2024e.index[-1]]), s_2025]).values)
    elif len(s_2025) > 0:
        ret_2025 = (s_2025.iloc[-1] / s_2025.iloc[0]) - 1
        mdd_2025 = max_drawdown(s_2025.values)
    else:
        ret_2025 = mdd_2025 = np.nan

    # 今年以来 (2026 YTD)
    s_2025e = s[s.index < '2026-01-01']
    s_2026  = s[s.index >= '2026-01-01']
    if len(s_2025e) > 0 and len(s_2026) > 0:
        ret_ytd = (s_2026.iloc[-1] / s_2025e.iloc[-1]) - 1
        mdd_ytd = max_drawdown(pd.concat([
            pd.Series([s_2025e.iloc[-1]], index=[s_2025e.index[-1]]), s_2026]).values)
    elif len(s_2026) > 0:
        ret_ytd = (s_2026.iloc[-1] / s_2026.iloc[0]) - 1
        mdd_ytd = max_drawdown(s_2026.values)
    else:
        ret_ytd = mdd_ytd = np.nan

    return {'成立以来涨幅': ret_inception, '2025年度涨幅': ret_2025, '今年以来涨幅': ret_ytd,
            '成立以来最大回撤': mdd_inception, '2025年度最大回撤': mdd_2025, '今年以来最大回撤': mdd_ytd}

METRIC_COLS = ['成立以来涨幅', '2025年度涨幅', '今年以来涨幅', '成立以来最大回撤', '2025年度最大回撤', '今年以来最大回撤']
```

### Step 3：从持仓表筛选权益基金

```python
holdings_df = pd.read_excel('<持仓盈亏明细文件路径>', sheet_name='Sheet1')

equity_cats = ['被动指数型基金', '偏股混合型基金', '普通股票型基金', '国际(QDII)被动指数型股票基金']

def get_equity_holdings(product_code):
    df = holdings_df[holdings_df['产品代码'] == product_code]
    eq = df[(df['新版资产大类'] == '公募基金') & (df['新版资产小类'].isin(equity_cats))].copy()
    eq = eq[['外部代码', '资产简称', '新版资产小类', '日终市值(元)-产品法估值']].dropna(subset=['外部代码', '日终市值(元)-产品法估值'])
    total_mv = eq['日终市值(元)-产品法估值'].sum()
    eq['weight'] = eq['日终市值(元)-产品法估值'] / total_mv
    return eq
```

### Step 4：通过 iChoice 获取基金累计净值

使用 `ichoice-data` skill 的标准模板登录，字段用 `ACCUMULATEDNAV`（累计净值）：

```python
# 查询起始日期取所有产品成立日中最早者往前推数天
data = c.csd(fund_code, "ACCUMULATEDNAV", start_date, end_date, "Ispandas=1")
# 解析
data['DATES'] = pd.to_datetime(data['DATES'], format='%Y/%m/%d')
series = data.set_index('DATES')['ACCUMULATEDNAV'].dropna()
```

注意：设置 `timeout=300000` 以应对 iChoice 登录和批量查询耗时。

### Step 5：构建加权组合净值序列

```python
def build_weighted_portfolio(holdings_df, fund_nav_dict, inception_date_str):
    inception_date = pd.Timestamp(inception_date_str)
    all_dates, fund_series = set(), {}
    for _, row in holdings_df.iterrows():
        code = row['外部代码']
        if code in fund_nav_dict:
            s = fund_nav_dict[code][fund_nav_dict[code].index >= inception_date]
            if len(s) > 0:
                fund_series[code] = (s, row['weight'])
                all_dates.update(s.index.tolist())
    if not all_dates:
        return pd.Series(dtype=float)
    date_index = pd.DatetimeIndex(sorted(all_dates))
    rebase, valid_w = {}, {}
    for code, (s, w) in fund_series.items():
        rebase[code] = s.reindex(date_index, method='ffill') / s.iloc[0]
        valid_w[code] = w
    total_w = sum(valid_w.values())
    portfolio = pd.Series(0.0, index=date_index)
    for code in rebase:
        portfolio += rebase[code] * (valid_w[code] / total_w)
    return portfolio
```

### Step 6：生成 Excel 报告

使用 `openpyxl` 生成三个 Sheet：

1. **汇总结果表**：所有委外产品 + 权益基金加权组合的6项指标，含分组标题行（业绩指标/风险指标）
2. **{产品代码}-权益持仓明细**：每个被分析产品的权益基金明细（基金代码、名称、小类、日终市值、权重、成立以来涨幅）

#### 格式规范
- 表头：深蓝底白字（`#1F4E79`），中蓝子表头（`#2E75B6`）
- 正涨幅：深绿色加粗（`#375623`），负涨幅/回撤：红色加粗（`#C00000`）
- 隔行填充浅蓝（`#DEEAF1`）
- 数字格式：`'0.00%;[Red]-0.00%;"-"'`（百分比，0显示为"-"）
- 固定首行：`freeze_panes = 'D5'`（汇总表）

详见 `references/excel_template.md` 中的完整格式代码。

## 关键注意事项

1. **2025年度回撤的特殊情况**：若产品成立于2025年内，则"2025年度最大回撤"与"成立以来最大回撤"计算区间相同（均从成立日起），因此数值可能相等，这是正常的。

2. **iChoice ACCUMULATEDNAV**：同时适用于 ETF（如 `515180.SH`）和普通开放式基金（如 `011981.OF`），涵盖分红再投资，比 CLOSE 价格更准确。

3. **持仓权重为截面快照**：当前权重来自持仓底表的单日数据，假设历史持仓比例固定，属简化处理。

4. **日期处理**：iChoice 返回的 DATES 列格式为 `'YYYY/MM/DD'` 字符串，需 `pd.to_datetime(df['DATES'], format='%Y/%m/%d')` 转换。

5. **今年以来** vs **2025年度**：当前年份（2026年）的"今年以来"是从2026-01-01起算；"2025年度"是2025全年（2025-01-01至2025-12-31）。

## 完整脚本参考

见 `scripts/run_analysis.py`，包含从数据读取到 Excel 输出的端到端可运行脚本模板。
