# Known limitations

1. Provider-side API revisions are not always exposed; blank revision fields are retained, never invented.
2. Some local model manifests lack immutable weight hashes or repository revisions; blanks are kept as-is.
3. Two internal reference tables are absent from both public packages and are optional in scripts: `robustness_120_task_setting_results_methods_v2.csv` and `mode_paired_contrasts_methods_v2.csv` (also `panel72_scoring.jsonl` for one generation-sensitivity path).
4. Completed H1/H2 individual human ratings are not in this minimal package; guidelines, blinded materials, and design manifests are public.
5. Length/structure compliance checks are separate diagnostics and are not further weighted quality dimensions (see `configs/generation_rubrics.json`).
