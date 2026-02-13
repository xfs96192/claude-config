# 可转债 API 参考

所有可转债专有API通过 `rqdatac.convertible` 模块调用。

## 合约信息

```python
rqdatac.convertible.all_instruments(date=None)     # 所有可转债
rqdatac.convertible.instruments(order_book_ids)     # 基础信息
rqdatac.convertible.instruments(order_book_ids).coupon_rate_table()  # 票面利率表
rqdatac.convertible.instruments(order_book_ids).option(option_type=None)  # 赎回/回售条款
# option_type: 'call'赎回, 'put'回售, None全部
```

## 转股/强赎/回售

```python
rqdatac.convertible.get_conversion_price(order_book_ids, start_date, end_date)  # 转股价
rqdatac.convertible.get_conversion_info(order_book_ids, start_date, end_date)   # 转股规模变动
rqdatac.convertible.get_call_info(order_book_ids, start_date, end_date)         # 强赎信息
rqdatac.convertible.get_call_announcement(order_book_ids, start_date, end_date) # 赎回公告
rqdatac.convertible.get_put_info(order_book_ids, start_date, end_date)          # 回售信息
rqdatac.convertible.get_cash_flow(order_book_ids, start_date, end_date)         # 现金流
rqdatac.convertible.is_suspended(order_book_ids, start_date, end_date)          # 停牌
```

## 行业/估值/衍生指标

```python
rqdatac.convertible.get_instrument_industry(order_book_ids, source='citics', level=1, date=None)
rqdatac.convertible.get_industry(industry, source='citics', date=None)
rqdatac.convertible.get_close_price(order_book_ids, start_date, end_date, fields=None)
# fields: 'clean_price'净价, 'dirty_price'全价
rqdatac.convertible.get_accrued_interest_eod(order_book_ids, start_date, end_date)  # 应计利息
rqdatac.convertible.get_indicators(order_book_ids, start_date, end_date, fields=None)  # 衍生指标
rqdatac.convertible.get_credit_rating(order_book_ids, start_date, end_date, institutions=None)
rqdatac.convertible.get_std_discount(order_book_ids, start_date, end_date)  # 标准券折算率
```
