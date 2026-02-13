# A股 API 参考

## 财务数据

```python
# 季度财务信息 (point-in-time，避免未来数据)
rqdatac.get_pit_financials_ex(
    order_book_ids,          # str/list, 合约代码
    fields,                  # list, 财务字段 (见下方三大表字段)
    start_quarter,           # str, 起始报告期 如'2018q2'
    end_quarter,             # str, 截止报告期 如'2018q4'
    date=None,               # 查询日期，默认最新
    statements='latest',     # 'latest'最新一条 / 'all'所有记录
    market='cn'
)
# 示例：
rqdatac.get_pit_financials_ex(
    fields=['revenue','net_profit'],
    start_quarter='2018q2', end_quarter='2018q3',
    order_book_ids=['000001.XSHE','000048.XSHE']
)

# 财务快报
rqdatac.current_performance(order_book_ids, info_date=None, quarter=None, interval='1q', fields=None)

# 业绩预告
rqdatac.performance_forecast(order_book_ids, info_date=None, end_date=None, fields=None)
```

### 利润表主要字段
revenue(营业总收入), operating_revenue(营业收入), cost_of_goods_sold(营业成本), selling_expense(销售费用), ga_expense(管理费用), financing_expense(财务费用), r_n_d(研发费用), profit_from_operation(营业利润), profit_before_tax(利润总额), income_tax(所得税), net_profit(净利润), net_profit_parent_company(归属母公司净利润), basic_earnings_per_share(基本EPS), non_recurring_pnl(非经常性损益)

### 资产负债表主要字段
cash_equivalent(货币资金), bill_receivable(应收票据), inventory(存货), current_assets(流动资产合计), net_fixed_assets(固定资产净额), intangible_assets(无形资产), goodwill(商誉), total_assets(总资产), short_term_loans(短期借款), accts_payable(应付账款), current_liabilities(流动负债合计), long_term_loans(长期借款), bond_payable(应付债券), non_current_liabilities(非流动负债合计)

### 现金流量表主要字段
cash_from_selling(销售商品收到现金), cash_paid_for_goods(购买商品支付现金), net_operating_cash_flow(经营活动现金流量净额), cash_paid_for_assets(购建固定资产支付现金), net_investing_cash_flow(投资活动现金流量净额), cash_from_borrowing(取得借款收到现金), net_financing_cash_flow(筹资活动现金流量净额), net_cash_change(现金净增加额)

## 因子数据

```python
# 获取因子值 (200+衍生因子)
rqdatac.get_factor(
    order_book_ids,  # str/list
    factor,          # str/list, 因子名称
    start_date=None, end_date=None,
    universe=None,   # 股票池筛选
    expect_df=True
)
# 示例：
rqdatac.get_factor(['000001.XSHE','000002.XSHE'], 'debt_to_equity_ratio', '20180102', '20180103')
rqdatac.get_factor(['000001.XSHE'], ['MACD_DIFF','OBOS','AR'], '20200401', '20200402')

# 获取所有因子名称
rqdatac.get_all_factor_names(type=None)
# type: 'valuation'估值, 'growth'成长, 'profitability'盈利, 'structure'财务结构,
#       'cash_flow'现金流, 'technical_indicator'技术指标, 'obos_indicator'超买超卖 等
```

## 行业与板块分类

```python
# 获取板块股票列表
rqdatac.sector(code)  # code: 'Energy','Materials','Industrials','ConsumerDiscretionary',
                       #        'ConsumerStaples','HealthCare','Financials','InformationTechnology',
                       #        'TelecommunicationServices','Utilities','RealEstate'

# 获取行业股票列表 (支持国民经济行业分类)
rqdatac.industry(code)  # code: 'A01'-'T98'

# 获取行业分类概览 (中信/申万/证监会)
rqdatac.get_industry_mapping(source='citics_2019', date=None)
# source: 'citics_2019','citics','sws_2021','zjh_2012'

# 获取某行业股票列表
rqdatac.get_industry(industry, source='citics_2019', date=None)
# industry: 行业名称如'银行', 或行业代号

# 获取股票行业分类
rqdatac.get_instrument_industry(order_book_ids, source='citics_2019', level=1, date=None)

# 概念股
rqdatac.get_concept_list(start_date=None, end_date=None)
rqdatac.get_concept(concepts, start_date=None, end_date=None)
rqdatac.get_stock_concept(order_book_ids)
```

## 分红/拆股/复权

```python
rqdatac.get_dividend_info(order_book_ids, start_date=None, end_date=None)  # 分红详情
rqdatac.get_dividend(order_book_ids, start_date=None, end_date=None)       # 现金分红
rqdatac.get_dividend_amount(order_book_ids, start_quarter=None, end_quarter=None)  # 分红总额
rqdatac.get_split(order_book_ids, start_date=None, end_date=None)          # 拆股
rqdatac.get_ex_factor(order_book_ids, start_date=None, end_date=None)      # 复权因子
```

## 股本/停牌/ST

```python
rqdatac.get_shares(order_book_ids, start_date, end_date, fields=None)
# fields: 'total'总股本, 'circulation_a'流通A股, 'non_circulation_a'非流通A股,
#         'management_circulation'管理层持股(流通), 'non_management_circulation'非管理层持股(流通)

rqdatac.is_suspended(order_book_ids, start_date, end_date)    # 判断停牌
rqdatac.is_st_stock(order_book_ids, start_date, end_date)     # 判断ST
rqdatac.get_turnover_rate(order_book_ids, start_date, end_date, fields=None)
# fields: 'today'当日换手率, 'week'周, 'month'月, 'three_month', 'six_month', 'year', 'current_year'
```

## 资金流/融资融券/沪深港通

```python
rqdatac.get_capital_flow(order_book_ids, start_date, end_date, frequency='1d')
# frequency: '1d','1m','tick'

rqdatac.current_capital_flow_minute(order_book_ids)  # 最新分钟资金流

rqdatac.get_securities_margin(order_book_ids, start_date, end_date, fields=None)
# fields: 'margin_balance'融资余额, 'short_balance'融券余额, 'margin_repayment'融资偿还等

rqdatac.get_margin_stocks(date=None, exchange=None, margin_type='stock')  # 融资融券标的列表

rqdatac.get_stock_connect(order_book_ids, start_date, end_date, fields=None)  # 沪深股通持股
rqdatac.current_stock_connect_quota(connect=None, fields=None)  # 实时每日额度
```

## 其他A股数据

```python
rqdatac.get_main_shareholder(order_book_ids, start_date, end_date, is_total=False)  # 主要股东
rqdatac.get_private_placement(order_book_ids, start_date, end_date)   # 定增
rqdatac.get_allotment(order_book_ids, start_date, end_date)           # 配股
rqdatac.get_block_trade(order_book_ids, start_date, end_date)         # 大宗交易
rqdatac.get_holder_number(order_book_ids, start_date, end_date)       # 股东户数
rqdatac.get_abnormal_stocks(start_date, end_date, types=None)         # 龙虎榜
rqdatac.get_buy_back(order_book_ids, start_date, end_date)            # 回购
rqdatac.get_announcement(order_book_ids, start_date, end_date)        # 公告
rqdatac.get_audit_opinion(order_book_ids, start_quarter, end_quarter) # 审计意见
rqdatac.get_restricted_shares(order_book_ids, start_date, end_date)   # 限售解禁
rqdatac.get_leader_shares_change(order_book_ids, start_date, end_date)# 高管持股变动
rqdatac.get_incentive_plan(order_book_ids, start_date, end_date)      # 股权激励
rqdatac.get_share_transformation(predecessor=None)                     # 股票代码变更历史
rqdatac.get_symbol_change_info(order_book_ids)                         # 历史简称
rqdatac.get_special_treatment_info(order_book_ids)                     # ST处理历史
rqdatac.current_freefloat_turnover(order_book_ids)                     # 当日自由流通换手率
rqdatac.get_forecast_report_date(order_book_ids, start_quarter, end_quarter)  # 预约披露日
```
