# 指数与ETF API 参考

## 指数估值指标

```python
rqdatac.index_indicator(order_book_ids, start_date, end_date, fields)
# fields: 'pe_ttm','pb_lf','dividend_yield' 等
```

## 指数成分股

```python
rqdatac.index_components(order_book_id, date=None, start_date=None, end_date=None, return_create_tm=False)
# date传入返回list, start_date/end_date传入返回DataFrame
```

## 指数权重

```python
rqdatac.index_weights(order_book_id, date=None)        # 月度更新
rqdatac.index_weights_ex(order_book_id, date=None, start_date=None, end_date=None)  # 日度

# 常用指数：000001.XSHG(上证综指), 399001.XSHE(深证成指), 000300.XSHG(沪深300),
# 000905.XSHG(中证500), 000852.XSHG(中证1000), 399006.XSHE(创业板指), 000016.XSHG(上证50)
```
