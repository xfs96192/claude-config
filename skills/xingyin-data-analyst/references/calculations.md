# 业绩计算公式参考

## 年化收益率计算
```python
def annualized_return(timeseries):
    """
    年化收益率 = (期末净值/期初净值 - 1) / 天数 * 365
    """
    return (timeseries.iloc[-1] / timeseries.iloc[0] - 1) / \
           (timeseries.index[-1] - timeseries.index[0]).days * 365
```

## 年化波动率计算
```python
def annualized_volatility(timeseries):
    """
    年化波动率 = 日收益率标准差 * sqrt(365)
    """
    return np.std(timeseries.pct_change()) * np.sqrt(365)
```

## 最大回撤计算
```python
def max_drawdown(timeseries):
    """
    最大回撤 = (当前净值 - 历史最高净值) / 历史最高净值 的最小值
    """
    roll_max = timeseries.cummax()
    daily_drawdown = timeseries / roll_max - 1.0
    return daily_drawdown.min()
```

## 收益预测计算 (丰利合享/悦动稳享)

### 非标提前到期调整
```python
# 当非标资产提前到期时的收益调整
adjusted_yield = (holding_days * coupon + idle_days * 0.015) / total_days
# 0.015 = 趴账收益率 (RET_ON_ACCOUNT)
```

### 静态收益计算
```python
# 费后静态 = 费前静态 - (管理费 + 托管费 + 销售费)
费后静态 = 费前静态 - (管理费 + 托管费 + 销售费)

# 预期年化收益率
预期年化 = ((单位净值 * (1 + 费后静态 * 剩余天数/365)) - 1) * 365 / 运作天数
```

### 超额业绩报酬计算
```python
def cal_excess_compensation(row, forecast=True):
    """
    计算超额业绩报酬
    基于业绩基准分档计提
    """
    ret = row['预期年化收益率'] if forecast else row['累计年化']
    basis_lower = row['超额计提基准下限']  # 如 "3.5%(20%)"
    
    # 解析: 3.5%为基准, 20%为计提比例
    basis = float(basis_lower.split('(')[0][:-1]) / 100
    ratio = float(basis_lower.split('(')[1][:-2]) / 100
    
    excess = max(0, ret - basis)
    return excess * row['净资产(亿)'] * 10000 * ratio / row['单位净值']
```

## 持有期标签划分
```python
def get_holding_period_label(days):
    if days == 1:
        return '日盈'
    elif days < 30:
        return '<1M'
    elif days < 93:
        return '1M-3M'
    elif days < 186:
        return '3M-6M'
    elif days < 372:
        return '6M-1Y'
    else:
        return '>1Y'
```

## 规模加权业绩计算
```python
def weighted_performance(group, field):
    """
    加权平均 = Σ(字段值 * 规模) / Σ(规模)
    只计算字段非空的产品
    """
    mask = group[field].notna()
    if not mask.any():
        return np.nan
    weights = group.loc[mask, '净资产(亿)']
    values = group.loc[mask, field]
    return (values * weights).sum() / weights.sum()
```

## 费前业绩还原
```python
# 费前 = 费后 + 管理费 + 托管费 + 销售费
费前年化 = 费后年化 + df[['销售费', '管理费', '托管费']].sum(axis=1)
```

## 业务参数
```python
RET_ON_ACCOUNT = 0.015   # 趴账收益率
LEVERAGE_COST = 0.02     # 杠杆成本
XINGHE4_COST = 0.07      # 兴合4号成本
```
