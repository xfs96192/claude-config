# 期货 API 参考

所有期货专有API通过 `rqdatac.futures` 模块调用。

## 主力合约

```python
# 获取主力合约代码
rqdatac.futures.get_dominant(
    underlying_symbol,   # str, 品种代码如'IF','RB','AU'
    start_date=None, end_date=None,
    rule=0,              # 0:按持仓量, 1:按成交量
    rank=1               # 1:主力, 2:次主力
)

# 获取可交易合约列表
rqdatac.futures.get_contracts(underlying_symbol, date=None)

# 获取主力连续合约行情 (自动换月+复权)
rqdatac.futures.get_dominant_price(
    underlying_symbols,   # str/list
    start_date, end_date,
    frequency='1d', fields=None,
    adjust_type='pre',    # 'pre'前复权, 'none'不复权
    adjust_method='prev_close_spread',  # 复权方法
    rule=0, rank=1
)

# 主力连续合约复权因子
rqdatac.futures.get_ex_factor(underlying_symbols, start_date, end_date,
    adjust_method='prev_close_spread', rule=0, rank=1)

# 当月/次月/季月/次季月连续合约
rqdatac.futures.get_continuous_contracts(underlying_symbol, start_date, end_date, type='front_month')
# type: 'front_month'当月, 'second_month'次月, 'current_quarter'季月, 'next_quarter'次季月
```

## 交易参数与数据

```python
rqdatac.futures.get_contract_multiplier(underlying_symbols, start_date, end_date)  # 合约乘数
rqdatac.futures.get_exchange_daily(order_book_ids, start_date, end_date, fields=None)  # 交易所日线
rqdatac.futures.get_trading_parameters(order_book_ids, start_date, end_date, fields=None)  # 交易参数
rqdatac.futures.get_member_rank(obj, trading_date=None, rank_by='volume')  # 会员持仓排名
# rank_by: 'volume'成交量, 'long'多头, 'short'空头
```

## 仓单/升贴水/展期收益

```python
rqdatac.futures.get_warehouse_stocks(underlying_symbols, start_date, end_date)  # 仓单
rqdatac.futures.get_basis(order_book_ids, start_date, end_date, fields=None,
    frequency='1d', dividend_adjusted=False)  # 股指期货升贴水
rqdatac.futures.get_current_basis(order_book_ids)  # 实时升贴水
rqdatac.futures.get_roll_yield(underlying_symbol, start_date, end_date,
    type='main_sub', rule=0)  # 展期收益率
# type: 'main_sub'主次合约价差, 'near_far'近远月价差
```
