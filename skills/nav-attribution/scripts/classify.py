"""
默认资产分类规则。供 run_attribution.py 调用。

设计：
- 默认按 资产名称 精确匹配
- 用户可通过 override (dict) 补充/替换某个类别的资产清单
- 同名类别：用 override 的清单**替换**默认清单
- 新类别：追加
- 未匹配任何分类的资产 → 落到 fallback_category（默认"债券"）
"""
from typing import Optional, Dict, List

# 默认四大类（资产名称精确匹配）
DEFAULT_CATEGORIES = {
    "衍生品-兴合3号": [
        "兴业期货-兴合3号集合资产管理计划",
    ],
    "衍生品-兴合4号": [
        "兴业期货-兴合4号集合资产管理计划",
    ],
    "转债": [
        "兴业信托·兴享稳健睿郡2号",
        "兴业信托·兴享稳健睿郡3号证券投资集合资金信托计划",
        "兴证全球新步步高28号集合资产管理计划",
        "中欧基金-优选可转债1号集合资产管理计划",
        "东方红资管-优选可转债1号集合资管计划",
        "中金赢和1号集合资产管理计划",
        "中信期货兴腾睿选3号管理人中管理人（MOM）集合资产管理计划",
    ],
    # 债券 = fallback，不在此显式列出
}

FALLBACK_CATEGORY = "债券"


def merge_categories(override: Optional[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """
    把用户 override 合并到默认类别上。
    override 形如 {"类别名": ["资产名1", "资产名2"]}
    """
    merged = {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}
    if not override:
        return merged
    for cat, names in override.items():
        merged[cat] = list(names)  # 同名替换；新名追加
    return merged


def build_classifier(override: Optional[Dict[str, List[str]]] = None):
    """
    返回一个 classify(asset_name) -> category 的函数，
    以及最终生效的分类映射 dict。
    """
    cats = merge_categories(override)
    # 反向索引：资产名 → 类别
    rev = {}
    for cat, names in cats.items():
        for n in names:
            if n in rev and rev[n] != cat:
                raise ValueError(
                    f"资产 {n!r} 同时映射到 {rev[n]!r} 和 {cat!r}，请检查 classification_override"
                )
            rev[n] = cat

    def classify(name: str) -> str:
        return rev.get(name, FALLBACK_CATEGORY)

    return classify, cats


if __name__ == "__main__":
    # 自检
    fn, _ = build_classifier()
    samples = [
        "兴业期货-兴合3号集合资产管理计划",
        "兴业期货-兴合4号集合资产管理计划",
        "中欧基金-优选可转债1号集合资产管理计划",
        "23无锡城南MTN002",
    ]
    for s in samples:
        print(f"{s} -> {fn(s)}")
