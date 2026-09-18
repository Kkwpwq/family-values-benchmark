#!/usr/bin/env python3
"""Validate Qwen3 / robustness scored-record inputs from the formal-records release asset.

Internal-only reference CSVs absent from both public packages are optional:
  - robustness_120_task_setting_results_methods_v2.csv
  - mode_paired_contrasts_methods_v2.csv
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from pathlib import Path


def gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8-sig") as f:
        return [json.loads(x) for x in f if x.strip()]


def csvrows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, required=True,
                    help="Extracted formal-records root (must contain scored_records/)")
    ap.add_argument("--paired-csv", type=Path, default=None,
                    help="Optional path to paired_main_3600_latest.csv")
    args = ap.parse_args()
    root = args.data_dir
    scored = root / "scored_records"
    if not scored.is_dir():
        raise SystemExit(f"missing scored_records/ under {root}")

    main_rows = gz(scored / "main_scored_items_methods_v2.jsonl.gz")
    rob = gz(scored / "robustness_scored_items_methods_v2.jsonl.gz")

    repo = Path(__file__).resolve().parents[1]
    paired_path = args.paired_csv or (repo / "results" / "dual_judge" / "paired_main_3600_latest.csv")
    if not paired_path.is_file():
        alt = scored / "paired_main_3600_latest.csv"
        paired_path = alt if alt.is_file() else paired_path
    if not paired_path.is_file():
        raise SystemExit(f"missing paired dual-judge CSV: {paired_path}")
    paired = csvrows(paired_path)

    optional = {}
    for name in (
        "robustness_120_task_setting_results_methods_v2.csv",
        "mode_paired_contrasts_methods_v2.csv",
    ):
        candidates = [scored / name, root / name, root / "reference_legacy" / name]
        hit = next((p for p in candidates if p.is_file()), None)
        optional[name] = str(hit) if hit else None

    assert len(main_rows) == 19800, len(main_rows)
    assert len(paired) == 3600, len(paired)
    assert len(rob) == 7425, len(rob)

    print(json.dumps({
        "status": "PASS",
        "data_dir": str(root),
        "main_rows": len(main_rows),
        "paired_rows": len(paired),
        "paired_csv": str(paired_path),
        "robustness_rows": len(rob),
        "optional_internal_files": optional,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
