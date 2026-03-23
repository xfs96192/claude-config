"""
委外产品及持仓权益基金业绩分析 - 端到端脚本模板

使用方法：根据实际路径修改下方 CONFIG 部分后直接运行。
"""

import sys, os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# =====================
# CONFIG - 按需修改
# =====================
NAV_FILE        = '/path/to/委外分析-净值走势.xlsx'        # 委外产品净值走势文件
HOLDINGS_FILE   = '/path/to/持仓盈亏明细列表_YYYYMMDD.xlsx'  # 持仓盈亏明细文件
OUTPUT_FILE     = '/path/to/委外产品及权益基金业绩汇总.xlsx'   # 输出Excel路径

# 需要分析权益持仓的产品：{产品代码: 成立日期}
PORTFOLIO_PRODUCTS = {
    '9K717120': '2025-01-21',
    '9K717310': '2024-09-24',
}

# 权益基金数据查询起始日（取所有成立日中最早者，可往前推几天）
DATA_START_DATE = '2024-09-20'
DATA_END_DATE   = '2026-03-19'  # 通常是今天或最新交易日

# =====================
# iChoice 配置
# =====================
ICHOICE_SDK_PATH = os.path.expanduser(
    '~/Desktop/ichoice_data/ichoice/EMQuantAPI_Python/python3')
ICHOICE_USER = 'xylczh0181'
ICHOICE_PASS = 'ef465509'

# =====================
# 常量
# =====================
METRIC_COLS = ['成立以来涨幅', '2025年度涨幅', '今年以来涨幅',
               '成立以来最大回撤', '2025年度最大回撤', '今年以来最大回撤']
EQUITY_CATS = ['被动指数型基金', '偏股混合型基金', '普通股票型基金',
               '国际(QDII)被动指数型股票基金']

# =====================
# 工具函数
# =====================

def max_drawdown(arr):
    arr = np.array(arr, dtype=float)
    if len(arr) < 2:
        return np.nan
    peak = np.maximum.accumulate(arr)
    return ((arr - peak) / peak).min()


def calc_metrics(series, inception_date=None):
    """从净值序列计算6项业绩/风险指标（非年化）"""
    s = series.copy()
    s = s[s != '--']
    s = pd.to_numeric(s, errors='coerce').dropna().sort_index()
    if inception_date:
        s = s[s.index >= pd.Timestamp(inception_date)]
    if len(s) < 2:
        return {k: np.nan for k in METRIC_COLS}

    ret_inception = (s.iloc[-1] / s.iloc[0]) - 1
    mdd_inception = max_drawdown(s.values)

    # 2025年度
    s_2024e = s[s.index < '2025-01-01']
    s_2025  = s[(s.index >= '2025-01-01') & (s.index <= '2025-12-31')]
    if len(s_2024e) > 0 and len(s_2025) > 0:
        ret_2025 = (s_2025.iloc[-1] / s_2024e.iloc[-1]) - 1
        mdd_2025 = max_drawdown(pd.concat([
            pd.Series([s_2024e.iloc[-1]], index=[s_2024e.index[-1]]), s_2025]).values)
    elif len(s_2025) > 0:
        ret_2025 = (s_2025.iloc[-1] / s_2025.iloc[0]) - 1
        mdd_2025 = max_drawdown(s_2025.values)
    else:
        ret_2025 = mdd_2025 = np.nan

    # 今年以来 (2026 YTD)
    s_2025e = s[s.index < '2026-01-01']
    s_2026  = s[s.index >= '2026-01-01']
    if len(s_2025e) > 0 and len(s_2026) > 0:
        ret_ytd = (s_2026.iloc[-1] / s_2025e.iloc[-1]) - 1
        mdd_ytd = max_drawdown(pd.concat([
            pd.Series([s_2025e.iloc[-1]], index=[s_2025e.index[-1]]), s_2026]).values)
    elif len(s_2026) > 0:
        ret_ytd = (s_2026.iloc[-1] / s_2026.iloc[0]) - 1
        mdd_ytd = max_drawdown(s_2026.values)
    else:
        ret_ytd = mdd_ytd = np.nan

    return {
        '成立以来涨幅':     ret_inception,
        '2025年度涨幅':     ret_2025,
        '今年以来涨幅':     ret_ytd,
        '成立以来最大回撤': mdd_inception,
        '2025年度最大回撤': mdd_2025,
        '今年以来最大回撤': mdd_ytd,
    }


def get_equity_holdings(holdings_df, product_code):
    """筛选指定产品的权益基金持仓，计算权重"""
    df = holdings_df[holdings_df['产品代码'] == product_code]
    eq = df[(df['新版资产大类'] == '公募基金') &
            (df['新版资产小类'].isin(EQUITY_CATS))].copy()
    eq = eq[['外部代码', '资产简称', '新版资产小类',
             '日终市值(元)-产品法估值']].dropna(
        subset=['外部代码', '日终市值(元)-产品法估值'])
    total_mv = eq['日终市值(元)-产品法估值'].sum()
    eq['weight'] = eq['日终市值(元)-产品法估值'] / total_mv
    return eq


def build_weighted_portfolio(holdings_df, fund_nav_dict, inception_date_str):
    """构建市值加权组合净值序列（rebase到1）"""
    inception_date = pd.Timestamp(inception_date_str)
    all_dates, fund_series = set(), {}
    for _, row in holdings_df.iterrows():
        code = row['外部代码']
        if code in fund_nav_dict:
            s = fund_nav_dict[code][fund_nav_dict[code].index >= inception_date]
            if len(s) > 0:
                fund_series[code] = (s, row['weight'])
                all_dates.update(s.index.tolist())
    if not all_dates:
        return pd.Series(dtype=float)
    date_index = pd.DatetimeIndex(sorted(all_dates))
    rebase, valid_w = {}, {}
    for code, (s, w) in fund_series.items():
        rebase[code] = s.reindex(date_index, method='ffill') / s.iloc[0]
        valid_w[code] = w
    total_w = sum(valid_w.values())
    portfolio = pd.Series(0.0, index=date_index)
    for code in rebase:
        portfolio += rebase[code] * (valid_w[code] / total_w)
    return portfolio


# =====================
# 主流程
# =====================

def main():
    results = {}

    # --- Step 1: 委外产品净值 ---
    print("读取委外产品净值...")
    nav_df = pd.read_excel(NAV_FILE, sheet_name=0)
    nav_df.iloc[:, 0] = pd.to_datetime(nav_df.iloc[:, 0])
    nav_df = nav_df.set_index(nav_df.columns[0])
    weiwai_products = nav_df.columns.tolist()
    for p in weiwai_products:
        results[p] = {'type': '委外产品', 'inception': '', 'metrics': calc_metrics(nav_df[p])}
    print(f"  {len(weiwai_products)} 个委外产品指标计算完成")

    # --- Step 2: 持仓数据 ---
    print("读取持仓盈亏明细...")
    holdings_df = pd.read_excel(HOLDINGS_FILE, sheet_name='Sheet1')
    all_holdings = {code: get_equity_holdings(holdings_df, code)
                    for code in PORTFOLIO_PRODUCTS}
    all_fund_codes = list(set(
        code for h in all_holdings.values() for code in h['外部代码'].tolist()))
    print(f"  需获取 {len(all_fund_codes)} 只基金净值")

    # --- Step 3: iChoice 获取基金净值 ---
    print("从 iChoice 获取基金累计净值...")
    if ICHOICE_SDK_PATH not in sys.path:
        sys.path.insert(0, ICHOICE_SDK_PATH)
    from EmQuantAPI import c
    r = c.start(f"UserName={ICHOICE_USER},Password={ICHOICE_PASS},ForceLogin=1")
    if r.ErrorCode != 0:
        print(f"iChoice 登录失败: {r.ErrorMsg}"); return

    fund_nav_dict = {}
    try:
        for code in all_fund_codes:
            data = c.csd(code, "ACCUMULATEDNAV", DATA_START_DATE, DATA_END_DATE, "Ispandas=1")
            if isinstance(data, pd.DataFrame) and len(data) > 0 and not data['ACCUMULATEDNAV'].isna().all():
                data['DATES'] = pd.to_datetime(data['DATES'], format='%Y/%m/%d')
                fund_nav_dict[code] = data.set_index('DATES')['ACCUMULATEDNAV'].dropna()
                print(f"  ✓ {code}: {len(fund_nav_dict[code])} 条")
            else:
                print(f"  ✗ {code}: 获取失败")
    finally:
        c.stop()
    print(f"  成功获取 {len(fund_nav_dict)}/{len(all_fund_codes)} 只")

    # --- Step 4: 构建加权组合并计算指标 ---
    portfolio_data = {}
    for code, inception_date in PORTFOLIO_PRODUCTS.items():
        h = all_holdings[code]
        portfolio = build_weighted_portfolio(h, fund_nav_dict, inception_date)
        m = calc_metrics(portfolio, inception_date=inception_date)
        results[f'{code}_portfolio'] = {'type': '权益基金加权组合', 'inception': inception_date, 'metrics': m}
        portfolio_data[code] = {'holdings': h, 'portfolio': portfolio}
        print(f"  {code} 组合: 成立以来涨幅={m['成立以来涨幅']:.2%}, MDD={m['成立以来最大回撤']:.2%}")

    # --- Step 5: 生成 Excel ---
    print(f"\n生成 Excel: {OUTPUT_FILE}")
    _write_excel(results, all_holdings, PORTFOLIO_PRODUCTS, fund_nav_dict, OUTPUT_FILE)
    print("完成！")


def _write_excel(results, all_holdings, portfolio_products, fund_nav_dict, output_path):
    """生成格式化 Excel 报告"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    C_DARK  = '1F4E79'
    C_MID   = '2E75B6'
    C_LIGHT = 'BDD7EE'
    C_ALT   = 'DEEAF1'
    C_WHITE = 'FFFFFF'
    C_RED   = 'C00000'
    C_GREEN = '375623'

    def bd(style='thin', color='B0B0B0'):
        s = Side(border_style=style, color=color)
        return Border(left=s, right=s, top=s, bottom=s)

    def hdr(cell, text, bg, size=9, bold=True, fg='FFFFFF', wrap=False, align='center'):
        cell.value = text
        cell.font = Font(name='微软雅黑', bold=bold, size=size, color=fg)
        cell.fill = PatternFill('solid', fgColor=bg)
        cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
        cell.border = bd()

    def num_cell(cell, val, fmt='0.00%;[Red]-0.00%;"-"', bg=C_WHITE):
        cell.fill = PatternFill('solid', fgColor=bg)
        cell.border = bd()
        cell.alignment = Alignment(horizontal='center', vertical='center')
        if pd.isna(val):
            cell.value = 'N/A'
            cell.font = Font(name='微软雅黑', size=10, color='808080')
        else:
            cell.value = val
            cell.number_format = fmt
            cell.font = Font(name='微软雅黑', size=10, bold=True,
                             color=C_RED if val < 0 else C_GREEN)

    wb = Workbook()
    ws = wb.active
    ws.title = '汇总结果表'

    # 标题
    ws.merge_cells('A1:I1')
    hdr(ws['A1'], '委外产品及权益基金组合 — 业绩与风险指标汇总', C_DARK, size=13)
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:I2')
    hdr(ws['A2'], '所有涨幅均为非年化数据；权益基金组合权重基于持仓日终市值（产品法估值）；基金净值使用累计净值（ACCUMULATEDNAV）',
        'D9E1F2', size=9, bold=False, fg='595959')
    ws.row_dimensions[2].height = 18

    # 分组标题行
    ws.merge_cells('A3:C3')
    hdr(ws['A3'], '', C_MID)
    ws.merge_cells('D3:F3')
    hdr(ws['D3'], '业绩指标', C_MID, size=10)
    ws.merge_cells('G3:I3')
    hdr(ws['G3'], '风险指标（最大回撤）', C_RED, size=10)
    ws.row_dimensions[3].height = 20

    col4 = ['产品 / 策略名称', '类型', '成立日期',
            '成立以来涨幅\n（截最新）', '2025年度涨幅', '今年以来涨幅\n（截最新）',
            '成立以来最大回撤\n（截最新）', '2025年度最大回撤', '今年以来最大回撤\n（截最新）']
    for j, h_text in enumerate(col4):
        hdr(ws.cell(4, j+1), h_text, C_MID, size=9, wrap=True)
    ws.row_dimensions[4].height = 42

    r = 5
    # 委外产品行
    weiwai_keys = [k for k, v in results.items() if v['type'] == '委外产品']
    for i, key in enumerate(weiwai_keys):
        m = results[key]['metrics']
        bg = C_ALT if i % 2 == 0 else C_WHITE
        ws.row_dimensions[r].height = 22

        c1 = ws.cell(r, 1); c1.value = key
        c1.font = Font(name='微软雅黑', size=9, bold=True)
        c1.fill = PatternFill('solid', fgColor=bg); c1.border = bd()
        c1.alignment = Alignment(horizontal='left', vertical='center', indent=1)

        for j, label in enumerate(['type', 'inception']):
            cell = ws.cell(r, 2+j)
            cell.value = results[key][label] if label == 'inception' else '委外产品'
            cell.font = Font(name='微软雅黑', size=9)
            cell.fill = PatternFill('solid', fgColor=bg); cell.border = bd()
            cell.alignment = Alignment(horizontal='center', vertical='center')

        for j, mk in enumerate(METRIC_COLS):
            num_cell(ws.cell(r, 4+j), m[mk], bg=bg)
        r += 1

    # 分隔行
    ws.merge_cells(f'A{r}:I{r}')
    sep = ws[f'A{r}']
    sep.value = '▶  权益基金持仓加权组合（新版资产大类=公募基金，含：被动指数型/偏股混合/普通股票/QDII被动指数型；权重=日终市值-产品法估值）'
    sep.font = Font(name='微软雅黑', bold=True, size=9, color=C_DARK)
    sep.fill = PatternFill('solid', fgColor='D6E4F0')
    sep.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    sep.border = bd('medium', C_DARK)
    ws.row_dimensions[r].height = 18
    r += 1

    # 权益基金组合行
    portfolio_keys = [k for k, v in results.items() if v['type'] == '权益基金加权组合']
    for i, key in enumerate(portfolio_keys):
        m = results[key]['metrics']
        inc = results[key]['inception']
        product_code = key.replace('_portfolio', '')
        n_funds = len(all_holdings.get(product_code, []))
        bg = C_ALT if i % 2 == 0 else C_WHITE
        ws.row_dimensions[r].height = 36

        c1 = ws.cell(r, 1)
        c1.value = f'{product_code} 权益基金加权组合（{n_funds}只基金）'
        c1.font = Font(name='微软雅黑', size=9, bold=True)
        c1.fill = PatternFill('solid', fgColor=bg); c1.border = bd()
        c1.alignment = Alignment(horizontal='left', vertical='center', indent=1, wrap_text=True)

        ws.cell(r, 2).value = '权益基金\n加权组合'
        ws.cell(r, 3).value = inc
        for j in [2, 3]:
            cell = ws.cell(r, j)
            cell.font = Font(name='微软雅黑', size=9)
            cell.fill = PatternFill('solid', fgColor=bg); cell.border = bd()
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        for j, mk in enumerate(METRIC_COLS):
            num_cell(ws.cell(r, 4+j), m[mk], bg=bg)
        r += 1

    ws.column_dimensions['A'].width = 46
    ws.column_dimensions['B'].width = 10
    ws.column_dimensions['C'].width = 12
    for col in ['D','E','F','G','H','I']:
        ws.column_dimensions[col].width = 17
    ws.freeze_panes = 'D5'

    # 持仓明细 Sheet
    for code, inception_date in portfolio_products.items():
        h = all_holdings.get(code)
        if h is None or len(h) == 0:
            continue
        ws2 = wb.create_sheet(f'{code}-权益持仓明细')
        total_mv = h['日终市值(元)-产品法估值'].sum()
        inc_ts = pd.Timestamp(inception_date)

        ws2.merge_cells('A1:G1')
        hdr(ws2['A1'], f'{code} — 权益基金持仓明细', C_DARK, size=11)
        ws2.row_dimensions[1].height = 26

        ws2.merge_cells('A2:G2')
        hdr(ws2['A2'],
            f'权益基金总市值：{total_mv/1e6:.2f} 百万元  |  合计 {len(h)} 只  |  成立日期：{inception_date}',
            'D9E1F2', size=9, bold=False, fg='595959')
        ws2.row_dimensions[2].height = 18

        det_hdrs = ['基金代码', '基金简称', '资产小类', '日终市值（元）\n产品法估值',
                    '持仓权重', f'成立以来涨幅\n（自{inception_date}，截最新）']
        for j, h_text in enumerate(det_hdrs):
            hdr(ws2.cell(3, j+1), h_text, C_MID, size=9, wrap=True)
        ws2.row_dimensions[3].height = 36

        for i2, (_, row) in enumerate(h.iterrows()):
            r2 = 4 + i2
            bg = C_ALT if i2 % 2 == 0 else C_WHITE
            code_f = row['外部代码']
            fund_ret = np.nan
            if code_f in fund_nav_dict:
                s = fund_nav_dict[code_f][fund_nav_dict[code_f].index >= inc_ts]
                if len(s) >= 2:
                    fund_ret = (s.iloc[-1] / s.iloc[0]) - 1

            row_vals = [code_f, row['资产简称'], row['新版资产小类'],
                        row['日终市值(元)-产品法估值'], row['weight'], fund_ret]
            fmts = [None, None, None, '#,##0', '0.00%', None]
            for j2, (val, fmt) in enumerate(zip(row_vals, fmts)):
                cell = ws2.cell(r2, j2+1)
                cell.fill = PatternFill('solid', fgColor=bg); cell.border = bd()
                if j2 == 5:
                    num_cell(cell, val, bg=bg)
                elif fmt:
                    cell.value = val; cell.number_format = fmt
                    cell.font = Font(name='微软雅黑', size=9)
                    cell.alignment = Alignment(horizontal='right' if j2==3 else 'center', vertical='center')
                else:
                    cell.value = val; cell.font = Font(name='微软雅黑', size=9)
                    cell.alignment = Alignment(horizontal='left' if j2<2 else 'center',
                                               vertical='center', indent=1 if j2<2 else 0,
                                               wrap_text=(j2==1))
            ws2.row_dimensions[r2].height = 18

        # 合计行
        r_tot = 4 + len(h)
        ws2.row_dimensions[r_tot].height = 20
        for j2 in range(6):
            cell = ws2.cell(r_tot, j2+1)
            cell.fill = PatternFill('solid', fgColor=C_LIGHT)
            cell.font = Font(name='微软雅黑', bold=True, size=9)
            cell.border = bd('medium', C_DARK)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        ws2.cell(r_tot, 1).value = '合计'
        ws2.cell(r_tot, 1).alignment = Alignment(horizontal='left', vertical='center', indent=1)
        ws2.cell(r_tot, 4).value = total_mv
        ws2.cell(r_tot, 4).number_format = '#,##0'
        ws2.cell(r_tot, 4).alignment = Alignment(horizontal='right', vertical='center')
        ws2.cell(r_tot, 5).value = 1.0
        ws2.cell(r_tot, 5).number_format = '0.00%'

        ws2.column_dimensions['A'].width = 14
        ws2.column_dimensions['B'].width = 36
        ws2.column_dimensions['C'].width = 22
        ws2.column_dimensions['D'].width = 18
        ws2.column_dimensions['E'].width = 10
        ws2.column_dimensions['F'].width = 22
        ws2.freeze_panes = 'A4'

    wb.save(output_path)


if __name__ == '__main__':
    main()
