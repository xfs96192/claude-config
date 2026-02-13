#!/usr/bin/env python3
"""
RQData 查询辅助工具
自动修正代码格式并执行查询
"""

def normalize_code(code: str, asset_type: str = 'auto') -> str:
    """
    自动修正合约代码格式

    Args:
        code: 原始代码
        asset_type: 资产类型 ('fund', 'stock', 'convertible', 'auto')

    Returns:
        修正后的代码
    """
    code = code.strip().upper()

    # 基金代码修正（去除.OF后缀）
    if code.endswith('.OF'):
        return code.replace('.OF', '')

    # 股票/ETF代码修正
    if '.SH' in code:
        return code.replace('.SH', '.XSHG')
    if '.SZ' in code:
        return code.replace('.SZ', '.XSHE')

    # 港股代码修正
    if '.HK' in code:
        return code.replace('.HK', '.XHKG')

    # 如果已经是标准格式或纯数字（基金），直接返回
    return code


def validate_fund_code(code: str) -> tuple[bool, str]:
    """
    验证基金代码是否有效

    Returns:
        (是否有效, 修正后的代码)
    """
    import rqdatac

    # 先尝试原始代码
    normalized = normalize_code(code, 'fund')

    try:
        fund_info = rqdatac.fund.instruments(normalized)
        if fund_info is not None:
            return True, normalized
    except:
        pass

    # 如果失败，尝试搜索
    try:
        all_funds = rqdatac.fund.all_instruments()
        matches = all_funds[all_funds['order_book_id'].str.contains(normalized, na=False)]
        if len(matches) > 0:
            correct_code = matches.iloc[0]['order_book_id']
            return True, correct_code
    except:
        pass

    return False, normalized


if __name__ == '__main__':
    # 测试用例
    test_cases = [
        '090007.OF',
        '110022.OF',
        '600000.SH',
        '000001.SZ',
        '113002.SH',
    ]

    for code in test_cases:
        normalized = normalize_code(code)
        print(f"{code:15s} → {normalized}")
