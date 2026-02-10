# Plan: 集成iChoice数据源到MarketDataProvider

## Context
当前 `market_data_provider.py` 仅支持Wind API作为市场数据源。由于Wind终端并非总是可用（尤其Mac环境），需要增加iChoice (EMQuantAPI) 作为替代数据源，并设为默认。iChoice SDK路径: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`

## 修改文件

### 1. `config.py` (~line 134, API配置区域)
新增数据源配置:
```python
# 市场数据源配置 ('ichoice' 或 'wind')
DATA_SOURCE = 'ichoice'

# iChoice API配置
ICHOICE_USERNAME = 'xylczh0181'
ICHOICE_PASSWORD = 'ef465509'
ICHOICE_SDK_PATH = '/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3'
```
在底部 backward-compatible 变量区域导出新变量。

### 2. `market_data_provider.py` (主要重构)

#### 架构设计
保持 `MarketDataProvider` 类的公共接口不变（所有调用方无需改动），内部增加iChoice后端:

```
MarketDataProvider
├── __init__(source='ichoice')   # 新增source参数
├── connect()                     # 路由到Wind或iChoice
├── disconnect()                  # 路由
├── _connect_ichoice()            # 新增: iChoice登录
├── _connect_wind()               # 原有Wind连接逻辑
├── _map_code(code)               # 新增: Wind→iChoice代码映射
│
├── get_index_close()             # 内部路由
├── get_index_returns()           # 内部路由 (iChoice需从收盘价计算)
├── get_index_names()             # 内部路由
├── get_index_volatility()        # 内部路由 (已是手动计算,复用)
├── get_exchange_rate()           # 内部路由 (代码映射.EX→.IB)
├── get_bond_attributes()         # 内部路由 (iChoice可能字段不同)
├── wss()                         # 内部路由
└── wsd()                         # 内部路由
```

#### Wind→iChoice 代码映射表 (WIND_TO_ICHOICE)
已确认的映射:
| Wind Code | iChoice Code | 说明 |
|-----------|-------------|------|
| `885008.WI` | `809007.EI` | 万得中长期纯债型基金指数 |
| `885001.WI` | `809002.EI` | 万得偏股混合型基金指数 |
| `881001.WI` | `800000.EI` | 万得全A |
| `000832.CSI` | `000832.SH` | 中证转债 |

后缀自动转换规则 (对未在映射表中的代码):
- `.SI` → `.SWI` (申万行业指数)

不可用代码 (iChoice无对应):
- `885007.WI` - 万得混合债券型二级基金指数
- `NH0100.NHF` - 南华商品指数
- `SPTAUUSDOZ.IDC` - 伦敦金现 (可尝试 `AU0.SHF` 沪金替代)

待确认代码 (先尝试原码):
- `885005.WI` - 万得短期纯债型基金指数
- `885006.WI` - 万得混合债券型一级基金指数
- `H30269.CSI` - 红利低波

#### API对照实现

| 方法 | Wind实现 | iChoice实现 |
|------|---------|------------|
| `get_index_close` | `w.wsd(code, "close", start, end)` | `c.csd(code, "CLOSE", start, end, "Ispandas=1")` |
| `get_index_returns` | `w.wss(codes, "pct_chg_per", "startDate=X;endDate=Y")` | 从 `c.csd()` 取首尾收盘价计算 `(end/start-1)*100` |
| `get_index_names` | `w.wss(codes, "sec_name")` | `c.css(codes, "NAME", "TradeDate=today,Ispandas=1")` |
| `get_exchange_rate` | `w.wss(pair+".EX", "close", "tradeDate=X")` | `c.csd(pair+".IB", "CLOSE", date, date, "Ispandas=1")` 或 `c.css(pair+".IB", "CLOSE", "TradeDate=X,Ispandas=1")` |
| `get_bond_attributes` | `w.wss(codes, "municipalbondWind,perpetualornot")` | `c.css(codes, "MUNICIPALBOND,PERPETUAL", "Ispandas=1")` (字段名待验证, 失败则返回None并警告) |
| `wsd` (通用) | `w.wsd(codes, fields, start, end)` | `c.csd(codes, fields.upper(), start, end, "Ispandas=1")` |
| `wss` (通用) | `w.wss(codes, fields, options)` | `c.css(codes, fields.upper(), options转换)` |

#### iChoice返回值处理要点
- `c.csd()` 带 `Ispandas=1` 返回DataFrame，列: `CODES, DATES, CLOSE`等
- DATES列为字符串 `"YYYY/MM/DD"` 格式，需 `pd.to_datetime()` 转换
- 多代码时数据是长格式(stacked)，需pivot
- 错误时可能返回非DataFrame的EmQuantData对象，需检查 `isinstance(result, pd.DataFrame)`

#### iChoice连接注意事项
- 首次登录耗时较长(可达2-3分钟)
- 必须在结束时调用 `c.stop()` 释放连接
- `c.start("UserName=xxx,Password=xxx,ForceLogin=1")`

### 3. 不修改的文件
- `generate_report.py` - 无需改动 (通过MarketDataProvider接口调用)
- `calculate_all_benchmarks.py` - 无需改动 (通过MarketDataProvider接口调用)

## 实现步骤

1. **更新 `config.py`**: 添加 `DATA_SOURCE`, iChoice账号配置, 代码映射表
2. **重构 `market_data_provider.py`**:
   - 保留所有Wind实现代码 (原方法加 `_wind` 后缀)
   - 新增所有iChoice实现 (方法加 `_ichoice` 后缀)
   - 公共方法根据 `self._source` 路由
   - 添加代码映射逻辑
   - 添加 `disconnect()` 中iChoice的 `c.stop()` 调用
3. **更新 `get_instance()`**: 读取Config.DATA_SOURCE决定数据源

## 验证方法

1. 运行 `python market_data_provider.py` 测试脚本 (底部 `__main__` 块)
2. 测试各方法: get_index_close, get_index_returns, get_exchange_rate, get_index_names
3. 确认 generate_report.py 和 calculate_all_benchmarks.py 无需修改即可工作
