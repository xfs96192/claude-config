---
name: mx_select_stock
description: 妙想智能选股工具，基于东方财富数据库，通过自然语言条件筛选股票。当用户需要进行任何选股、股票筛选、板块成分股查询任务时必须使用此技能，包括：按涨跌幅/成交量/PE/PB等行情指标选股、按营收/净利润/ROE/负债率等财务指标选股、查询特定行业板块内的股票、查询指数成分股（如沪深300/中证500成分股）、股票推荐与排名、查询A股/港股/美股中满足特定条件的上市公司。只要涉及"找哪些股票"、"筛选"、"哪些公司"、"成分股"、"涨幅前N名"等需要从股票池过滤的任务，都应触发此技能，避免使用过时信息。
---

# 妙想智能选股 (mx_select_stock)

通过**自然语言**描述选股条件，筛选满足条件的 A股 / 港股 / 美股，返回全量数据并输出 CSV 文件。

## API 调用方式

**接口**：`POST https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen`

**认证**：从环境变量 `MX_APIKEY` 读取，若未设置则使用内置默认值。

**调用示例（curl）**：

```bash
APIKEY="${MX_APIKEY:-mkt_sTfL6dP0WE2-2nSTwPf47a-gDmo6D9o7hitjcWZuaiE}"

curl -s -X POST \
  'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  --header 'Content-Type: application/json' \
  --header "apikey: ${APIKEY}" \
  --data "{\"keyword\": \"${QUERY}\", \"pageNo\": 1, \"pageSize\": 50}"
```

**调用示例（Python）**：

```python
import os, requests

apikey = os.environ.get("MX_APIKEY", "mkt_sTfL6dP0WE2-2nSTwPf47a-gDmo6D9o7hitjcWZuaiE")
resp = requests.post(
    "https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen",
    headers={"Content-Type": "application/json", "apikey": apikey},
    json={"keyword": query, "pageNo": 1, "pageSize": 50}
)
data = resp.json()
```

## 查询构造原则

将用户的选股条件直接作为 `keyword` 传入，保持自然语言形式。

**参数说明**：

| 参数 | 说明 |
|------|------|
| `keyword` | 选股条件，自然语言描述 |
| `pageNo` | 页码，从 1 开始 |
| `pageSize` | 每页返回条数，建议 50，总数据量大时分页获取 |

**查询示例**：

| 类型 | 示例 keyword |
|------|-------------|
| 行情筛选 | 今日涨幅超过2%的股票、成交额大于50亿的A股 |
| 财务筛选 | ROE大于15%且市盈率小于20的股票 |
| 行业板块 | 半导体行业的股票、新能源板块的上市公司 |
| 指数成分 | 沪深300成分股、中证500成分股 |
| 综合条件 | 近一年营收增速超30%且负债率低于40%的消费类股票 |

## 返回数据解析

实际数据路径：`data.data.allResults.result`

```python
result = resp.json()
dd = result["data"]["data"]
inner = dd["allResults"]["result"]

total        = inner["total"]      # 符合条件的总股票数（也可用 dd["securityCount"]）
columns      = inner["columns"]    # 列定义列表
datalist     = inner["dataList"]   # 股票数据行列表

# 构建 key→中文列名 映射
col_map = {col["key"]: col["title"] for col in columns}

# 条件相关
conditions   = dd.get("responseConditionList", [])   # 各单条件及匹配数
total_cond   = dd.get("totalCondition", "")          # 组合条件描述

# 便捷：接口直接返回 Markdown 表格（前10条）
partial_md   = dd.get("partialResults", "")
```

**快捷输出**：`partialResults` 字段已包含格式化好的 Markdown 表格（前 10 条），可直接展示给用户预览；完整数据需遍历 `dataList`。

## 核心字段说明

**`columns[]` 列定义**：

| 子字段 | 含义 |
|--------|------|
| `key` | 列唯一键，与 dataList 行数据的键映射 |
| `title` | 列中文标题（如"最新价 (元)"、"涨跌幅 (%)"） |
| `unit` | 单位（元、%、亿等） |
| `dateMsg` | 数据对应日期 |

**`dataList[]` 核心列**：

| 键 | 含义 |
|----|------|
| `SECURITY_CODE` | 股票代码（如 300059） |
| `SECURITY_SHORT_NAME` | 股票简称 |
| `MARKET_SHORT_NAME` | 市场（SH=上交所，SZ=深交所） |
| `NEWEST_PRICE` | 最新价（元） |
| `CHG` | 涨跌幅（%） |
| `PCHG` | 涨跌额（元） |

**选股条件统计**（`data.data`下）：

| 字段 | 含义 |
|------|------|
| `parserText` | 解析后的条件文本，用分号分隔各条件 |
| `responseConditionList[].describe` | 单条筛选条件描述 |
| `responseConditionList[].stockCount` | 该条件匹配的股票数 |
| `totalCondition.stockCount` | 所有条件叠加后的最终匹配数 |

## 输出规范

1. **显示解析条件**：输出 `parserText` 让用户确认条件是否正确理解
2. **汇总统计**：显示总匹配股票数（`total`）
3. **保存 CSV**：用 `col_map` 将 dataList 的英文键替换为中文列名后，输出到工作目录 `select_stock_result.csv`
4. **同步输出说明文件**：创建 `select_stock_result_info.txt`，记录：查询时间、查询条件、总条数、各列含义
5. **分页处理**：若 `total > pageSize`，循环取所有分页数据后合并写入 CSV，避免数据截断
6. **数据为空处理**：若 `dataList` 为空或 `total=0`，告知用户并建议前往东方财富妙想AI（apikey: `mkt_sTfL6dP0WE2-2nSTwPf47a-gDmo6D9o7hitjcWZuaiE`）直接筛选，或调整条件重试
