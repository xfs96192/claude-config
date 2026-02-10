---
name: ichoice-data
description: "iChoice/EMQuantAPI 金融市场数据查询工具。通过东方财富Choice量化接口(EMQuantAPI Python SDK)获取中国及全球市场数据，包括：(1)宏观经济数据(GDP/CPI/PMI/社融/M2等)，(2)债券收益率曲线(国债/国开/中票/城投/银行债各期限各评级)，(3)股票指数行情(A股/海外/申万行业)及估值(PE)，(4)资金利率(DR/SHIBOR/IRS)，(5)外汇汇率，(6)商品期货价格，(7)可转债指数，(8)指数成分股，(9)交易日历。当用户需要获取市场数据、宏观数据、利率数据、汇率数据、指数行情、债券收益率、商品价格等金融数据时自动触发。触发关键词：市场数据、宏观数据、债券收益率、利率、汇率、股票行情、指数数据、PMI、GDP、CPI、国债、国开债、信用利差、收益率曲线、SHIBOR、DR007、iChoice、Choice数据、EMQuant。"
---

# iChoice Data Query

通过 EMQuantAPI (Choice量化接口) 获取金融市场数据。

## Environment

- SDK路径: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`
- 账号信息: `/Users/fanshengxia/Desktop/ichoice/account.json`
- 指标映射表: `/Users/fanshengxia/Desktop/ichoice/数据指标.xlsx`

## Quick Start

所有数据查询遵循统一流程：

```python
import sys
sys.path.insert(0, '/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3')
from EmQuantAPI import c
import pandas as pd

# 1. Login
result = c.start("UserName=xylczh0181,Password=ef465509,ForceLogin=1")

# 2. Fetch data (see patterns below)
# ...

# 3. Logout
c.stop()
```

## Data Query Patterns

### Pattern 1: EDB Macro Data (宏观/利率/EDB指标)

Use `c.edb()` for indicators with EMM/EMG/EMI/E codes. Covers macro, bond yields, money rates.

```python
# Single indicator
data = c.edb("EMM00087117", "Ispandas=1")

# Multiple indicators with date range
data = c.edb("EMM00072301,EMM00073348", "StartDate=2024-01-01,EndDate=2025-01-31,Ispandas=1")

# Latest value only
data = c.edb("E1000180", "IsLatest=1,Ispandas=1")
```

### Pattern 2: CSD Time Series (股票/指数/外汇/商品行情序列)

Use `c.csd()` for price time series with security codes (.SH/.SZ/.GI/.FX/.IB etc).

```python
data = c.csd("000300.SH,000016.SH", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1")
```

Common fields: CLOSE, OPEN, HIGH, LOW, VOLUME, AMOUNT, PETTM

### Pattern 3: CSS Cross-Section (截面数据)

Use `c.css()` for multi-security single-date snapshots.

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
offset = c.getdate("20250120", -3, "Market=CNSESH")
```

## Indicator Code Lookup

Determine the correct function and code based on the indicator type:

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

**For full indicator code mappings (453 indicators):** Read [references/indicator_codes.md](references/indicator_codes.md)

**For complete API function reference:** Read [references/api_reference.md](references/api_reference.md)

## Key Notes

- Wind code `.SI` suffix maps to Choice `.SWI` suffix for Shenwan industry indices
- Wind code `881001.WI` (万得全A) maps to Choice `800000.EI`
- Some indicators have no Choice code (南华指数, 螺纹钢Wind码, USDCNYM.IB)
- `Ispandas=1` returns DataFrame directly; without it returns EmQuantData object
- Rate limits: css/csd max 700 requests/minute
- EDB max 100 indicators per request
- Always call `c.stop()` when finished
