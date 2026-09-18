# Packaged analysis inputs

This directory contains minimal public projections of the item-level scored records and auxiliary files consumed by the packaged Methods-3.5 recalculation scripts. Values retained here are copied from the matching frozen formal-records archive; fields not used by these scripts are omitted from the Git repository copy.

The complete public raw-output and scored-record archive is distributed separately as the version-matched GitHub Release asset.

`robustness_120_task_setting_results_methods_v2.csv` is the archived 120-cell robustness summary used by the Qwen3 robustness audit. `panel72_scoring.jsonl` is the frozen generation-panel metadata used to reconstruct the registered source clustering for generation sensitivity.

`raw_output_sha256` is retained only in the minimal robustness scored input because the Qwen3 robustness audit uses it to verify exact-output duplication between registered settings. It is an output-integrity checksum, not a prompt identifier.
