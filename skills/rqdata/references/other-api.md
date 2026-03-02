# 风险因子 / 现货 / 货币市场 / 宏观经济 API 参考

## 风险因子 (A股多因子模型)

```python
# 因子暴露度
rqdatac.get_factor_exposure(order_book_ids, start_date, end_date,
    factors=None, industry_mapping='sws_2021', model='v1')

# 细分风格因子暴露度
rqdatac.get_descriptor_exposure(order_book_ids, start_date, end_date, descriptors=None, model='v1')

# 个股Beta
rqdatac.get_stock_beta(order_book_ids, start_date, end_date,
    benchmark='000300.XSHG', model='v1')

# 因子收益率
rqdatac.get_factor_return(start_date, end_date, factors=None,
    universe='whole_market', method='implicit', industry_mapping='sws_2021', model='v1')

# 个股特异收益率
rqdatac.get_specific_return(order_book_ids, start_date, end_date, model='v1')

# 因子协方差矩阵
rqdatac.get_factor_covariance(date, horizon='daily', model='v1')
# horizon: 'daily'日度, 'long_term'长期

# 特异波动率
rqdatac.get_specific_risk(order_book_ids, start_date, end_date, horizon='daily', model='v1')
```

## 现货 (上海黄金交易所)

```python
# 行情通过 rqdatac.get_price('AU9999.SGEX', ...) 获取
rqdatac.get_spot_benchmark_price(order_book_ids, start_date, end_date)  # 早午盘价
```

## 货币市场

```python
rqdatac.get_interbank_offered_rate(start_date, end_date)  # SHIBOR
# 国债回购行情通过 get_price 获取，代码如 '204001.XSHG' (GC001)
```

## 宏观经济

```python
rqdatac.get_reserve_ratio(start_date, end_date)    # 存款准备金率
rqdatac.get_money_supply(start_date, end_date)     # 货币供应量
rqdatac.get_macro_factor(factor_name, start_date, end_date)  # 宏观因子
```

## 另类数据

```python
rqdatac.get_consensus_expectation(order_book_ids, start_date, end_date, fields=None)  # 一致预期
rqdatac.get_news_sentiment(order_book_ids, start_date, end_date)  # 新闻舆情
rqdatac.get_esg_rating(order_book_ids, start_date, end_date)      # ESG评价
```

## 实时行情推送 (WebSocket)

```python
from rqdatac import LiveMarketDataClient

client = LiveMarketDataClient()
client.subscribe('tick_000001.XSHE')      # 订阅tick
client.subscribe('bar_000001.XSHE')       # 订阅1分钟线
client.subscribe('bar_000001.XSHE_3m')    # 订阅3分钟线
client.unsubscribe('tick_000001.XSHE')    # 取消订阅

# 阻塞监听
for market in client.listen():
    print(market)

# 非阻塞监听
client.listen(handler=lambda msg: print(msg))
```
