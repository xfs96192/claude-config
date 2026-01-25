#!/usr/bin/env python3
"""
生成产品运作报告的核心脚本
根据产品代码/名称和日期，自动生成标准化的产品运作说明
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def normalize_text(text):
    """标准化文本，去除空格"""
    if pd.isna(text):
        return ""
    return str(text).strip()

def find_operation_file(data_dir, date_str):
    """根据日期查找产品运作概览文件"""
    pattern = f"产品运作概览信息表增加指标变化_{date_str}.xlsx"
    files = list(Path(data_dir).glob(pattern))
    if not files:
        pattern = f"产品运作概览信息表_{date_str}.xlsx"
        files = list(Path(data_dir).glob(pattern))
    return files[0] if files else None

def find_holding_file(data_dir, date_str):
    """根据日期查找持仓盈亏文件"""
    pattern = f"持仓盈亏明细列表_{date_str}.xlsx"
    files = list(Path(data_dir).glob(pattern))
    return files[0] if files else None

def load_fund_classification(classification_file):
    """加载基金分类数据"""
    df = pd.read_excel(classification_file, sheet_name='修改稿')
    classifications = {}

    for _, row in df.iterrows():
        external_code = normalize_text(row['外部代码'])
        asset_code = normalize_text(row['资产代码'])
        style = normalize_text(row['风格'])
        equity_position = int(row['权益仓位']) if pd.notna(row['权益仓位']) else 0

        match_key = external_code if external_code else asset_code
        if match_key and style:
            classifications[match_key] = {
                'style': style,
                'equity_position': equity_position
            }

    return classifications

def calculate_style_distribution(holding_df, product_name, classifications):
    """计算权益持仓风格分布"""
    product_holdings = holding_df[holding_df['产品简称'] == product_name].copy()

    if product_holdings.empty:
        return None

    style_exposures = {}

    for _, row in product_holdings.iterrows():
        external_code = normalize_text(row['外部代码'])
        asset_code = normalize_text(row['资产代码'])
        holding_value = float(row['日终市值(元)-产品法估值']) if pd.notna(row['日终市值(元)-产品法估值']) else 0

        if holding_value == 0:
            continue

        match_key = external_code if external_code else asset_code
        classification = classifications.get(match_key)

        if classification:
            style = classification['style']
            equity_position = classification['equity_position']
            equity_exposure = holding_value * (equity_position / 100)

            if style not in style_exposures:
                style_exposures[style] = 0
            style_exposures[style] += equity_exposure

    total_equity = sum(style_exposures.values())
    if total_equity == 0:
        return None

    style_percentages = {style: (value / total_equity) * 100
                        for style, value in style_exposures.items()}

    return style_percentages

def format_style_distribution(style_dist):
    """格式化风格分布为文本"""
    if not style_dist:
        return "无权益持仓"

    sorted_styles = sorted(style_dist.items(), key=lambda x: x[1], reverse=True)
    parts = [f"{style}{percent:.0f}%" for style, percent in sorted_styles]
    return "、".join(parts)

def generate_report(product_identifier, date_str, operation_dir, holding_dir, classification_file):
    """生成产品运作报告"""

    operation_file = find_operation_file(operation_dir, date_str)
    if not operation_file:
        return f"错误：找不到日期 {date_str} 的产品运作概览文件"

    holding_file = find_holding_file(holding_dir, date_str)
    if not holding_file:
        return f"错误：找不到日期 {date_str} 的持仓盈亏文件"

    operation_df = pd.read_excel(operation_file)

    product_row = operation_df[
        (operation_df['产品代码'] == product_identifier) |
        (operation_df['产品简称'] == product_identifier)
    ]

    if product_row.empty:
        return f"错误：找不到产品 {product_identifier}"

    product_row = product_row.iloc[0]

    product_name = product_row['产品简称']
    annual_return = product_row['累计年化']
    duration = product_row['组合久期']
    leverage = product_row['杠杆']
    equity_position = product_row['权益仓位']

    holding_df = pd.read_excel(holding_file)
    classifications = load_fund_classification(classification_file)

    style_dist = calculate_style_distribution(holding_df, product_name, classifications)
    style_text = format_style_distribution(style_dist)

    date_obj = datetime.strptime(date_str, "%Y%m%d")
    date_display = f"{date_obj.month}月{date_obj.day}日"

    report = (
        f"截止{date_display}，{product_name}当前组合成立以来年化收益率为{annual_return:.2%}，"
        f"组合有效久期约{duration:.2f}年，杠杆{leverage:.0%}，"
        f"权益仓位{equity_position:.1%}左右，权益持仓风格分布为{style_text}。"
    )

    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <产品代码或名称> <日期YYYYMMDD>")
        print("示例: python generate_report.py 逸动1年 20260115")
        sys.exit(1)

    product_identifier = sys.argv[1]
    date_str = sys.argv[2]

    operation_dir = Path("/Users/fanshengxia/Desktop/周报V2/数据/产品运作概览数据-母子产品")
    holding_dir = Path("/Users/fanshengxia/Desktop/周报V2/数据/周度更新数据")
    classification_file = Path("/Users/fanshengxia/Desktop/投资助理工作/基金分类标签/基金分类数据_2026-01.xlsx")

    report = generate_report(product_identifier, date_str, operation_dir, holding_dir, classification_file)
    print(report)
