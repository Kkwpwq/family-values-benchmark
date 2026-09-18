# ASLIB Family Values Benchmark

Chinese-language LLM evaluation suite for traditional family values / family-rule understanding (release **v1.0.4**).

## Tasks and scale

| Task id | Items |
|---|---:|
| classification | 100 |
| reasoning | 100 |
| structuring | 100 |
| relationship | 50 |
| qa_v4_5 | 100 |
| story_generation | 100 |
| rewriting | 100 |
| continuation | 100 |
| **Total** | **750** |

Primary cross-model comparison is **zero-shot**. One-shot and three-shot analyses are secondary prompt-sensitivity experiments. QA also ships a separate 20-item development split that is not included in the 100-item primary QA test results. The three fixed demonstrations used by the main QA 0/1/3-shot protocol are disjoint from development and test; a subset of development items is used only in the separate diagnostic ablation experiments.

## Repository layout

```text
configs/               # model/checkpoint/runtime settings, prompts, rubrics, shot protocol
inputs/                # scored/auxiliary inputs consumed by packaged Methods-3.5 scripts
data/benchmark/        # canonical_gold_750.jsonl
data/demonstrations/   # fixed demonstrations and constrained demonstration pool
data/qa/               # 20-item QA development split + no-gold inference view
data/experiment_plans/ # matched-order, ablation, robustness, generation-sensitivity plans
reference_legacy/      # frozen Methods-V2 comparison tables used by explicit audit code
code/                  # verify, validate, and recompute scripts
results/               # final machine-readable result tables
human_validation/      # guidelines, design manifests, and blinded validation packets
release_assets/        # matching formal-records release-asset name and checksum
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Verify the repository

```bash
python3 code/verify_package.py
python3 code/validate_fewshot_inputs.py
python3 code/validate_qwen3_inputs.py
```

The two Methods-3.5 validation scripts use the packaged `inputs/` and `reference_legacy/` directories by default.

## Recompute Methods-3.5 analyses

```bash
python3 code/recompute_fewshot_methods35.py
python3 code/recompute_qwen3_methods35.py
```

Optional `--data-dir` arguments can instead point the scripts at an extracted formal-records archive. No model inference is required to regenerate these supplied analysis tables from stored scored records.

## Formal model-output archive

Large raw outputs and the complete item-level scored-record archive are distributed as the matching GitHub Release asset:

```text
aslib-formal-records-v1.0.4-reviewer-complete.zip
```

It contains all output families used in the reported automatic analyses:

- 19,800 primary outputs across all 12 primary model configurations;
- 2,376 generation few-shot outputs;
- 6,600 matched-order outputs;
- 9,000 ablation outputs;
- 7,425 repeated-sampling robustness outputs.

For zero-shot recomputation from the full scored-record archive:

```bash
python3 code/recompute_zero_shot.py \
  --data-dir path/to/aslib-formal-records-v1.0.4-reviewer-complete \
  --out results/recomputed_zero_shot
```

See `release_assets/README.md` for the SHA-256 checksum.

## Inference and prompt metadata

`configs/model_inference_configurations.csv` contains one reviewer-facing row for each of the 12 evaluated model configurations, including model/source identifier, local/API deployment type, provider model identifier where available, retained checkpoint fingerprint, reasoning mode, dtype/runtime versions, sampling controls, temperature, top-p/top-k/min-p, maximum output budget, context limit, model access/load time, main-run start/end time, and system-prompt policy.

System-prompt records are provided in:

- `configs/qa_system_prompt.txt`
- `configs/system_prompt_policy.json`
- `configs/diagnostic_system_prompts.json`

Repository revisions or provider-side revisions that were not retained by the original execution records are left blank rather than reconstructed retrospectively.

## Scoring

Generation rubrics and weights are in `configs/generation_rubrics.json`. Structuring uses the Methods-version CNHI definition: recoverable structural compliance × field-level BERTScore semantic alignment via a harmonic mean, averaged across items.

## Human validation

The public package contains annotation guidelines, design/sampling manifests, and blinded review materials. Completed H1/H2 individual rating files, reviewer identities, private mapping keys, and adjudication records are not distributed in this public package; aggregate reliability analyses are reported in the manuscript.

## Known limitations

See `KNOWN_LIMITATIONS.md`.

## Citation

Cite the accompanying article when using the benchmark. A `CITATION.cff` file is not included in this release because final author/DOI metadata was not supplied to this packaging step; no placeholder author metadata is published.

## License and data notice

- Code and researcher-authored package materials: Apache License 2.0 (`LICENSE`).
- Source-derived / third-party materials: see `DATA_AND_SOURCE_NOTICE.md`; the code license does not expand third-party reuse rights.
