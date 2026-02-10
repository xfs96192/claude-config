#!/usr/bin/env python3
"""
债券建仓周报生成脚本
用法: python generate_report.py <日期> [输出目录]
日期格式: YYYY-MM-DD (例如: 2026-01-30)
"""

import sys
import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime

def get_duration_from_wind(bond_codes, trade_date):
    """从Wind获取债券行权久期"""
    try:
        from WindPy import w
        w.start()

        date_str = trade_date.replace('-', '')
        result = w.wss(",".join(bond_codes), "modidura_cnbd", f"tradeDate={date_str};credibility=3;")

        duration_data = {}
        if result.ErrorCode == 0 and result.Data:
            for i, code in enumerate(bond_codes):
                duration_data[code] = result.Data[0][i] if i < len(result.Data[0]) else None

        w.stop()
        return duration_data
    except Exception as e:
        print(f"Wind数据获取失败: {e}")
        return {}

def generate_report(date_str, output_dir=None):
    """生成债券建仓周报"""

    # 源文件路径
    base_dir = "/Users/fanshengxia/Desktop/债券建仓登记"
    source_file = os.path.join(base_dir, f"正式指令台账信息{date_str}.xlsx")

    if not os.path.exists(source_file):
        print(f"错误: 源文件不存在 - {source_file}")
        sys.exit(1)

    # 读取源数据
    df = pd.read_excel(source_file, sheet_name='正式指令')

    # 筛选买入交易
    df_buy = df[df['交易方向'] == '买入']

    if len(df_buy) == 0:
        print("没有买入交易记录")
        sys.exit(0)

    # 分类: CD(同业存单) vs 其他债券
    df_cd = df_buy[df_buy['债券简称'].str.contains('CD', na=False)]
    df_bond = df_buy[~df_buy['债券简称'].str.contains('CD', na=False)]

    # 获取所有唯一债券代码
    all_codes = df_buy['债券代码'].unique().tolist()

    # 从Wind获取行权久期
    print("正在从Wind获取行权久期数据...")
    duration_data = get_duration_from_wind(all_codes, date_str)

    # 处理债券数据
    bond_records = []
    for _, row in df_bond.iterrows():
        yield_rate = row['行权收益率'] if pd.notna(row['行权收益率']) else row['到期收益率']
        duration = duration_data.get(row['债券代码'], '')

        trade_date = row['交易日']
        if pd.notna(trade_date):
            if isinstance(trade_date, str):
                trade_date = pd.to_datetime(trade_date).date()
            elif hasattr(trade_date, 'date'):
                trade_date = trade_date.date()

        bond_records.append({
            '日期': trade_date,
            '人员': row.get('委托人', ''),
            '投资经理': '',
            '投资经理本周需求（亿）': '',
            '方向': '买入',
            '代码': row['债券代码'],
            '简称': row['债券简称'],
            '量（万）': row['券面总额(万元)'],
            '期限（行权/到期，年）': duration,
            '收益率（%）': yield_rate,
            '交易对手': row['本币交易对手方'] if pd.notna(row['本币交易对手方']) else ''
        })

    # 处理CD数据
    cd_records = []
    for _, row in df_cd.iterrows():
        yield_rate = row['行权收益率'] if pd.notna(row['行权收益率']) else row['到期收益率']
        duration = duration_data.get(row['债券代码'], '')

        trade_date = row['交易日']
        if pd.notna(trade_date):
            if isinstance(trade_date, str):
                trade_date = pd.to_datetime(trade_date).date()
            elif hasattr(trade_date, 'date'):
                trade_date = trade_date.date()

        cd_records.append({
            '交割日期': trade_date,
            '人员': row.get('委托人', ''),
            '投资经理': '',
            '投资经理本周需求（亿）': '',
            '方向': '买入',
            '专户名称/直投名称': row['债券简称'],
            '背后资产（若有）': '',
            '量（万）': row['券面总额(万元)'],
            '期限（行权/到期，年）': duration,
            '收益率（%）': yield_rate
        })

    # 创建Excel
    wb = Workbook()

    # Sheet 1: 二级收券
    ws_bond = wb.active
    ws_bond.title = '二级收券'

    bond_headers = ['日期', '人员', '投资经理', '投资经理本周需求（亿）', '方向', '代码', '简称', '量（万）', '期限（行权/到期，年）', '收益率（%）', '交易对手']
    for col, header in enumerate(bond_headers, 1):
        ws_bond.cell(row=1, column=col, value=header)
        ws_bond.cell(row=1, column=col).font = Font(bold=True)
        ws_bond.cell(row=1, column=col).alignment = Alignment(horizontal='center')

    for row_idx, record in enumerate(bond_records, 2):
        for col_idx, key in enumerate(bond_headers, 1):
            ws_bond.cell(row=row_idx, column=col_idx, value=record.get(key, ''))

    # 调整列宽
    col_widths = [12, 10, 10, 18, 8, 18, 18, 10, 18, 12, 25]
    for i, width in enumerate(col_widths, 1):
        ws_bond.column_dimensions[chr(64 + i)].width = width

    # Sheet 2: 二级NCD和货币类资产建仓
    ws_cd = wb.create_sheet('二级NCD和货币类资产建仓')

    cd_headers = ['交割日期', '人员', '投资经理', '投资经理本周需求（亿）', '方向', '专户名称/直投名称', '背后资产（若有）', '量（万）', '期限（行权/到期，年）', '收益率（%）']
    for col, header in enumerate(cd_headers, 1):
        ws_cd.cell(row=1, column=col, value=header)
        ws_cd.cell(row=1, column=col).font = Font(bold=True)
        ws_cd.cell(row=1, column=col).alignment = Alignment(horizontal='center')

    for row_idx, record in enumerate(cd_records, 2):
        for col_idx, key in enumerate(cd_headers, 1):
            ws_cd.cell(row=row_idx, column=col_idx, value=record.get(key, ''))

    # 调整列宽
    cd_col_widths = [12, 10, 10, 18, 8, 20, 15, 10, 18, 12]
    for i, width in enumerate(cd_col_widths, 1):
        ws_cd.column_dimensions[chr(64 + i)].width = width

    # 保存文件
    if output_dir is None:
        output_dir = base_dir

    output_file = os.path.join(output_dir, f"债券建仓登记_{date_str}.xlsx")
    wb.save(output_file)

    print(f"\n文件已生成: {output_file}")
    print(f"二级收券: {len(bond_records)} 条记录")
    print(f"二级NCD和货币类资产建仓: {len(cd_records)} 条记录")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_report.py <日期> [输出目录]")
        print("日期格式: YYYY-MM-DD")
        sys.exit(1)

    date_str = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    generate_report(date_str, output_dir)
