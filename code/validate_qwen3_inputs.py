#!/usr/bin/env python3
"""Validate Qwen3 and robustness inputs for the packaged Methods-3.5 recalculation."""
from __future__ import annotations

import argparse
import csv
import gzip
import json
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
    robust = read_gz(scored / "robustness_scored_items_methods_v2.jsonl.gz")

    paired_candidates = [repo / "results" / "dual_judge" / "paired_main_3600_latest.csv",
                         scored / "paired_main_3600_latest.csv"]
    paired_path = next((p for p in paired_candidates if p.is_file()), None)
    if paired_path is None:
        raise SystemExit("missing paired_main_3600_latest.csv")
    paired = read_csv(paired_path)

    summary_candidates = [scored / "robustness_120_task_setting_results_methods_v2.csv",
                          repo / "inputs" / "robustness_120_task_setting_results_methods_v2.csv"]
    if data_root is not None:
        summary_candidates.insert(1, data_root / "robustness_120_task_setting_results_methods_v2.csv")
    summary_path = next((p for p in summary_candidates if p.is_file()), None)
    if summary_path is None:
        raise SystemExit("missing robustness_120_task_setting_results_methods_v2.csv")
    summary = read_csv(summary_path)

    ref_candidates = [repo / "reference_legacy"]
    if data_root is not None:
        ref_candidates.insert(0, data_root / "reference_legacy")
    ref = next((p for p in ref_candidates if p.is_dir()), None)
    if ref is None or not (ref / "mode_paired_contrasts_methods_v2.csv").is_file():
        raise SystemExit("missing reference_legacy/mode_paired_contrasts_methods_v2.csv")
    legacy = read_csv(ref / "mode_paired_contrasts_methods_v2.csv")

    assert len(main_rows) == 19800, len(main_rows)
    assert len(paired) == 3600, len(paired)
    assert len(robust) == 7425, len(robust)
    assert len(summary) == 120, len(summary)
    assert len(legacy) == 15, len(legacy)

    qwen_models = {"Qwen3-8B-Thinking", "Qwen3-8B-NonThinking"}
    for model in qwen_models:
        for task, n in {"classification":100,"reasoning":100,"structuring":100,"relationship":50,"qa_v4_5":100}.items():
            for shot in (0,1,3):
                rows = [r for r in main_rows if r["model_id"] == model and r["task_id"] == task and r.get("shot") == shot]
                assert len(rows) == n, (model, task, shot, len(rows), n)
                if task == "structuring":
                    assert all(r.get("cnhi_v2") is not None for r in rows)

    failures = [r for r in robust if r.get("final_delivered") is False]
    assert len(failures) == 10, len(failures)
    assert all(r.get("raw_output_sha256") for r in robust), "raw_output_sha256 missing from robustness scored records"

    print(json.dumps({
        "status": "PASS",
        "main_rows": len(main_rows),
        "paired_rows": len(paired),
        "robustness_rows": len(robust),
        "robustness_summary_rows": len(summary),
        "legacy_mode_rows": len(legacy),
        "final_delivery_failures": len(failures),
    }, indent=2))


if __name__ == "__main__":
    main()
