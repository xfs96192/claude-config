#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_products.py
比较本期 Excel 与上期 Word 季报，输出新增/删除产品列表。

用法：
    python compare_products.py <excel_path> <prev_word_path> [--manager 徐莹]
"""
import sys
import argparse
import pandas as pd
from docx import Document


def extract_products_from_excel(excel_path: str, managers: list[str]) -> pd.DataFrame:
    """从 Excel 提取指定投资经理的产品列表"""
    df = pd.read_excel(excel_path, header=1)
    df['产品代码'] = df['产品代码'].astype(str).str.strip()
    mask = df['主投资经理/投资经理姓名'].astype(str).apply(
        lambda x: any(m in x for m in managers)
    )
    return df[mask][['产品代码', '产品名称', '主投资经理/投资经理姓名']].copy()


def extract_products_from_word(word_path: str) -> list[str]:
    """从上期 Word 季报中提取产品/系列短名称列表"""
    doc = Document(word_path)
    product_names = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # 识别产品标题段落（短段落且含冒号，或以产品关键词开头）
        keywords = ['合享', '悦动', '逸动', '兴动', '灵动', '绿色发展', '责任投资',
                    '优质企业', '价值回报', '资源优势', '兴承恒享', '增盈优选',
                    '丰利兴动', '多策略', '兴动ESG', '兴动未来']
        is_header = (len(text) < 30 and ('：' in text or text.endswith('：')))
        is_inline = any(text.startswith(kw) for kw in keywords)
        if is_header or is_inline:
            name = text.split('：')[0].split(':')[0].strip()
            if name and name != '投资策略和运作分析':
                product_names.append(name)
    return product_names


def normalize_product_name(full_name: str) -> str:
    """将 Excel 全称映射为季报短名称（用于比对）"""
    mapping = {
        'ESG兴动绿色发展': '绿色发展',
        'ESG兴动责任投资': '责任投资',
        'ESG兴动优质企业': '优质企业',
        'ESG兴动未来': '兴动未来1号',
        '兴动价值回报': '价值回报',
        '兴动多策略资源优势': '资源优势',
        '兴动多策略一年持有期3号': '多策略1年持有期3号',
        '兴动ESG日开': '丰利兴动ESG日开',
        '灵动全天候36号': '灵动36号',
        '灵动优选九个月': '灵动优选九个月持有期1号',
        '兴承恒享增盈两年': '兴承恒享1号',
        '逸动1个月最短持有期日开1号': '逸动1M',
        '悦动1个月最短持有期日开1号': '悦动1M',
        '悦动(9个月最短持有期)日开1号': '悦动9M',
        '悦动2号ESG': '悦动2号',
        'ESG悦动7号': '悦动7号',
        '逸动6个月最短持有期日开03号': '逸动6个月最短持有期日开03号',
        '逸动10个月最短持有期日开2号': '逸动10M 2号',
        '逸动1年最短持有期日开6号': '逸动1年6号',
        '逸动3个月最短持有期日开7号': '逸动3M日开7号',
        '灵动日开增强型': '灵动日开',
    }
    for key, val in mapping.items():
        if key in full_name:
            return val
    # 合享/悦动封闭式系列：提取编号
    import re
    m = re.search(r'合享封闭式(\d+)号', full_name)
    if m:
        return f'合享{m.group(1)}号'
    m = re.search(r'悦动封闭式(\d+)号', full_name)
    if m:
        return f'悦动{m.group(1)}号'
    return full_name


def main():
    parser = argparse.ArgumentParser(description='比较本期 Excel 与上期 Word 季报的产品变化')
    parser.add_argument('excel_path', help='本期 Excel 模板路径')
    parser.add_argument('prev_word_path', help='上期 Word 季报路径')
    parser.add_argument('--manager', nargs='+', default=['徐莹', '夏凡盛'],
                        help='要筛选的投资经理姓名（可多个）')
    args = parser.parse_args()

    print(f"筛选投资经理：{args.manager}")
    print()

    # 本期 Excel 产品
    excel_df = extract_products_from_excel(args.excel_path, args.manager)
    excel_short_names = {
        normalize_product_name(row['产品名称']): row
        for _, row in excel_df.iterrows()
    }

    # 上期 Word 产品
    prev_names = set(extract_products_from_word(args.prev_word_path))

    # 比较
    current_names = set(excel_short_names.keys())
    added = current_names - prev_names
    removed = prev_names - current_names
    unchanged = current_names & prev_names

    print(f"本期产品（{len(current_names)}）：")
    for n in sorted(current_names):
        print(f"  {n}")

    print(f"\n上期产品（{len(prev_names)}）：")
    for n in sorted(prev_names):
        print(f"  {n}")

    print(f"\n=== 新增产品（{len(added)}）——需在 Word 中添加 ===")
    for n in sorted(added):
        row = excel_short_names.get(n, {})
        manager = row.get('主投资经理/投资经理姓名', '') if isinstance(row, dict) else ''
        code = row.get('产品代码', '') if isinstance(row, dict) else ''
        print(f"  [{code}] {n}  ({manager})")

    print(f"\n=== 删除产品（{len(removed)}）——需从 Word 中移除 ===")
    for n in sorted(removed):
        print(f"  {n}")

    print(f"\n=== 保留产品（{len(unchanged)}）===")
    for n in sorted(unchanged):
        print(f"  {n}")

    return {
        'added': sorted(added),
        'removed': sorted(removed),
        'unchanged': sorted(unchanged),
        'excel_df': excel_df,
    }


if __name__ == '__main__':
    main()
