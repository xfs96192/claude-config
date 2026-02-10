#!/usr/bin/env python3
"""
生成产品运作说明/近期波动解释

兼容旧用法：
  python scripts/generate_report.py <产品代码或产品名称> <日期YYYYMMDD>
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd


DEFAULT_OPERATION_DIR = Path("/Users/fanshengxia/Desktop/周报V2/数据/产品运作概览数据-母子产品")
DEFAULT_HOLDING_DIR = Path("/Users/fanshengxia/Desktop/周报V2/数据/周度更新数据")
DEFAULT_CLASSIFICATION_DIR = Path("/Users/fanshengxia/Desktop/投资助理工作/基金分类标签")
DEFAULT_EQUITY_STYLE_SCRIPT = Path(
    "/Users/fanshengxia/Desktop/投资助理工作/基金分类标签/generate_equity_style_report.py"
)


def normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def parse_date(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"日期格式不支持：{value}（支持 YYYYMMDD / YYYY-MM-DD）")


def format_cn_md(date_obj: datetime) -> str:
    return f"{date_obj.month}月{date_obj.day}日"


def find_operation_file(operation_dir: Path, date_str_yyyymmdd: str) -> Optional[Path]:
    patterns = [
        f"产品运作概览信息表增加指标变化_{date_str_yyyymmdd}.xlsx",
        f"产品运作概览信息表_{date_str_yyyymmdd}.xlsx",
    ]
    for pattern in patterns:
        files = list(operation_dir.glob(pattern))
        if files:
            return files[0]
    return None


def find_holding_file(holding_dir: Path, date_str_yyyymmdd: str) -> Optional[Path]:
    files = list(holding_dir.glob(f"持仓盈亏明细列表_{date_str_yyyymmdd}.xlsx"))
    return files[0] if files else None


def find_latest_classification_file(classification_dir: Path) -> Optional[Path]:
    candidates = sorted(classification_dir.glob("基金分类数据_*.xlsx"))
    return candidates[-1] if candidates else None


def _read_excel(path: Path, **kwargs: Any) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl", **kwargs)


def load_operation_df(operation_file: Path) -> pd.DataFrame:
    df = _read_excel(operation_file)
    if "产品代码" not in df.columns or "产品简称" not in df.columns:
        raise ValueError("产品运作概览文件缺少必要列：产品代码/产品简称")
    df["产品代码"] = df["产品代码"].map(normalize_text)
    df["产品简称"] = df["产品简称"].map(normalize_text)
    return df


def select_product_row(operation_df: pd.DataFrame, product_identifier: str) -> pd.Series:
    pid = normalize_text(product_identifier)
    exact = operation_df[(operation_df["产品代码"] == pid) | (operation_df["产品简称"] == pid)]
    if len(exact) == 1:
        return exact.iloc[0]
    if len(exact) > 1:
        raise ValueError(f"产品标识匹配到多条记录：{pid}（请使用更精确的产品代码）")

    # 允许简称包含匹配（唯一时）
    fuzzy = operation_df[operation_df["产品简称"].str.contains(pid, na=False)]
    if len(fuzzy) == 1:
        return fuzzy.iloc[0]
    if len(fuzzy) > 1:
        raise ValueError(f"产品简称模糊匹配到多条记录：{pid}（请改用产品代码或完整简称）")

    raise ValueError(f"找不到产品：{pid}")


def _dynamic_import(module_path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ImportError(f"无法加载模块：{module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compute_equity_style_distribution(
    product_name: str,
    holding_file: Path,
    classification_file: Path,
    equity_style_script: Path,
) -> Dict[str, float]:
    """
    使用指定的 generate_equity_style_report.py 计算“权益持仓风格分布”（占总权益暴露的比例）。
    返回：{风格: 百分比(0-100)}
    """
    if not equity_style_script.exists():
        raise FileNotFoundError(f"找不到权益风格计算脚本：{equity_style_script}")

    mod = _dynamic_import(equity_style_script, "equity_style_report")

    # 外部脚本含较多控制台输出；这里静默处理，只保留最终文案输出
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        df_holding, df_trade, df_classification, product_order, _style_order = mod.load_data(
            str(holding_file), str(classification_file)
        )
        fund_classifications = mod.build_fund_classifications(df_classification)
        trade_map = mod.build_trade_map(df_trade, product_order, df_holding)
        product_net_assets = mod.calculate_product_net_assets(df_holding)
        detail_data = mod.process_holdings(df_holding, fund_classifications, trade_map, product_net_assets)
        product_results, _product_total_equity = mod.aggregate_results(detail_data)

    if product_name not in product_results:
        raise ValueError(f"权益风格结果中找不到产品：{product_name}（请检查持仓表的产品简称）")

    style_map: Dict[str, float] = {}
    for style, info in product_results[product_name].items():
        pct = float(info.get("percentage", 0))
        if pct > 0:
            style_map[str(style)] = pct

    if not style_map:
        raise ValueError(f"产品无可用权益风格分布：{product_name}")
    return style_map


def format_style_distribution(style_dist: Dict[str, float]) -> str:
    sorted_styles = sorted(style_dist.items(), key=lambda x: x[1], reverse=True)
    parts = [f"{style}{pct:.0f}%" for style, pct in sorted_styles]
    return "、".join(parts)


@dataclass(frozen=True)
class StageBpMetrics:
    period_bp: float
    week_bp: float
    month_bp: float


def _to_float(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _extract_bp_from_row(row: pd.Series) -> Optional[float]:
    bp_cols = [
        "净值变动bp",
        "净值变动BP",
        "区间净值变动bp",
        "区间净值变动BP",
        "净值累计变动bp",
        "净值累计变动BP",
    ]
    for c in bp_cols:
        if c in row.index:
            v = _to_float(row.get(c))
            if v is not None:
                return v

    # 支持收益率列（%或小数）
    for c in ["区间收益率", "区间收益率(%)", "收益率", "收益率(%)"]:
        if c in row.index:
            v = _to_float(row.get(c))
            if v is None:
                continue
            # 经验规则：绝对值<1 视为小数；否则视为百分数
            if abs(v) < 1:
                return v * 10000
            return (v / 100) * 10000

    return None


def load_stage_df(stage_file: Path) -> pd.DataFrame:
    if stage_file.suffix.lower() in (".csv", ".tsv"):
        sep = "\t" if stage_file.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(stage_file, sep=sep)
    else:
        df = _read_excel(stage_file)

    # 标准化常见列名
    rename_map = {
        "开始日期": "起始日期",
        "起始日": "起始日期",
        "结束日期": "截止日期",
        "终止日期": "截止日期",
        "截止日": "截止日期",
        "阶段名称": "阶段",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


def extract_stage_metrics(
    stage_df: pd.DataFrame,
    product_code: str,
    product_name: str,
    period_start: datetime,
    period_end: datetime,
    week_stage_name: str = "近1周",
    month_stage_name: str = "近1月",
) -> StageBpMetrics:
    df = stage_df.copy()
    for c in ["产品代码", "产品简称", "阶段"]:
        if c in df.columns:
            df[c] = df[c].map(normalize_text)

    if "起始日期" in df.columns:
        df["起始日期_dt"] = df["起始日期"].map(lambda x: parse_date(str(x)) if normalize_text(x) else None)
    else:
        df["起始日期_dt"] = None
    if "截止日期" in df.columns:
        df["截止日期_dt"] = df["截止日期"].map(lambda x: parse_date(str(x)) if normalize_text(x) else None)
    else:
        df["截止日期_dt"] = None

    mask = pd.Series([True] * len(df))
    if "产品代码" in df.columns and product_code:
        mask = mask & (df["产品代码"] == product_code)
    if "产品简称" in df.columns and product_name:
        # 若代码匹配失败，使用简称兜底
        mask_code = mask.copy()
        mask_name = df["产品简称"] == product_name
        mask = mask_code | mask_name

    df_p = df[mask].copy()
    if df_p.empty:
        raise ValueError("阶段表现数据中未找到该产品（请检查 产品代码/产品简称 列）")

    def pick_by_dates() -> Optional[pd.Series]:
        if df_p["起始日期_dt"].isna().all() or df_p["截止日期_dt"].isna().all():
            return None
        m = (df_p["起始日期_dt"] == period_start) & (df_p["截止日期_dt"] == period_end)
        hits = df_p[m]
        if len(hits) == 1:
            return hits.iloc[0]
        return None

    period_row = pick_by_dates()
    if period_row is None and "阶段" in df_p.columns:
        # 尝试阶段为“自定义区间/区间/本次区间”等且日期匹配
        candidates = df_p[df_p["阶段"].isin(["自定义区间", "区间", "本次区间", "本段区间"])]
        if not candidates.empty and not candidates["起始日期_dt"].isna().all():
            m = (candidates["起始日期_dt"] == period_start) & (candidates["截止日期_dt"] == period_end)
            hits = candidates[m]
            if len(hits) == 1:
                period_row = hits.iloc[0]

    week_row = None
    month_row = None
    if "阶段" in df_p.columns:
        w = df_p[df_p["阶段"] == week_stage_name]
        m = df_p[df_p["阶段"] == month_stage_name]
        if len(w) >= 1:
            week_row = w.iloc[0]
        if len(m) >= 1:
            month_row = m.iloc[0]

    period_bp = _extract_bp_from_row(period_row) if period_row is not None else None
    week_bp = _extract_bp_from_row(week_row) if week_row is not None else None
    month_bp = _extract_bp_from_row(month_row) if month_row is not None else None

    missing = []
    if period_bp is None:
        missing.append("区间累计bp（period）")
    if week_bp is None:
        missing.append("近1周bp（week）")
    if month_bp is None:
        missing.append("近1月bp（month）")
    if missing:
        raise ValueError("阶段表现数据缺少必要字段：" + "、".join(missing))

    return StageBpMetrics(period_bp=float(period_bp), week_bp=float(week_bp), month_bp=float(month_bp))


def bp_phrase(value_bp: float, up_word: str = "上涨", down_word: str = "下跌") -> str:
    if value_bp < 0:
        return f"{down_word}{abs(value_bp):.0f}bp"
    return f"{up_word}{abs(value_bp):.0f}bp"


def build_snapshot_text(
    operation_row: pd.Series,
    date_display: str,
    style_text: str,
) -> str:
    product_name = normalize_text(operation_row.get("产品简称"))
    annual_return = float(operation_row.get("累计年化"))
    duration = float(operation_row.get("组合久期"))
    leverage = float(operation_row.get("杠杆"))
    equity_position = float(operation_row.get("权益仓位"))

    return (
        f"截止{date_display}，{product_name}当前组合成立以来年化收益率为{annual_return:.2%}，"
        f"组合有效久期约{duration:.2f}年，杠杆{leverage:.0%}，"
        f"权益仓位{equity_position:.1%}左右，权益持仓风格分布为{style_text}。"
    )


def build_volatility_text(
    snapshot_text: str,
    period_start: datetime,
    period_end: datetime,
    metrics: StageBpMetrics,
    drivers_text: str,
    market_text: str,
    recovery_text: str,
) -> str:
    start_str = period_start.strftime("%Y年%-m月%-d日") if os.name != "nt" else period_start.strftime("%Y年%m月%d日")
    end_str = period_end.strftime("%Y年%-m月%-d日") if os.name != "nt" else period_end.strftime("%Y年%m月%d日")

    line2 = (
        f"自{start_str}至{end_str}，产品净值累计{bp_phrase(metrics.period_bp, up_word='上涨', down_word='下跌')}。"
        f"近1周净值{bp_phrase(metrics.week_bp)}，近1月净值{bp_phrase(metrics.month_bp)}，"
        f"主要受到{drivers_text}的影响。"
    )
    market_text = market_text.rstrip("。") + "。"
    recovery_text = recovery_text.rstrip("。") + "。"
    return "\n".join([snapshot_text, line2, f"期间，{market_text}", recovery_text])


def generate_snapshot(
    product_identifier: str,
    asof_date: datetime,
    operation_dir: Path,
    holding_dir: Path,
    operation_file: Optional[Path],
    holding_file: Optional[Path],
    classification_file: Optional[Path],
    equity_style_script: Path,
    asof_display: Optional[str],
) -> Tuple[pd.Series, str, str, str, str, Path]:
    asof_yyyymmdd = asof_date.strftime("%Y%m%d")
    op_file = operation_file or find_operation_file(operation_dir, asof_yyyymmdd)
    if not op_file:
        raise FileNotFoundError(f"找不到日期 {asof_yyyymmdd} 的产品运作概览文件")
    operation_df = load_operation_df(op_file)
    operation_row = select_product_row(operation_df, product_identifier)

    product_code = normalize_text(operation_row.get("产品代码"))
    product_name = normalize_text(operation_row.get("产品简称"))

    h_file = holding_file or find_holding_file(holding_dir, asof_yyyymmdd)
    if not h_file:
        raise FileNotFoundError(f"找不到日期 {asof_yyyymmdd} 的持仓盈亏文件（可用 --holding-file 指定）")

    cls_file = classification_file or find_latest_classification_file(DEFAULT_CLASSIFICATION_DIR)
    if not cls_file:
        raise FileNotFoundError(f"找不到基金分类数据文件（目录：{DEFAULT_CLASSIFICATION_DIR}）")

    style_dist = compute_equity_style_distribution(product_name, h_file, cls_file, equity_style_script)
    style_text = format_style_distribution(style_dist)

    date_display = asof_display or format_cn_md(asof_date)
    snapshot_text = build_snapshot_text(operation_row, date_display, style_text)

    return operation_row, product_code, product_name, date_display, snapshot_text, h_file


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="产品运作说明/近期波动解释生成器")
    subparsers = parser.add_subparsers(dest="command")

    def add_common_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("product", help="产品代码或产品简称（建议产品代码）")
        p.add_argument("asof", help="截止日期（YYYYMMDD 或 YYYY-MM-DD）")
        p.add_argument("--asof-display", help="展示用日期（如 1月12日），不影响取数")
        p.add_argument("--operation-dir", default=str(DEFAULT_OPERATION_DIR), help="产品运作概览目录")
        p.add_argument("--holding-dir", default=str(DEFAULT_HOLDING_DIR), help="持仓盈亏目录")
        p.add_argument("--operation-file", help="直接指定产品运作概览文件路径（优先级最高）")
        p.add_argument("--holding-file", help="直接指定持仓盈亏明细列表文件路径（优先级最高）")
        p.add_argument("--classification-file", help="基金分类数据文件路径（默认取最新）")
        p.add_argument(
            "--equity-style-script",
            default=str(DEFAULT_EQUITY_STYLE_SCRIPT),
            help="权益风格占比计算脚本路径（generate_equity_style_report.py）",
        )

    p_snapshot = subparsers.add_parser("snapshot", help="生成产品运作快照（单句）")
    add_common_args(p_snapshot)

    p_vol = subparsers.add_parser("volatility", help="生成近期波动解释（按模板多段）")
    add_common_args(p_vol)
    p_vol.add_argument("--period-start", required=True, help="区间起始日期（YYYYMMDD 或 YYYY-MM-DD）")
    p_vol.add_argument("--period-end", required=True, help="区间截止日期（YYYYMMDD 或 YYYY-MM-DD）")
    p_vol.add_argument("--stages-file", help="阶段表现数据（Excel/CSV），用于自动提取区间/近1周/近1月bp")
    p_vol.add_argument("--period-bp", type=float, help="区间累计净值变动（bp，负数代表下跌）")
    p_vol.add_argument("--week-bp", type=float, help="近1周净值变动（bp，负数代表下跌）")
    p_vol.add_argument("--month-bp", type=float, help="近1月净值变动（bp，负数代表下跌）")
    p_vol.add_argument("--drivers-text", default="权益市场加速调整及债券市场持续震荡", help="影响因素描述")
    p_vol.add_argument(
        "--market-text",
        help="市场表现一句话（如：沪深300指数下跌3.42%，最大回撤6.52%；债券方面，万得短期纯债型基金指数微幅上涨3bp）",
    )
    p_vol.add_argument(
        "--recovery-text",
        default="随着权益市场止跌企稳及债券票息的持续积累，产品净值已得到一定修复",
        help="结尾修复/展望描述",
    )

    # 兼容旧用法：两个位置参数 => snapshot
    if argv is None:
        argv = []
    if len(argv) == 0:
        import sys

        argv = sys.argv[1:]
    if argv and argv[0] not in ("snapshot", "volatility") and len(argv) >= 2:
        argv = ["snapshot", argv[0], argv[1], *argv[2:]]

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 2

    asof_date = parse_date(args.asof)
    operation_dir = Path(args.operation_dir)
    holding_dir = Path(args.holding_dir)
    operation_file = Path(args.operation_file) if getattr(args, "operation_file", None) else None
    holding_file = Path(args.holding_file) if getattr(args, "holding_file", None) else None
    classification_file = Path(args.classification_file) if getattr(args, "classification_file", None) else None
    equity_style_script = Path(args.equity_style_script)

    operation_row, product_code, product_name, _date_display, snapshot_text, _h_file = generate_snapshot(
        product_identifier=args.product,
        asof_date=asof_date,
        operation_dir=operation_dir,
        holding_dir=holding_dir,
        operation_file=operation_file,
        holding_file=holding_file,
        classification_file=classification_file,
        equity_style_script=equity_style_script,
        asof_display=getattr(args, "asof_display", None),
    )

    if args.command == "snapshot":
        print(snapshot_text)
        return 0

    # volatility
    period_start = parse_date(args.period_start)
    period_end = parse_date(args.period_end)

    stage_metrics = None
    if args.period_bp is not None and args.week_bp is not None and args.month_bp is not None:
        stage_metrics = StageBpMetrics(period_bp=args.period_bp, week_bp=args.week_bp, month_bp=args.month_bp)
    elif args.stages_file:
        stage_df = load_stage_df(Path(args.stages_file))
        stage_metrics = extract_stage_metrics(stage_df, product_code, product_name, period_start, period_end)

    if stage_metrics is None:
        raise ValueError("缺少区间/近1周/近1月bp：请提供 --stages-file 或手工传入 --period-bp/--week-bp/--month-bp")
    if not args.market_text:
        raise ValueError("缺少市场表现：请提供 --market-text（按模板一句话）")

    text = build_volatility_text(
        snapshot_text=snapshot_text,
        period_start=period_start,
        period_end=period_end,
        metrics=stage_metrics,
        drivers_text=args.drivers_text,
        market_text=args.market_text,
        recovery_text=args.recovery_text,
    )
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
