"""
Wind连接测试脚本

用于验证Wind API连接和数据代码是否正确
在运行主程序前，先运行此脚本确保环境正常

使用方法:
    python test_wind_connection.py
"""

from WindPy import w
from datetime import datetime, timedelta
import sys

print("=" * 80)
print("Wind连接和数据测试")
print("=" * 80)

# 测试1: Wind连接
print("\n[测试1] Wind连接状态")
print("-" * 40)

w.start()

if w.isconnected():
    print("✓ Wind连接成功")
else:
    print("❌ Wind连接失败")
    print("请确保:")
    print("  1. Wind终端已打开")
    print("  2. 已登录Wind账号")
    print("  3. 网络连接正常")
    sys.exit(1)

# 测试2: 日度行情数据
print("\n[测试2] 日度行情数据获取")
print("-" * 40)

test_codes = {
    "000001.SH": "上证指数",
    "SPX.GI": "标普500",
    "USDCNY.IB": "美元人民币",
}

end_date = datetime.now()
start_date = end_date - timedelta(days=7)

for code, name in test_codes.items():
    data = w.wsd(
        codes=code,
        fields="close",
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d"),
        options="Period=D"
    )

    if data.ErrorCode == 0:
        print(f"✓ {name} ({code}): 获取到 {len(data.Times)} 个交易日数据")
        if len(data.Times) > 0:
            print(f"  最新: {data.Times[-1].strftime('%Y-%m-%d')} = {data.Data[0][-1]:.2f}")
    else:
        print(f"❌ {name} ({code}): 错误码 {data.ErrorCode}")

# 测试3: 估值数据
print("\n[测试3] 估值数据（PE、PB）")
print("-" * 40)

for code, name in [("000001.SH", "上证指数"), ("SPX.GI", "标普500")]:
    # PE
    data = w.wsd(
        codes=code,
        fields="pe_ttm",
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d"),
        options="Period=D"
    )

    if data.ErrorCode == 0 and len(data.Times) > 0:
        print(f"✓ {name} PE: {data.Data[0][-1]:.2f}")
    else:
        print(f"❌ {name} PE: 错误码 {data.ErrorCode}")

    # PB
    data = w.wsd(
        codes=code,
        fields="pb_lf",
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d"),
        options="Period=D"
    )

    if data.ErrorCode == 0 and len(data.Times) > 0:
        print(f"✓ {name} PB: {data.Data[0][-1]:.2f}")
    else:
        print(f"❌ {name} PB: 错误码 {data.ErrorCode}")

# 测试4: EDB数据（债券收益率）
print("\n[测试4] EDB经济数据")
print("-" * 40)
print("⚠️ 注意: EDB代码需要根据实际情况修改")

# 这里使用示例代码，实际需要替换
test_edb = {
    "M0017142": "中债国债10年（示例代码）",
}

for code, name in test_edb.items():
    data = w.edb(
        codes=code,
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d")
    )

    if data.ErrorCode == 0:
        print(f"✓ {name}: 获取成功")
        if len(data.Times) > 0:
            print(f"  最新: {data.Times[-1].strftime('%Y-%m-%d')} = {data.Data[0][-1]:.4f}%")
    else:
        print(f"❌ {name}: 错误码 {data.ErrorCode}")
        print(f"  提示: 需要在Wind终端查询正确的EDB代码")

# 测试5: 特殊代码（锁汇成本相关）
print("\n[测试5] 特殊代码测试")
print("-" * 40)

special_codes = {
    "USDCNY1YS.IB": "1年掉期点",
    "USDCNH.FX": "离岸人民币",
}

for code, name in special_codes.items():
    data = w.wsd(
        codes=code,
        fields="close",
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d"),
        options="Period=D"
    )

    if data.ErrorCode == 0 and len(data.Times) > 0:
        print(f"✓ {name} ({code}): {data.Data[0][-1]:.4f}")
    else:
        print(f"❌ {name} ({code}): 错误码 {data.ErrorCode}")

# 测试6: 商品期货
print("\n[测试6] 商品期货数据")
print("-" * 40)

commodity_codes = {
    "AU.SHF": "沪金",
    "RB.SHF": "螺纹钢",
    "SC.INE": "原油",
    "M.DCE": "豆粕",
}

for code, name in commodity_codes.items():
    data = w.wsd(
        codes=code,
        fields="close",
        beginTime=start_date.strftime("%Y-%m-%d"),
        endTime=end_date.strftime("%Y-%m-%d"),
        options="Period=D"
    )

    if data.ErrorCode == 0 and len(data.Times) > 0:
        print(f"✓ {name} ({code}): {data.Data[0][-1]:.2f}")
    else:
        print(f"❌ {name} ({code}): 错误码 {data.ErrorCode}")

# 总结
print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
print("\n如果所有测试都通过 ✓，可以运行主程序:")
print("  python generate_tables_from_wind.py")
print("\n如果有测试失败 ❌，请检查:")
print("  1. Wind代码是否正确")
print("  2. 账号是否有相应数据权限")
print("  3. EDB代码是否需要更新")
print("\nWind客服电话: 400-820-9463")

w.stop()
