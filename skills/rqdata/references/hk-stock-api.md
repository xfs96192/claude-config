# 港股 API 参考 (公测版本)

所有港股API需要传入 `market='hk'`。港股代码格式：`00001.XHKG`

## 合约信息

```python
rqdatac.all_instruments(type=None, market='hk', date=None)
rqdatac.instruments(order_book_ids, market='hk')
```

## 行情数据

```python
rqdatac.get_price(order_book_ids, start_date, end_date, frequency='1d',
                  fields=None, adjust_type='pre', market='hk')
```

## 复权因子 / 汇率

```python
rqdatac.get_ex_factor(order_book_ids, start_date, end_date, market='hk')
rqdatac.get_exchange_rate(start_date=None, end_date=None, fields=None)
# fields: 'currency_pair', 'middle_referrence_rate' 等
```

## 流通股 / 行业

```python
rqdatac.get_shares(order_book_ids, start_date, end_date, fields=None, market='hk')
rqdatac.get_industry(industry, source='hsi', market='hk')
rqdatac.get_industry_change(industry, source='hsi', market='hk')
rqdatac.get_instrument_industry(order_book_ids, market='hk')
rqdatac.get_industry_mapping(market='hk')
rqdatac.get_turnover_rate(order_book_ids, start_date, end_date, fields=None, market='hk')
rqdatac.get_dividend(order_book_ids, market='hk')
```

## 财务 / 因子 / 公告

```python
rqdatac.get_pit_financials_ex(order_book_ids, fields, start_quarter, end_quarter, market='hk')
rqdatac.hk.get_detailed_financial_items(order_book_ids, fields, start_quarter, end_quarter, market='hk')
rqdatac.get_factor(order_book_ids, factor, start_date, end_date, market='hk')
# 港股因子: 'hk_share_market_val', 'hk_share_market_val_in_circulation', 'hk_total_market_val'
rqdatac.get_all_factor_names(type='eod_indicator', market='hk')
rqdatac.hk.get_announcement(order_book_ids, start_date, end_date, market='hk')
```

## 南向资金

```python
rqdatac.hk.get_southbound_eligible_secs(trading_type='sh', date=None)
# trading_type: 'sh'沪港通, 'sz'深港通
```
