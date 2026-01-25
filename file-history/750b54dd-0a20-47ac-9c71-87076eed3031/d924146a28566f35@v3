# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Market View Enhancement (市场观点美化) - A financial market analysis system that generates Excel data files from Wind Financial Terminal API for consumption by a React frontend dashboard. The system covers multi-asset class analysis including equities, bonds, forex, and commodities.

## Core Workflow

```
Wind Financial Terminal API
    ↓
Python Data Generation Scripts
    ↓
Excel Files (近1月净值走势.xlsx, 指标值.xlsx)
    ↓
excel_to_json_converter.py
    ↓
JSON Data Files
    ↓
React Frontend Dashboard
```

## Development Commands

### Python Data Generation (Root Directory)

**Primary Program (v2.0 - Production):**
```bash
# Generate Excel data files from Wind API
python generate_tables_from_wind.py

# Test Wind connection before running main program
python test_wind_connection.py
```

**Legacy Program (v1.0 - With mock data support):**
```bash
# Generate data (falls back to mock data if Wind unavailable)
python generate_market_data.py
```

**Data Conversion:**
```bash
# Convert Excel to JSON for frontend consumption
cd asset-analysis-real-data
python excel_to_json_converter.py
```

### Frontend Dashboard (asset-analysis-real-data/asset-analysis-dashboard/)

```bash
cd asset-analysis-real-data/asset-analysis-dashboard
pnpm dev          # Start dev server at http://localhost:5173
pnpm build        # Production build
pnpm preview      # Preview production build
pnpm lint         # Run ESLint
```

## Python Environment Requirements

**Critical:** This project requires Wind Financial Terminal (万得金融终端):
- Wind terminal must be installed and logged in
- WindPy library must be installed: `pip install WindPy`
- Required Python packages: `pandas numpy openpyxl WindPy`

**Wind Connection Check:**
```python
from WindPy import w
w.start()
w.isconnected()  # Must return True
```

## Architecture

### Data Generation System (Python)

**Two Programs Available:**

1. **generate_tables_from_wind.py** (v2.0 - Recommended)
   - Production-ready, no mock data
   - Strict Wind API requirement
   - Based on exact Excel formula mappings
   - Generates 2 Excel files with 31-37 indicators

2. **generate_market_data.py** (v1.0 - Legacy)
   - Falls back to mock data if Wind unavailable
   - Useful for testing without Wind terminal
   - Some formula deviations from original Excel

**Key Classes:**
- `WindDataFetcher`: Wrapper for Wind API calls (wsd, edb functions)
- Data fetching functions: `fetch_daily_data()`, `fetch_weekly_data()`, `fetch_edb_data()`
- Calculation functions: Financial indicator computations (spreads, ratios, percentiles)

**Generated Files:**
1. **近1月净值走势.xlsx**: ~20-25 rows × 12 columns (daily prices for last month)
2. **指标值.xlsx**: 31-37 rows × 8 columns (indicators with current value, historical stats, percentiles)

### Data Conversion Layer

**excel_to_json_converter.py:**
- Converts Excel files to JSON format
- Maps Chinese asset categories to English keys
- Processes time series data for frontend charts
- Output: `asset_data.json`, `enhanced_asset_data.json`

### Frontend (React Dashboard)

- **Stack:** React 19, Vite 6.3.5, Tailwind CSS 4.x
- **UI Library:** shadcn/ui (35+ components, Radix UI primitives)
- **Data Flow:** Static JSON files consumed via props
- **Component Structure:** Section-based by asset class (`EquitySection.jsx`, `BondSection.jsx`, etc.)
- **Package Manager:** pnpm (enforced, version 10.4.1)
- **Language:** Pure JavaScript (no TypeScript), UI text in Chinese

## Critical Financial Calculations

All formulas are documented in `Excel公式详细映射表.md` and must match exactly:

### Core Indicator Formulas

**Equity-Bond Ratio (股债性价比):**
```python
ratio = (1 / PE) - (bond_yield_10y / 100)
```

**Credit Spread (信用利差, in basis points):**
```python
spread_bp = (credit_bond_yield - treasury_yield) * 100
```

**Term Spread (期限利差, in basis points):**
```python
term_spread_bp = (long_term_yield - short_term_yield) * 100
```

**FX Hedging Cost (锁汇成本):**
```python
hedging_cost = -swap_points / 10000 / offshore_cny
```

**Shanghai-COMEX Gold Spread (沪金内外盘价差):**
```python
spread = shfe_gold - (comex_gold * usdcny / 31.1035)
```

**Percentile Calculation:**
```python
# For "higher is better" indicators
percentile = PERCENTRANK.INC(historical_series, current_value)

# For "lower is better" indicators (reverse)
percentile = 1 - PERCENTRANK.INC(historical_series, current_value)
```

## Wind API Code Mappings

### Daily Price Codes (for 近1月净值走势.xlsx)
- Equity: `000001.SH` (上证), `000832.CSI` (中证转债), `SPX.GI` (标普500)
- Bonds: `931472.CSI` (7-10年国开), `CBA01921.CS` (1-3年高等级债), `10yrnote.gbm` (美债10Y)
- FX: `USDCNY.IB` (中间价), `USDCNY1YS.IB` (掉期点), `USDCNH.FX` (离岸)
- Commodities: `AU.SHF` (沪金), `RB.SHF` (螺纹钢), `SC.INE` (原油), `M.DCE` (豆粕)

### EDB Codes (Economic Database - for 指标值.xlsx)

**✓ Status (as of 2026-01-22):** EDB codes have been verified and corrected using `/Users/fanshengxia/Desktop/data_api/data/数据指标.xlsx`

**Verified and Corrected (7 codes):**
- S0059749: 中债国债10年 (China Gov't Bond 10Y)
- M1004271: 中债国开债10年 (China Dev Bank 10Y)
- S0059737: 中债AAA 2年 (AAA Commercial Paper 2Y)
- S0059736: 中债AAA 1年 (AAA Commercial Paper 1Y)
- S0059745: 中债国债2年 (China Gov't Bond 2Y)
- M1004263: 中债国开债1年 (China Dev Bank 1Y)
- G0000891: 美国10年国债 (US Treasury 10Y)

⚠️ **Still Need Verification (2 codes):**
- `PLACEHOLDER_US_1Y`: US 1-year Treasury yield (for term spread calculation at line 442)
- `PLACEHOLDER_US_TIPS`: US 10-year TIPS/Real Yield (for commodity indicators at line 513)

**How to find missing codes:**
1. Wind Terminal: Search "美国国债收益率" or "US Treasury Yield 1Y"
2. Search for "TIPS" or "美国实际收益率" for real yield
3. Replace placeholders in generate_tables_from_wind.py lines 66-87
4. Codes typically start with "G" for global indicators

**See detailed correction report:** `债券代码修正说明.md`

### Weekly Data Fields
- Valuation: `pe_ttm` (PE ratio), `pb_lf` (PB ratio)
- Retrieved via `w.wsd(codes, fields, start, end, "Period=W")`

## Data Quality Characteristics

### Fully Supported (Direct from Wind)
- Stock index prices and valuations (PE, PB)
- Bond yields from China Bond Index (中债收益率曲线)
- FX rates (spot, offshore, swap points)
- Commodity futures prices (main contracts)
- VIX, US Dollar Index

### Calculated Indicators
- Equity-bond ratio, credit spreads, term spreads
- FX hedging cost, gold price differentials
- All percentile rankings (based on 3-year history)

### Not Currently Supported
- Convertible bond metrics (转股溢价率, 纯债溢价率, 隐含波动率) - were manual entries in original Excel
- These require specific Wind fields or custom calculations

## Time Ranges

- **Daily data:** Last 30 days (近1月净值走势)
- **Weekly data:** Last 3 years (指标值 historical statistics)
- **Percentile calculations:** Based on 3-year weekly data (156 weeks)

## Configuration

**Output Directory:**
```python
OUTPUT_DIR = "/Users/fanshengxia/Desktop/市场观点美化/asset-analysis-real-data"
```

**Modify date ranges in generate_tables_from_wind.py:**
```python
END_DATE = datetime.now()
START_DATE_DAILY = END_DATE - timedelta(days=30)      # Change 30 for different lookback
START_DATE_WEEKLY = END_DATE - timedelta(days=365*3)  # Change 3 for different years
```

## Error Handling

**Wind Connection Failures:**
- Error code 40520001: Not connected - ensure Wind terminal is logged in
- EDB errors: Incorrect EDB codes or insufficient data permissions
- Missing data: Check Wind terminal code validity and account permissions

**Data Quality Checks:**
- Program exits if Wind not connected (v2.0)
- Validates data completeness after fetching
- Excel formatting applied automatically (headers, borders, column widths)

## Documentation Files

- **README.md**: Full user guide and API documentation
- **程序使用说明.md**: Detailed program usage instructions
- **README-程序版本.md**: Quick start guide and version comparison
- **指标计算逻辑文档.md**: Financial calculation logic and business meaning
- **Excel公式详细映射表.md**: Complete Excel formula mappings
- **快速开始.txt**: Quick start text guide

## Version History

**v2.0 (Current - 2026-01-22):**
- Production-ready, no mock data
- All formulas match Excel exactly
- Enhanced error handling and Excel formatting
- Added test_wind_connection.py for pre-flight checks

**v1.0 (Legacy):**
- Included mock data fallback
- Some formula deviations from original Excel

## Important Notes

1. **Never commit sensitive data:** Wind terminal credentials, API keys, or raw financial data files
2. **EDB codes are environment-specific:** Always verify codes in your Wind terminal instance
3. **Excel formatting matters:** Both data accuracy and presentation formatting are critical for end users
4. **Chinese text encoding:** All file I/O uses UTF-8, Excel files may need `openpyxl` encoding handling
5. **Frontend is read-only:** Dashboard consumes static JSON, no backend API or real-time updates
