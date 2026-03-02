# 期权 API 参考

所有期权专有API通过 `rqdatac.options` 模块调用。

## 合约筛选

```python
rqdatac.options.get_contracts(
    underlying,          # str, 标的代码如'510050.XSHG','IF'
    option_type=None,    # 'C'认购, 'P'认沽
    maturity=None,       # str, 到期月份如'202412'
    strike=None,         # float, 行权价
    trading_date=None    # 交易日期
)
```

## Greeks (风险指标)

```python
rqdatac.options.get_greeks(
    order_book_ids,
    start_date=None, end_date=None,
    fields=None,         # 'delta','gamma','theta','vega','rho','iv'(隐含波动率)
    model='implied_forward',  # 定价模型
    price_type='close',  # 'close'收盘价, 'settlement'结算价
    frequency='1d'       # '1d'日线, '1m'分钟线
)
```

## 合约属性 / 主力月份 / 衍生指标

```python
rqdatac.options.get_contract_property(order_book_ids, start_date, end_date, fields=None)
rqdatac.options.get_dominant_month(underlying_symbol, start_date, end_date, rule=0, rank=1)
rqdatac.options.get_indicators(underlying_symbols, maturity, start_date, end_date, fields=None)
```
