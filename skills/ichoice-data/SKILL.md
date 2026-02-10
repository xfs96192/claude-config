---
name: ichoice-data
description: "iChoice/EMQuantAPI 金融市场数据查询工具。通过东方财富Choice量化接口(EMQuantAPI Python SDK)获取中国及全球市场数据，包括：(1)宏观经济数据(GDP/CPI/PMI/社融/M2等)，(2)债券收益率曲线(国债/国开/中票/城投/银行债各期限各评级)，(3)股票指数行情(A股/海外/申万行业)及估值(PE)，(4)资金利率(DR/SHIBOR/IRS)，(5)外汇汇率，(6)商品期货价格，(7)可转债指数，(8)指数成分股，(9)交易日历。当用户需要获取市场数据、宏观数据、利率数据、汇率数据、指数行情、债券收益率、商品价格等金融数据时自动触发。触发关键词：市场数据、宏观数据、债券收益率、利率、汇率、股票行情、指数数据、PMI、GDP、CPI、国债、国开债、信用利差、收益率曲线、SHIBOR、DR007、iChoice、Choice数据、EMQuant。"
---

# iChoice Data Query

通过 EMQuantAPI (Choice量化接口) 获取金融市场数据。

## Environment

- SDK路径: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`
- 账号: `xylczh0181` / 密码: `ef465509`
- 指标映射表: `/Users/fanshengxia/Desktop/ichoice/数据指标.xlsx`

## Critical: Execution Requirements

**iChoice API 登录和数据获取耗时较长，必须遵循以下规则：**

1. **Bash timeout 必须设置 `timeout=300000`（5分钟）或更长**。首次登录需下载配置文件（ChoiceToHQ.xml等），总耗时可达2-3分钟。
2. **将所有逻辑写在单个 Python 脚本中运行**，使用 `python3 << 'EOF' ... EOF` 格式。不要分步调用。
3. **多代码长周期数据分开获取**：对多个证券代码获取长时间序列时（如10年），逐个代码调用 `c.csd()`，避免单次请求过大。
4. **始终使用 `Ispandas=1`** 返回 DataFrame，便于处理。
5. **始终在 finally 块中调用 `c.stop()`** 确保退出。

## Standard Script Template

```python
import sys
sys.path.insert(0, '/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3')
from EmQuantAPI import c
import pandas as pd

# Login
result = c.start("UserName=xylczh0181,Password=ef465509,ForceLogin=1")
if result.ErrorCode != 0:
    print(f"Login failed: {result.ErrorMsg}")
    exit()
print("Login OK")

try:
    # === Fetch data here ===
    data = c.csd("000300.SH", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1")
    if isinstance(data, pd.DataFrame):
        print(data)
    else:
        print(f"Error: {data.ErrorCode}, {data.ErrorMsg}")
finally:
    c.stop()
    print("Logout done")
```

## Data Query Patterns

### Pattern 1: EDB (宏观/债券收益率/EDB指标)

用于 EMM/EMG/EMI/E 开头的指标代码。覆盖宏观经济、债券收益率曲线、部分资金利率。

```python
# 单指标
data = c.edb("EMM00087117", "Ispandas=1")

# 多指标+日期范围
data = c.edb("EMM00072301,EMM00073348", "StartDate=2024-01-01,EndDate=2025-01-31,Ispandas=1")

# 仅最新值
data = c.edb("E1000180", "IsLatest=1,Ispandas=1")
```

### Pattern 2: CSD Time Series (行情序列)

用于带交易所后缀的证券代码（.SH/.SZ/.GI/.FX/.IB/.SWI等）。

```python
# 单代码
data = c.csd("000300.SH", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1")

# 多代码短周期可以合并
data = c.csd("000300.SH,000905.SH", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1")

# 多代码长周期（>1年）：逐个获取，避免超时
for code in ["000300.SH", "000905.SH"]:
    data = c.csd(code, "CLOSE", "2016-01-01", "2026-01-31", "Ispandas=1")
```

常用字段: CLOSE, OPEN, HIGH, LOW, VOLUME, AMOUNT, PETTM

### Pattern 3: CSS Cross-Section (截面数据)

```python
data = c.css("000001.SZ,600519.SH", "CLOSE,VOLUME", "TradeDate=2025-01-20,Ispandas=1")
```

### Pattern 4: Sector Components (指数成分)

```python
data = c.sector("000300.SH", "2025-01-20", "Ispandas=1")
```

### Pattern 5: Trading Calendar

```python
dates = c.tradedates("2025-01-01", "2025-01-31", "")
# dates.Data 返回交易日列表

offset = c.getdate("20250120", -3, "Market=CNSESH")
# 往前推3个交易日
```

## Indicator Code Lookup

| Data Type | Function | Code Format | Example |
|-----------|----------|-------------|---------|
| 宏观经济 | `c.edb()` | EMM/EMG/EMI+number | EMM00087117 (GDP) |
| 债券收益率 | `c.edb()` | E/EMM+number | E1000180 (国债10Y) |
| A股指数行情 | `c.csd()` | code.SH/SZ | 000300.SH (沪深300) |
| 海外指数 | `c.csd()` | code.GI | SPX.GI (标普500) |
| 申万行业 | `c.csd()` | code.SWI | 801780.SWI (银行) |
| 外汇汇率 | `c.csd()` | code.FX/IB | USDCNY.IB |
| 资金利率(市场) | `c.csd()` | code.IB/IR | DR007.IB, Shibor3M.IR |
| 资金利率(EDB) | `c.edb()` | E/EMM+number | E1715081 (7天逆回购) |
| 商品期货 | `c.csd()` | code.SHF/DCE/INE | AU0.SHF (沪金) |
| 商品(EDB) | `c.edb()` | EMI/EMM+number | EMI01618427 (原油) |
| 国债期货 | `c.csd()` | TSM/TFM/TM.CFE | TM.CFE (10Y国债期货) |
| 债券指数 | `c.csd()` | code.CS/CSI/EI | CBA00121.CS |
| 指数成分 | `c.sector()` | code.SH | 000300.SH |

### Quick Reference: Common Indicators

**宏观:**
- GDP同比: EMM01526652 (现价), EMM00000012 (不变价)
- CPI同比: EMM00072301 | PPI同比: EMM00073348
- PMI: EMM00121996 | 工业增加值同比: EMM00008445
- M2同比: EMM00087086 | 社融当月: EMM00088684
- MLF1年: EMM00650875

**债券收益率(EDB):**
- 国债10Y: E1000180 | 国债5Y: EMM00166462 | 国债1Y: E1000172
- 国开10Y: E1701714 | 国开5Y: E1701710 | 国开3Y: E1701708
- 中票AAA 3Y: E1000590 | 中票AA+ 3Y: E1000621
- 城投AAA 3Y: E1702579 | 城投AA 3Y: E1702615
- 同业存单AAA 1Y: E1706149
- 二级资本债AAA- 3Y: E1705908

**指数行情(CSD, CLOSE):**
- 沪深300: 000300.SH | 中证500: 000905.SH | 中证1000: 000852.SH
- 上证50: 000016.SH | 创业板指: 399006.SZ | 万得全A: 800000.EI
- 标普500: SPX.GI | 纳斯达克: IXIC.GI | 日经225: N225.GI

**资金利率(CSD, CLOSE):**
- DR001: DR001.IB | DR007: DR007.IB
- SHIBOR3M: Shibor3M.IR | FR007 IRS 1Y: FR007_1Y.IB

**外汇(CSD, CLOSE):**
- 美元指数: USDX.FX | 美元兑人民币: USDCNY.IB | 离岸人民币: USDCNH.FX

**商品(CSD, CLOSE):**
- 沪金: AU0.SHF | 原油: scm.INE | 螺纹钢: RB0.SHF | 豆粕: M0.DCE

**For full 453 indicator code mappings:** Read [references/indicator_codes.md](references/indicator_codes.md)

**For complete API function reference:** Read [references/api_reference.md](references/api_reference.md)

## Chart Generation Notes

生成中文图表时设置字体：
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False
```

## Key Notes

- Wind `.SI` → Choice `.SWI` (申万行业)
- Wind `881001.WI` (万得全A) → Choice `800000.EI`
- 部分指标无Choice对应码：南华指数, USDCNYM.IB, 螺纹钢期货Wind码
- `Ispandas=1` 返回 DataFrame，否则返回 EmQuantData 对象
- Rate limits: css/csd 700次/分钟, edb 单次最多100个指标
- csd 返回的 DataFrame 中 DATES 列为字符串格式 "YYYY/MM/DD"，需 `pd.to_datetime()` 转换
- 务必在脚本结束时调用 `c.stop()` 释放连接
