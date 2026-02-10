# 计划：generate_report.py 从脚本式改为函数式

## 核心原则
- **逻辑和执行结果与改前100%一致**
- 只改结构，不改业务逻辑
- 小步骤修改，每一步都可验证

## 设计思路

### 数据容器：`ReportContext` dataclass
将当前散落在模块命名空间的共享状态，统一收到一个数据类中：

```python
@dataclass
class ReportContext:
    data_loader: DataLoader
    market_data: MarketDataProvider
    nav_data: pd.DataFrame           # Part 4
    nav_pivot: pd.DataFrame          # Part 4
    product_info: pd.DataFrame       # Part 4
    classification_df: pd.DataFrame  # Part 4
    classification_ye: pd.Series     # Part 4
    parent_sort: pd.DataFrame        # Part 4
    yunzuogailan_all: pd.DataFrame   # Part 6
    channel_df: pd.DataFrame         # Part 6
    rank_here: list                  # Part 6
    date: str                        # Part 6
```

### 每个报表部分 → 一个函数
Part 7-21 各提取为独立函数，签名统一：
```python
def generate_channel_report(ctx: ReportContext, writer: pd.ExcelWriter) -> dict:
    """第七部分：渠道分析 → 写入 '1、分渠道余额', '渠道明细'"""
    # ... 原 Part 7 代码 ...
    return {'Channel_result1': ..., 'Channel_result2': ...}  # 供 Part 21 使用的中间结果
```

返回 dict 只包含后续 Part 21（AI总结）需要的中间变量。

### main() 串联
```python
def main():
    ctx = init_context()                       # Part 2+4+5+6
    writer = pd.ExcelWriter(Config.get_current_output_writer(ctx.date))

    results = {}
    steps = [
        ("渠道分析", generate_channel_report),
        ("产品规模", generate_scale_report),
        ...
    ]
    for name, func in steps:
        print(f"\n📈 {name}...")
        try:
            ret = func(ctx, writer)
            if ret:
                results.update(ret)
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            raise

    generate_summary_text(ctx, writer, results)  # Part 21
    writer.close()
```

## 函数拆分清单

| 函数名 | 原Part | 写入sheet | 返回给Part21 |
|--------|--------|-----------|-------------|
| `init_context()` | 2+4+5+6 | 无 | ReportContext |
| `generate_channel_report()` | 7 | 1、分渠道余额, 渠道明细 | Channel_result1 |
| `generate_scale_report()` | 8 | 2、产品规模 | result_3 |
| `generate_scale_change_report()` | 9 | 3、本月定开..., 本周新发产品, 待售产品 | result_3_2_df |
| `generate_performance_report()` | 10 | 系列产品业绩×4, 5.2×2 | 无 |
| `generate_manager_report()` | 11 | 投资经理维度..., 不同形态... | 无 |
| `generate_zhaoshang_report()` | 12 | 招商在售产品不达基准, 封闭及定开... | 无 |
| `generate_asset_table()` | 13 | 8.资产大表 | Chicang_df(供Part16) |
| `generate_fee_report()` | 14 | 9.中收监控 | result_9 |
| `generate_maturity_report()` | 15 | 10.×3 | result_df_10_2 |
| `generate_holdings_report()` | 16 | 11.×10+ | 无 |
| `generate_volatility_report()` | 17 | 12.周净值高波动 | 无 |
| `generate_cycle_report()` | 18 | 13+14 | 无 |
| `generate_market_index_report()` | 19 | 15.市场指数收益 | 无 |
| `generate_pojing_report()` | 20 | 破净结果 | 无 |
| `generate_summary_text()` | 21 | 总结文字 | 无 |

## 特殊依赖处理

Part 13 生成的 `Chicang_df` 被 Part 16 需要。解决方案：
- `generate_asset_table()` 返回 `{'Chicang_df': Chicang_df}`
- results 字典传递给 `generate_holdings_report(ctx, writer, chicang_df=results['Chicang_df'])`

## 执行步骤

1. 在文件顶部添加 `ReportContext` dataclass
2. 将 Part 2+4+5+6 包成 `init_context()` 函数
3. 将 Part 7-21 逐个提取为函数（保持原代码缩进进函数体，将全局变量替换为 ctx.xxx）
4. 将已有的辅助函数（Part 3）保持不动（它们已经是函数了）
5. 写 `main()` 函数串联所有步骤
6. 文件末尾加 `if __name__ == '__main__': main()`
7. 测试：语法检查 + 导入检查 + 数据加载验证
8. git commit

## 修改的文件
- `/Users/fanshengxia/Desktop/周报V2/generate_report.py` — 唯一需要修改的文件

## 验证方法
1. `python -c "import py_compile; py_compile.compile('generate_report.py', doraise=True)"` — 语法
2. `python -c "from generate_report import main, init_context, ReportContext"` — 导入
3. `python -c "from generate_report import init_context; ctx = init_context(); print('OK', ctx.date)"` — 数据加载
4. 对比改前/改后执行结果的输出Excel文件（sheet数量和内容一致）
