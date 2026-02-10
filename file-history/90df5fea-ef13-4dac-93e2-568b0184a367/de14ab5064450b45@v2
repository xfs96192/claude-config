# EMQuantAPI (iChoice) Python API Reference

## Table of Contents
- [Environment Setup](#environment-setup)
- [Login/Logout](#loginlogout)
- [Core Data Functions](#core-data-functions)
  - [edb - Macro Economic Data](#edb---macro-economic-data)
  - [css - Cross-Section Data](#css---cross-section-data)
  - [csd - Time Series Data](#csd---time-series-data)
  - [cmc - Minute Data](#cmc---minute-data)
  - [ctr - Thematic Reports](#ctr---thematic-reports)
  - [cses - Sector Cross-Section](#cses---sector-cross-section)
- [Real-time Functions](#real-time-functions)
  - [csq - Real-time Quote Subscribe](#csq---real-time-quote-subscribe)
  - [csqsnapshot - Quote Snapshot](#csqsnapshot---quote-snapshot)
  - [cst - Intraday Tick Data](#cst---intraday-tick-data)
- [Info/News Functions](#infonews-functions)
  - [cfn - News Query](#cfn---news-query)
  - [cnq - News Subscribe](#cnq---news-subscribe)
- [Utility Functions](#utility-functions)
  - [sector - Index/Sector Components](#sector---indexsector-components)
  - [tradedates - Trading Calendar](#tradedates---trading-calendar)
  - [getdate - Trade Date Offset](#getdate---trade-date-offset)
  - [tradedatesnum - Trading Days Count](#tradedatesnum---trading-days-count)
  - [edbquery - EDB Indicator Query](#edbquery---edb-indicator-query)
  - [cps - Stock Screener](#cps---stock-screener)
  - [cfc - Indicator Validation](#cfc---indicator-validation)
  - [cec - Code Validation](#cec---code-validation)
  - [datastatistics - Usage Statistics](#datastatistics---usage-statistics)
- [Portfolio Functions](#portfolio-functions)
- [Date Macros](#date-macros)
- [Error Codes](#error-codes)
- [Market Codes](#market-codes)

---

## Environment Setup

EMQuantAPI Python SDK location: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`

Import and PYTHONPATH setup:
```python
import sys
sys.path.insert(0, '/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3')
from EmQuantAPI import c
import pandas as pd
```

## Login/Logout

### c.start(options, logcallback, mainCallback)

Login to iChoice. Must be called before any data function.

```python
# Account credentials login
result = c.start("UserName=xylczh0181,Password=ef465509,ForceLogin=1")
if result.ErrorCode != 0:
    print(f"Login failed: {result.ErrorMsg}")
```

Key options:
| Parameter | Values | Description |
|-----------|--------|-------------|
| UserName | string | Account username |
| PassWord | string | Account password |
| ForceLogin | 0,1 (default 0) | 1=force login, kick previous session |
| TestLatency | 0,1 (default 0) | 1=test server speed before connecting |

### c.stop()

Logout and release resources. Always call when done.

```python
c.stop()
```

---

## Core Data Functions

### edb - Macro Economic Data

`c.edb(edbids, options)`

Fetch macro economic indicator data (GDP, CPI, PMI, bond yields, etc.)

**Parameters:**
- `edbids`: EDB indicator IDs, comma-separated, max 100. Format: EMM/EMG/EMI/E + numbers
- `options`: Optional parameters string

**Options:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| Ispandas | 0,1 (default 0) | 1=return pandas DataFrame |
| RowIndex | 1,2 (default 1) | 1=index by indicator ID, 2=index by date |
| StartDate | YYYY-MM-DD | Start date filter |
| EndDate | YYYY-MM-DD | End date filter |
| IsLatest | 0,1 (default 0) | 1=return only latest data point |
| IsPublishDate | 0,1 (default 0) | 1=include publish date |
| FixDate | 0,1 (default 0) | 1=adjust dates to period end dates |

**Example:**
```python
# Single indicator
data = c.edb("EMM00087117", "Ispandas=1")

# Multiple indicators with date range
data = c.edb("EMM00087117,EMM00121996", "StartDate=2024-01-01,EndDate=2025-01-31,Ispandas=1")

# Latest value only
data = c.edb("EMM00072301", "IsLatest=1,Ispandas=1")
```

### css - Cross-Section Data

`c.css(codes, indicators, options)`

Fetch cross-sectional data (multiple securities, one date).

**Parameters:**
- `codes`: Security codes, comma-separated (e.g., "000001.SZ,600000.SH")
- `indicators`: Indicator names, comma-separated, max 64 (e.g., "CLOSE,OPEN,HIGH,LOW,VOLUME")
- `options`: Optional parameters

**Options:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| TradeDate | YYYY-MM-DD | Required: the cross-section date |
| Ispandas | 0,1 | 1=return DataFrame |
| RowIndex | 1,2 | 1=by code, 2=by date |
| ShowBlank | integer | Replace blank values |
| RECVtimeout | integer | Timeout in seconds |

**Example:**
```python
data = c.css("000001.SZ,600519.SH", "CLOSE,OPEN,HIGH,LOW,VOLUME,AMOUNT", "TradeDate=2025-01-20,Ispandas=1")
```

**Rate limit:** Max 700 requests per minute.

### csd - Time Series Data

`c.csd(codes, indicators, startdate, enddate, options)`

Fetch time series data (one or more securities, date range).

**Parameters:**
- `codes`: Security codes, comma-separated
- `indicators`: Indicator names, comma-separated, max 64
- `startdate`: Start date (YYYY-MM-DD)
- `enddate`: End date (YYYY-MM-DD)
- `options`: Optional parameters

**Options:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| Ispandas | 0,1 | 1=return DataFrame |
| RowIndex | 1,2 | 1=by code, 2=by date |
| Period | 1-4 | 1=daily, 2=weekly, 3=monthly, 4=yearly |
| AdjustFlag | 1-3 | 1=no adjust, 2=backward, 3=forward |
| CurType | 1-4 | 1=original, 2=RMB, 3=USD, 4=HKD |
| Order | 1-2 | 1=ascending, 2=descending |
| Market | string | Market code for calendar, default CNSESH |
| ShowBlank | integer | Replace blank values |
| filldata | 0,1 | 1=forward fill missing data |

**Example:**
```python
# Single stock time series
data = c.csd("000001.SZ", "CLOSE,VOLUME", "2025-01-01", "2025-01-31", "Ispandas=1")

# Multiple stocks comparison
data = c.csd("000001.SZ,600519.SH,000858.SZ", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1,Period=1")

# Weekly data
data = c.csd("000300.SH", "CLOSE", "2024-01-01", "2025-01-31", "Ispandas=1,Period=2")
```

**Rate limit:** Max 700 requests per minute.

### cmc - Minute Data

`c.cmc(codes, indicators, startdate, enddate, options)`

Fetch minute-level bar data.

**Example:**
```python
data = c.cmc("300059.SZ", "OPEN,CLOSE,HIGH", "2025-01-20", "2025-01-24", "RowIndex=2,Ispandas=1")
```

### ctr - Thematic Reports

`c.ctr(ctrName, indicators, options)`

Fetch thematic report data.

**Parameters:**
- `ctrName`: Report name (see indicator manual)
- `indicators`: Report field names, comma-separated (empty=all fields)
- `options`: Parameters including StartDate, EndDate

**Example:**
```python
data = c.ctr("StockInfo", "", "StartDate=2025-01-01,EndDate=2025-01-31,Ispandas=1")
```

### cses - Sector Cross-Section

`c.cses(blockcodes, indicators, options)`

Fetch sector-level cross-section data. Block codes start with "B_".

**Example:**
```python
data = c.cses("B_011001003,B_018005001001", "SECTOPREAVG,CFOPSAVG", "TradeDate=2025-01-20,DelType=1,IsHistory=0")
```

---

## Real-time Functions

### csq - Real-time Quote Subscribe

`c.csq(codes, indicators, options, callback)`

Subscribe to real-time market quotes. Requires callback function.

```python
def csqCallback(quantdata):
    print(str(quantdata))

data = c.csq('600000.SH,300059.SZ', 'TIME,Now,Volume', 'Pushtype=2', csqCallback)
# Cancel: c.csqcancel(data.SerialID)
```

### csqsnapshot - Quote Snapshot

`c.csqsnapshot(codes, indicators, options)`

Get current market snapshot (no subscription).

```python
data = c.csqsnapshot("000001.SZ,600000.SH", "PRECLOSE,OPEN,HIGH,LOW,NOW,AMOUNT", "Ispandas=1")
```

### cst - Intraday Tick Data

`c.cst(codes, indicators, starttime, endtime, options, callback)`

Get intraday tick-by-tick data.

---

## Info/News Functions

### cfn - News Query

`c.cfn(codes, content, mode, options)`

Query historical news and announcements.

**Content types:** companynews, industrynews, report, regularreport, tradeinfo, sectornews

**Mode:** eCfnMode_StartToEnd=1, eCfnMode_EndCount=2

### cnq - News Subscribe

`c.cnq(codes, content, options, callback)`

Subscribe to real-time news. Cancel with `c.cnqcancel(serialID)`.

---

## Utility Functions

### sector - Index/Sector Components

`c.sector(pukeycode, enddate, options)`

Get constituent securities of an index or sector.

**Common sector codes:**
| Code | Name |
|------|------|
| 001004 | All A-shares |
| 000300.SH | CSI 300 |
| 000016.SH | SSE 50 |
| 000905.SH | CSI 500 |
| 000852.SH | CSI 1000 |

```python
# Get CSI 300 constituents
data = c.sector("000300.SH", "2025-01-20", "Ispandas=1")
```

### tradedates - Trading Calendar

`c.tradedates(startdate, enddate, options)`

Get list of trading dates in a range.

```python
data = c.tradedates("2025-01-01", "2025-01-31", "")
# data.Data contains list of trading dates
```

**Options:** Period (1=daily,2=weekly,3=monthly,4=yearly,5=quarterly), Order (1=asc,2=desc), Market

### getdate - Trade Date Offset

`c.getdate(tradedate, offday, options)`

Get the trading date N days offset from a given date.

```python
# 3 trading days before 2025-01-20
data = c.getdate("20250120", -3, "Market=CNSESH")
```

### tradedatesnum - Trading Days Count

`c.tradedatesnum(startdate, enddate, options)`

Get number of trading days in a range.

### edbquery - EDB Indicator Query

`c.edbquery(edbids, indicators, options)`

Query EDB indicator metadata (name, unit, source, frequency, etc.)

**Available fields:** ID, Name, Unit, Source, Region, Frequency (1=daily,2=weekly,3=10-day,5=monthly,6=quarterly,8=yearly,9=irregular), Startdate, Enddate, Updatetime

```python
data = c.edbquery("EMM00087117,EMM00121996", "NAME,ID,FREQUENCY,UNIT", "")
```

### cps - Stock Screener

`c.cps(cpsCodes, cpsIndicators, cpsConditions, cpsOptions)`

Conditional stock screening.

### cfc - Indicator Validation

`c.cfc(codes, indicators, options)`

Validate if indicators are valid for given codes. `options`: FunType=css|csd|cses

### cec - Code Validation

`c.cec(codes, options)`

Validate security codes. ReturnType=0 (check mode), ReturnType=1 (auto-complete mode).

### datastatistics - Usage Statistics

`c.datastatistics(funcname, indicators, options)`

Query API usage/quota statistics.

---

## Portfolio Functions

| Function | Description |
|----------|-------------|
| `c.pcreate(code, name, capital, remark)` | Create portfolio |
| `c.pctransfer(code, direction, date, amount, remark)` | Transfer funds |
| `c.pquery(options)` | Query portfolio info |
| `c.porder(code, orderdict, remark)` | Batch order |
| `c.preport(code, type, options)` | Portfolio report |
| `c.pdelete(code)` | Delete portfolio |

---

## Date Macros

Relative date macros usable in date parameters:

| Macro | Description |
|-------|-------------|
| TD | Trading day |
| D | Calendar day |
| W | Week |
| M | Month |
| Q | Quarter |
| HY | Half year |
| Y | Year |
| SD | Reference to StartDate |
| ED | Reference to EndDate |

Absolute date macros:

| Macro | Description |
|-------|-------------|
| N | Latest |
| MRQ | Latest report period |
| LYE | Last year end |
| RYF | This year start |
| LME | Last month end |
| RMF | This month start |
| LWE | Last week end |
| RWF | This Monday |

**Examples:** `StartDate=-1W, EndDate=N` (last week to now), `StartDate=ED-5D` (5 days before end date)

---

## Error Codes

Common error codes from mainCallback:
| Code | Description |
|------|-------------|
| 10001009 | Login limit reached (kicked) |
| 10001011 | Disconnected |
| 10001021 | Quote login auth failed |
| 10001022 | Quote traffic auth failed |
| 10002009 | Quote reconnect 6x failed |
| 10002012 | Quote subscription error, auto-reconnecting |

---

## Market Codes

| Code | Market |
|------|--------|
| CNSESH | Shanghai Stock Exchange |
| CNSESZ | Shenzhen Stock Exchange |
| HKSE00 | Hong Kong Stock Exchange |
| USSE00 | US Securities Exchange |
| USSENY | NYSE |
| USSEND | NASDAQ |
| CNFEDC | Dalian Commodity Exchange |
| CNFESF | Shanghai Futures Exchange |
| CNFEZC | Zhengzhou Commodity Exchange |
| INE000 | Shanghai International Energy Exchange |
| NYMEX0 | NYMEX |
| CME000 | CME |
| LDMETL | London Metal Exchange |
| LDEXCH | London Stock Exchange |
| SGSE00 | Singapore Exchange |

---

## EmQuantData Return Object

All functions return `EmQuantData` with:
- `ErrorCode`: 0=success
- `ErrorMsg`: Error description
- `Codes`: List of security codes
- `Indicators`: List of indicator names
- `Dates`: List of dates
- `Data`: Dict of results (structure varies by function)
- `RequestID`: Request ID
- `SerialID`: Subscription ID (for csq/cnq)

When `Ispandas=1`, functions return a pandas DataFrame directly instead of EmQuantData.

---

## Security Code Suffixes

| Suffix | Market |
|--------|--------|
| .SZ | Shenzhen A-share |
| .SH | Shanghai A-share |
| .SWI | Shenwan Industry Index |
| .GI | Global Index |
| .FX | Forex |
| .IB | Interbank |
| .IR | Interest Rate |
| .CFE | China Financial Futures Exchange |
| .SHF | Shanghai Futures Exchange |
| .DCE | Dalian Commodity Exchange |
| .INE | Shanghai International Energy Exchange |
| .NHF | Nanhua Futures Index |
| .CS/.CSI | China Securities Index |
| .EI | EastMoney Index |
| .GBM | Global Bond Market |
