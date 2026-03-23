---
name: portfolio-backtest
description: 个人公募基金持仓组合回测分析工具。当用户提供基金E账户App导出的持仓Excel文件，或说"帮我分析持仓"、"更新持仓回测"、"我更新了持仓"、"帮我做组合回测"等时，立即使用此技能。自动读取持仓Excel、分类大类资产、通过iChoice获取复权净值、构建加权组合并回测近10年业绩，输出净值走势图、Excel分析底表和Markdown报告。
---

# 个人基金持仓组合回测分析

用户提供最新的基金E账户持仓Excel文件时，执行完整的回测分析流程并输出三类结果文件。

## 输出目录

所有输出保存至：`/Users/fanshengxia/Desktop/个人事项/资产/portfolio_analysis/`

## 执行流程

### Step 1：读取并解析持仓Excel

基金E账户App导出的Excel格式固定：
- Sheet名：`持有信息`
- 从第5行（index=4）开始为表头：序号、基金代码、基金名称、份额类别、基金管理人、基金账户、销售机构、交易账户、持有份额、份额日期、基金净值、净值日期、资产情况（结算币种）、结算币种、分红方式
- 数据从第6行（index=5）开始
- **关键字段**：基金代码（col 1）、基金名称（col 2）、资产情况（col 12，即日终持仓金额）

用 pandas 读取，注意：
- 同一基金代码可能出现在多个账户（蚂蚁/中信），需按代码合并市值求和
- 市值极小（<1元）的基金可保留但权重忽略不计

```python
import pandas as pd
df_raw = pd.read_excel(excel_path, sheet_name="持有信息", header=None)
# 找到表头行（含"基金代码"的行）
header_row = df_raw[df_raw.apply(lambda r: r.astype(str).str.contains("基金代码").any(), axis=1)].index[0]
df = pd.read_excel(excel_path, sheet_name="持有信息", header=header_row)
df = df.dropna(subset=["基金代码"])
df = df[df["基金代码"].astype(str).str.match(r"^\d{6}$")]
df["market_value"] = pd.to_numeric(df.iloc[:, 12], errors="coerce")
holdings = df.groupby("基金代码")["market_value"].sum().reset_index()
holdings.columns = ["code", "market_value"]
holdings = holdings[holdings["market_value"] > 0]
```

### Step 2：资产分类

根据基金代码和名称对每只基金进行大类分类。分类规则如下：

| 大类 | 判断依据 |
|------|--------|
| 货币基金 | 名称含"货币"、"天天红"、"增金宝" |
| 纯债 | 名称含"债券"且不含"混合"、"股票"，且不是二级债基 |
| 固收+ | 名称含"稳健"、"安心"、"稳泰"，或债券型基金中含权益仓位，或偏债混合 |
| 权益-A股 | 名称含"混合"/"股票"且无"QDII"/"港股"/"纳斯达克"/"纳指"/"海外"等字样 |
| 权益-港股 | 名称含"港股"/"恒生"/"港股通"/"海外中国互联网"/"亚洲精选" |
| 权益-美股 | 名称含"纳斯达克"/"纳指"/"美国"，QDII基金 |

**重要**：分类有歧义时，优先参考基金名称关键词，宁可归为固收+也不要误归为纯债（因为很多"双利"、"回报"类债基实际持有股票）。

将分类结果保存为 DataFrame，列：`code`, `name`, `market_value`, `weight`, `asset_class`, `sub_class`

### Step 3：通过 iChoice 获取复权净值数据

使用 `ichoice-data` skill 的标准模板。**必须将所有逻辑写在单个脚本中，timeout=300000**。

```python
# 代码格式：XXXXXX.OF
# 字段：ADJUSTEDNAV（复权净值，已含分红再投资，最适合回测）
# 回测区间：start_date = "2016-XX-XX"（持仓日期前10年），end_date = 持仓日期

data = c.csd(f"{code}.OF", "ADJUSTEDNAV", start_date, end_date, "Ispandas=1")
```

- 逐只基金获取，避免批量超时
- 保存至 `nav_data/{code}_nav.csv`（列：date, nav）
- 若 ADJUSTEDNAV 失败，fallback 至 UNITNAV

### Step 4：构建组合净值并回测

**权重处理**：以持仓市值为固定权重；对于成立时间短于10年的基金，在成立前权重归零并将其权重按比例分配至其余有数据的基金。

```python
# 构建净值面板，前向填充
nav_panel = pd.DataFrame(index=date_range)
for code, df in nav_dict.items():
    nav_panel[code] = df.set_index("date")["nav"].reindex(date_range)
nav_panel = nav_panel.ffill()

# 按日计算时变权重加权收益率
ret_panel = nav_panel.pct_change()
for code in ret_panel.columns:
    ret_panel.loc[ret_panel.index < fund_start_dates[code], code] = np.nan

portfolio_ret = []
for i in range(len(ret_panel)):
    row = ret_panel.iloc[i].values
    valid = ~np.isnan(row)
    if valid.sum() == 0:
        portfolio_ret.append(0.0)
    else:
        w = base_weights * valid
        w = w / w.sum()
        portfolio_ret.append(np.dot(w, np.where(valid, row, 0)))

portfolio_nav = (1 + pd.Series(portfolio_ret, index=ret_panel.index)).cumprod()
portfolio_nav.iloc[0] = 1.0
```

**业绩指标**（无风险利率 rf=1.5%）：
- 累计收益率、年化收益率、年化波动率（252日）
- 夏普比率、最大回撤（及区间）、卡玛比率、月度胜率
- 年度收益率逐年列示
- 分段指标：近1年、近3年、近5年、近10年、今年以来

### Step 5：输出结果

使用 `scripts/generate_outputs.py` 脚本生成三类输出。直接调用：

```bash
python3 /Users/fanshengxia/.claude/skills/portfolio-backtest/scripts/generate_outputs.py \
    --holdings <holdings_csv> \
    --nav_dir <nav_data_dir> \
    --output_dir <output_dir> \
    --start_date <YYYY-MM-DD> \
    --end_date <YYYY-MM-DD>
```

**输出文件**：
1. `portfolio_analysis_chart.png` — 综合图表（4行3列布局）：
   - 组合净值走势（含最大回撤阴影区域、关键指标文字框）
   - 年度收益柱状图（正负不同颜色）
   - 历史回撤序列图
   - 大类资产饼图
   - 细分风格横条图
   - 前15大持仓权重柱状图

2. `portfolio_analysis_report.xlsx` — 4个Sheet：
   - `持仓明细`：所有基金的代码、名称、分类、市值、权重
   - `大类资产分析`：大类汇总 + 细分风格汇总（双列布局）
   - `组合业绩分析`：综合指标、分期段指标、年度收益率
   - `组合净值序列`：月度净值及累计收益率

3. `portfolio_analysis_report.md` — 完整Markdown分析报告，包含：
   - 大类资产配置分析（含核心观察文字）
   - 细分风格分析
   - 前10大持仓列表
   - 回测说明、综合指标、分期段指标、年度收益
   - 收益风险特征综合分析（亮点+风险点+优化建议）

## 图表配色规范

```python
COLORS = {
    "固收+": "#2196F3",
    "纯债": "#4CAF50",
    "货币基金": "#9E9E9E",
    "权益-A股": "#F44336",
    "权益-港股": "#FF9800",
    "权益-美股": "#9C27B0",
}
```

中文字体设置：
```python
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'STHeiti', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
```

## iChoice 环境设置

每个脚本开头必须调用 setup_emquant()，然后登录：
```python
result = c.start("UserName=xylczh0181,Password=ef465509,ForceLogin=1")
```
详见 `ichoice-data` skill 的完整模板。

## 当用户说"更新持仓"时

1. 询问新的持仓Excel文件路径（或用户已在消息中提供文件路径）
2. 自动检测持仓日期（从Excel文件名或数据中提取）
3. 将 start_date 设为持仓日期前10年
4. 重新执行完整流程（Steps 1-5）
5. 覆盖输出目录中的旧文件

## 注意事项

- 同一基金代码在多账户出现时合并市值，只获取一次净值数据
- 货币基金净值恒为1，ADJUSTEDNAV可能是累计收益体现在规模上，直接用1处理其收益贡献
- QDII基金可能有T+1净值延迟，用 ffill() 处理即可
- 市值权重极小（<0.1%）的基金对组合影响微乎其微，但仍保留
- 生成报告时注意保护持仓人隐私（姓名脱敏为"夏**"已在源数据中处理）
