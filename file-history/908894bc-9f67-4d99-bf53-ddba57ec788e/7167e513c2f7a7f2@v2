#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_reports.py
合并多个投资经理的季报 Excel 文件，生成全部汇总版本和说明 Markdown。

用法：
    python merge_reports.py <folder_path> \
        --base 多资产投资部投资经理和投资策略部分-徐莹.xlsx \
        --output 多资产投资部投资经理和投资策略部分-全部汇总2026Q1.xlsx \
        --report 汇总说明_2026Q1.md
"""
import sys
import os
import re
import argparse
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill, Font

STRAT_COL = '投资策略和运作分析'  # 模糊匹配用

YELLOW_FILL = PatternFill("solid", fgColor="FFF2CC")


def find_strategy_col(df: pd.DataFrame) -> str:
    """在 DataFrame 中找到策略列名"""
    for col in df.columns:
        if STRAT_COL in str(col):
            return col
    raise ValueError("未找到策略列")


def merge_excel_files(
    folder: str,
    base_file: str,
    extra_files: list[str],
    output_path: str,
) -> pd.DataFrame:
    """
    以 base_file 为基础，将 extra_files 中有内容的策略合并进来。
    若某产品在多个文件中都有策略，以先出现的（base_file 优先）为准。
    """
    base_path = os.path.join(folder, base_file)
    base_df = pd.read_excel(base_path, header=1)
    base_df['产品代码'] = base_df['产品代码'].astype(str).str.strip()
    strat_col = find_strategy_col(base_df)

    print(f"基础文件：{base_file}（{base_df[strat_col].notna().sum()} 条已填）")

    for fname in extra_files:
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            print(f"  ⚠ 文件不存在：{fname}，跳过")
            continue
        df = pd.read_excel(path, header=1)
        df['产品代码'] = df['产品代码'].astype(str).str.strip()
        try:
            sc = find_strategy_col(df)
        except ValueError:
            print(f"  ⚠ 文件无策略列：{fname}，跳过")
            continue
        filled = df[df[sc].notna()][['产品代码', sc]]
        count = 0
        for _, row in filled.iterrows():
            mask = base_df['产品代码'] == row['产品代码']
            if mask.any() and pd.isna(base_df.loc[mask, strat_col].values[0]):
                base_df.loc[mask, strat_col] = row[sc]
                count += 1
        print(f"  合并 {fname}：新增 {count} 条")

    # 写 Excel（黄色标记未填行）
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        base_df.to_excel(writer, sheet_name='全部产品汇总', index=False, startrow=1)
        wb = writer.book
        ws = writer.sheets['全部产品汇总']

        ws['A1'] = f'多资产投资部投资经理和投资策略部分 - {_current_quarter()}汇总'
        ws['A1'].font = Font(bold=True, size=13)
        ws.merge_cells('A1:I1')

        ws.column_dimensions['A'].width = 14
        ws.column_dimensions['B'].width = 42
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 62
        for col in ['E', 'F', 'G', 'H', 'I']:
            ws.column_dimensions[col].width = 12

        strat_col_idx = list(base_df.columns).index(strat_col) + 1
        for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
            cell = row[strat_col_idx - 1]
            if not cell.value or str(cell.value).strip() in ('', 'nan', 'None'):
                for c in row:
                    c.fill = YELLOW_FILL
            else:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    print(f"✓ 汇总 Excel 已保存：{output_path}")
    return base_df


def generate_report(
    merged_df: pd.DataFrame,
    folder: str,
    source_files: dict[str, tuple[str, int]],
    report_path: str,
) -> None:
    """
    生成 Markdown 说明文档。
    source_files: {label: (filename, filled_count)}
    """
    strat_col = find_strategy_col(merged_df)
    total = len(merged_df)
    filled_mask = merged_df[strat_col].notna() & (
        merged_df[strat_col].astype(str).str.len() > 3
    )
    filled_count = filled_mask.sum()
    unfilled_count = total - filled_count

    # 按投资经理统计
    mgr_stats = []
    for mgr, grp in merged_df.groupby('主投资经理/投资经理姓名', dropna=False):
        mgr = str(mgr) if pd.notna(mgr) else '未知'
        done = filled_mask.reindex(grp.index, fill_value=False).sum()
        total_m = len(grp)
        mgr_stats.append({'投资经理': mgr, '产品总数': total_m,
                          '已汇总': int(done), '未汇总': total_m - int(done)})
    stats_df = pd.DataFrame(mgr_stats)

    unfilled_df = merged_df[~filled_mask][
        ['产品代码', '产品名称', '主投资经理/投资经理姓名']
    ]

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    quarter = _current_quarter()
    lines = [
        f'# {quarter}投资策略汇总说明',
        '',
        f'**生成时间**: {now}  ',
        f'**总产品数**: {total}  |  **已汇总**: {filled_count}  |  **未汇总**: {unfilled_count}',
        '',
        '---',
        '',
        '## 一、已提交文件',
        '',
        '| 文件 | 负责老师 | 已填产品数 |',
        '|------|---------|-----------|',
    ]
    for label, (fname, cnt) in source_files.items():
        lines.append(f'| `{fname}` | {label} | {cnt} |')

    lines += [
        '',
        '---',
        '',
        '## 二、各投资经理汇总状态',
        '',
        '| 投资经理 | 产品总数 | 已汇总 | 未汇总 | 状态 |',
        '|---------|---------|-------|-------|------|',
    ]
    for _, r in stats_df.sort_values(['未汇总', '投资经理'],
                                      ascending=[False, True]).iterrows():
        if r['未汇总'] == 0:
            status = '✅ 完成'
        elif r['已汇总'] > 0:
            status = '⚠️ 部分完成'
        else:
            status = '❌ 未提交'
        lines.append(
            f"| {r['投资经理']} | {r['产品总数']} | {r['已汇总']} "
            f"| {r['未汇总']} | {status} |"
        )

    lines += [
        '',
        '---',
        '',
        f'## 三、未汇总产品清单（共 {unfilled_count} 条）',
        '',
        '| 产品代码 | 产品名称 | 投资经理 |',
        '|---------|---------|---------|',
    ]
    for _, r in unfilled_df.iterrows():
        name = str(r['产品名称'])
        if len(name) > 35:
            name = name[:35] + '...'
        lines.append(f"| {r['产品代码']} | {name} | {r['主投资经理/投资经理姓名']} |")

    # 待催促
    not_submitted = stats_df[stats_df['已汇总'] == 0].sort_values('产品总数',
                                                                    ascending=False)
    if len(not_submitted):
        lines += [
            '',
            '---',
            '',
            '## 四、待催促提交的老师',
            '',
            '以下老师所有产品均未填写，请优先催促：',
            '',
        ]
        for _, r in not_submitted[not_submitted['产品总数'] >= 3].iterrows():
            lines.append(f"- **{r['投资经理']}**：{r['产品总数']} 个产品，全部未填")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✓ 说明文档已保存：{report_path}")


def _current_quarter() -> str:
    """返回当前季度字符串，如 '2026年一季报'"""
    m = datetime.now().month
    y = datetime.now().year
    q = ['一', '二', '三', '四'][(m - 1) // 3]
    return f'{y}年{q}季报'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='季报文件夹路径')
    parser.add_argument('--base', required=True, help='基础文件（主管理人的 Excel）')
    parser.add_argument('--extra', nargs='*', default=[], help='其他投资经理的 Excel 文件')
    parser.add_argument('--output', required=True, help='输出汇总 Excel 文件名')
    parser.add_argument('--report', default='汇总说明.md', help='输出说明文档文件名')
    args = parser.parse_args()

    if not args.extra:
        # 自动找其他 Excel
        all_xlsx = [f for f in os.listdir(args.folder)
                    if f.endswith('.xlsx') and f != args.base
                    and '汇总' not in f and '标签' not in f]
        args.extra = all_xlsx
        print(f"自动发现其他文件：{all_xlsx}")

    output_path = os.path.join(args.folder, args.output)
    merged = merge_excel_files(args.folder, args.base, args.extra, output_path)

    source_files = {args.base.replace('.xlsx', ''): (args.base, -1)}
    report_path = os.path.join(args.folder, args.report)
    generate_report(merged, args.folder, source_files, report_path)
