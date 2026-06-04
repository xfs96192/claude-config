# DM API Reference

## Source Materials

- Local manual: `/Users/fanshengxia/Desktop/data/market_data/dm/DM PythonAPI数据调用用户手册V1.3(20260522)(1).pdf`
- Local SDK wheel: `/Users/fanshengxia/Desktop/data/market_data/dm/dm_quant_api_client-0.2.2-py3-none-any(1).whl`
- Local EDB dictionary: `/Users/fanshengxia/Desktop/data/market_data/dm/【字典】EDB指标层级(1).xlsx`

## SDK Facts

- Package: `dm_quant_api_client`
- Version: `0.2.2`
- Python: `>=3.8`
- Dependencies: `requests>=2.25.0`, `pandas>=1.0.0`, `gmssl>=3.2.0`
- Default base URL: `https://gapi-ext.innodealing.com`
- Auth environment variables: `INNO_APP_KEY`, `INNO_SM4_KEY`
- Main class: `DMQuantApiClient`
- Main method: `post_data(data, api_path, return_type="dataframe")`
- `pythonic=True`: request keys are converted from snake_case to camelCase; response keys are converted to snake_case.

## API Aliases

| Alias | DM function | Path | Required fields |
|---|---|---|---|
| `bond_bars` | 债券-高频序列 | `/dm-quant-func-service/api/v1/bond/market-data/bars` | `security_id_list`, `data_source_list`, `kline_type` |
| `bond_date` | 债券-日期序列 | `/dm-quant-func-service/api/v1/bond/market-data/date` | `security_id_list`, `data_source_list` |
| `bond_realtime_quote` | 债券-实时最新行情 | `/dm-quant-func-service/api/v1/bond/market-data/realtime-quote` | `security_id_list` |
| `bond_insti_sentiment` | 债券-机构行为 | `/dm-quant-func-service/api/v1/bond/analysis/insti-sentiment` | `data_source` |
| `bond_basic_info` | 债券-基础资料 | `/dm-quant-func-service/api/v1/bond/basic-info/info` | `security_id_list` |
| `bond_yield_curve` | 债券-收益率曲线 | `/dm-quant-func-service/api/v1/bond/yield-curve/data` | `data_source`, `curve_name`, `curve_term_list` |
| `bond_outstanding_bonds` | 债券-发行人维度存续债 | `/dm-quant-func-service/api/v1/bond/basic-info/outstanding-bonds` | `issuer_full_name` or `society_code` |
| `bond_rolling_bonds` | 债券-活跃券/次活跃券 | `/dm-quant-func-service/api/v1/bond/market-data/rolling-bonds` | `sequence_type`, `bond_filter_type`, `key_tenor` |
| `money_market_date` | 货币市场-日期序列 | `/dm-quant-func-service/api/v1/money-market/data/date` | `instrument_type_list` or `instrument_code` |
| `money_market_sentiment` | 货币市场-资金情绪指数 | `/dm-quant-func-service/api/v1/money-market/analysis/sentiment-index` | none |
| `futures_bars` | 期货-高频序列 | `/dm-quant-func-service/api/v1/futures/market-data/bars` | `security_id_list`, `kline_type` |
| `futures_basis` | 期货-日期序列衍生 | `/dm-quant-func-service/api/v1/futures/analysis/basis` | `security_id_list` |
| `futures_vol_oi_rank` | 期货-成交持仓排名 | `/dm-quant-func-service/api/v1/futures/analysis/vol-oi-rank` | `security_id_list` |
| `equity_bars` | 权益-高频序列 | `/dm-quant-func-service/api/v1/equity/market-data/bars` | `security_category`, `security_id_list`, `kline_type` |
| `edb_codes` | EDB-指标ID获取 | `/dm-quant-func-service/api/v1/edb/data-info/code` | `edb_level_id_list` |
| `edb_data` | EDB-指标数值调取 | `/dm-quant-func-service/api/v1/edb/data-info/data` | `indicator_id` |
| `trade_dates` | 交易日历 | `/dm-quant-func-service/api/v1/market/trade-dates` | `market_type`, `start_date`, `end_date` |

## EDB Dictionary

`references/edb_levels.csv` contains 3192 EDB hierarchy rows:

| Column | Meaning |
|---|---|
| `edb_level_id` | Input for `edb_codes` |
| `category_system` | 中国宏观 or 全球宏观 |
| `level1` to `level5` | Hierarchy labels |

Counts from the source workbook:

| Category system | Rows |
|---|---:|
| 中国宏观 | 3006 |
| 全球宏观 | 186 |

## Common Examples

Search EDB hierarchy locally:

```bash
python3 scripts/dm_query.py search-edb 社融 --limit 20
```

Get indicator IDs under EDB levels:

```bash
python3 scripts/dm_query.py call edb_codes \
  --return-type dict \
  --data '{"edb_level_id_list":["CN0011841695","CN0011841696"]}'
```

Get EDB data:

```bash
python3 scripts/dm_query.py edb-data M00100066100000 \
  --start-date 2025-12-31 \
  --end-date 2025-12-31
```

Get bond basic info:

```bash
python3 scripts/dm_query.py call bond_basic_info \
  --data '{"security_id_list":["2500005.IB","232580001.IB"]}'
```

Get money-market rates:

```bash
python3 scripts/dm_query.py call money_market_date \
  --data '{"instrument_type_list":["DR","Shibor"],"start_date":"2026-03-31","end_date":"2026-03-31"}'
```

Get trade dates:

```bash
python3 scripts/dm_query.py trade-dates 1 2026-05-01 2026-05-18
```

## Limits And Enums

- K-line type: `1` 1分钟, `2` 5分钟, `3` 15分钟, `4` 30分钟, `5` 60分钟, `6` 日, `7` 周, `8` 月.
- Bond data source: `1` 经纪商, `2` 外汇交易中心, `3` 上交所, `4` 上固收, `7` 深交所.
- Yield-curve data source: `18` 中债, `19` 中证.
- Rolling bond sequence: `1` 活跃券, `2` 次活跃券.
- Rolling bond type: `1` 国债, `3` 国开.
- Money-market instrument types: `DR`, `R`, `OR`, `IBO`, `L`, `Shibor`, `FDR`, `FR`, `GC`, `R-`.
- Equity security category: `1` 股票, `2` 基金, `3` 指数.
- Trade calendar market type: `1` 银行间市场, `2` 交易所市场.

Date-window constraints:

- Intraday K-line windows vary by `kline_type`: 1分钟 <= 1天, 5分钟 <= 7天, 15分钟 <= 2周, 30分钟 <= 1个月, 60分钟 <= 2个月, 日 <= 1年, 周 <= 2年, 月 <= 3年.
- `bond_date`: <= 3个月.
- `bond_insti_sentiment`: <= 1周.
- `bond_yield_curve`: <= 1个月.
- `money_market_date`: <= 1周.
- `money_market_sentiment`: <= 2个月.
- `futures_basis`: <= 3个月.
- `futures_vol_oi_rank`: <= 1周.
- `trade_dates`: <= 2年.
- `edb_data`: 日度/不定期 < 1年; 周度/旬度 < 5年; 月度/季度/半年度/年度 < 10年.

## Error Handling

Report exact error strings. Frequent causes:

- `app_key is required`: set `INNO_APP_KEY`.
- `sm4_key is required`: set `INNO_SM4_KEY`.
- HTTP non-200: check path, network, subscription, and request body.
- decrypt/JSON failure: check SM4 key and whether the endpoint returned encrypted content.
- "无订阅套餐": account lacks the package.
- "额度已耗尽" or "限流": quota/rate limit.
