# 市场观点美化 - Python数据生成程序使用说明

## 项目概述

本项目提供基于Wind API的Python程序，用于自动生成市场观点分析所需的两个核心Excel文件：

1. **近1月净值走势.xlsx** - 最近1个月各类资产的日度行情数据
2. **指标值.xlsx** - 各类资产的最新指标值、历史统计和分位数

---

## 文件说明

### 核心文件

| 文件名 | 说明 |
|---|---|
| `generate_market_data.py` | 主程序 - 从Wind获取数据并生成Excel文件 |
| `指标计算逻辑文档.md` | 详细的指标计算逻辑和公式说明 |
| `README.md` | 本使用说明文档 |

### 数据文件

| 文件名 | 说明 | 更新频率 |
|---|---|---|
| `近1月净值走势.xlsx` | 最近1个月日度行情 | 每日 |
| `指标值.xlsx` | 指标值和历史统计 | 每周 |
| `市场观点美化数据源-自动更新.xlsx` | 原始Excel文件(含Wind公式) | 手动更新 |

---

## 环境准备

### 1. 安装Python依赖

```bash
pip install pandas numpy openpyxl WindPy
```

**依赖说明:**
- `pandas`: 数据处理
- `numpy`: 数值计算
- `openpyxl`: Excel文件读写
- `WindPy`: Wind金融终端Python接口

### 2. Wind终端要求

**必需条件:**
- 已安装Wind金融终端
- Wind终端已登录
- 具有相应数据权限

**验证Wind API:**
```python
from WindPy import w
w.start()
w.isconnected()  # 返回True表示连接成功
```

---

## 快速开始

### 运行程序

```bash
cd /Users/fanshengxia/Desktop/市场观点美化
python generate_market_data.py
```

### 预期输出

```
============================================================
市场观点美化 - 数据生成程序
============================================================
Wind API已初始化

开始生成: 近1月净值走势.xlsx
日期范围: 2025-12-22 至 2026-01-22
获取 12 个资产的行情数据...
✓ 已生成: /Users/fanshengxia/Desktop/市场观点美化/asset-analysis-real-data/近1月净值走势.xlsx
  - 行数: 23
  - 列数: 13
✓ 已美化格式: .../近1月净值走势.xlsx

开始生成: 指标值.xlsx
日期范围: 2023-01-22 至 2026-01-22 (周度数据)
获取股票估值数据...
获取债券收益率数据...
计算衍生指标...
计算统计指标...
✓ 已生成: .../指标值.xlsx
  - 指标数量: 12
✓ 已美化格式: .../指标值.xlsx

============================================================
✓ 所有文件生成完成!
============================================================

输出文件:
  1. .../近1月净值走势.xlsx
  2. .../指标值.xlsx
```

---

## 程序功能详解

### 1. 数据获取模块 (`WindDataFetcher`)

#### 主要方法

##### `get_daily_prices(codes, start_date, end_date)`
获取日度收盘价数据

**参数:**
- `codes`: Wind代码列表，如 `["000001.SH", "SPX.GI"]`
- `start_date`: 开始日期，格式 `"YYYY-MM-DD"`
- `end_date`: 结束日期，格式 `"YYYY-MM-DD"`

**返回:**
- DataFrame，index为日期，columns为资产代码

**使用示例:**
```python
fetcher = WindDataFetcher()
df = fetcher.get_daily_prices(
    codes=["000001.SH", "SPX.GI"],
    start_date="2025-12-01",
    end_date="2026-01-22"
)
```

##### `get_weekly_data(codes, start_date, end_date)`
获取周度数据（用于近3年历史数据）

##### `get_valuation_data(codes, start_date, end_date)`
获取估值指标（PE、PB）的周度数据

**返回:**
```python
{
    "PE": DataFrame,  # PE数据
    "PB": DataFrame   # PB数据
}
```

##### `get_edb_data(edb_codes, start_date, end_date)`
获取经济数据库（EDB）指标，主要用于债券收益率

**参数:**
- `edb_codes`: 字典，如 `{"中债国债10年": "M1004263"}`

---

### 2. 指标计算函数

#### `calculate_equity_bond_ratio(pe, bond_yield)`
计算股债性价比

**公式:**
```
股债性价比 = (1/PE) - (国债收益率/100)
```

**含义:** 股票盈利收益率与无风险利率的差值，数值越大表示股票相对债券越有吸引力

#### `calculate_credit_spread(credit_yield, treasury_yield)`
计算信用利差（基点）

**公式:**
```
信用利差(bp) = (信用债收益率 - 国债收益率) × 100
```

#### `calculate_term_spread(long_yield, short_yield)`
计算期限利差（基点）

**公式:**
```
期限利差(bp) = (长期收益率 - 短期收益率) × 100
```

#### `calculate_fx_hedging_cost(us_rate, cn_rate, spot_rate)`
计算锁汇成本

**公式:**
```
锁汇成本 = (美国利率 - 中国利率)/100 + 即期汇率
```

**含义:** 基于利率平价理论的远期汇率估计

#### `calculate_percentile(series, value, reverse)`
计算分位数

**参数:**
- `series`: 历史数据序列
- `value`: 当前值
- `reverse`: 是否反转（对于"越低越好"的指标设为True）

**返回:** 0-1之间的分位数

---

### 3. 文件生成函数

#### `generate_recent_prices_file(fetcher, output_path)`
生成近1月净值走势Excel文件

**生成逻辑:**
1. 计算日期范围（当前日期往前推30天）
2. 获取所有资产的日度收盘价
3. 将Wind代码列名替换为中文资产名称
4. 保存为Excel文件

**输出列:**
- 日期
- 上证指数、中证转债、标普500
- 7-10年国开、1-3年高信用等级债券财富、10年期美国国债收益率
- USDCNY、沪金、螺纹钢、原油、豆粕
- 锁汇成本（计算值）

#### `generate_indicators_file(fetcher, output_path)`
生成指标值Excel文件

**生成逻辑:**
1. 获取近3年周度数据
   - 股票估值数据（PE、PB）
   - 债券收益率数据（EDB）
2. 计算衍生指标
   - 股债性价比
   - 信用利差、期限利差
3. 对每个指标计算统计值
   - 当前值（最新一期）
   - 最大值、最小值、中位数
   - 当前分位点（0-1）
4. 保存为Excel文件

**输出列:**
- 大类资产
- 子类资产
- 观察指标（近三年）
- 当前值
- 最大值
- 最小值
- 历史中位数
- 当前分位点

---

## Wind代码配置

### 修改资产列表

在 `generate_market_data.py` 文件开头的配置区域修改：

```python
# 指数行情代码
EQUITY_CODES = {
    "上证指数": "000001.SH",
    "中证转债": "000832.CSI",
    "标普500": "SPX.GI"
    # 添加新资产: "资产名称": "Wind代码"
}

# 债券收益率EDB代码
BOND_YIELD_EDB = {
    "中债国债10年": "M1004263",  # ⚠️ 需要替换为实际的Wind EDB代码
    "中债国开债10年": "M1004264",
    # ... 其他代码
}
```

**注意:** 债券收益率的EDB代码需要根据实际Wind终端中的代码进行替换。

### 查询Wind代码的方法

1. **在Wind终端中查询:**
   - 打开Wind终端
   - 使用"代码查询"功能
   - 搜索资产名称获取代码

2. **在Excel中查询:**
   ```excel
   =w("000001.SH", "windcode,sec_name")
   ```

3. **在Python中查询:**
   ```python
   from WindPy import w
   w.start()
   data = w.wss("000001.SH", "windcode,sec_name")
   ```

---

## 无Wind环境运行

如果没有Wind终端或WindPy库，程序会自动使用模拟数据：

```
警告: WindPy未安装，将使用模拟数据
...
⚠️ 注意: 由于Wind API不可用,以上文件使用模拟数据生成
   请安装WindPy并登录Wind终端后重新运行以获取真实数据
```

**模拟数据特点:**
- 使用随机游走生成价格数据
- 基于合理的基准值（如上证指数3800点）
- 仅用于测试程序逻辑，不可用于实际分析

---

## 自定义修改

### 1. 修改历史数据范围

默认使用近3年数据计算分位数，如需修改：

```python
# 在 generate_indicators_file 函数中
start_date = end_date - timedelta(days=365*3)  # 改为365*5使用5年数据
```

### 2. 修改日度数据范围

默认获取最近1个月，如需修改：

```python
# 在 generate_recent_prices_file 函数中
start_date = end_date - timedelta(days=30)  # 改为60获取最近2个月
```

### 3. 添加新的计算指标

在 `generate_indicators_file` 函数的指标列表中添加：

```python
indicators.append({
    "大类资产": "权益",
    "子类资产": "上证指数",
    "观察指标": "新指标名称",
    "历史数据": 计算得到的pd.Series,
    "reverse": False  # 是否反转分位数
})
```

### 4. 修改Excel格式

在 `format_excel_file` 函数中修改：

```python
# 修改表头颜色
header_fill = PatternFill(start_color="4472C4", ...)  # 改为其他颜色代码

# 修改列宽限制
adjusted_width = min(max_length + 2, 50)  # 改为其他最大宽度
```

---

## 常见问题

### 1. Wind API连接失败

**错误信息:**
```
Wind API错误: 40520001
```

**解决方法:**
- 确认Wind终端已登录
- 检查网络连接
- 重启Wind终端
- 运行 `w.start()` 重新连接

### 2. 找不到某些Wind代码

**错误信息:**
```
Wind API错误: 数据不存在
```

**解决方法:**
- 检查Wind代码是否正确
- 确认账号有相应数据权限
- 在Wind终端中验证代码可用性

### 3. 数据缺失或NaN值过多

**可能原因:**
- 某些资产在特定日期停牌
- 债券收益率数据更新延迟
- EDB代码不正确

**解决方法:**
- 在Wind数据获取时使用 `Fill=Previous` 选项填充缺失值
- 检查数据源的更新频率
- 联系Wind客服确认数据可用性

### 4. 生成的分位数异常

**检查项:**
- 历史数据是否完整（至少需要52周数据）
- `reverse` 参数是否设置正确
- 当前值是否在历史数据范围内

---

## 程序扩展建议

### 1. 添加数据验证

```python
def validate_data(df: pd.DataFrame) -> bool:
    """验证数据完整性"""
    if df.isnull().sum().sum() > len(df) * 0.1:  # 缺失值超过10%
        print("警告: 数据缺失值过多")
        return False
    return True
```

### 2. 添加日志记录

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_generation.log'
)

logging.info("开始生成数据文件")
```

### 3. 添加数据缓存

```python
import pickle
from datetime import datetime

def cache_data(data, cache_file):
    """缓存数据避免重复获取"""
    with open(cache_file, 'wb') as f:
        pickle.dump({'data': data, 'timestamp': datetime.now()}, f)

def load_cache(cache_file, max_age_hours=24):
    """加载缓存数据"""
    if not os.path.exists(cache_file):
        return None

    with open(cache_file, 'rb') as f:
        cache = pickle.load(f)

    age = (datetime.now() - cache['timestamp']).total_seconds() / 3600
    if age > max_age_hours:
        return None

    return cache['data']
```

### 4. 添加邮件通知

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(subject, message):
    """发送邮件通知"""
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'

    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)
```

---

## 定期自动运行

### Linux/Mac 使用 cron

编辑crontab:
```bash
crontab -e
```

添加定时任务（每天早上9点运行）:
```
0 9 * * * cd /Users/fanshengxia/Desktop/市场观点美化 && /usr/bin/python3 generate_market_data.py >> /tmp/market_data.log 2>&1
```

### Windows 使用任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（如每天上午9点）
4. 操作：启动程序
   - 程序：`python.exe`
   - 参数：`generate_market_data.py`
   - 起始位置：`C:\Users\...\市场观点美化`

---

## 技术支持

### 相关文档
- [Wind Python API文档](https://www.wind.com.cn/API/Python.html)
- [pandas文档](https://pandas.pydata.org/docs/)
- [openpyxl文档](https://openpyxl.readthedocs.io/)

### 联系方式
如有问题，请查看项目GitHub仓库的Issues页面。

---

## 更新日志

### v1.0.0 (2026-01-22)
- 初始版本
- 支持生成近1月净值走势和指标值两个Excel文件
- 支持Wind API和模拟数据两种模式
- 包含完整的指标计算逻辑
- 支持自动Excel格式美化

---

## 许可证

本项目仅供内部使用。
