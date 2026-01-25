"""
市场观点美化 - 同花顺数据生成程序 v1.0

基于同花顺iFind API生成市场分析Excel文件
专注于国内市场数据（A股、债券、商品、外汇）

生成文件:
1. 近1月净值走势.xlsx - 日度行情数据
2. 指标值.xlsx - 指标统计和分位数分析

数据来源: 同花顺iFind金融数据API
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置区 ====================

# 同花顺API配置
IFIND_ACCESS_TOKEN = "33a71d06d1e9b9d2a880125487f0ed234b7e161d.signs_NjcxOTc0NDk2"
IFIND_API_BASE = "https://quantapi.51ifind.com/api/v1"
IFIND_HEADERS = {
    "Content-Type": "application/json",
    "access_token": IFIND_ACCESS_TOKEN
}

# 输出路径
OUTPUT_DIR = "/Users/fanshengxia/Desktop/市场观点美化/asset-analysis-real-data"

# 日期范围
END_DATE = datetime(2026, 1, 16)  # 设定为2026年1月16日
START_DATE_DAILY = END_DATE - timedelta(days=30)  # 近1月
START_DATE_WEEKLY = END_DATE - timedelta(days=365 * 3)  # 近3年

# 同花顺代码映射
IFIND_CODES = {
    # 日度行情数据（使用Wind格式代码，同花顺兼容）
    "daily": {
        "000001.SH": "上证指数",
        "000832.CSI": "中证转债",
        "AU.SHF": "沪金",
        "RB.SHF": "螺纹钢",
        "SC.INE": "原油",
        "M.DCE": "豆粕",
        "USDCNY.IB": "USDCNY中间价",
        "USDCNY1YS.IB": "掉期点1Y",
        "USDCNH.FX": "离岸人民币CNH",
    },

    # 经济数据库代码（债券收益率等）
    "edb": {
        # 中国债券收益率
        "L001619604": "中债国债10年",
        "L002959790": "中债国开债2年",  # 替代1年期
        "L003783688": "中债国开债9年",  # 替代10年期
        "L001619331": "中债AAA 2年",
        "L001618023": "中债AAA 1年",
        "L001619275": "中债国债2年",
    },

    # 周度指数数据
    "weekly": {
        "000001.SH": "上证指数",
        "USDCNY.IB": "USDCNY",
        "AU.SHF": "沪金",
        "RB.SHF": "螺纹钢",
        "HC.SHF": "热卷",
        "I.DCE": "铁矿石",
        "M.DCE": "豆粕期货",
        "USDCNY1YS.IB": "1年掉期点",
        "USDCNH.FX": "离岸人民币",
    }
}


# ==================== 同花顺API调用类 ====================

class IFindDataFetcher:
    """同花顺iFind数据获取器"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "access_token": access_token
        }
        self.base_url = IFIND_API_BASE

    def _post_request(self, endpoint, params):
        """统一的POST请求方法"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url=url, json=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return json.loads(response.content)
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ API请求失败: {e}")
            return None

    def get_history_quotation(self, codes, indicators, start_date, end_date, fill="Previous"):
        """
        获取历史行情数据（日频）

        Parameters:
        -----------
        codes : str or list
            证券代码，多个代码用逗号分隔
        indicators : str or list
            指标名称，如 "open,high,low,close"
        start_date : str
            开始日期 "YYYY-MM-DD"
        end_date : str
            结束日期 "YYYY-MM-DD"
        fill : str
            填充方式，"Previous"=前值填充, "Blank"=空值
        """
        if isinstance(codes, list):
            codes = ",".join(codes)
        if isinstance(indicators, list):
            indicators = ",".join(indicators)

        params = {
            "codes": codes,
            "indicators": indicators,
            "startdate": start_date,
            "enddate": end_date,
            "functionpara": {"Fill": fill}
        }

        return self._post_request("cmd_history_quotation", params)

    def get_edb_data(self, indicators, start_date, end_date):
        """
        获取经济数据库数据

        Parameters:
        -----------
        indicators : str or list
            EDB指标代码，多个代码用逗号分隔
        start_date : str
            开始日期 "YYYY-MM-DD"
        end_date : str
            结束日期 "YYYY-MM-DD"
        """
        if isinstance(indicators, list):
            indicators = ",".join(indicators)

        params = {
            "indicators": indicators,
            "startdate": start_date,
            "enddate": end_date
        }

        return self._post_request("edb_service", params)

    def get_date_sequence(self, codes, indicators, start_date, end_date, fill="Previous"):
        """
        获取日期序列数据（可获取基础数据和财务指标）

        Parameters:
        -----------
        codes : str or list
            证券代码
        indicators : list of dict
            指标配置列表，格式：[{"indicator": "ths_pe_ttm_stock", "indiparams": [""]}]
        start_date : str
            开始日期 "YYYYMMDD"
        end_date : str
            结束日期 "YYYYMMDD"
        """
        if isinstance(codes, list):
            codes = ",".join(codes)

        params = {
            "codes": codes,
            "startdate": start_date,
            "enddate": end_date,
            "functionpara": {"Fill": fill},
            "indipara": indicators
        }

        return self._post_request("date_sequence", params)


# ==================== 数据获取函数 ====================

def fetch_daily_data(fetcher, codes, start_date, end_date):
    """获取日度行情数据"""
    print(f"  获取 {len(codes)} 个资产的日度数据...")

    response = fetcher.get_history_quotation(
        codes=list(codes.keys()),
        indicators="close",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        fill="Previous"
    )

    if not response or 'tables' not in response:
        print(f"  ❌ 数据获取失败")
        return None

    # 解析返回数据
    tables = response['tables']
    if not tables:
        print(f"  ❌ 无数据返回")
        return None

    # 转换为DataFrame
    df_list = []
    for table in tables:
        code = table.get('thscode')
        time = table.get('time', [])
        table_data = table.get('table', {})

        if code and time and 'close' in table_data:
            df_temp = pd.DataFrame({
                'date': time,
                code: table_data['close']
            })
            df_list.append(df_temp)

    if not df_list:
        print(f"  ❌ 数据解析失败")
        return None

    # 合并所有数据
    df = df_list[0]
    for i in range(1, len(df_list)):
        df = pd.merge(df, df_list[i], on='date', how='outer')

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()

    print(f"  ✓ 获取成功: {len(df)} 个交易日")
    return df


def fetch_edb_data(fetcher, edb_codes, start_date, end_date):
    """获取经济数据库数据（债券收益率等）"""
    print(f"  获取 {len(edb_codes)} 个EDB指标...")

    response = fetcher.get_edb_data(
        indicators=list(edb_codes.keys()),
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    if not response or 'tables' not in response:
        print(f"  ❌ EDB数据获取失败")
        return None

    # 解析返回数据
    tables = response['tables']
    if not tables:
        print(f"  ❌ 无EDB数据返回")
        return None

    # 转换为DataFrame
    df_list = []
    for table in tables:
        indicator = table.get('indicator')
        time = table.get('time', [])
        table_data = table.get('table', {})

        if indicator and time and len(table_data) > 0:
            # 找到对应的中文名称
            indicator_name = edb_codes.get(indicator, indicator)
            # EDB返回的table是一个字典，取第一个值（数据列表）
            data_values = list(table_data.values())[0] if table_data else []

            df_temp = pd.DataFrame({
                'date': time,
                indicator_name: data_values
            })
            df_list.append(df_temp)

    if not df_list:
        print(f"  ❌ EDB数据解析失败")
        return None

    # 合并所有数据
    df = df_list[0]
    for i in range(1, len(df_list)):
        df = pd.merge(df, df_list[i], on='date', how='outer')

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()

    print(f"  ✓ 获取成功: {len(df)} 条记录")
    return df


def fetch_weekly_data(fetcher, codes, start_date, end_date):
    """获取周度数据"""
    print(f"  获取 {len(codes)} 个资产的周度数据...")

    # 同花顺没有直接的周度参数，我们获取日度数据后重采样
    response = fetcher.get_history_quotation(
        codes=list(codes.keys()),
        indicators="close",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        fill="Previous"
    )

    if not response or 'tables' not in response:
        print(f"  ❌ 周度数据获取失败")
        return None

    # 解析数据（同日度数据）
    tables = response['tables']
    df_list = []
    for table in tables:
        code = table.get('thscode')
        time = table.get('time', [])
        table_data = table.get('table', {})

        if code and time and 'close' in table_data:
            df_temp = pd.DataFrame({
                'date': time,
                code: table_data['close']
            })
            df_list.append(df_temp)

    if not df_list:
        return None

    df = df_list[0]
    for i in range(1, len(df_list)):
        df = pd.merge(df, df_list[i], on='date', how='outer')

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()

    # 重采样为周度（取每周最后一个交易日）
    df_weekly = df.resample('W').last()

    print(f"  ✓ 获取成功: {len(df_weekly)} 周")
    return df_weekly


def fetch_valuation_data(fetcher, codes, start_date, end_date):
    """获取估值数据（PE、PB）"""
    print(f"  获取估值数据（PE、PB）...")

    # 同花顺使用date_sequence接口获取PE、PB
    indicators = [
        {"indicator": "ths_pe_ttm_stock", "indiparams": [""]},  # PE(TTM)
        {"indicator": "ths_pb_stock", "indiparams": [""]}        # PB
    ]

    response = fetcher.get_date_sequence(
        codes=list(codes.keys()),
        indicators=indicators,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        fill="Previous"
    )

    if not response or 'tables' not in response:
        print(f"  ❌ 估值数据获取失败")
        return None

    # 解析数据
    pe_data = {}
    pb_data = {}

    tables = response.get('tables', [])
    for table in tables:
        code = table.get('thscode')
        if not code:
            continue

        # 解析PE数据
        if 'ths_pe_ttm_stock' in table:
            pe_table = table['ths_pe_ttm_stock']
            if 'time' in pe_table and 'table' in pe_table:
                pe_data[code] = pd.DataFrame({
                    'date': pd.to_datetime(pe_table['time']),
                    code: pe_table['table'][0] if len(pe_table['table']) > 0 else []
                }).set_index('date')

        # 解析PB数据
        if 'ths_pb_stock' in table:
            pb_table = table['ths_pb_stock']
            if 'time' in pb_table and 'table' in pb_table:
                pb_data[code] = pd.DataFrame({
                    'date': pd.to_datetime(pb_table['time']),
                    code: pb_table['table'][0] if len(pb_table['table']) > 0 else []
                }).set_index('date')

    if not pe_data and not pb_data:
        print(f"  ❌ 估值数据解析失败")
        return None

    # 合并PE数据
    df_pe = pd.concat([pe_data[code] for code in pe_data.keys()], axis=1) if pe_data else pd.DataFrame()
    # 合并PB数据
    df_pb = pd.concat([pb_data[code] for code in pb_data.keys()], axis=1) if pb_data else pd.DataFrame()

    print(f"  ✓ 获取成功")
    return {'PE': df_pe, 'PB': df_pb}


# ==================== 计算函数（基于Excel公式） ====================

def calculate_equity_bond_ratio(pe, bond_yield_pct):
    """
    股债性价比 = 1/PE - 国债收益率/100

    Parameters:
    -----------
    pe : float
        市盈率
    bond_yield_pct : float
        债券收益率（百分比，如2.5表示2.5%）
    """
    if pd.isna(pe) or pd.isna(bond_yield_pct) or pe <= 0:
        return np.nan
    return (1 / pe) - (bond_yield_pct / 100)


def calculate_credit_spread(credit_yield, treasury_yield):
    """
    信用利差 = (信用债收益率 - 国债收益率) × 100
    单位：基点(bp)
    """
    if pd.isna(credit_yield) or pd.isna(treasury_yield):
        return np.nan
    return (credit_yield - treasury_yield) * 100


def calculate_term_spread(long_yield, short_yield):
    """
    期限利差 = (长期收益率 - 短期收益率) × 100
    单位：基点(bp)
    """
    if pd.isna(long_yield) or pd.isna(short_yield):
        return np.nan
    return (long_yield - short_yield) * 100


def calculate_fx_hedging_cost(swap_points, offshore_cny):
    """
    锁汇成本 = -掉期点 / 10000 / 离岸人民币
    """
    if pd.isna(swap_points) or pd.isna(offshore_cny) or offshore_cny == 0:
        return np.nan
    return -swap_points / 10000 / offshore_cny


def calculate_cny_us_spread(cny_yield, us_yield):
    """
    中美利差 = (中国10年国债 - 美国10年国债) × 100
    单位：基点(bp)
    """
    if pd.isna(cny_yield) or pd.isna(us_yield):
        return np.nan
    return (cny_yield - us_yield) * 100


def calculate_steel_spread(hot_coil, rebar):
    """
    螺卷差 = 热卷价格 - 螺纹钢价格
    """
    if pd.isna(hot_coil) or pd.isna(rebar):
        return np.nan
    return hot_coil - rebar


# ==================== Excel生成函数 ====================

def generate_daily_trend(fetcher):
    """生成近1月净值走势表"""
    print("\n[2/5] 生成近1月净值走势...")

    # 获取日度数据
    daily_codes = IFIND_CODES['daily']
    daily_data = fetch_daily_data(fetcher, daily_codes, START_DATE_DAILY, END_DATE)

    if daily_data is None:
        print("❌ 日度数据获取失败")
        return False

    # 计算锁汇成本
    if "USDCNY1YS.IB" in daily_data.columns and "USDCNH.FX" in daily_data.columns:
        daily_data["锁汇成本"] = daily_data.apply(
            lambda row: calculate_fx_hedging_cost(row["USDCNY1YS.IB"], row["USDCNH.FX"]),
            axis=1
        )

    # 重命名列
    rename_map = {code: name for code, name in daily_codes.items()}
    df_output = daily_data.rename(columns=rename_map)

    # 添加日期列
    df_output.insert(0, '日期', df_output.index)

    # 删除中间计算列
    if "掉期点1Y" in df_output.columns:
        df_output = df_output.drop(columns=["掉期点1Y"])
    if "离岸人民币CNH" in df_output.columns:
        df_output = df_output.drop(columns=["离岸人民币CNH"])

    # 保存到Excel
    output_file = f"{OUTPUT_DIR}/近1月净值走势.xlsx"
    df_output.to_excel(output_file, index=False)

    # 格式化Excel
    format_excel(output_file)

    print(f"✓ 已生成: {output_file}")
    print(f"  - 交易日数: {len(df_output)}")
    print(f"  - 资产数: {len(df_output.columns) - 1}")

    return True


def generate_indicators():
    """生成指标值表"""
    print("\n[3/5] 获取周度数据...")

    fetcher = IFindDataFetcher(IFIND_ACCESS_TOKEN)

    # 获取估值数据
    valuation_codes = {"000001.SH": "上证指数"}
    valuation_data = fetch_valuation_data(fetcher, valuation_codes, START_DATE_WEEKLY, END_DATE)

    # 获取债券收益率数据
    bond_yields = fetch_edb_data(fetcher, IFIND_CODES['edb'], START_DATE_WEEKLY, END_DATE)

    # 获取周度行情数据
    weekly_codes = IFIND_CODES['weekly']
    weekly_data = fetch_weekly_data(fetcher, weekly_codes, START_DATE_WEEKLY, END_DATE)

    if valuation_data is None or bond_yields is None or weekly_data is None:
        print("❌ 数据获取失败")
        return False

    print("\n[4/5] 计算衍生指标...")

    # 计算股债性价比
    if "000001.SH" in valuation_data['PE'].columns:
        pe_sh = valuation_data['PE']["000001.SH"]
        bond_yield_cn = bond_yields["中债国债10年"]
        df_temp = pd.DataFrame({'pe': pe_sh, 'yield': bond_yield_cn})
        equity_bond_ratio_sh = df_temp.apply(
            lambda row: calculate_equity_bond_ratio(row['pe'], row['yield']),
            axis=1
        )
    else:
        equity_bond_ratio_sh = pd.Series()

    # 计算债券利差（使用2年和9年替代1年和10年）
    credit_spread_9y = bond_yields.apply(
        lambda row: calculate_credit_spread(row["中债国开债9年"], row["中债国债10年"]),
        axis=1
    )

    term_spread_9y = bond_yields.apply(
        lambda row: calculate_term_spread(row["中债国开债9年"], row["中债国开债2年"]),
        axis=1
    )

    credit_spread_2y = bond_yields.apply(
        lambda row: calculate_credit_spread(row["中债AAA 2年"], row["中债国债2年"]),
        axis=1
    )

    # 计算外汇指标
    if "USDCNY1YS.IB" in weekly_data.columns and "USDCNH.FX" in weekly_data.columns:
        fx_hedging_cost = weekly_data.apply(
            lambda row: calculate_fx_hedging_cost(row["USDCNY1YS.IB"], row["USDCNH.FX"]),
            axis=1
        )
    else:
        fx_hedging_cost = pd.Series()

    # 计算商品指标
    if "HC.SHF" in weekly_data.columns and "RB.SHF" in weekly_data.columns:
        steel_spread = weekly_data.apply(
            lambda row: calculate_steel_spread(row["HC.SHF"], row["RB.SHF"]),
            axis=1
        )
    else:
        steel_spread = pd.Series()

    print("\n[5/5] 计算指标统计值和分位数...")

    # 构建指标列表
    indicators = []

    # 权益类指标
    if "000001.SH" in valuation_data['PE'].columns:
        indicators.extend([
            {"大类": "权益", "子类": "上证指数", "指标": "PE", "数据": valuation_data['PE']["000001.SH"], "反转": False},
            {"大类": "权益", "子类": "上证指数", "指标": "PB", "数据": valuation_data['PB']["000001.SH"], "反转": False},
            {"大类": "权益", "子类": "上证指数", "指标": "股债性价比", "数据": equity_bond_ratio_sh, "反转": True},
        ])

    # 债券类指标
    indicators.extend([
        {"大类": "债券", "子类": "9年国开", "指标": "收益率", "数据": bond_yields["中债国开债9年"], "反转": True},
        {"大类": "债券", "子类": "9年国开", "指标": "信用利差", "数据": credit_spread_9y, "反转": False},
        {"大类": "债券", "子类": "9年国开", "指标": "期限利差", "数据": term_spread_9y, "反转": False},
        {"大类": "债券", "子类": "2年AAA", "指标": "收益率", "数据": bond_yields["中债AAA 2年"], "反转": True},
        {"大类": "债券", "子类": "2年AAA", "指标": "信用利差", "数据": credit_spread_2y, "反转": False},
    ])

    # 汇率类指标
    if len(fx_hedging_cost) > 0:
        indicators.extend([
            {"大类": "汇率", "子类": "锁汇成本", "指标": "锁汇成本", "数据": fx_hedging_cost, "反转": True},
            {"大类": "汇率", "子类": "锁汇成本", "指标": "掉期点1Y", "数据": weekly_data["USDCNY1YS.IB"], "反转": False},
            {"大类": "汇率", "子类": "锁汇成本", "指标": "离岸人民币CNH", "数据": weekly_data["USDCNH.FX"], "反转": True},
        ])

    if "USDCNY.IB" in weekly_data.columns:
        indicators.append(
            {"大类": "汇率", "子类": "USDCNY", "指标": "中间价", "数据": weekly_data["USDCNY.IB"], "反转": True}
        )

    # 商品类指标
    if len(steel_spread) > 0:
        indicators.append(
            {"大类": "商品", "子类": "螺纹钢", "指标": "螺卷差", "数据": steel_spread, "反转": False}
        )

    if "I.DCE" in weekly_data.columns:
        indicators.append(
            {"大类": "商品", "子类": "螺纹钢", "指标": "铁矿价格", "数据": weekly_data["I.DCE"], "反转": True}
        )

    if "USDCNY.IB" in weekly_data.columns:
        indicators.extend([
            {"大类": "商品", "子类": "沪金", "指标": "USDCNY中间价", "数据": weekly_data["USDCNY.IB"], "反转": True},
            {"大类": "商品", "子类": "原油", "指标": "USDCNY中间价", "数据": weekly_data["USDCNY.IB"], "反转": True},
        ])

    # 计算统计值和分位数
    result_rows = []
    for ind in indicators:
        series = ind["数据"].dropna()
        if len(series) == 0:
            continue

        current_value = series.iloc[-1]
        max_value = series.max()
        min_value = series.min()
        median_value = series.median()

        # 计算分位数
        percentile = series.rank(pct=True).iloc[-1]
        if ind["反转"]:
            percentile = 1 - percentile

        result_rows.append({
            "大类资产": ind["大类"],
            "子类资产": ind["子类"],
            "观察指标（近三年）": ind["指标"],
            "当前值": current_value,
            "最大值": max_value,
            "最小值": min_value,
            "历史中位数": median_value,
            "当前分位点": percentile
        })

    # 创建DataFrame
    df_indicators = pd.DataFrame(result_rows)

    # 保存到Excel
    output_file = f"{OUTPUT_DIR}/指标值.xlsx"
    df_indicators.to_excel(output_file, index=False)

    # 格式化Excel
    format_excel(output_file)

    print(f"✓ 已生成: {output_file}")
    print(f"  - 指标数: {len(df_indicators)}")

    return True


def format_excel(file_path):
    """格式化Excel文件"""
    wb = load_workbook(file_path)
    ws = wb.active

    # 设置表头样式
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    # 边框样式
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 应用表头样式
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # 应用边框到所有单元格
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = thin_border

    # 冻结首行
    ws.freeze_panes = 'A2'

    # 自动调整列宽
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(file_path)


# ==================== 主程序 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("市场观点美化 - 同花顺数据生成程序 v1.0")
    print("=" * 80)

    # 创建数据获取器
    fetcher = IFindDataFetcher(IFIND_ACCESS_TOKEN)

    # 步骤1：生成日度走势表
    if not generate_daily_trend(fetcher):
        print("\n❌ 日度走势表生成失败")
        return

    # 步骤2：生成指标值表
    if not generate_indicators():
        print("\n❌ 指标值表生成失败")
        return

    print("\n" + "=" * 80)
    print("✓ 所有文件生成完成!")
    print("=" * 80)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print("  1. 近1月净值走势.xlsx")
    print("  2. 指标值.xlsx")


if __name__ == '__main__':
    main()
