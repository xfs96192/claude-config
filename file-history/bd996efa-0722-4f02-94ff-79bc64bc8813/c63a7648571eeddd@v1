---
name: xingyin-data-analyst
description: 兴银理财多资产投资部数据统计分析助手。用于分析部门产品的规模、业绩、持仓、投资经理归因等数据。当用户询问"统计部门规模"、"产品业绩"、"持仓分析"、"投资经理产品数据"、"渠道分布"、"招商产品"、"外币产品"等相关问题时触发。支持从产品运作概览、持仓盈亏、净值数据、业绩指标等多个数据源进行查询和计算。
---

# 兴银理财多资产投资部数据分析

## 数据目录结构

```
/Users/fanshengxia/Desktop/周报V2/
├── 数据/                              # 主数据目录
│   ├── 底层数据汇总.xlsx              # 主参考数据(产品分类、标签)
│   ├── 主投资经理标签.xlsx            # 投资经理映射
│   ├── 指数业绩基准数据.xlsx          # 市场基准数据
│   ├── 产品净值数据/                  # 每日NAV文件
│   ├── 产品业绩指标数据/              # 周度业绩(内部产品业绩_{DATE}.xlsx)
│   ├── 产品运作概览数据-母产品/       # 仅母产品运作概览
│   ├── 产品运作概览数据-母子产品/     # 母子产品完整运作概览
│   ├── 周度更新数据/                  # 周度报表(渠道、战报、持仓等)
│   ├── 资产持仓数据/                  # 8资产大表
│   └── 收益测算数据/                  # 收益预测输出
├── 输出结果/                          # 周报输出(输出结果{DATE}.xlsx)
├── config.py                         # 配置文件(日期、路径、参数)
└── utils.py                          # 工具函数(年化收益、波动率、最大回撤)
```

## 核心数据文件说明

### 1. 产品运作概览 (最常用)
- 路径: `数据/产品运作概览数据-母产品/产品运作概览{DATE}-仅母产品.xlsx`
- 关键字段: 产品简称、净资产(亿)、单位净值、累计年化、本期年化、杠杆、组合久期、组合静态、权益仓位、运作天、剩余天、产品经理、多资产品类、形态、是否招商

### 2. 持仓盈亏明细
- 路径: `数据/周度更新数据/持仓盈亏明细列表_{DATE}.xlsx`
- 关键字段: 产品代码、债券简称、新版资产小类、日终市值(元)-产品法估值、持仓成本(元)、持有期收益

### 3. 周度更新数据文件
| 文件名模式 | 用途 |
|-----------|------|
| 各渠道保有量{DATE}.xlsx | 渠道分布和规模 |
| 战报底表(v2){DATE}.xlsx | 销量和规模变化 |
| 产品运作概览{DATE}.xlsx | 完整产品列表 |
| 理财产品信息查询{DATE}.xlsx | 产品信息(币种、周期) |
| 委外产品概览(团队视角){DATE}.xlsx | 委外产品 |

### 4. 输出结果文件 (周报)
- 路径: `输出结果/输出结果{DATE}.xlsx`
- Sheet列表: 分渠道余额、渠道明细、产品规模、本周新发产品、系列产品业绩-费后加权、投资经理维度产品规模和数量、8.资产大表等

## 投资经理团队

```python
# 一处 (人民币团队)
first = ['徐莹', '胡艳婷', '姜锡峰', '朱轶伦', '李佳航', '苏文津', '夏凡盛', '黄亦尧']

# 二处 (人民币团队)  
second = ['严泓', '高翰昆', '薛纪晔', '任雁', '周仕盈', '罗谨深']

# 外币团队
third = ['杨漠', '余洁雅', '张玉杰', '廖炯臣']

# 投资助理关系
# 李佳航 -> 姜锡峰的助理
# 夏凡盛 -> 徐莹的助理
# 黄亦尧 -> 薛纪晔的助理
# 罗谨深 -> 高翰昆的助理
# 束钰、薛家云 -> 朱轶伦的助理
```

## 产品分类体系

### 产品形态判断
```python
def map_product_xingtai(series):
    if series['产品开放形式'] == '封闭式':
        return '封闭'
    elif series['周期属性'] == '客户周期':
        return '客户周期'
    elif series['周期天数'] == 1:
        return '日开'
    else:
        return '定开'
```

### 多资产品类 -> 母分类 -> 总分类
从 `底层数据汇总.xlsx` 的 `销售战报系列分类` sheet读取映射关系:
- 中低波稳健产品: 悦动稳享短持、悦动稳/纯享、优先股短持、丰利/增盈
- 中高波市值产品: 和瑞BOF、悦动短持/定开、逸动短持、灵动短持、兴动短持
- 外币产品: 外币低波、外币市值

## 常用分析操作

### 1. 读取产品运作概览
```python
import pandas as pd
from config import Config

# 读取母产品概览
df = pd.read_excel(Config.get_overview_parent_file(), index_col=0)

# 读取母子产品完整概览
df_all = pd.read_excel(Config.get_overview_history_file(), index_col=0)
```

### 2. 剔除非我部产品
```python
def del_Innovation_department(df):
    # 剔除量化和结构性产品
    df = df[~df['多资产品类'].isin(['结构性理财R2+', '结构性理财R3', '结构性理财R4', '量化系列'])]
    # 剔除创新部经理产品
    df = df[df['产品经理'].map(lambda x: 
        sum([k not in ['王浩', '张雅婕', '孙新华'] for k in str(x).split(',')]) != 0)]
    return df
```

### 3. 计算规模和数量统计
```python
# 按品类统计
result = df.groupby(['总分类', '母分类']).agg({
    '净资产(亿)': ['sum', 'count']
})
result.columns = ['规模(亿)', '数量']
```

### 4. 投资经理维度统计(处理双挂)
```python
def adjust_manager_aum(df):
    """处理双挂产品,规模按人头分摊"""
    df['双挂调整后规模'] = df['净资产(亿)']
    for idx in df.index:
        managers = df.loc[idx, '产品经理'].split(',')
        if len(managers) > 1:
            df.loc[idx, '双挂调整后规模'] /= len(managers)
    return df
```

### 5. 计算加权平均业绩
```python
def weighted_avg(group, field):
    mask = group[field].notna()
    if mask.any():
        weights = group.loc[mask, '净资产(亿)']
        return (group.loc[mask, field] * weights).sum() / weights.sum()
    return np.nan
```

### 6. 读取持仓数据
```python
# 持仓金额默认使用"日终市值(元)-产品法估值"字段
chicang = pd.read_excel(f'{Config.WEEKLY_DATA_DIR}/持仓盈亏明细列表_{date}.xlsx')
chicang['规模(亿)'] = chicang['日终市值(元)-产品法估值'] / 1e8
```

## 渠道标签判断

```python
def get_zhaoshang_label(channels):
    """判断招商渠道标签"""
    if '招商银行股份有限公司' in channels:
        if len(channels - {'-', '招商银行股份有限公司'}) == 0:
            return '招商独有'
        return '招商共有'
    return '非招商'
```

## 业绩计算公式

详见 `references/calculations.md`

## 注意事项

1. **母子产品处理**: 统计规模时默认使用母产品，避免重复计算
2. **日期格式**: 文件名使用 `YYYYMMDD` 格式
3. **美元产品汇率**: 从Wind获取USDCNY汇率转换
4. **数据验证**: 运行前检查 `config.py` 中的 `YUNZUOGAILAN_DATE` 是否正确
