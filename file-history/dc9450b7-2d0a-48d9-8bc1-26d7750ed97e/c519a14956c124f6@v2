# 基金 API 参考

所有基金专有API通过 `rqdatac.fund` 模块调用。

## 基金信息

```python
rqdatac.fund.instruments(order_book_ids)           # 基金基础信息
rqdatac.fund.all_instruments(date=None)             # 所有公募基金
rqdatac.fund.get_transition_info(order_book_ids)    # 基金转型信息
rqdatac.fund.get_related_code(order_book_ids)       # 分级基金关系
```

## 净值与交易

```python
rqdatac.fund.get_nav(order_book_ids, start_date, end_date, fields=None, expect_df=False)
# fields: 'unit_net_value'单位净值, 'acc_net_value'累计净值,
#         'adjusted_net_value'复权净值, 'change_rate'日收益率 等

rqdatac.fund.get_transaction_status(order_book_ids, start_date, end_date, fields=None, investor='institution')
```

## 持仓数据

```python
rqdatac.fund.get_holdings(order_book_ids, date=None)           # 基金持仓
rqdatac.fund.get_asset_allocation(order_book_ids, date=None)   # 资产配置
rqdatac.fund.get_industry_allocation(order_book_ids, date=None)# 行业配置
rqdatac.fund.get_bond_structure(order_book_ids, date=None)     # 债券结构
rqdatac.fund.get_credit_quality(order_book_ids, date=None)     # 信用评级
rqdatac.fund.get_stock_change(order_book_ids, start_date, end_date)  # 重大持仓变动
rqdatac.fund.get_qdii_scope(order_book_ids, start_date, end_date)    # QDII地区配置
rqdatac.fund.get_term_to_maturity(order_book_ids, start_date, end_date) # 货基持仓期限
```

## 份额/分红/ETF

```python
rqdatac.fund.get_units_change(order_book_ids, date=None)       # 份额变动
rqdatac.fund.get_daily_units(order_book_ids, start_date, end_date)  # 日度份额
rqdatac.fund.get_holder_structure(order_book_ids, start_date, end_date)
rqdatac.fund.get_split(order_book_ids)                          # 拆分
rqdatac.fund.get_dividend(order_book_ids)                       # 分红
rqdatac.fund.get_etf_components(order_book_ids, trading_date=None)  # ETF申赎清单
rqdatac.fund.get_etf_cash_components(order_book_ids, start_date, end_date)
```

## 衍生指标/评级/经理

```python
rqdatac.fund.get_snapshot(order_book_ids, fields=None, rule='ricequant', indicator_type='value')
rqdatac.fund.get_indicators(order_book_ids, start_date, end_date, fields=None, rule='ricequant')
rqdatac.fund.get_ratings(order_book_ids, date=None)
rqdatac.fund.get_manager(order_book_ids)
rqdatac.fund.get_manager_info(manager_id, fields=None)
rqdatac.fund.get_manager_indicators(manager_ids, start_date, end_date, fields=None)
rqdatac.fund.get_manager_weight_info(managers, start_date, end_date)
```

## 分类/费率/基准

```python
rqdatac.fund.get_instrument_category(order_book_ids, date=None, category_type=None, source='gildata')
rqdatac.fund.get_category(category, date=None, source='gildata')
rqdatac.fund.get_category_mapping(source='gildata', category_type=None)
rqdatac.fund.get_financials(order_book_ids, start_date, end_date, fields=None)
rqdatac.fund.get_fee(order_book_ids, fee_type=None, charge_type='front', date=None)
rqdatac.fund.get_benchmark(order_book_ids)
rqdatac.fund.get_benchmark_price(order_book_ids, start_date, end_date)
```
