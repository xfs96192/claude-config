"""
nav-attribution 主脚本

输入: --config xx.json
输出至 config["output_dir"]:
  - 净值与归因.xlsx (5张sheet)
  - 今年以来净值走势对比.png (多产品场景)
  - summary.md
  - 校验日志.txt
"""
import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

# 中文字体
for f in ["PingFang SC", "Heiti SC", "Arial Unicode MS", "STHeiti", "SimHei"]:
    try:
        mpl.font_manager.findfont(f, fallback_to_default=False)
        mpl.rcParams['font.sans-serif'] = [f]
        break
    except Exception:
        continue
mpl.rcParams['axes.unicode_minus'] = False

# 让 classify 可被 import
sys.path.insert(0, str(Path(__file__).parent))
from classify import build_classifier  # noqa: E402

FEE_COLS = [
    '期间管理人报酬(元)', '期间销售服务费(元)', '期间托管费(元)',
    '期间超额管理费(元)', '期间税费(元)', '期间交易费用(元)',
]
NAV_DEFAULT_SHEET = "净值走势图"
CONTRIB_DEFAULT_SHEET = "资产收益贡献信息0"


def load_nav(path: str, sheet: Optional[str]) -> pd.DataFrame:
    sheet = sheet or NAV_DEFAULT_SHEET
    try:
        df = pd.read_excel(path, sheet_name=sheet)
    except Exception:
        # 兜底用第一个sheet
        df = pd.read_excel(path, sheet_name=0)
    if len(df.columns) < 2:
        raise ValueError(f"净值文件 {path} 至少要有 [日期, 净值] 两列")
    df = df.iloc[:, :2].copy()
    df.columns = ["日期", "净值"]
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.dropna(subset=["净值"]).sort_values("日期").reset_index(drop=True)
    return df


def load_contrib(path: str, sheet: Optional[str]) -> pd.DataFrame:
    sheet = sheet or CONTRIB_DEFAULT_SHEET
    try:
        df = pd.read_excel(path, sheet_name=sheet)
    except Exception:
        # 兜底：找含"资产收益贡献"的sheet
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True)
        cand = [s for s in wb.sheetnames if "资产收益贡献" in s]
        if not cand:
            raise ValueError(f"{path} 找不到资产收益贡献明细sheet")
        df = pd.read_excel(path, sheet_name=cand[0])
    return df


def nav_at(nav_df: pd.DataFrame, target: pd.Timestamp):
    """取目标日期或之前最近一个有效净值"""
    sub = nav_df[nav_df["日期"] <= target]
    if len(sub) == 0:
        return None, None
    last = sub.iloc[-1]
    return last["日期"], float(last["净值"])


def compute_nav_returns(nav_df: pd.DataFrame, periods: dict, end_date: pd.Timestamp):
    """返回 list of dict, 每个区间一条"""
    rows = []
    ed, ev = nav_at(nav_df, end_date)
    for name, start_str in periods.items():
        sd_target = pd.Timestamp(start_str)
        sd, sv = nav_at(nav_df, sd_target)
        if sv is None or ev is None:
            rows.append({
                "区间": name, "起始日期": None, "起始净值": None,
                "终止日期": None, "终止净值": None, "涨跌幅(%)": None,
            })
            continue
        ret = (ev / sv - 1) * 100
        rows.append({
            "区间": name,
            "起始日期": sd.strftime("%Y-%m-%d"),
            "起始净值": round(sv, 6),
            "终止日期": ed.strftime("%Y-%m-%d"),
            "终止净值": round(ev, 6),
            "涨跌幅(%)": round(ret, 6),
        })
    return rows


def attribute_one(contrib_df: pd.DataFrame, nav_return_pct: float, classify_fn):
    """对单个 (产品,区间) 做归因，返回 dict 含 by_cat / total_gross / fees / after_fee / df_with_cat"""
    df = contrib_df.copy()
    df["类别"] = df["资产名称"].apply(classify_fn)
    by_cat = df.groupby("类别")["资产杠杆后收益(元)"].sum()
    total_gross = float(df["资产杠杆后收益(元)"].sum())
    fees_row = df.iloc[0][FEE_COLS]
    total_fees = float(fees_row.sum())
    after_fee = total_gross - total_fees
    if total_gross == 0:
        attr_pct = by_cat * 0
    else:
        attr_pct = (by_cat / total_gross) * nav_return_pct
    return {
        "df": df,
        "by_cat": by_cat,
        "total_gross": total_gross,
        "fees_row": fees_row,
        "total_fees": total_fees,
        "after_fee": after_fee,
        "attr_pct": attr_pct,
    }


def make_ytd_chart(products_data: list, ytd_start: pd.Timestamp, end_date: pd.Timestamp, out_path: Path):
    """多产品净值走势对比PNG"""
    if len(products_data) < 1:
        return False
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), gridspec_kw={"height_ratios": [1, 1]})
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
    for i, pd_data in enumerate(products_data):
        name = pd_data["name"]
        nav = pd_data["nav"]
        sub = nav[(nav["日期"] >= ytd_start) & (nav["日期"] <= end_date)].copy()
        if len(sub) == 0:
            continue
        base = sub.iloc[0]["净值"]
        sub["归一化涨跌%"] = (sub["净值"] / base - 1) * 100
        c = colors[i % len(colors)]
        ax1.plot(sub["日期"], sub["净值"], label=f"{name} ({base:.4f} → {sub['净值'].iloc[-1]:.4f})", color=c, linewidth=1.6)
        ax2.plot(sub["日期"], sub["归一化涨跌%"], label=f"{name} (+{sub['归一化涨跌%'].iloc[-1]:.4f}%)", color=c, linewidth=1.8)
    ax1.set_title(f"产品净值走势对比 ({ytd_start.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})", fontsize=13, pad=10)
    ax1.set_ylabel("单位净值")
    ax1.legend(loc="lower right", fontsize=10)
    ax1.grid(alpha=0.3)
    ax2.set_title(f"以 {ytd_start.strftime('%Y-%m-%d')} 为基日的累计涨跌幅对比", fontsize=13, pad=10)
    ax2.set_ylabel("累计涨跌幅(%)")
    ax2.set_xlabel("日期")
    ax2.axhline(0, color="grey", linewidth=0.7, linestyle="--")
    ax2.legend(loc="lower right", fontsize=10)
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return True


def write_summary_md(out_md: Path, nav_table: pd.DataFrame, attr_pct_pivot: pd.DataFrame,
                     attr_income_pivot: pd.DataFrame, validate_rows: list):
    lines = ["# 产品净值与归因分析\n"]
    lines.append("## 一、净值涨跌幅对比\n")
    lines.append(nav_table.to_markdown(index=False))
    lines.append("\n\n## 二、归因汇总（费后归因到净值涨跌，单位：%）\n")
    lines.append(attr_pct_pivot.to_markdown(index=False))
    lines.append("\n\n## 三、归因明细（资产杠杆后收益，单位：元）\n")
    lines.append(attr_income_pivot.to_markdown(index=False))
    lines.append("\n\n## 四、费后核对\n")
    if validate_rows:
        v = pd.DataFrame(validate_rows)
        lines.append(v.to_markdown(index=False))
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="JSON配置文件路径")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    end_date = pd.Timestamp(cfg["end_date"])
    periods: dict = cfg["periods"]
    ytd_start = pd.Timestamp(cfg.get("ytd_start") or periods.get("今年以来") or end_date - pd.DateOffset(years=1))
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    classify_fn, eff_cats = build_classifier(cfg.get("classification_override"))

    # 净值涨跌幅对比（宽表）
    nav_rows = []
    products_data = []
    for prod in cfg["products"]:
        name = prod["name"]
        nav_df = load_nav(prod["nav_file"], prod.get("nav_sheet"))
        products_data.append({"name": name, "nav": nav_df})
        ret_rows = compute_nav_returns(nav_df, periods, end_date)
        for r in ret_rows:
            nav_rows.append({"产品": name, **r})

    nav_long = pd.DataFrame(nav_rows)
    # 透视成宽表，每个产品涨跌幅一列
    nav_wide = nav_long.pivot_table(index="区间", columns="产品", values="涨跌幅(%)").reset_index()
    nav_wide = nav_wide.reindex(columns=["区间"] + [p["name"] for p in cfg["products"]])
    nav_wide.columns = ["区间"] + [f"{c}_涨跌幅(%)" for c in nav_wide.columns[1:]]
    # 保留区间顺序
    nav_wide["区间"] = pd.Categorical(nav_wide["区间"], categories=list(periods.keys()), ordered=True)
    nav_wide = nav_wide.sort_values("区间").reset_index(drop=True)

    # 详细净值表（含起止日期、起止净值）
    nav_detail = nav_long.copy()

    # 归因
    attr_rows = []
    detail_rows = []
    validate_rows = []
    for prod in cfg["products"]:
        name = prod["name"]
        nav_df = next(p["nav"] for p in products_data if p["name"] == name)
        contrib_files = prod.get("contribution_files") or {}
        for period_name, fpath in contrib_files.items():
            # 找对应净值涨跌幅
            sub = nav_long[(nav_long["产品"] == name) & (nav_long["区间"] == period_name)]
            if len(sub) == 0 or sub.iloc[0]["涨跌幅(%)"] is None:
                continue
            nav_ret = float(sub.iloc[0]["涨跌幅(%)"])
            contrib_df = load_contrib(fpath, prod.get("contribution_sheet"))
            res = attribute_one(contrib_df, nav_ret, classify_fn)
            # 收集
            for cat in sorted(set(list(eff_cats.keys()) + ["债券"])):
                income = float(res["by_cat"].get(cat, 0))
                share = income / res["total_gross"] * 100 if res["total_gross"] else 0
                attr = float(res["attr_pct"].get(cat, 0))
                attr_rows.append({
                    "产品": name, "区间": period_name, "类别": cat,
                    "资产杠杆后收益(元)": round(income, 2),
                    "占总收益占比(%)": round(share, 4),
                    "归因净值涨跌(%)": round(attr, 6),
                    "净值涨跌(%)": round(nav_ret, 6),
                })
            # 明细
            for _, r in res["df"].iterrows():
                detail_rows.append({
                    "产品": name, "区间": period_name, "类别": r["类别"],
                    "资产大类": r.get("资产大类", ""), "资产小类": r.get("资产小类", ""),
                    "资产名称": r["资产名称"],
                    "资产杠杆后收益(元)": r["资产杠杆后收益(元)"],
                    "资产杠杆后日均规模(元)": r.get("资产杠杆后日均规模(元)", None),
                    "资产杠杆后回报率(%)": r.get("资产杠杆后回报率(%)", None),
                })
            # 校验
            avg_p = float(res["df"]["期间客户本金日均规模(元)"].iloc[0])
            after_fee_ret = res["after_fee"] / avg_p * 100 if avg_p else None
            report_ret = float(res["df"]["产品收益率(%)"].iloc[0])
            validate_rows.append({
                "产品": name, "区间": period_name,
                "净值涨跌(%)": round(nav_ret, 4),
                "费前收益(元)": round(res["total_gross"], 2),
                "费用(元)": round(res["total_fees"], 2),
                "费后收益(元)": round(res["after_fee"], 2),
                "费后/日均规模(%)": round(after_fee_ret, 4) if after_fee_ret is not None else None,
                "报表产品收益率(%)": round(report_ret, 4),
            })

    attr_df = pd.DataFrame(attr_rows)
    detail_df = pd.DataFrame(detail_rows)

    # 透视
    if not attr_df.empty:
        attr_pct_pivot = attr_df.pivot_table(index=["产品", "区间"], columns="类别", values="归因净值涨跌(%)").reset_index()
        attr_income_pivot = attr_df.pivot_table(index=["产品", "区间"], columns="类别", values="资产杠杆后收益(元)").reset_index()
    else:
        attr_pct_pivot = pd.DataFrame()
        attr_income_pivot = pd.DataFrame()

    # 输出
    xlsx_path = out_dir / "净值与归因.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        nav_wide.to_excel(writer, sheet_name="净值涨跌幅-宽表", index=False)
        nav_detail.to_excel(writer, sheet_name="净值涨跌幅-长表", index=False)
        if not attr_pct_pivot.empty:
            attr_pct_pivot.to_excel(writer, sheet_name="归因-涨跌占比%", index=False)
            attr_income_pivot.to_excel(writer, sheet_name="归因-收益元", index=False)
            attr_df.to_excel(writer, sheet_name="归因明细长表", index=False)
        if not detail_df.empty:
            detail_df.to_excel(writer, sheet_name="资产明细底表", index=False)
        if validate_rows:
            pd.DataFrame(validate_rows).to_excel(writer, sheet_name="费后核对", index=False)

    # PNG
    png_path = out_dir / "今年以来净值走势对比.png"
    made = make_ytd_chart(products_data, ytd_start, end_date, png_path)

    # summary.md
    md_path = out_dir / "summary.md"
    write_summary_md(md_path, nav_wide, attr_pct_pivot, attr_income_pivot, validate_rows)

    # 校验日志
    log_path = out_dir / "校验日志.txt"
    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"end_date={end_date.strftime('%Y-%m-%d')}\n")
        f.write(f"ytd_start={ytd_start.strftime('%Y-%m-%d')}\n")
        f.write(f"生效分类: {json.dumps(eff_cats, ensure_ascii=False, indent=2)}\n")
        f.write(f"产品数: {len(cfg['products'])}\n")
        for r in validate_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[OK] Excel: {xlsx_path}")
    print(f"[OK] Summary: {md_path}")
    print(f"[OK] Log: {log_path}")
    if made:
        print(f"[OK] Chart: {png_path}")
    else:
        print(f"[skip] Chart not generated")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERR] {e}")
        traceback.print_exc()
        sys.exit(1)
