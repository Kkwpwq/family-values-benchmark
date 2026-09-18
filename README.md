# ASLIB Family Values Benchmark

Chinese-language LLM evaluation suite for traditional family values / family-rule understanding (release **v1.0.3**).

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

Primary cross-model comparison is **zero-shot**. 1-shot / 3-shot analyses are secondary prompt-sensitivity experiments. QA also ships a 20-item development split (not in the primary test results). Fixed QA demonstrations are disjoint from development and test.

## Repository layout

```
configs/               # models, decoding, prompts, rubrics, shot protocol
data/benchmark/        # canonical_gold_750.jsonl
data/demonstrations/
data/qa/
data/experiment_plans/
code/                  # verify_package.py + recompute / validate scripts
results/               # paper tables and summary CSVs
human_validation/      # guidelines + blinded packets
release_assets/        # formal-records zip checksum
```

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Data and Release asset

This Git repository is the **minimal public package**. Large formal outputs live in the Release asset:

```bash
gh release download <tag> -p aslib-formal-records-v1.0.3-reviewer-complete.zip
unzip aslib-formal-records-v1.0.3-reviewer-complete.zip
```

SHA-256: see `release_assets/README.md`.

## Reproduce automatic analyses

```bash
# Package integrity
python3 code/verify_package.py

# Zero-shot recompute (scored_records/ inside the formal-records extract)
python3 code/recompute_zero_shot.py \
  --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete \
  --out results/recomputed_zero_shot

# Few-shot / Qwen3 (same --data-dir interface)
python3 code/recompute_fewshot_methods35.py \
  --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete
python3 code/recompute_qwen3_methods35.py \
  --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete

# Optional input checks
python3 code/validate_fewshot_inputs.py --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete
python3 code/validate_qwen3_inputs.py --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete
```

No model inference is required to regenerate the supplied result tables from stored scored records.

## Prompts and scoring rules

- QA system prompt: `configs/qa_system_prompt.txt`
- System-prompt policy: `configs/system_prompt_policy.json`
- Diagnostic prompts: `configs/diagnostic_system_prompts.json`
- Generation rubrics (weights): `configs/generation_rubrics.json`
- Shot protocol: `configs/qa_shot_conditions.json`
- Shared QA response schema: `configs/qa_response_schema.json`

Structuring uses Methods-version **CNHI**: recoverable structural compliance × field-level BERTScore semantic alignment (harmonic mean), averaged over items.

## Known limitations

See `KNOWN_LIMITATIONS.md`.

## Citation

See `CITATION.cff` (author / year / DOI fields are blank until the authors complete them).

## License and data notice

- Code and researcher-authored package materials: **Apache License 2.0** (`LICENSE`).
- Data / third-party passages: `DATA_AND_SOURCE_NOTICE.md` (redistribution of source-derived text is not confirmed in-package; Apache-2.0 does not expand third-party source rights).
