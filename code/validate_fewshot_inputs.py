#!/usr/bin/env python3
"""Validate few-shot, matched-order, ablation, and generation-sensitivity inputs."""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path


def read_gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None,
                    help="Optional extracted formal-records root. If omitted, packaged inputs/ are used.")
    args = ap.parse_args()

    if args.data_dir is None:
        scored = repo / "inputs"
        data_root = None
    else:
        data_root = args.data_dir
        scored = data_root / "scored_records" if (data_root / "scored_records").is_dir() else data_root
    if not scored.is_dir():
        raise SystemExit(f"missing scored input directory: {scored}")

    main_rows = read_gz(scored / "main_scored_items_methods_v2.jsonl.gz")
    matched = read_gz(scored / "matched_order_scored_items_methods_v2.jsonl.gz")
    ablation = read_gz(scored / "ablation_scored_items_methods_v2.jsonl.gz")
    generation = read_csv(scored / "dual_2376_item_scores.csv")

    panel_candidates = [scored / "panel72_scoring.jsonl", repo / "inputs" / "panel72_scoring.jsonl"]
    if data_root is not None:
        panel_candidates.insert(1, data_root / "panel72_scoring.jsonl")
    panel_path = next((p for p in panel_candidates if p.is_file()), None)
    if panel_path is None:
        raise SystemExit("missing panel72_scoring.jsonl")

    ref_candidates = [repo / "reference_legacy"]
    if data_root is not None:
        ref_candidates.insert(0, data_root / "reference_legacy")
    ref = next((p for p in ref_candidates if p.is_dir()), None)
    required = [
        "main_shot_paired_contrasts_methods_v2.csv",
        "matched_order_paired_contrasts_methods_v2.csv",
        "ablation_paired_contrasts_methods_v2.csv",
    ]
    if ref is None or any(not (ref / name).is_file() for name in required):
        raise SystemExit("missing one or more required reference_legacy tables")

    assert len(main_rows) == 19800, len(main_rows)
    assert len(matched) == 6600, len(matched)
    assert len(ablation) == 9000, len(ablation)
    assert len(generation) == 2376, len(generation)
    assert sum(1 for r in main_rows if r["task_id"] == "structuring" and r.get("cnhi_v2") is None) == 0
    assert sum(1 for r in ablation if r["task_id"] == "structuring" and r.get("cnhi_v2") is None) == 0
    assert sum(1 for r in ablation if r["task_id"] == "relationship" and any(r.get(k) is None for k in ("tp","fp","fn"))) == 0

    perms = defaultdict(set)
    for r in matched:
        perms[(r["model_id"], r["task_id"], r["condition_id"], r["item_id"])].add(int(r["permutation_index"]))
    assert all(v == {1,2,3,4,5,6} for v in perms.values())

    shots = defaultdict(set)
    for r in generation:
        shots[(r["model_id"], r["task_id"], r["item_id"])].add(int(r["shot"]))
    assert len(shots) == 792, len(shots)
    assert all(v == {0,1,3} for v in shots.values())

    print(json.dumps({
        "status": "PASS",
        "main_rows": len(main_rows),
        "matched_rows": len(matched),
        "ablation_rows": len(ablation),
        "generation_rows": len(generation),
        "generation_item_triplets": len(shots),
        "panel72": str(panel_path),
    }, indent=2))


if __name__ == "__main__":
    main()
