#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd


DEFAULT_SHEET = "产品运作概览"

# Report-name -> Excel “产品简称” matching string (prefer the non-“(子X)” row)
DEFAULT_PRODUCT_MAP: Dict[str, str] = {
    "丰利逸动6个月持有3号": "丰利逸动6个月最短持有期日开03号增强型",
    "丰利逸动10M持有2号": "丰利逸动10个月最短持有期日开2号增强型",
    "丰利兴动多策略１Y持有３号（中证８００增强）": "丰利兴动多策略一年持有期3号增强型",
}


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if pd.isna(value):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fmt_pct(value: Optional[float], digits: int = 2) -> Optional[str]:
    if value is None:
        return None
    return f"{value * 100:.{digits}f}%"


def _fmt_num(value: Optional[float], digits: int = 2) -> Optional[str]:
    if value is None:
        return None
    return f"{value:.{digits}f}"


def _fmt_nav(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    return f"{value:.4f}".rstrip("0").rstrip(".")


@dataclass(frozen=True)
class ProductMetrics:
    source_name: str
    aum_bil: Optional[float]
    nav: Optional[float]
    period_ann: Optional[float]
    cum_ann: Optional[float]
    leverage: Optional[float]
    duration_multi: Optional[float]
    static_multi: Optional[float]
    equity_weight: Optional[float]
    deriv_weight: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "raw": {
                "净资产(亿)": self.aum_bil,
                "单位净值": self.nav,
                "本期年化": self.period_ann,
                "累计年化": self.cum_ann,
                "杠杆": self.leverage,
                "组合久期(多资产)": self.duration_multi,
                "组合静态(多资产)": self.static_multi,
                "权益仓位": self.equity_weight,
                "衍生品仓位": self.deriv_weight,
            },
            "fmt": {
                "净资产(亿)": _fmt_num(self.aum_bil, 2),
                "单位净值": _fmt_nav(self.nav),
                "本期年化": _fmt_pct(self.period_ann, 2),
                "累计年化": _fmt_pct(self.cum_ann, 2),
                "杠杆": None if self.leverage is None else f"{self.leverage * 100:.0f}%",
                "组合久期(多资产)": _fmt_num(self.duration_multi, 2),
                "组合静态(多资产)": _fmt_pct(self.static_multi, 2),
                "权益仓位": _fmt_pct(self.equity_weight, 2),
                "衍生品仓位": _fmt_pct(self.deriv_weight, 2),
            },
        }


def _find_product_row(df: pd.DataFrame, target_name: str) -> pd.Series:
    if "产品简称" not in df.columns:
        raise ValueError("Excel缺少列：产品简称")

    name_col = df["产品简称"].astype(str)
    is_child = name_col.str.contains(r"\(子", na=False)

    exact = df[(name_col == target_name) & (~is_child)]
    if len(exact) == 1:
        return exact.iloc[0]
    if len(exact) > 1:
        return exact.iloc[0]

    contains = df[(name_col.str.contains(target_name, na=False)) & (~is_child)]
    if len(contains) >= 1:
        return contains.iloc[0]

    any_match = df[name_col.str.contains(target_name, na=False)]
    if len(any_match) >= 1:
        return any_match.iloc[0]

    raise ValueError(f"未在Excel中匹配到产品简称：{target_name}")


def _extract_metrics(df: pd.DataFrame, target_name: str) -> ProductMetrics:
    row = _find_product_row(df, target_name)
    source_name = str(row.get("产品简称", target_name))

    return ProductMetrics(
        source_name=source_name,
        aum_bil=_to_float(row.get("净资产(亿)")),
        nav=_to_float(row.get("单位净值")),
        period_ann=_to_float(row.get("本期年化")),
        cum_ann=_to_float(row.get("累计年化")),
        leverage=_to_float(row.get("杠杆")),
        duration_multi=_to_float(row.get("组合久期(多资产)")),
        static_multi=_to_float(row.get("组合静态(多资产)")),
        equity_weight=_to_float(row.get("权益仓位")),
        deriv_weight=_to_float(row.get("衍生品仓位")),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从“产品运作概览.xlsx”提取徐莹三只重点固收+产品的当月运作指标，输出JSON。"
    )
    parser.add_argument("xlsx", help="产品运作概览 xlsx 路径")
    parser.add_argument("--sheet", default=DEFAULT_SHEET, help=f"工作表名（默认：{DEFAULT_SHEET}）")
    parser.add_argument("--as-of", default=None, help="数据截至日期（可选，原样写入JSON）")
    parser.add_argument("--out", default="-", help="输出JSON路径；- 表示 stdout")
    args = parser.parse_args()

    df = pd.read_excel(args.xlsx, sheet_name=args.sheet)

    products: Dict[str, Any] = {}
    for report_name, excel_name in DEFAULT_PRODUCT_MAP.items():
        metrics = _extract_metrics(df, excel_name)
        products[report_name] = metrics.to_dict()

    out: Dict[str, Any] = {
        "as_of": args.as_of,
        "source": {
            "xlsx": args.xlsx,
            "sheet": args.sheet,
        },
        "products": products,
    }

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out == "-":
        print(payload)
        return

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(payload)
        f.write("\n")


if __name__ == "__main__":
    main()

