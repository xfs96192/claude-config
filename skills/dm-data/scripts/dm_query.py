#!/usr/bin/env python3
"""Helper for DM PythonAPI calls and local EDB level search."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_DIR / "references" / "api_catalog.json"
EDB_LEVELS_PATH = SKILL_DIR / "references" / "edb_levels.csv"
WHEEL_PATH = SKILL_DIR / "assets" / "vendor" / "dm_quant_api_client-0.2.2-py3-none-any.whl"


def load_catalog() -> dict[str, dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_sdk() -> None:
    if importlib.util.find_spec("dm_quant_api_client") is not None:
        return
    if not WHEEL_PATH.exists():
        raise SystemExit(f"SDK wheel not found: {WHEEL_PATH}")
    cmd = [sys.executable, "-m", "pip", "install", str(WHEEL_PATH)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip()
        raise SystemExit(f"Failed to install DM SDK wheel: {msg}")


def build_client(args: argparse.Namespace):
    ensure_sdk()
    from dm_quant_api_client import DMQuantApiClient

    try:
        return DMQuantApiClient(
            app_key=args.app_key,
            sm4_key=args.sm4_key,
            base_url=args.base_url,
            timeout=args.timeout,
            pythonic=True,
        )
    except ValueError as exc:
        raise SystemExit(f"DM client init failed: {exc}") from exc


def parse_json_arg(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def parse_csv_or_json_list(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    out: list[str] = []
    for value in values:
        out.extend([part.strip() for part in value.split(",") if part.strip()])
    return out


def resolve_api_path(api_or_path: str, catalog: dict[str, dict[str, Any]]) -> str:
    if api_or_path.startswith("/"):
        return api_or_path
    if api_or_path not in catalog:
        known = ", ".join(sorted(catalog))
        raise SystemExit(f"Unknown API alias '{api_or_path}'. Known aliases: {known}")
    return catalog[api_or_path]["path"]


def normalize_records(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [row if isinstance(row, dict) else {"value": row} for row in raw]
    if isinstance(raw, dict):
        for key in ("list", "records", "items", "data"):
            value = raw.get(key)
            if isinstance(value, list):
                return [row if isinstance(row, dict) else {"value": row} for row in value]
        if "data" in raw and isinstance(raw["data"], dict):
            return [raw["data"]]
        return [raw]
    return [{"value": raw}]


def normalize_scalar(value: Any) -> Any:
    if isinstance(value, (int, float)) and value > 1000000000000:
        try:
            from datetime import datetime

            return datetime.fromtimestamp(value / 1000).date().isoformat()
        except Exception:
            return value
    return value


def normalize_display_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: normalize_scalar(value) for key, value in row.items()} for row in records]


def write_output(raw: Any, output: str | None, as_json: bool, limit: int) -> None:
    if as_json and not output:
        print(json.dumps(raw, ensure_ascii=False, indent=2, default=str))
        return

    records = normalize_display_records(normalize_records(raw))
    if output:
        output_path = Path(output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() == ".json" or as_json:
            output_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        else:
            fieldnames: list[str] = []
            for row in records:
                for key in row:
                    if key not in fieldnames:
                        fieldnames.append(key)
            with output_path.open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
        print(f"saved={output_path} rows={len(records)}")
        return

    preview = records[:limit]
    if not preview:
        print("rows=0")
        return
    fieldnames = list(preview[0].keys())
    for row in preview[1:]:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    print("\t".join(fieldnames))
    for row in preview:
        print("\t".join("" if row.get(k) is None else str(row.get(k)) for k in fieldnames))
    if len(records) > limit:
        print(f"... rows={len(records)} shown={limit}")


def cmd_list_apis(args: argparse.Namespace) -> None:
    catalog = load_catalog()
    if args.json:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return
    print("alias\tname\tpath\trequired")
    for alias, info in sorted(catalog.items()):
        print(f"{alias}\t{info['name']}\t{info['path']}\t{', '.join(info['required'])}")


def cmd_search_edb(args: argparse.Namespace) -> None:
    tokens = [token.lower() for token in args.keywords]
    category = args.category.lower() if args.category else None
    matches: list[dict[str, str]] = []
    with EDB_LEVELS_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            haystack = " ".join(row.values()).lower()
            if category and category not in row.get("category_system", "").lower():
                continue
            if all(token in haystack for token in tokens):
                matches.append(row)
            if len(matches) >= args.limit:
                break
    if args.json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
        return
    print("edb_level_id\tcategory_system\tlevel1\tlevel2\tlevel3\tlevel4\tlevel5")
    for row in matches:
        print("\t".join(row.get(k, "") for k in ["edb_level_id", "category_system", "level1", "level2", "level3", "level4", "level5"]))


def call_api(args: argparse.Namespace, api_alias: str, data: dict[str, Any]) -> Any:
    catalog = load_catalog()
    api_path = resolve_api_path(api_alias, catalog)
    client = build_client(args)
    try:
        return client.post_data(data=data, api_path=api_path, return_type=args.return_type)
    finally:
        client.close()


def cmd_call(args: argparse.Namespace) -> None:
    data = parse_json_arg(args.data)
    try:
        raw = call_api(args, args.api, data)
    except Exception as exc:
        raise SystemExit(f"DM API call failed: {exc}") from exc
    write_output(raw, args.output, args.json, args.limit)


def cmd_edb_codes(args: argparse.Namespace) -> None:
    level_ids = parse_csv_or_json_list(args.level_id)
    data: dict[str, Any] = {"edb_level_id_list": level_ids}
    if args.field_names:
        data["field_names"] = parse_csv_or_json_list(args.field_names)
    if args.offset:
        data["offset"] = args.offset
    try:
        raw = call_api(args, "edb_codes", data)
    except Exception as exc:
        raise SystemExit(f"DM API call failed: {exc}") from exc
    write_output(raw, args.output, args.json, args.limit)


def cmd_edb_data(args: argparse.Namespace) -> None:
    data: dict[str, Any] = {"indicator_id": args.indicator_id}
    if args.start_date:
        data["start_date"] = args.start_date
    if args.end_date:
        data["end_date"] = args.end_date
    if args.field_names:
        data["field_names"] = parse_csv_or_json_list(args.field_names)
    try:
        raw = call_api(args, "edb_data", data)
    except Exception as exc:
        raise SystemExit(f"DM API call failed: {exc}") from exc
    write_output(raw, args.output, args.json, args.limit)


def cmd_trade_dates(args: argparse.Namespace) -> None:
    market_type: Any
    parts = [part.strip() for part in args.market_type.split(",") if part.strip()]
    market_type = [int(part) for part in parts] if len(parts) > 1 else int(parts[0])
    data: dict[str, Any] = {
        "market_type": market_type,
        "start_date": args.start_date,
        "end_date": args.end_date,
    }
    if args.field_names:
        data["field_names"] = parse_csv_or_json_list(args.field_names)
    try:
        raw = call_api(args, "trade_dates", data)
    except Exception as exc:
        raise SystemExit(f"DM API call failed: {exc}") from exc
    write_output(raw, args.output, args.json, args.limit)


def add_common_call_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--app-key", default=None, help="DM app key; defaults to INNO_APP_KEY.")
    parser.add_argument("--sm4-key", default=None, help="DM SM4 key; defaults to INNO_SM4_KEY.")
    parser.add_argument("--base-url", default=None, help="Override DM base URL.")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--return-type", choices=["dict", "dataframe"], default="dict")
    parser.add_argument("--output", help="Write CSV or JSON output.")
    parser.add_argument("--json", action="store_true", help="Print/write raw JSON.")
    parser.add_argument("--limit", type=int, default=20, help="Preview row limit.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call DM quant APIs and search local EDB levels.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-apis", help="List supported API aliases.")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list_apis)

    p = sub.add_parser("search-edb", help="Search local EDB level hierarchy.")
    p.add_argument("keywords", nargs="+")
    p.add_argument("--category", help="Filter category_system, e.g. 中国宏观 or 全球宏观.")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_search_edb)

    p = sub.add_parser("call", help="Call an API alias or raw API path with JSON data.")
    add_common_call_args(p)
    p.add_argument("api", help="API alias from list-apis, or raw /dm-quant... path.")
    p.add_argument("--data", required=True, help="JSON string, or @path/to/data.json.")
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("edb-codes", help="Get indicator IDs for EDB level IDs.")
    add_common_call_args(p)
    p.add_argument("--level-id", action="append", required=True, help="EDB level ID. Repeat or comma-separate.")
    p.add_argument("--field-names", action="append", help="Fields. Repeat or comma-separate.")
    p.add_argument("--offset", help="Pagination offset from max_offset.")
    p.set_defaults(func=cmd_edb_codes)

    p = sub.add_parser("edb-data", help="Get EDB indicator values.")
    add_common_call_args(p)
    p.add_argument("indicator_id")
    p.add_argument("--start-date")
    p.add_argument("--end-date")
    p.add_argument("--field-names", action="append", help="Fields. Repeat or comma-separate.")
    p.set_defaults(func=cmd_edb_data)

    p = sub.add_parser("trade-dates", help="Get DM trade calendar.")
    add_common_call_args(p)
    p.add_argument("market_type", help="1 bank/interbank, 2 exchange; comma-separate for both.")
    p.add_argument("start_date")
    p.add_argument("end_date")
    p.add_argument("--field-names", action="append", help="Fields. Repeat or comma-separate.")
    p.set_defaults(func=cmd_trade_dates)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
