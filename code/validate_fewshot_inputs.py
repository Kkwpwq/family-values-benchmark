#!/usr/bin/env python3
"""Validate few-shot scored-record inputs from the formal-records release asset."""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from pathlib import Path


def jl_gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8-sig") as f:
        return [json.loads(x) for x in f if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Extracted formal-records root (must contain scored_records/)",
    )
    args = ap.parse_args()
    root = args.data_dir
    scored = root / "scored_records"
    if not scored.is_dir():
        raise SystemExit(f"missing scored_records/ under {root}")

    main_rows = jl_gz(scored / "main_scored_items_methods_v2.jsonl.gz")
    matched = jl_gz(scored / "matched_order_scored_items_methods_v2.jsonl.gz")
    abl = jl_gz(scored / "ablation_scored_items_methods_v2.jsonl.gz")
    gen_path = scored / "dual_2376_item_scores.csv"
    with gen_path.open(encoding="utf-8-sig", newline="") as f:
        gen = list(csv.DictReader(f))

    assert len(main_rows) == 19800, len(main_rows)
    assert len(matched) == 6600, len(matched)
    assert len(abl) == 9000, len(abl)
    assert len(gen) == 2376, len(gen)

    print(
        json.dumps(
            {
                "status": "PASS",
                "data_dir": str(root),
                "main_rows": len(main_rows),
                "matched_rows": len(matched),
                "ablation_rows": len(abl),
                "generation_rows": len(gen),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
