#!/usr/bin/env python3
"""
个人基金持仓组合回测分析 - 输出生成脚本
用法:
  python3 generate_outputs.py \
    --holdings <holdings_csv> \
    --nav_dir <nav_data_dir> \
    --output_dir <output_dir> \
    --start_date YYYY-MM-DD \
    --end_date YYYY-MM-DD
"""
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import warnings
warnings.filterwarnings("ignore")

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti TC", "STHeiti", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = {
    "固收+": "#2196F3",
    "纯债": "#4CAF50",
    "货币基金": "#9E9E9E",
    "权益-A股": "#F44336",
    "权益-港股": "#FF9800",
    "权益-美股": "#9C27B0",
}

# ── Excel styling helpers ──────────────────────────────────────────────────────

def make_border():
    thin = Side(style="thin", color="CCCCCC")
    return Border(left=thin, right=thin, top=thin, bottom=thin)

BORDER = make_border()
CENTER = Alignment(horizontal="center", vertical="center")

HEADER_FILL = PatternFill("solid", start_color="1565C0", end_color="1565C0")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
SUB_FILL = PatternFill("solid", start_color="E3F2FD", end_color="E3F2FD")
SUB_FONT = Font(bold=True, color="1565C0", size=9)
NORMAL_FONT = Font(size=9)
ALT_FILL = PatternFill("solid", start_color="F5F9FF", end_color="F5F9FF")
POS_FONT = Font(size=9, color="2E7D32")   # 绿色正收益
NEG_FONT = Font(size=9, color="C62828")   # 红色负收益

def sc(cell, fill=None, font=None, alignment=CENTER, number_format=None):
    cell.border = BORDER
    if fill: cell.fill = fill
    if font: cell.font = font
    cell.alignment = alignment
    if number_format: cell.number_format = number_format

def pn_font(val):
    """根据正负收益返回字体颜色"""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return NORMAL_FONT
    return POS_FONT if val >= 0 else NEG_FONT


# ── Individual fund performance metrics ───────────────────────────────────────

def calc_fund_period_return(nav_series, end_date, days_back):
    """计算基金某时间段的累计收益率，若数据不足返回 None"""
    end = pd.Timestamp(end_date)
    start = end - pd.Timedelta(days=days_back)
    sub = nav_series[(nav_series.index <= end)]
    sub_start = sub[(sub.index >= start)]
    if len(sub_start) < 2:
        return None
    return sub_start.iloc[-1] / sub_start.iloc[0] - 1

def calc_fund_ann_return(nav_series, end_date, years_back=None):
    """计算年化收益率，years_back=None 表示成立以来"""
    end = pd.Timestamp(end_date)
    sub = nav_series[nav_series.index <= end]
    if years_back is not None:
        start = end - pd.DateOffset(years=years_back)
        sub = sub[sub.index >= start]
    if len(sub) < 10:
        return None
    days = (sub.index[-1] - sub.index[0]).days
    if days < 30:
        return None
    total = sub.iloc[-1] / sub.iloc[0] - 1
    return (1 + total) ** (365.25 / days) - 1

def calc_fund_max_drawdown(nav_series):
    """计算成立以来最大回撤"""
    if len(nav_series) < 2:
        return None
    roll_max = nav_series.cummax()
    dd = (nav_series - roll_max) / roll_max
    return float(dd.min())

def enrich_holdings_with_perf(holdings_df, nav_dir, end_date):
    """为每只基金计算各期收益率，追加为新列"""
    metrics_cols = {
        "近1周": 7,
        "近1月": 30,
        "近3月": 91,
        "近6月": 182,
        "近1年": 365,
    }

    results = {col: [] for col in metrics_cols}
    results["近3年年化"] = []
    results["成立以来年化"] = []
    results["成立以来最大回撤"] = []

    for _, row in holdings_df.iterrows():
        code = row["code"]
        fpath = os.path.join(nav_dir, f"{code}_nav.csv")
        if not os.path.exists(fpath):
            for col in results:
                results[col].append(None)
            continue

        df = pd.read_csv(fpath, parse_dates=["date"]).sort_values("date")
        nav = df.set_index("date")["nav"]
        nav = nav[~nav.index.duplicated(keep="last")]

        for col, days in metrics_cols.items():
            results[col].append(calc_fund_period_return(nav, end_date, days))

        results["近3年年化"].append(calc_fund_ann_return(nav, end_date, years_back=3))
        results["成立以来年化"].append(calc_fund_ann_return(nav, end_date, years_back=None))
        results["成立以来最大回撤"].append(calc_fund_max_drawdown(nav))

    for col, vals in results.items():
        holdings_df[col] = vals

    return holdings_df


# ── Performance metrics ────────────────────────────────────────────────────────

def calc_metrics(nav_series, rf=0.015):
    nav = nav_series.dropna()
    rets = nav.pct_change().dropna()
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total_ret = nav.iloc[-1] / nav.iloc[0] - 1
    ann_ret = (1 + total_ret) ** (1 / years) - 1
    ann_vol = rets.std() * np.sqrt(252)
    sharpe = (ann_ret - rf) / ann_vol if ann_vol > 0 else 0
    roll_max = nav.cummax()
    dd = (nav - roll_max) / roll_max
    max_dd = dd.min()
    dd_end = dd.idxmin()
    dd_start = nav[:dd_end].idxmax()
    calmar = ann_ret / abs(max_dd) if max_dd != 0 else 0
    monthly = nav.resample("M").last().pct_change().dropna()
    win_rate = (monthly > 0).mean()
    annual_ret = nav.resample("Y").last().pct_change().dropna()
    return {
        "累计收益率": total_ret,
        "年化收益率": ann_ret,
        "年化波动率": ann_vol,
        "夏普比率": sharpe,
        "最大回撤": max_dd,
        "最大回撤开始": dd_start.strftime("%Y-%m-%d"),
        "最大回撤结束": dd_end.strftime("%Y-%m-%d"),
        "卡玛比率": calmar,
        "月度胜率": win_rate,
        "期末净值": nav.iloc[-1],
        "年度收益": annual_ret,
    }

def period_metrics(nav, start, end, rf=0.015):
    sub = nav[(nav.index >= pd.Timestamp(start)) & (nav.index <= pd.Timestamp(end))]
    if len(sub) < 10:
        return None
    return calc_metrics(sub, rf)


# ── Portfolio construction ─────────────────────────────────────────────────────

def build_portfolio_nav(holdings_df, nav_dir, start_date, end_date):
    nav_dict = {}
    for _, row in holdings_df.iterrows():
        fpath = os.path.join(nav_dir, f"{row['code']}_nav.csv")
        if os.path.exists(fpath):
            df = pd.read_csv(fpath, parse_dates=["date"]).sort_values("date")
            nav_dict[row["code"]] = df

    all_dates = set()
    for df in nav_dict.values():
        all_dates.update(df["date"].tolist())
    date_range = pd.DatetimeIndex(sorted(all_dates))
    date_range = date_range[(date_range >= pd.Timestamp(start_date)) &
                            (date_range <= pd.Timestamp(end_date))]

    nav_panel = pd.DataFrame(index=date_range)
    for code, df in nav_dict.items():
        s = df.set_index("date")["nav"]
        s = s[~s.index.duplicated(keep="last")]
        nav_panel[code] = s.reindex(date_range)
    nav_panel = nav_panel.ffill()

    fund_starts = {code: df["date"].min() for code, df in nav_dict.items()}

    codes = [c for c in holdings_df["code"] if c in nav_panel.columns]
    weight_map = dict(zip(holdings_df["code"], holdings_df["weight"]))
    base_w = np.array([weight_map[c] for c in codes])
    ret_data = nav_panel[codes].pct_change().values

    for i, code in enumerate(codes):
        fsd = fund_starts.get(code, pd.Timestamp(start_date))
        mask = nav_panel.index < fsd
        ret_data[mask, i] = np.nan

    port_rets = []
    for row in ret_data:
        valid = ~np.isnan(row)
        if valid.sum() == 0:
            port_rets.append(0.0)
        else:
            w = base_w * valid
            w = w / w.sum()
            port_rets.append(float(np.dot(w, np.where(valid, row, 0))))

    nav_series = pd.Series(port_rets, index=nav_panel.index)
    nav_series = (1 + nav_series).cumprod()
    nav_series.iloc[0] = 1.0
    return nav_series


# ── Chart generation ───────────────────────────────────────────────────────────

def generate_chart(portfolio_nav, metrics, holdings_df, class_summary, sub_summary, end_date, output_path):
    fig = plt.figure(figsize=(20, 24))
    gs = GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(portfolio_nav.index, portfolio_nav.values, color="#1565C0", linewidth=1.8, label="组合净值")
    roll_max = portfolio_nav.cummax()
    dd_s = (portfolio_nav - roll_max) / roll_max
    dd_end = dd_s.idxmin()
    dd_start = portfolio_nav[:dd_end].idxmax()
    ax1.axvspan(dd_start, dd_end, alpha=0.15, color="red",
                label=f"最大回撤区间 ({metrics['最大回撤']:.1%})")
    ax1.set_title(f"持仓组合净值走势（至{end_date}）", fontsize=14, fontweight="bold", pad=10)
    ax1.set_ylabel("净值", fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_facecolor("#F8F9FA")
    textstr = (f"累计收益 {metrics['累计收益率']:.1%}  |  年化收益 {metrics['年化收益率']:.1%}  |  "
               f"年化波动 {metrics['年化波动率']:.1%}  |  最大回撤 {metrics['最大回撤']:.1%}  |  "
               f"夏普 {metrics['夏普比率']:.2f}  |  卡玛 {metrics['卡玛比率']:.2f}")
    ax1.text(0.5, -0.1, textstr, transform=ax1.transAxes, fontsize=10, ha="center", va="top",
             bbox=dict(boxstyle="round", facecolor="#EEF2FF", alpha=0.8))

    ax2 = fig.add_subplot(gs[1, :2])
    ann_ret = metrics["年度收益"]
    years = [str(y.year) for y in ann_ret.index]
    vals = ann_ret.values * 100
    bar_c = ["#EF5350" if v < 0 else "#42A5F5" for v in vals]
    bars = ax2.bar(years, vals, color=bar_c, width=0.65, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + (0.3 if val >= 0 else -1.2),
                 f"{val:.1f}%", ha="center",
                 va="bottom" if val >= 0 else "top", fontsize=9, fontweight="bold")
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("历年年度收益率", fontsize=12, fontweight="bold")
    ax2.set_ylabel("收益率 (%)", fontsize=10)
    ax2.set_facecolor("#F8F9FA")
    ax2.grid(axis="y", alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 2])
    dd_plot = dd_s * 100
    ax3.fill_between(dd_plot.index, dd_plot.values, 0, color="#EF5350", alpha=0.6)
    ax3.set_title("历史回撤序列", fontsize=12, fontweight="bold")
    ax3.set_ylabel("回撤 (%)", fontsize=10)
    ax3.set_facecolor("#F8F9FA")
    ax3.grid(axis="y", alpha=0.3)

    ax4 = fig.add_subplot(gs[2, 0])
    pie_labels = class_summary["asset_class"].tolist()
    pie_vals = class_summary["市值"].tolist()
    pie_colors = [COLORS.get(l, "#BDBDBD") for l in pie_labels]
    wedges, _, autotexts = ax4.pie(
        pie_vals, labels=None, colors=pie_colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for at in autotexts:
        at.set_fontsize(9)
    ax4.legend(wedges, pie_labels, loc="lower center", bbox_to_anchor=(0.5, -0.12),
               ncol=2, fontsize=8, frameon=False)
    ax4.set_title("大类资产配置占比", fontsize=12, fontweight="bold")

    ax5 = fig.add_subplot(gs[2, 1:])
    sub_top = sub_summary.sort_values("市值", ascending=True).tail(15)
    bar_c5 = [COLORS.get(r["asset_class"], "#78909C") for _, r in sub_top.iterrows()]
    bars2 = ax5.barh(sub_top["sub_class"], sub_top["占比%"], color=bar_c5, edgecolor="white", height=0.6)
    for bar, val in zip(bars2, sub_top["占比%"]):
        ax5.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                 f"{val:.1f}%", va="center", ha="left", fontsize=8)
    ax5.set_title("细分风格/策略占比", fontsize=12, fontweight="bold")
    ax5.set_xlabel("持仓占比 (%)", fontsize=10)
    ax5.set_facecolor("#F8F9FA")
    ax5.grid(axis="x", alpha=0.3)

    ax6 = fig.add_subplot(gs[3, :])
    top15 = holdings_df.nlargest(15, "market_value")
    bar_c6 = [COLORS.get(r["asset_class"], "#78909C") for _, r in top15.iterrows()]
    xpos = range(len(top15))
    bars3 = ax6.bar(xpos, top15["weight"] * 100, color=bar_c6, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars3, top15["weight"] * 100):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f"{val:.1f}%", ha="center", va="bottom", fontsize=8)
    ax6.set_xticks(list(xpos))
    ax6.set_xticklabels([n[:8] for n in top15["name"].tolist()],
                        rotation=30, ha="right", fontsize=9)
    ax6.set_title("前15大持仓权重", fontsize=12, fontweight="bold")
    ax6.set_ylabel("持仓占比 (%)", fontsize=10)
    ax6.set_facecolor("#F8F9FA")
    ax6.grid(axis="y", alpha=0.3)
    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in COLORS.items()]
    ax6.legend(handles=legend_patches, loc="upper right", ncol=3, fontsize=8, framealpha=0.8)

    plt.suptitle(f"个人公募基金持仓组合分析报告（截至{end_date}）",
                 fontsize=16, fontweight="bold", y=0.98)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"图表已保存: {output_path}")


# ── Excel report ───────────────────────────────────────────────────────────────

PERF_COLS = ["近1周", "近1月", "近3月", "近6月", "近1年", "近3年年化", "成立以来年化", "成立以来最大回撤"]

def generate_excel(holdings_df, class_summary, sub_summary, metrics, period_results,
                   portfolio_nav, total_mv, output_path):
    wb = Workbook()

    # ── Sheet 1: 持仓明细（含各期收益率）──
    ws1 = wb.active
    ws1.title = "持仓明细"

    base_headers = ["序号", "基金代码", "基金名称", "大类资产", "细分类型", "持仓市值(元)", "持仓权重"]
    perf_headers = ["近1周", "近1月", "近3月", "近6月", "近1年", "近3年年化", "成立以来年化", "成立以来最大回撤"]
    all_headers = base_headers + perf_headers

    # 表头
    for col, h in enumerate(all_headers, 1):
        cell = ws1.cell(row=1, column=col, value=h)
        sc(cell, fill=HEADER_FILL, font=HEADER_FONT)

    # 数据行
    for i, row in holdings_df.reset_index(drop=True).iterrows():
        r = i + 2
        fill = ALT_FILL if i % 2 == 0 else None

        # 基础列
        base_vals = [i+1, row["code"], row["name"], row["asset_class"],
                     row.get("sub_class", ""), row["market_value"], row["weight"]]
        for col, val in enumerate(base_vals, 1):
            cell = ws1.cell(row=r, column=col, value=val)
            sc(cell, fill=fill, font=NORMAL_FONT)
            if col == 6: cell.number_format = "#,##0.00"
            if col == 7: cell.number_format = "0.00%"

        # 收益率列（含正负颜色）
        for j, pcol in enumerate(PERF_COLS):
            col = len(base_headers) + j + 1
            val = row.get(pcol)
            if val is not None and not (isinstance(val, float) and np.isnan(val)):
                cell = ws1.cell(row=r, column=col, value=float(val))
                sc(cell, fill=fill, font=pn_font(val))
                cell.number_format = "0.00%"
            else:
                cell = ws1.cell(row=r, column=col, value="N/A")
                sc(cell, fill=fill, font=Font(size=9, color="999999"))

    # 合计行
    r_tot = len(holdings_df) + 2
    tot_vals = ["合计", "", "", "", "", total_mv, 1.0] + [""] * len(PERF_COLS)
    for col, val in enumerate(tot_vals, 1):
        cell = ws1.cell(row=r_tot, column=col, value=val)
        sc(cell, fill=SUB_FILL, font=Font(bold=True, size=9))
        if col == 6: cell.number_format = "#,##0.00"
        if col == 7: cell.number_format = "0.00%"

    # 列宽
    col_widths = [6, 10, 26, 12, 14, 14, 10, 8, 8, 8, 8, 8, 9, 10, 10]
    for i, w in enumerate(col_widths[:len(all_headers)], 1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    ws1.freeze_panes = "A2"

    # ── Sheet 2: 大类资产分析 ──
    ws2 = wb.create_sheet("大类资产分析")
    ws2.merge_cells("A1:D1"); ws2["A1"] = "一、大类资产配置"
    ws2["A1"].fill = HEADER_FILL; ws2["A1"].font = HEADER_FONT
    ws2["A1"].alignment = CENTER; ws2["A1"].border = BORDER
    for col, h in enumerate(["大类资产", "持仓市值(元)", "占比", "只数"], 1):
        sc(ws2.cell(row=2, column=col, value=h), fill=SUB_FILL, font=SUB_FONT)
    for i, row in class_summary.reset_index(drop=True).iterrows():
        r = i + 3
        fill = ALT_FILL if i % 2 == 0 else None
        for col, val in enumerate([row["asset_class"], row["市值"],
                                   row["持仓占比"]/100, row["只数"]], 1):
            cell = ws2.cell(row=r, column=col, value=val)
            sc(cell, fill=fill, font=NORMAL_FONT)
            if col == 2: cell.number_format = "#,##0.00"
            if col == 3: cell.number_format = "0.00%"
    r_tot2 = len(class_summary) + 3
    for col, val in enumerate(["合计", total_mv, 1.0, len(holdings_df)], 1):
        cell = ws2.cell(row=r_tot2, column=col, value=val)
        sc(cell, fill=SUB_FILL, font=Font(bold=True, size=9))
        if col == 2: cell.number_format = "#,##0.00"
        if col == 3: cell.number_format = "0.00%"

    ws2.merge_cells("F1:I1"); ws2["F1"] = "二、细分风格/策略"
    ws2["F1"].fill = HEADER_FILL; ws2["F1"].font = HEADER_FONT
    ws2["F1"].alignment = CENTER; ws2["F1"].border = BORDER
    for col, h in enumerate(["大类资产", "细分类型", "持仓市值(元)", "占比"], 6):
        sc(ws2.cell(row=2, column=col, value=h), fill=SUB_FILL, font=SUB_FONT)
    sub_sorted = sub_summary.sort_values(["asset_class", "市值"], ascending=[True, False])
    for i, row in sub_sorted.reset_index(drop=True).iterrows():
        r = i + 3
        fill = ALT_FILL if i % 2 == 0 else None
        for col, val in enumerate([row["asset_class"], row["sub_class"],
                                   row["市值"], row["占比%"]/100], 6):
            cell = ws2.cell(row=r, column=col, value=val)
            sc(cell, fill=fill, font=NORMAL_FONT)
            if col == 8: cell.number_format = "#,##0.00"
            if col == 9: cell.number_format = "0.00%"
    for i, w in enumerate([12, 16, 16, 10, 4, 12, 14, 16, 10], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ── Sheet 3: 组合业绩分析 ──
    ws3 = wb.create_sheet("组合业绩分析")
    ws3.merge_cells("A1:B1"); ws3["A1"] = "一、综合业绩指标"
    ws3["A1"].fill = HEADER_FILL; ws3["A1"].font = HEADER_FONT
    ws3["A1"].alignment = CENTER; ws3["A1"].border = BORDER
    items = [
        ("累计收益率", metrics["累计收益率"], "0.00%"),
        ("年化收益率", metrics["年化收益率"], "0.00%"),
        ("年化波动率", metrics["年化波动率"], "0.00%"),
        ("夏普比率（rf=1.5%）", metrics["夏普比率"], "0.00"),
        ("最大回撤", metrics["最大回撤"], "0.00%"),
        ("最大回撤区间", f"{metrics['最大回撤开始']} 至 {metrics['最大回撤结束']}", None),
        ("卡玛比率", metrics["卡玛比率"], "0.00"),
        ("月度胜率", metrics["月度胜率"], "0.00%"),
        ("期末净值（初始=1）", metrics["期末净值"], "0.0000"),
    ]
    for i, (label, val, fmt) in enumerate(items, 2):
        cell_l = ws3.cell(row=i, column=1, value=label)
        cell_v = ws3.cell(row=i, column=2, value=val)
        sc(cell_l, fill=SUB_FILL, font=Font(bold=True, size=9))
        sc(cell_v, font=NORMAL_FONT)
        if fmt: cell_v.number_format = fmt

    r2 = len(items) + 3
    ws3.merge_cells(f"A{r2}:E{r2}"); ws3[f"A{r2}"] = "二、分期段业绩指标"
    ws3[f"A{r2}"].fill = HEADER_FILL; ws3[f"A{r2}"].font = HEADER_FONT
    ws3[f"A{r2}"].alignment = CENTER; ws3[f"A{r2}"].border = BORDER
    for col, h in enumerate(["期间", "年化收益率", "最大回撤", "夏普比率", "年化波动率"], 1):
        sc(ws3.cell(row=r2+1, column=col, value=h), fill=SUB_FILL, font=SUB_FONT)
    for i, p in enumerate(period_results, r2+2):
        fill = ALT_FILL if i % 2 == 0 else None
        for col, val in enumerate([p["期间"], p["年化收益"], p["最大回撤"],
                                   p["夏普"], p["波动率"]], 1):
            cell = ws3.cell(row=i, column=col, value=val)
            sc(cell, fill=fill, font=NORMAL_FONT)
            if col in [2, 3, 5]: cell.number_format = "0.00%"
            if col == 4: cell.number_format = "0.00"

    r3 = r2 + len(period_results) + 3
    ws3.merge_cells(f"A{r3}:B{r3}"); ws3[f"A{r3}"] = "三、年度收益率"
    ws3[f"A{r3}"].fill = HEADER_FILL; ws3[f"A{r3}"].font = HEADER_FONT
    ws3[f"A{r3}"].alignment = CENTER; ws3[f"A{r3}"].border = BORDER
    for col, h in enumerate(["年份", "年度收益率"], 1):
        sc(ws3.cell(row=r3+1, column=col, value=h), fill=SUB_FILL, font=SUB_FONT)
    for i, (yr, ret) in enumerate(metrics["年度收益"].items(), r3+2):
        neg_fill = PatternFill("solid", start_color="FFF3E0", end_color="FFF3E0") if ret < 0 else (
            ALT_FILL if i % 2 == 0 else None)
        sc(ws3.cell(row=i, column=1, value=str(yr.year)), fill=neg_fill, font=NORMAL_FONT)
        cell_r = ws3.cell(row=i, column=2, value=ret)
        sc(cell_r, fill=neg_fill,
           font=Font(size=9, color="C62828" if ret < 0 else "2E7D32", bold=True))
        cell_r.number_format = "0.00%"

    for i, w in enumerate([22, 14, 12, 12, 12], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ── Sheet 4: 组合净值序列（月度）──
    ws4 = wb.create_sheet("组合净值序列")
    for col, h in enumerate(["日期", "组合净值（初始=1）", "累计收益率"], 1):
        sc(ws4.cell(row=1, column=col, value=h), fill=HEADER_FILL, font=HEADER_FONT)
    monthly = portfolio_nav.resample("M").last()
    for i, (dt, nav) in enumerate(monthly.items(), 2):
        ws4.cell(row=i, column=1, value=dt.strftime("%Y-%m-%d")).border = BORDER
        cell_n = ws4.cell(row=i, column=2, value=round(float(nav), 4))
        cell_n.border = BORDER; cell_n.number_format = "0.0000"
        cell_r = ws4.cell(row=i, column=3, value=float(nav) - 1)
        cell_r.border = BORDER; cell_r.number_format = "0.00%"
    for i, w in enumerate([14, 20, 14], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w
    ws4.freeze_panes = "A2"

    wb.save(output_path)
    print(f"Excel已保存: {output_path}")


# ── Markdown report ────────────────────────────────────────────────────────────

def generate_markdown(holdings_df, class_summary, sub_summary, metrics,
                      period_results, total_mv, start_date, end_date, output_path):
    ann_ret = metrics["年度收益"]

    class_table = "\n".join(
        f"| {r['asset_class']} | {r['市值']:,.2f} | {r['持仓占比']:.2f}% | {r['只数']} |"
        for _, r in class_summary.iterrows())

    sub_sorted = sub_summary.sort_values(["asset_class", "市值"], ascending=[True, False])
    sub_table = "\n".join(
        f"| {r['asset_class']} | {r['sub_class']} | {r['市值']:,.2f} | {r['占比%']:.2f}% |"
        for _, r in sub_sorted.iterrows())

    top10 = holdings_df.nlargest(10, "market_value")
    top10_table = "\n".join(
        f"| {i+1} | {r['code']} | {r['name']} | {r['asset_class']} | {r['market_value']:,.2f} | {r['weight']:.2%} |"
        for i, (_, r) in enumerate(top10.iterrows()))

    period_table = "\n".join(
        f"| {p['期间']} | {p['年化收益']:.2%} | {p['最大回撤']:.2%} | {p['夏普']:.2f} | {p['波动率']:.2%} |"
        for p in period_results)

    ann_rows = "\n".join(f"| {yr.year}年 | {ret:.2%} |" for yr, ret in ann_ret.items())

    cs = {r["asset_class"]: r for _, r in class_summary.iterrows()}

    def pct(cls):
        return cs[cls]["持仓占比"] if cls in cs else 0.0

    md = f"""# 个人公募基金持仓组合分析报告

> **数据截止：** {end_date} | **总市值：** ¥{total_mv:,.2f} 元 | **{len(holdings_df)} 只基金**

---

## 一、大类资产配置分析

### 1.1 大类资产分布

| 大类资产 | 持仓市值（元） | 占比 | 只数 |
|--------|------------|------|------|
{class_table}
| **合计** | **{total_mv:,.2f}** | **100.00%** | **{len(holdings_df)}** |

### 1.2 细分风格/策略分布

| 大类资产 | 细分类型 | 持仓市值（元） | 占比 |
|--------|--------|------------|------|
{sub_table}

---

## 二、前10大持仓

| 排名 | 基金代码 | 基金名称 | 大类资产 | 持仓市值（元） | 权重 |
|------|--------|--------|--------|------------|------|
{top10_table}

---

## 三、组合历史回测分析（{start_date} 至 {end_date}）

### 3.1 综合业绩指标

| 指标 | 数值 |
|------|------|
| 累计收益率 | **{metrics['累计收益率']:.2%}** |
| 年化收益率 | **{metrics['年化收益率']:.2%}** |
| 年化波动率 | {metrics['年化波动率']:.2%} |
| 夏普比率（rf=1.5%） | **{metrics['夏普比率']:.2f}** |
| 最大回撤 | **{metrics['最大回撤']:.2%}** |
| 最大回撤区间 | {metrics['最大回撤开始']} 至 {metrics['最大回撤结束']} |
| 卡玛比率 | {metrics['卡玛比率']:.2f} |
| 月度胜率 | {metrics['月度胜率']:.2%} |
| 期末净值（初始=1） | {metrics['期末净值']:.4f} |

### 3.2 分期段指标

| 期间 | 年化收益率 | 最大回撤 | 夏普 | 波动率 |
|------|----------|--------|------|------|
{period_table}

### 3.3 年度收益率

| 年份 | 收益率 |
|------|------|
{ann_rows}

---

## 四、收益风险特征分析

### 4.1 绝对回报
- 回测区间累计收益约 **{metrics['累计收益率']:.1%}**，年化约 **{metrics['年化收益率']:.1%}**
- 月度胜率 **{metrics['月度胜率']:.1%}**，大多数月份实现正收益

### 4.2 风险控制
- 年化波动率 **{metrics['年化波动率']:.1%}**，最大回撤 **{metrics['最大回撤']:.1%}**
- 主要回撤区间：{metrics['最大回撤开始']} 至 {metrics['最大回撤结束']}

### 4.3 资产配置特点
- 权益-A股占 {pct('权益-A股'):.1f}%，固收+占 {pct('固收+'):.1f}%，纯债占 {pct('纯债'):.1f}%
- 权益总敞口约 {sum(pct(c) for c in ['权益-A股','权益-港股','权益-美股']):.1f}%，固收类约 {sum(pct(c) for c in ['固收+','纯债']):.1f}%

---

*本报告仅供参考，不构成投资建议。历史业绩不代表未来表现。*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Markdown已保存: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--holdings", required=True)
    parser.add_argument("--nav_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--start_date", required=True)
    parser.add_argument("--end_date", required=True)
    args = parser.parse_args()

    holdings_df = pd.read_csv(args.holdings, dtype={"code": str})
    holdings_df["code"] = holdings_df["code"].str.zfill(6)  # 确保6位补零
    total_mv = holdings_df["market_value"].sum()

    # 计算每只基金的各期收益率
    print("计算各基金分期收益率...")
    holdings_df = enrich_holdings_with_perf(holdings_df, args.nav_dir, args.end_date)

    # 汇总统计
    class_summary = holdings_df.groupby("asset_class").agg(
        市值=("market_value", "sum"), 只数=("code", "count")).reset_index()
    class_summary["持仓占比"] = class_summary["市值"] / total_mv * 100
    class_summary = class_summary.sort_values("市值", ascending=False)

    sub_summary = holdings_df.groupby(["asset_class", "sub_class"]).agg(
        市值=("market_value", "sum")).reset_index()
    sub_summary["占比%"] = sub_summary["市值"] / total_mv * 100

    # 构建组合净值
    portfolio_nav = build_portfolio_nav(holdings_df, args.nav_dir, args.start_date, args.end_date)
    portfolio_nav.to_csv(os.path.join(args.output_dir, "portfolio_nav.csv"), header=["nav"])

    # 计算组合指标
    metrics = calc_metrics(portfolio_nav)

    # 分期段
    end_ts = pd.Timestamp(args.end_date)
    period_defs = [
        ("近1年", end_ts - pd.DateOffset(years=1), args.end_date),
        ("近3年", end_ts - pd.DateOffset(years=3), args.end_date),
        ("近5年", end_ts - pd.DateOffset(years=5), args.end_date),
        ("近10年", args.start_date, args.end_date),
        ("今年以来", end_ts.replace(month=1, day=1), args.end_date),
    ]
    period_results = []
    for label, s, e in period_defs:
        m = period_metrics(portfolio_nav, str(s)[:10], str(e)[:10])
        if m:
            period_results.append({
                "期间": label, "年化收益": m["年化收益率"],
                "最大回撤": m["最大回撤"], "夏普": m["夏普比率"], "波动率": m["年化波动率"]
            })

    # 生成三类输出
    generate_chart(
        portfolio_nav, metrics, holdings_df, class_summary, sub_summary,
        args.end_date,
        os.path.join(args.output_dir, "portfolio_analysis_chart.png"))

    generate_excel(
        holdings_df, class_summary, sub_summary, metrics, period_results,
        portfolio_nav, total_mv,
        os.path.join(args.output_dir, "portfolio_analysis_report.xlsx"))

    generate_markdown(
        holdings_df, class_summary, sub_summary, metrics, period_results,
        total_mv, args.start_date, args.end_date,
        os.path.join(args.output_dir, "portfolio_analysis_report.md"))

    # 保存带收益率的持仓底表
    holdings_df.to_csv(os.path.join(args.output_dir, "holdings_classified.csv"),
                       index=False, encoding="utf-8-sig")

    print("\n====== 全部输出完成 ======")


if __name__ == "__main__":
    main()
