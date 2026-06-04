#!/usr/bin/env python3
"""
银行理财产品申赎分析与流动性预测脚本
用法: python redemption_analysis.py <工作目录> [参数...]
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta, datetime

# 中文字体配置
matplotlib.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'Arial Unicode MS', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


def discover_files(directory):
    """发现目录下的所有 Excel 文件"""
    files = sorted([
        f for f in os.listdir(directory)
        if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$') and '处理后' not in f and '预测' not in f and '底表' not in f
    ])
    return [os.path.join(directory, f) for f in files]


def read_and_identify(filepath):
    """读取 Excel 文件，识别数据所在的 sheet 和列结构"""
    xl = pd.ExcelFile(filepath)
    results = []
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(filepath, sheet_name=sheet)
            if df.empty:
                continue
            cols = list(df.columns)
            # 识别包含申赎数据的 sheet
            has_sub = any('申购' in str(c) for c in cols)
            has_red = any('赎回' in str(c) for c in cols)
            has_date = any('日期' in str(c) for c in cols)
            has_name = any('简称' in str(c) or '名称' in str(c) for c in cols)
            if has_sub or has_red:
                results.append({
                    'sheet': sheet,
                    'columns': cols,
                    'rows': len(df),
                    'has_sub': has_sub,
                    'has_red': has_red,
                    'has_date': has_date,
                    'has_name': has_name,
                })
        except Exception:
            continue
    return results


def parse_amount(col):
    """解析金额列：处理千分位逗号、字符串等"""
    return pd.to_numeric(
        col.astype(str).str.replace(',', '').str.replace('，', '').str.strip(),
        errors='coerce'
    )


def find_column(cols, keywords):
    """在列名列表中查找匹配的列"""
    for col in cols:
        if all(kw in str(col) for kw in keywords):
            return col
    return None


def load_data(filepath):
    """
    加载单个文件的申赎数据，自动识别列名
    返回标准化的 DataFrame: 确认日期, 产品简称, 申购, 赎回
    """
    xl = pd.ExcelFile(filepath)
    all_dfs = []

    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet)
        if df.empty:
            continue
        cols = list(df.columns)

        # 查找关键列
        date_col = find_column(cols, ['日期'])
        name_col = find_column(cols, ['简称']) or find_column(cols, ['名称'])
        sub_in_col = find_column(cols, ['行内', '申购'])
        sub_out_col = find_column(cols, ['行外', '申购'])
        red_in_col = find_column(cols, ['行内', '赎回'])
        red_out_col = find_column(cols, ['行外', '赎回'])

        if date_col is None:
            continue
        # 至少需要有申购或赎回之一
        has_any_sub = sub_in_col or sub_out_col
        has_any_red = red_in_col or red_out_col
        if not has_any_sub and not has_any_red:
            continue

        # 提取并标准化
        result = pd.DataFrame()
        result['确认日期'] = pd.to_datetime(df[date_col], errors='coerce')

        if name_col:
            result['产品简称'] = df[name_col].astype(str)
        else:
            result['产品简称'] = '未知产品'

        # 申购 = 行内 + 行外
        sub = pd.Series(0.0, index=df.index)
        if sub_in_col:
            sub += pd.to_numeric(df[sub_in_col], errors='coerce').fillna(0)
        if sub_out_col:
            sub += parse_amount(df[sub_out_col]).fillna(0)
        result['申购'] = sub

        # 赎回 = 行内 + 行外
        red = pd.Series(0.0, index=df.index)
        if red_in_col:
            red += pd.to_numeric(df[red_in_col], errors='coerce').fillna(0)
        if red_out_col:
            red += parse_amount(df[red_out_col]).fillna(0)
        result['赎回'] = red

        # 净申赎
        result['净申赎'] = result['申购'] - result['赎回']

        all_dfs.append(result)

    if not all_dfs:
        return None

    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.dropna(subset=['确认日期'])
    combined = combined.drop_duplicates(subset=['确认日期', '产品简称'], keep='first')
    combined = combined.sort_values('确认日期').reset_index(drop=True)
    return combined


def run_analysis(
    directory,
    product_name_filter=None,
    exclude_children=True,
    product_start=None,
    lockup_days=365,
    pre_total_sub=None,
    scenarios=None,
    forecast_months=6,
    output_prefix=None,
):
    """
    主分析函数

    参数:
        directory: 数据文件所在目录
        product_name_filter: 产品名称过滤关键词（如'灵动1年'），None则不过滤
        exclude_children: 是否排除子产品（产品名含"子"）
        product_start: 产品成立日期 (YYYY-MM-DD)
        lockup_days: 锁定期天数，默认365
        pre_total_sub: 数据起始日之前的总申购金额（元）
        scenarios: 赎回率情景列表，如 [0.40, 0.50, 0.65]
        forecast_months: 预测月数
        output_prefix: 输出文件前缀
    """
    if scenarios is None:
        scenarios = [0.40, 0.50, 0.65]

    print("=" * 60)
    print("  银行理财产品申赎分析与流动性预测")
    print("=" * 60)

    # ── 1. 发现并加载文件 ──
    files = discover_files(directory)
    if not files:
        print("错误: 未找到 Excel 数据文件")
        return None

    print(f"\n发现 {len(files)} 个数据文件:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    all_data = []
    for f in files:
        df = load_data(f)
        if df is not None and len(df) > 0:
            all_data.append(df)
            print(f"  加载 {os.path.basename(f)}: {len(df)} 行, "
                  f"日期范围 {df['确认日期'].min().date()} ~ {df['确认日期'].max().date()}")

    if not all_data:
        print("错误: 未能从文件中提取有效数据")
        return None

    # 合并所有数据
    raw = pd.concat(all_data, ignore_index=True)
    raw = raw.drop_duplicates(subset=['确认日期', '产品简称'], keep='first')
    raw = raw.sort_values('确认日期').reset_index(drop=True)

    # ── 2. 产品过滤 ──
    if product_name_filter:
        raw = raw[raw['产品简称'].str.contains(product_name_filter, na=False)]
    if exclude_children:
        raw = raw[~raw['产品简称'].str.contains('子', na=False)]

    if len(raw) == 0:
        print("错误: 过滤后无数据")
        return None

    products = raw['产品简称'].unique()
    print(f"\n过滤后产品: {list(products)}")
    print(f"数据范围: {raw['确认日期'].min().date()} ~ {raw['确认日期'].max().date()}, "
          f"共 {len(raw)} 行")

    # ── 3. 聚合到日级别 ──
    daily = raw.groupby('确认日期').agg(
        申购合计=('申购', 'sum'),
        赎回合计=('赎回', 'sum'),
        净申赎=('净申赎', 'sum'),
    ).reset_index()
    daily = daily.sort_values('确认日期').reset_index(drop=True)

    DATA_START = daily['确认日期'].min()
    DATA_END = daily['确认日期'].max()

    print(f"\n日聚合后: {len(daily)} 个交易日")

    # ── 4. 补充前期申购 ──
    ONE_YEAR = timedelta(days=lockup_days)

    if product_start and pre_total_sub:
        product_start_dt = pd.Timestamp(product_start)
        pre_days = (DATA_START - product_start_dt).days
        if pre_days > 0:
            pre_daily_sub = pre_total_sub / pre_days
            pre_dates = pd.date_range(product_start_dt, DATA_START - timedelta(days=1), freq='D')
            pre_df = pd.DataFrame({
                '确认日期': pre_dates,
                '申购合计': pre_daily_sub,
                '赎回合计': 0.0,
                '净申赎': pre_daily_sub,
            })
            full = pd.concat([pre_df, daily], ignore_index=True)
            full = full.sort_values('确认日期').reset_index(drop=True)
            print(f"补充前期: {len(pre_dates)} 天, 日均申购 {pre_daily_sub/1e4:.0f} 万, "
                  f"累计 {pre_total_sub/1e8:.2f} 亿")
        else:
            full = daily.copy()
            print("注意: product_start 晚于或等于数据起始日，未补充前期数据")
    else:
        full = daily.copy()
        if not pre_total_sub:
            print("注意: 未提供前期申购总额，分析仅基于文件数据")
        if not product_start:
            print("注意: 未提供产品成立日，使用数据起始日作为产品成立日")
            product_start_dt = DATA_START

    # ── 5. 计算可赎回金额 & 累计赎回率 ──
    full['可赎回金额'] = 0.0
    for i in range(len(full)):
        date = full.loc[i, '确认日期']
        cutoff = date - ONE_YEAR
        full.loc[i, '可赎回金额'] = full.loc[full['确认日期'] <= cutoff, '申购合计'].sum()

    # 仅在有赎回数据的区间计算累计值
    hist = full[full['确认日期'] >= DATA_START].copy()
    hist['累计赎回'] = hist['赎回合计'].cumsum()
    hist['累计赎回率'] = np.where(
        hist['可赎回金额'] > 0,
        hist['累计赎回'] / hist['可赎回金额'] * 100,
        0
    )

    current_redeemable = hist['可赎回金额'].iloc[-1]
    current_redeemed = hist['累计赎回'].iloc[-1]
    current_rate = current_redeemed / current_redeemable * 100 if current_redeemable > 0 else 0

    print(f"\n当前状态 (截至 {DATA_END.date()}):")
    print(f"  可赎回金额: {current_redeemable/1e8:.2f} 亿")
    print(f"  累计赎回:   {current_redeemed/1e8:.2f} 亿")
    print(f"  累计赎回率: {current_rate:.2f}%")

    # ── 6. 未来预测 ──
    FUTURE_DAYS = forecast_months * 30
    future_dates = pd.date_range(DATA_END + timedelta(days=1), periods=FUTURE_DAYS, freq='D')

    # 计算未来每日新增可赎回
    cum_new_redeemable = 0
    future_rows = []
    for fd in future_dates:
        cutoff = fd - ONE_YEAR
        new = full.loc[full['确认日期'] == cutoff, '申购合计'].sum()
        cum_new_redeemable += new
        future_rows.append({
            '日期': fd,
            '当日新增可赎回': new,
            '累计可赎回总额': current_redeemable + cum_new_redeemable,
        })
    future = pd.DataFrame(future_rows)

    # 多情景预测
    decay = 0.03  # 赎回率收敛速度
    scenario_colors = {
        0.40: ('#10AC84', '--', '乐观'),
        0.50: ('#F39C12', '-', '基准'),
        0.65: ('#EE5A24', '-.', '悲观'),
    }

    all_projections = {}
    for rate in scenarios:
        terminal = rate * 100  # 转为百分比
        label = scenario_colors.get(rate, ('#888888', '-', f'{rate*100:.0f}%'))[2]
        color = scenario_colors.get(rate, ('#888888', '-', f'{rate*100:.0f}%'))[0]
        ls = scenario_colors.get(rate, ('#888888', '-', f'{rate*100:.0f}%'))[1]

        pred = future[['日期', '累计可赎回总额']].copy()
        rates = []
        cum_red = current_redeemed
        day_reds = []

        for i in range(len(pred)):
            day = i + 1
            r = terminal - (terminal - current_rate) * np.exp(-decay * day)
            rates.append(r)
            total_redeemable = pred.iloc[i]['累计可赎回总额']
            target = total_redeemable * r / 100
            day_red = max(0, target - cum_red)
            cum_red += day_red
            day_reds.append(day_red)

        pred['累计赎回率'] = rates
        pred['当日赎回'] = day_reds
        pred['累计赎回'] = np.cumsum(day_reds) + current_redeemed
        all_projections[rate] = {
            'label': label,
            'color': color,
            'ls': ls,
            'data': pred,
        }

    # ── 7. 汇总统计 ──
    total_sub = daily['申购合计'].sum()
    total_red = daily['赎回合计'].sum()
    avg_daily_sub = daily['申购合计'].mean()
    avg_daily_red = daily['赎回合计'].mean()

    print(f"\n数据期间汇总:")
    print(f"  累计申购: {total_sub/1e8:.2f} 亿")
    print(f"  累计赎回: {total_red/1e8:.2f} 亿")
    print(f"  净申赎:   {(total_sub-total_red)/1e8:.2f} 亿")
    print(f"  日均申购: {avg_daily_sub/1e4:.0f} 万")
    print(f"  日均赎回: {avg_daily_red/1e4:.0f} 万")

    # ── 8. 月度汇总 ──
    hist['月份'] = hist['确认日期'].dt.to_period('M')
    monthly = hist.groupby('月份').agg(
        申购=('申购合计', 'sum'),
        赎回=('赎回合计', 'sum'),
        月末可赎回=('可赎回金额', 'last'),
        月末累计赎回率=('累计赎回率', 'last'),
    ).reset_index()
    monthly['净申赎'] = monthly['申购'] - monthly['赎回']
    monthly['月份'] = monthly['月份'].astype(str)

    # 未来月度预测
    for rate, proj in all_projections.items():
        pred = proj['data']
        pred['月份'] = pred['日期'].dt.to_period('M')
        fut_monthly = pred.groupby('月份').agg(
            当月赎回流出=('当日赎回', 'sum'),
            月末累计赎回率=('累计赎回率', 'last'),
        ).reset_index()
        fut_monthly['月份'] = fut_monthly['月份'].astype(str)
        label = proj['label']
        print(f"\n{label}情景 ({rate*100:.0f}%赎回率) 未来月度赎回流出:")
        for _, mr in fut_monthly.iterrows():
            print(f"  {mr['月份']}: {mr['当月赎回流出']/1e8:.2f}亿, "
                  f"月末累计赎回率 {mr['月末累计赎回率']:.1f}%")

    # ── 9. 生成图表 ──
    if output_prefix is None:
        output_prefix = os.path.join(directory, '赎回分析')

    fig, axes = plt.subplots(3, 1, figsize=(18, 14))

    # 图1: 每日申购赎回
    ax1 = axes[0]
    hist_weekly = hist.set_index('确认日期').resample('W-MON').agg(
        {'申购合计': 'sum', '赎回合计': 'sum'}
    )
    ax1.bar(hist_weekly.index, hist_weekly['申购合计'] / 1e8, width=5,
            color='#2E86DE', alpha=0.6, label='申购')
    ax1.bar(hist_weekly.index, -hist_weekly['赎回合计'] / 1e8, width=5,
            color='#EE5A24', alpha=0.6, label='赎回')
    ax1.axhline(y=0, color='black', linewidth=0.5)
    ax1.set_ylabel('金额（亿）', fontsize=11)
    ax1.set_title('每周申赎金额', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # 图2: 累计值
    ax2 = axes[1]
    ax2.fill_between(hist['确认日期'], hist['申购合计'].cumsum() / 1e8,
                     alpha=0.15, color='#2E86DE')
    ax2.plot(hist['确认日期'], hist['申购合计'].cumsum() / 1e8,
             color='#2E86DE', linewidth=1.5, label='累计申购')
    ax2.plot(hist['确认日期'], hist['可赎回金额'] / 1e8,
             color='#10AC84', linewidth=2, label=f'可赎回申购（满{lockup_days}天）')
    ax2.fill_between(hist['确认日期'], hist['累计赎回'] / 1e8,
                     alpha=0.3, color='#EE5A24')
    ax2.plot(hist['确认日期'], hist['累计赎回'] / 1e8,
             color='#EE5A24', linewidth=1.5, label='累计赎回')
    ax2.set_ylabel('金额（亿）', fontsize=11)
    ax2.set_title('累计申购 vs 可赎回申购 vs 累计赎回', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(alpha=0.3)

    # 图3: 累计赎回率 + 预测
    ax3 = axes[2]
    ax3.plot(hist['确认日期'], hist['累计赎回率'],
             color='#2E86DE', linewidth=2, label='历史累计赎回率')
    ax3.fill_between(hist['确认日期'], hist['累计赎回率'],
                     alpha=0.1, color='#2E86DE')

    for rate, proj in all_projections.items():
        pred = proj['data']
        ax3.plot(pred['日期'], pred['累计赎回率'],
                 color=proj['color'], linewidth=1.8, linestyle=proj['ls'],
                 label=f'预测 {proj["label"]}')

    ax3.axvline(x=DATA_END, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    ax3.set_ylabel('累计赎回率（%）', fontsize=11)
    ax3.set_xlabel('日期', fontsize=11)
    ax3.set_title('累计赎回率走势 & 预测', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(alpha=0.3)

    # 标注当前值
    ax3.annotate(f'{current_rate:.1f}%',
                 xy=(DATA_END, current_rate),
                 xytext=(15, 15), textcoords='offset points',
                 fontsize=12, fontweight='bold', color='#EE5A24',
                 arrowprops=dict(arrowstyle='->', color='#EE5A24'))

    for ax in axes:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    fig.tight_layout()
    chart_path = f'{output_prefix}_趋势图.png'
    fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n趋势图已保存: {chart_path}")

    # ── 10. 保存 Excel 输出 ──
    # 表1: 申赎明细
    detail_out = daily.copy()
    detail_out['确认日期'] = detail_out['确认日期'].dt.strftime('%Y-%m-%d')
    detail_path = f'{output_prefix}_申赎明细.xlsx'
    detail_out.to_excel(detail_path, index=False, sheet_name='申赎明细')

    # 表2: 赎回率分析
    rate_out = hist[['确认日期', '申购合计', '赎回合计', '可赎回金额', '累计赎回', '累计赎回率']].copy()
    rate_out['确认日期'] = rate_out['确认日期'].dt.strftime('%Y-%m-%d')
    rate_out.columns = ['确认日期', '申购', '赎回', '可赎回申购累计', '累计赎回', '累计赎回率(%)']
    rate_out['累计赎回率(%)'] = rate_out['累计赎回率(%)'].round(2)
    rate_path = f'{output_prefix}_赎回率底表.xlsx'
    rate_out.to_excel(rate_path, index=False, sheet_name='赎回率分析')

    # 表3: 流动性预测
    pred_out = future[['日期', '当日新增可赎回', '累计可赎回总额']].copy()
    pred_out['日期'] = pred_out['日期'].dt.strftime('%Y-%m-%d')
    for rate, proj in all_projections.items():
        pct = f'{int(rate*100)}'
        pred_out[f'{pct}%_累计赎回率'] = proj['data']['累计赎回率'].round(2).values
        pred_out[f'{pct}%_当日赎回'] = proj['data']['当日赎回'].round(0).values
        pred_out[f'{pct}%_累计赎回'] = proj['data']['累计赎回'].round(0).values
    pred_path = f'{output_prefix}_流动性预测.xlsx'
    pred_out.to_excel(pred_path, index=False, sheet_name='流动性预测')

    print(f"申赎明细: {detail_path}")
    print(f"赎回率底表: {rate_path}")
    print(f"流动性预测: {pred_path}")

    # ── 11. 打印关键结论 ──
    print(f"\n{'=' * 60}")
    print("核心结论")
    print(f"{'=' * 60}")

    # 近期赎回率变化
    recent_7 = hist[hist['确认日期'] >= DATA_END - timedelta(days=7)]
    if len(recent_7) >= 2:
        rate_change_7d = (recent_7['累计赎回率'].iloc[-1] - recent_7['累计赎回率'].iloc[0])
        print(f"近7天赎回率变化: {rate_change_7d:+.1f}%")

    recent_30 = hist[hist['确认日期'] >= DATA_END - timedelta(days=30)]
    avg_daily_red_30 = recent_30['赎回合计'].mean() / 1e4
    print(f"近30天日均赎回: {avg_daily_red_30:.0f} 万")

    # 未来关键月份
    future['月份'] = future['日期'].dt.to_period('M')
    for rate, proj in all_projections.items():
        pred = proj['data']
        pred['月份'] = pred['日期'].dt.to_period('M')
        fut_monthly = pred.groupby('月份')['当日赎回'].sum()
        # 找峰值月
        peak_month = fut_monthly.idxmax()
        peak_val = fut_monthly.max() / 1e8
        m3_total = fut_monthly.iloc[:3].sum() / 1e8
        m6_total = fut_monthly.sum() / 1e8
        print(f"{proj['label']}: 峰值月 {peak_month} {peak_val:.2f}亿, "
              f"前3月 {m3_total:.2f}亿, 前6月 {m6_total:.2f}亿")

    return {
        'daily': daily,
        'hist': hist,
        'future': future,
        'projections': all_projections,
        'monthly': monthly,
        'chart_path': chart_path,
        'detail_path': detail_path,
        'rate_path': rate_path,
        'pred_path': pred_path,
    }


def main():
    parser = argparse.ArgumentParser(description='银行理财产品申赎分析与流动性预测')
    parser.add_argument('directory', help='数据文件所在目录')
    parser.add_argument('--product-name', '-n', default=None,
                        help='产品名称过滤关键词（如"灵动1年"）')
    parser.add_argument('--no-exclude-children', action='store_true',
                        help='不过滤子产品')
    parser.add_argument('--product-start', '-s', default=None,
                        help='产品成立日期 (YYYY-MM-DD)')
    parser.add_argument('--lockup-days', '-l', type=int, default=365,
                        help='锁定期天数 (默认365)')
    parser.add_argument('--pre-total-sub', '-p', type=float, default=None,
                        help='数据起始日前累计申购总额（亿）')
    parser.add_argument('--scenarios', type=str, default='0.40,0.50,0.65',
                        help='赎回率情景，逗号分隔 (默认: 0.40,0.50,0.65)')
    parser.add_argument('--forecast-months', '-m', type=int, default=6,
                        help='预测月数 (默认6)')
    parser.add_argument('--output-prefix', '-o', default=None,
                        help='输出文件前缀')

    args = parser.parse_args()

    scenarios = [float(s.strip()) for s in args.scenarios.split(',')]
    pre_total = args.pre_total_sub * 1e8 if args.pre_total_sub else None

    run_analysis(
        directory=args.directory,
        product_name_filter=args.product_name,
        exclude_children=not args.no_exclude_children,
        product_start=args.product_start,
        lockup_days=args.lockup_days,
        pre_total_sub=pre_total,
        scenarios=scenarios,
        forecast_months=args.forecast_months,
        output_prefix=args.output_prefix,
    )


if __name__ == '__main__':
    main()
