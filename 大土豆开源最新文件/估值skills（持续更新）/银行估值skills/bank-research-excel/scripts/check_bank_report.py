#!/usr/bin/env python3
"""Structural checker for full and shareable bank-research workbooks.

Uses only the Python standard library. It checks the expected sheet structure,
formula/chart presence where required, and cached Excel error values.
Recalculation and visual QA are still required before delivery.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SHEET_SETS = {
    "full": [
        "一图流",
        "投资者画像",
        "投资结论",
        "估值系统",
        "估值敏感性",
        "股息估值",
        "财务十年",
        "资产质量",
        "同业比较",
        "巴菲特框架",
        "数据与来源",
    ],
    "share": ["总榜与四类榜", "三类投资者榜"],
    "ranking": ["总榜", "四大行", "股份行", "城商行", "农商行"],
}

ERROR_LITERALS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a bank-research Excel workbook")
    parser.add_argument("workbook", type=Path, help="Path to the .xlsx workbook")
    parser.add_argument(
        "--mode",
        choices=["auto", "full", "share", "ranking"],
        default="auto",
        help="Workbook layout; auto detects the known layout (default: auto)",
    )
    return parser.parse_args()


def read_sheet_names(zf: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = root.find(f"{{{MAIN_NS}}}sheets")
    if sheets is None:
        return []
    return [sheet.attrib.get("name", "") for sheet in sheets]


def detect_mode(sheet_names: list[str]) -> str | None:
    for mode, expected in SHEET_SETS.items():
        if sheet_names == expected:
            return mode
    return None


def inspect_workbook(path: Path, requested_mode: str) -> tuple[dict[str, object], bool]:
    if not path.exists() or not path.is_file():
        return {"workbook": str(path), "status": "FAIL", "reason": "file not found"}, False
    if path.suffix.lower() != ".xlsx":
        return {"workbook": str(path), "status": "FAIL", "reason": "not an .xlsx file"}, False

    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            if "xl/workbook.xml" not in names:
                return {"workbook": str(path), "status": "FAIL", "reason": "invalid workbook package"}, False

            sheet_names = read_sheet_names(zf)
            mode = detect_mode(sheet_names) if requested_mode == "auto" else requested_mode
            expected = SHEET_SETS.get(mode, [])

            formula_count = 0
            cached_errors: list[dict[str, str]] = []
            worksheet_files = sorted(
                name for name in names if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
            )
            for xml_name in worksheet_files:
                root = ET.fromstring(zf.read(xml_name))
                formula_count += len(root.findall(f".//{{{MAIN_NS}}}f"))
                for cell in root.findall(f".//{{{MAIN_NS}}}c[@t='e']"):
                    value = cell.find(f"{{{MAIN_NS}}}v")
                    literal = value.text if value is not None and value.text else "UNKNOWN"
                    if literal in ERROR_LITERALS or literal == "UNKNOWN":
                        cached_errors.append({"part": xml_name, "cell": cell.attrib.get("r", "?"), "error": literal})

            chart_count = len(
                [
                    name
                    for name in names
                    if (name.startswith("xl/charts/chart") or name.startswith("xl/drawings/charts/chart"))
                    and name.endswith(".xml")
                ]
            )

            problems: list[str] = []
            if mode is None:
                problems.append("unknown sheet layout; use --mode only if this is an intended supported layout")
            elif sheet_names != expected:
                problems.append(f"sheet layout does not match {mode} mode")
            if mode == "full" and formula_count == 0:
                problems.append("no formulas found in full mode")
            if mode == "full" and chart_count == 0:
                problems.append("no charts found in full mode")
            if cached_errors:
                problems.append("cached formula errors found")

            ok = not problems
            result: dict[str, object] = {
                "workbook": str(path.resolve()),
                "status": "PASS" if ok else "FAIL",
                "mode": mode or "unknown",
                "sheet_names": sheet_names,
                "expected_sheets": expected,
                "formula_count": formula_count,
                "chart_count": chart_count,
                "cached_formula_errors": cached_errors,
                "problems": problems,
                "note": (
                    "Static share/ranking snapshots may contain no formulas or chart objects. "
                    "This structural check does not replace spreadsheet recalculation or visual QA."
                ),
            }
            return result, ok
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
        return {"workbook": str(path), "status": "FAIL", "reason": str(exc)}, False


def main() -> int:
    args = parse_args()
    result, ok = inspect_workbook(args.workbook, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
