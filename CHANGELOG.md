# Changelog

## 1.0.4 — public packaging follow-up

- Rewrote four reasoning event stems (REA-021 / REA-066 / REA-076 / REA-095) into concrete vignettes; classical clauses and gold labels unchanged.
- Replaced internal pipeline version tags (`formal11`, `4.6.0-cross-task-diagnostics-rc1`) with public `v1.0.4`.
- Regenerated `MANIFEST_SHA256.csv`.


## 1.0.4 — public reproducibility completion

- Restored the formal 20-item QA development split already present in the experimental archive and clarified its relationship to the fixed QA demonstrations and diagnostic ablation demonstrations.
- Added the scored/auxiliary inputs actually consumed by the packaged Methods-3.5 recalculation scripts.
- Added the frozen legacy comparison tables required by the explicit legacy-comparison audits, including `robustness_120_task_setting_results_methods_v2.csv` and `mode_paired_contrasts_methods_v2.csv`.
- Restored reviewer-required model access/load and main-run timestamps to the compact model configuration table and model manifests.
- Updated validation/recalculation scripts so they run from packaged inputs by default while still accepting an extracted formal-records directory.
- Removed package-cleaning/internal field-audit notes that are not needed for public reproducibility.
- Retained the public-package policy of excluding prompt-identification hashes, raw judge rationales/comments, and completed H1/H2 individual rating files.

## 1.0.3 — public package hygiene

- Flattened the public GitHub tree from the earlier reviewer package layout.
- Removed nonessential process/authoring fields from public benchmark, demonstration, and experiment-plan records.
- Added Apache-2.0 license and citation metadata template.
