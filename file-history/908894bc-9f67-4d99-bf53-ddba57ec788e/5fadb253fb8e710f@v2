#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill_excel.py
从更新后的 Word 季报提取各产品策略文本，填入 Excel 对应行。

用法：
    python fill_excel.py <word_path> <excel_path> \
        --code-map 9K221040:绿色发展 9K221050:责任投资 ...

    或者直接调用 fill_excel_from_word() 函数（推荐）
"""
import sys
import argparse
from docx import Document
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

STRAT_COL_KEY = '投资策略'  # 用于定位策略列（模糊匹配）


def extract_content_from_word(word_path: str) -> dict[str, str]:
    """
    从 Word 文档提取每个产品的完整策略文本。
    返回：{产品代码: 策略文本}
    需要传入 code_to_para_indices 映射（产品代码 → 段落索引列表）。
    """
    doc = Document(word_path)
    paras = [p.text.strip() for p in doc.paragraphs]
    return paras


def build_content_map(paras: list[str],
                      code_para_map: dict[str, list[int]]) -> dict[str, str]:
    """
    根据段落索引映射构建 {产品代码: 策略文本}。
    多段落内容用换行符合并（每段首加两个全角空格）。
    """
    result = {}
    for code, indices in code_para_map.items():
        parts = [paras[i] for i in indices if i < len(paras) and paras[i]]
        if parts:
            result[code] = '\n  '.join(parts)
    return result


def fill_excel_from_word(
    word_path: str,
    excel_path: str,
    code_para_map: dict[str, list[int]],
    output_path: str = None,
) -> dict[str, int]:
    """
    主函数：从 Word 提取文本，填入 Excel。

    Args:
        word_path: 更新后的 Word 文档路径
        excel_path: Excel 模板路径
        code_para_map: {产品代码: [段落索引, ...]} 的映射
                       例如 {'9K221040': [3, 5], '9K221050': [8, 10, 11]}
        output_path: 输出 Excel 路径（None 则覆盖 excel_path）

    Returns:
        {'filled': 填入数量, 'not_found': 未找到的产品代码列表}
    """
    if output_path is None:
        output_path = excel_path

    # 提取 Word 文本
    paras = extract_content_from_word(word_path)
    content_map = build_content_map(paras, code_para_map)
    print(f"从 Word 提取 {len(content_map)} 个产品策略文本")

    # 读取 Excel
    wb = load_workbook(excel_path)
    ws = wb.active

    # 找到策略列和产品代码列
    header_row = 2
    code_col = strategy_col = None
    for cell in ws[header_row]:
        if cell.value and '产品代码' in str(cell.value):
            code_col = cell.column
        if cell.value and STRAT_COL_KEY in str(cell.value):
            strategy_col = cell.column

    if not code_col or not strategy_col:
        raise ValueError(f"未找到必要列（产品代码列={code_col}, 策略列={strategy_col}）")

    # 填入
    filled = 0
    not_found = []
    for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row):
        code_cell = row[code_col - 1]
        code = str(code_cell.value).strip() if code_cell.value else ''
        if code in content_map:
            cell = row[strategy_col - 1]
            cell.value = content_map[code]
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            filled += 1
        elif code and code not in ('nan', '', 'None'):
            # 检查是否是目标投资经理的产品（第3列）
            manager_cell = row[2]
            manager = str(manager_cell.value) if manager_cell.value else ''
            if any(m in manager for m in ['徐莹', '夏凡盛']):
                not_found.append(code)

    wb.save(output_path)
    print(f"已填入 {filled} 个产品，保存至：{output_path}")
    if not_found:
        print(f"⚠ 以下产品代码未在 code_para_map 中配置：{not_found}")

    return {'filled': filled, 'not_found': not_found}


def auto_detect_para_indices(word_path: str) -> dict[str, tuple[str, list[int]]]:
    """
    自动检测 Word 文档中各产品的段落索引。
    返回：{产品短名: (首行文字, [段落索引列表])}
    用于辅助人工确认 code_para_map。
    """
    doc = Document(word_path)
    paras = [(i, p.text.strip()) for i, p in enumerate(doc.paragraphs)]

    product_keywords = [
        '绿色发展', '责任投资', '优质企业', '多策略1年', '兴动ESG日开', '丰利兴动ESG',
        '价值回报', '资源优势', '灵动优选九个月', '逸动1M', '逸动6个月', '逸动10M',
        '逸动1年', '逸动3M', '兴动未来', '兴承恒享', '灵动36号', '灵动日开',
        '悦动9M', '悦动1M', '悦动2号', '悦动7号', '合享', '悦动封闭',
    ]

    result = {}
    for i, text in paras:
        if not text:
            continue
        for kw in product_keywords:
            if kw in text:
                short = text[:25]
                result[short] = (text[:60], [i])
                break

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word_path', help='更新后的 Word 季报')
    parser.add_argument('excel_path', help='Excel 模板')
    parser.add_argument('--detect', action='store_true',
                        help='自动检测段落索引（用于辅助配置 code_para_map）')
    args = parser.parse_args()

    if args.detect:
        indices = auto_detect_para_indices(args.word_path)
        print("检测到以下产品段落：")
        for name, (text, idxs) in indices.items():
            print(f"  [{idxs}] {text}")
    else:
        print("请使用 --detect 参数检测段落索引，或在代码中直接调用 fill_excel_from_word()")
