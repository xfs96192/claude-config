---
name: xfs-market-data
description: 查询兴银理财市场数据库（xfs-market），通过 REST API 调用 https://market.xiafansheng.com 获取金融时间序列数据。覆盖9大类400+指标：A股指数(000300.SH/000016.SH/中证指数等)、中债国债/国开债到期收益率曲线(E1xxx)、宏观经济数据(CPI/PMI/GDP/M2/社融，EMM/EMI/EMG开头)、SHIBOR/DR007/IRS资金利率、汇率、商品期货、可转债指数、海外指数。当用户问到查询市场数据、A股走势、债券收益率、宏观经济数据、CPI/PMI/GDP、利率数据、汇率商品价格、市场指标、xfs-market、市场数据库时务必使用此skill。支持搜索指标、获取时间序列、新增删除指标、触发数据更新。
---

# XFS Market Data Skill

兴银理财多资产投资部市场数据库的远程调用skill。数据库由 iChoice/EMQuantAPI 拉取，每个工作日 17:00 自动更新。

## API 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://market.xiafansheng.com/api` |
| 网页 UI | `https://market.xiafansheng.com` |
| 写操作 API Key | `xfs-market-admin-2026`（仅本人使用） |
| 数据更新频率 | 周一至周五 17:00 自动 smart 更新 |

## 数据分类与代码识别规则

| 分类 | 代码示例 | 数据源 | 默认字段 |
|------|---------|-------|---------|
| 权益（A股指数） | `000300.SH`, `000016.SH`, `399006.SZ` | CSD | `CLOSE`, `PETTM` |
| 债券（中债收益率） | `E1000183`（30年）, `E1701667`（0年） | EDB | `value` |
| 债券（中债指数） | `CBA00101.CS` 中债综合财富 | CSD | `CLOSE` |
| 宏观 | `EMM00072301`（CPI同比）, `EMG*`, `EMI*` | EDB | `value` |
| 资金 | `Shibor3M.IR`, `DR007.IB` | CSD | `CLOSE` |
| 外汇 | `USDCNY.FX` 等 | CSD | `CLOSE` |
| 商品 | 期货代码 | CSD | `CLOSE` |
| 海外 | 国际指数 | CSD | `CLOSE` |
| 可转债 | 转债指数 | CSD | `CLOSE` |

代码识别：
- `EMM*` / `EMG*` / `EMI*` / `E1xxx` / `E17xxx` → EDB
- 含 `.SH/.SZ/.CSI/.SWI/.IB/.IR/.CS/.EI/.FX` → CSD

## 典型查询场景

### 场景 1：获取某指标的时间序列

**用户问**: "帮我拉一下沪深300过去一年的收盘价"

```python
import requests
import pandas as pd

r = requests.get(
    "https://market.xiafansheng.com/api/indicators/000300.SH/timeseries",
    params={"field": "CLOSE", "start": "2024-01-01", "end": "2024-12-31"}
)
data = r.json()["data"]
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')
```

### 场景 2：搜索某主题指标

**用户问**: "数据库里有哪些 CPI 相关的指标"

```python
r = requests.get(
    "https://market.xiafansheng.com/api/indicators",
    params={"search": "CPI", "page_size": 50}
)
items = r.json()["items"]
for ind in items:
    print(f"{ind['ichoice_code']}: {ind['name']} ({ind['data_count']}条, 至{ind['last_date']})")
```

### 场景 3：数据库总览

**用户问**: "看一下市场数据库现状"

```python
r = requests.get("https://market.xiafansheng.com/api/stats").json()
print(f"指标总数: {r['total_indicators']}")
print(f"有数据指标: {r['indicators_with_data']} ({r['data_completeness']:.1f}%)")
print(f"数据点: {r['total_data_points']:,}")
print(f"最新数据: {r['latest_data_date']}")
print(f"上次成功更新: {r['last_successful_update']}")
print("分类分布:", r['indicators_by_category'])
```

### 场景 4：批量获取多个指标用于分析

**用户问**: "把沪深300、中证500、上证50的最近一年走势画在一张图"

```python
import requests, pandas as pd

def get_series(code, field="CLOSE", start="2024-01-01"):
    r = requests.get(
        f"https://market.xiafansheng.com/api/indicators/{code}/timeseries",
        params={"field": field, "start": start}
    )
    df = pd.DataFrame(r.json()["data"])
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index('date')['value'].rename(code)

df = pd.concat([
    get_series("000300.SH"),
    get_series("000905.SH"),
    get_series("000016.SH"),
], axis=1).ffill()

# 然后用 matplotlib 画图
```

### 场景 5：查中债国债收益率曲线

**用户问**: "查下10年期国债到期收益率"

```python
# 10年期国债到期收益率的 iChoice 代码（需先搜索确认）
r = requests.get(
    "https://market.xiafansheng.com/api/indicators",
    params={"search": "国债到期收益率:10年"}
).json()
codes = [(i['ichoice_code'], i['name']) for i in r['items']]
# 取第一个匹配
yield_code = codes[0][0]
ts = requests.get(
    f"https://market.xiafansheng.com/api/indicators/{yield_code}/timeseries",
    params={"start": "2023-01-01"}
).json()
```

### 场景 6：新增指标（写操作）

**用户问**: "把美国核心 CPI 加入数据库（代码 EMG00135050）"

```python
r = requests.post(
    "https://market.xiafansheng.com/api/indicators",
    headers={"X-API-Key": "xfs-market-admin-2026"},
    json={
        "category": "海外",
        "name": "美国核心CPI同比",
        "ichoice_code": "EMG00135050",
        "fields": None  # 留空：EDB 自动用 value
    }
)
print(r.json())
# 下次 17:00 自动更新时会拉 2000 年至今历史
```

### 场景 7：手动触发更新

**用户问**: "刚加了几个指标，立刻拉历史数据"

```python
r = requests.post(
    "https://market.xiafansheng.com/api/update",
    headers={"X-API-Key": "xfs-market-admin-2026"},
    json={"update_type": "smart"}  # smart/full/incremental/retry
)
# 返回后台异步执行，查进度：
status = requests.get("https://market.xiafansheng.com/api/update/status").json()
```

## API 端点参考

### 只读端点（无需 API Key）

| 端点 | 说明 |
|------|------|
| `GET /api/stats` | 数据库总览（指标数、完整度、最新日期、近14天更新次数） |
| `GET /api/categories` | 9大分类及各自指标数 |
| `GET /api/indicators?search=&category=&has_data=&page=&page_size=` | 搜索/分页查询指标 |
| `GET /api/indicators/{code}` | 单指标详情（含字段、首末日期、数据条数、最近5条更新日志） |
| `GET /api/indicators/{code}/timeseries?field=&start=&end=` | 时间序列数据 |
| `GET /api/logs?status=failed&limit=50` | 最近更新日志（可按 status 过滤） |
| `GET /api/health` | 健康检查 |

### 写操作端点（需要 `X-API-Key: xfs-market-admin-2026` Header）

| 端点 | 说明 |
|------|------|
| `POST /api/indicators` | 新增指标（body: `{category, name, ichoice_code, fields}`），下次更新拉历史 |
| `DELETE /api/indicators/{code}` | 删除指标和所有数据 |
| `POST /api/update` | 触发更新（body: `{update_type: "smart\|full\|incremental\|retry"}`） |
| `GET /api/update/status` | 查询更新进度（任何人可读） |

## 操作准则

1. **优先用搜索而不是猜代码**：如果用户说"CPI"，先 `GET /api/indicators?search=CPI` 找出准确代码，再调时间序列。
2. **时间序列默认返回所有字段**：不指定 `field` 参数时返回该指标第一个字段。多字段指标（如`000300.SH`同时有CLOSE和PETTM）要明确指定。
3. **大数据量分页**：搜索类查询使用 `page_size` 控制，默认50，最大500。
4. **写操作要谨慎**：新增/删除/更新前要跟用户确认。删除是不可逆的（会清除该指标所有历史数据）。
5. **本地缓存**：长期同一会话查询多次同代码，可以缓存 JSON 结果避免重复请求。
6. **错误处理**：API 错误返回 HTTP 4xx/5xx + `{"detail": "..."}`，请 raise_for_status 后再解析。

## 给用户的输出建议

- 数据查询返回后，用 pandas DataFrame 整理，截取头尾几行展示给用户
- 多于 20 条数据时建议输出走势统计（首末值、最大/最小、均值），完整数据存为 csv 给用户引用
- 显示数据时附加 "数据源：xfs-market 数据库（market.xiafansheng.com），最新到 YYYY-MM-DD" 标注

## 注意事项

- 本数据库为兴银理财多资产投资部内部使用，请勿外传 API Key
- 数据延迟：日度数据通常 T+0 当天 17:00 后入库，宏观月度数据 iChoice 公布后入库
- 部分代码可能因 iChoice 订阅级别返回空，请用搜索API确认代码是否有效
