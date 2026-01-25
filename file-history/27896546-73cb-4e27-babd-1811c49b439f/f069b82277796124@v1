# 市场观点美化 - Wind数据生成程序

## 📋 文件概览

| 文件名 | 用途 | 何时使用 |
|---|---|---|
| `test_wind_connection.py` | 测试Wind连接和代码 | **首次使用前** |
| `generate_tables_from_wind.py` | 主程序 - 生成Excel | **每次生成数据时** |
| `程序使用说明.md` | 详细使用手册 | 遇到问题时查阅 |

## 🚀 快速开始（3步）

### 步骤1：测试环境
```bash
python test_wind_connection.py
```

**预期结果：**
```
[测试1] Wind连接状态
✓ Wind连接成功

[测试2] 日度行情数据获取
✓ 上证指数 (000001.SH): 获取到 5 个交易日数据
✓ 标普500 (SPX.GI): 获取到 5 个交易日数据
...
```

如果有 ❌ 失败项，请先解决后再继续。

### 步骤2：修改EDB代码

打开 `generate_tables_from_wind.py`，找到第59-68行：

```python
EDB_CODES = {
    "M0017142": "中债国债10年",  # ⚠️ 需要替换为实际代码
    "M0017143": "中债国开债10年",
    ...
}
```

**如何查询正确的EDB代码：**

方法A - Wind终端：
1. 打开Wind终端
2. 搜索"中债国债10年收益率"
3. 查看指标详情中的代码

方法B - Excel：
1. 在Excel中输入: `=EDB("中债国债10年", "2023-01-01", "2026-01-22")`
2. 查看函数帮助中的实际代码

### 步骤3：运行主程序
```bash
python generate_tables_from_wind.py
```

**预期输出：**
```
[1/6] 初始化Wind连接...
✓ Wind连接成功

[2/6] 生成近1月净值走势...
✓ 已生成: .../近1月净值走势.xlsx

[3/6] 获取周度数据...
[4/6] 计算衍生指标...
[5/6] 计算指标统计值和分位数...
✓ 已生成: .../指标值.xlsx

✓ 所有文件生成完成!
```

## 📊 生成的文件

### 1. 近1月净值走势.xlsx
- **位置：** `asset-analysis-real-data/近1月净值走势.xlsx`
- **行数：** 约20-25行（交易日）
- **列数：** 12列
- **内容：**
  - 11个资产的日度收盘价
  - 1个计算列（锁汇成本）

### 2. 指标值.xlsx
- **位置：** `asset-analysis-real-data/指标值.xlsx`
- **行数：** 31-37行（指标数）
- **列数：** 8列
- **内容：**
  - 权益类指标：PE、PB、股债性价比
  - 债券类指标：收益率、信用利差、期限利差
  - 汇率类指标：锁汇成本、中美利差等
  - 商品类指标：价差、美元指数等

## ⚙️ 程序配置

### 日期范围

在 `generate_tables_from_wind.py` 第46-48行：

```python
END_DATE = datetime.now()
START_DATE_DAILY = END_DATE - timedelta(days=30)  # 近1月
START_DATE_WEEKLY = END_DATE - timedelta(days=365 * 3)  # 近3年
```

### 输出目录

第44行：
```python
OUTPUT_DIR = "/Users/fanshengxia/Desktop/市场观点美化/asset-analysis-real-data"
```

## 🔍 数据来源说明

### ✅ 完全支持（Wind直接获取）

| 类型 | 具体指标 | Wind字段 |
|---|---|---|
| 股票 | 上证指数、标普500价格 | close |
| 估值 | PE、PB | pe_ttm, pb_lf |
| 债券 | 各类债券收益率 | EDB |
| 外汇 | USDCNY、掉期点、CNH | close |
| 商品 | 期货主连价格 | close |
| 指数 | VIX、美元指数 | close |

### ⚠️ 部分支持（需额外配置）

| 指标 | 原因 | 解决方案 |
|---|---|---|
| 中证转债转股溢价率 | 需特殊字段 | 联系Wind客服查询字段名 |
| 豆粕现货价格 | 可能需单独数据源 | 检查Wind是否有对应代码 |
| 豆粕持仓量 | 需期货持仓数据 | 使用 `oi` 字段 |

### ❌ 不支持（原Excel为手动输入）

在原Excel的股票指标sheet中，以下为固定值：
- 中证转债转股溢价率（E列）
- 中证转债纯债溢价率（F列）
- 中证转债隐含波动率（G列）

这些指标在当前程序中**不包含**。如需添加，需要：
1. 查询Wind对应的字段名
2. 在程序中添加获取逻辑

## 🐛 常见错误及解决

### 错误1：Wind未连接
```
❌ 错误: Wind未连接，请确保Wind终端已登录
```
**解决：** 打开Wind终端并登录

### 错误2：EDB错误码40520001
```
⚠️ 警告: Wind EDB返回错误码 40520001
```
**解决：** EDB代码不正确，需要替换为实际代码

### 错误3：数据缺失过多
**现象：** 生成的Excel中很多NaN
**原因：**
- 日期范围包含节假日/停牌
- Wind代码错误
- 数据权限不足

**解决：**
1. 缩短日期范围
2. 检查Wind代码
3. 联系Wind客服

### 错误4：ImportError: No module named 'WindPy'
```
ImportError: No module named 'WindPy'
```
**解决：** 安装WindPy
```bash
pip install WindPy
```

## 📖 详细文档

| 文档 | 说明 |
|---|---|
| `程序使用说明.md` | 完整的使用手册和配置说明 |
| `Excel公式详细映射表.md` | 所有Excel公式的技术文档 |
| `指标计算逻辑文档.md` | 指标的业务含义和计算逻辑 |

## 🔄 与原Excel的对应关系

### 数据流向
```
Wind API
  ↓
generate_tables_from_wind.py
  ↓
├─→ 近1月净值走势.xlsx  ←→  原Excel: 近一月指数走势 sheet
└─→ 指标值.xlsx         ←→  原Excel: 指标值 sheet
```

### 计算公式对应

| 指标 | 原Excel公式 | Python实现 |
|---|---|---|
| 股债性价比 | `=1/B3-所有指标!B7/100` | `(1/pe) - (bond_yield/100)` |
| 信用利差 | `=(C7-B7)*100` | `(credit-treasury)*100` |
| 锁汇成本 | `=-AG7/10000/AH7` | `-swap/10000/cnh` |
| 沪金价差 | `=W7-X7*U7/31.1035` | `shfe - comex*usdcny/31.1035` |

所有公式已验证与Excel一致！

## 📞 技术支持

- **Wind客服：** 400-820-9463
- **Wind API文档：** https://www.wind.com.cn/API/Python.html
- **项目文档：** 见同目录下的其他.md文件

## 📝 版本历史

### v2.0 (2026-01-22) - 当前版本
- ✅ 完全基于真实Excel公式
- ✅ 移除所有模拟数据
- ✅ 添加完整的错误处理
- ✅ 优化Excel格式（边框、颜色、列宽）
- ✅ 添加测试脚本

### v1.0 (初始版本)
- 包含模拟数据功能
- 部分计算公式与Excel不一致

---

**推荐使用流程：**
1. 首次使用：运行 `test_wind_connection.py` 检查环境
2. 修改EDB代码为实际代码
3. 运行 `generate_tables_from_wind.py` 生成数据
4. 检查生成的Excel文件
5. 如有问题，查阅 `程序使用说明.md`
