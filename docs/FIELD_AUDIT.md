# FIELD_AUDIT.md — ASLIB Family Values Benchmark v1.0.3 (pre-edit)

Written **before** any content edits to `cleaned/`. Actions: KEEP / DROP / MOVE / RENAME. Reasons cite public-eval hygiene (spec §3).

Legend: **BREAKING** = field used by a public script; change script first.

---

## 1. `data/benchmark/canonical_gold_750.jsonl` (750 rows)

### Non-QA tasks (classification/reasoning/structuring/relationship/story_generation/rewriting/continuation)

| Field | Action | Reason |
|---|---|---|
| item_id | KEEP | Stable id |
| task_id | KEEP | Task key |
| instruction | KEEP | Model-facing prompt |
| input | KEEP | Model-facing content |
| reference | KEEP | Gold (where present) |
| reference_type | KEEP | Scoring type |

### QA task `qa_v4_5` (100 rows)

| Field | Action | Reason |
|---|---|---|
| item_id, task_id | KEEP | Ids |
| source_text, question | KEEP | Model-facing |
| statements[].id, .marker, .text, .truth | KEEP | Scoring keys |
| statements[].evidence_key | DROP | Item-authoring blueprint |
| options[].label, .text | KEEP | Choices shown to model |
| options[].truth_mask | DROP | Reconstructible from answer + statements[].truth; process field |
| options[].diagnostic_role | DROP | Authoring blueprint |
| answer, answer_text | KEEP | Gold |
| gold_truth_mask | DROP | Reconstructible; process field (no public script depends on package-A gold file masks) |
| response_schema | MOVE | Identical across QA rows → `configs/qa_response_schema.json`; drop per-row copy |

Task counts verified: 100/100/100/50/100/100/100/100.

---

## 2. `data/benchmark/source_record_manifest.json`

| Field | Action | Reason |
|---|---|---|
| count, task_counts, records[].item_id/task_id | KEEP | Inventory |
| note | DROP | Prose fluff |

---

## 3. `data/qa/development_gold_20.jsonl`

| Field | Action | Reason |
|---|---|---|
| item_id, task_id, source_text, question | KEEP | Core |
| statements[].id/.marker/.text/.truth | KEEP | Gold |
| options[].label/.text | KEEP | Choices |
| options[].truth_mask | DROP | Process |
| answer, answer_text | KEEP | Gold |
| gold_truth_mask | DROP | Process |
| response_schema | MOVE | Same as configs/qa_response_schema.json |
| dataset_version | DROP | Internal version soup (`4.5.0-qa100-rc1`) |
| scored | DROP | Pipeline flag |
| source_unit_id | DROP | Internal unit id |
| template_family | DROP | Authoring tag |
| ability | DROP | Internal ability label |
| gold_rationale | DROP | Duplicate of truth+answer; draft-like |
| split | RENAME value | `development` → `dev` (short) or DROP; choose DROP (file path already encodes split) |

---

## 4. `data/qa/development_inference_20.jsonl`

Same DROP set as gold for process fields. Confirm no `answer`/`truth`/`gold_rationale` leakage (currently none for answer/truth — KEEP that property).

| Field | Action | Reason |
|---|---|---|
| item_id, task_id, source_text, question, statements text, options label/text | KEEP | Inference view |
| ability, dataset_version, scored, source_unit_id, template_family, release_role, split, response_schema | DROP/MOVE | Process / duplicate schema |

---

## 5. `data/demonstrations/constrained_demo_pool.jsonl`

| Field | Action | Reason |
|---|---|---|
| demo_id, task_id, instruction, input, source_text, question | KEEP | Demo content |
| correct_output, wrong_output, label_only_output | KEEP | Controlled-experiment outputs |
| answer, answer_text, wrong_answer | KEEP | QA demos |
| statements truth / options label/text | KEEP | Needed |
| statements[].evidence_key, options[].diagnostic_role, options[].truth_mask, gold_truth_mask | DROP | Process |
| response_schema | DROP | Lifted to config |
| corruption_type | RENAME | → `demo_kind` short enum is not 1:1; DROP long value `deterministic_wrong_label_cycle` (kind already implied by presence of wrong_* fields). Spec allows delete. |

---

## 6. `data/demonstrations/qa_fixed_examples.jsonl`

Align with QA public fields: KEEP core; DROP evidence_key, diagnostic_role, truth_mask, gold_truth_mask, response_schema.

---

## 7. `data/demonstrations/generation_demo_review12.csv`

| Action | Reason |
|---|---|
| MOVE slim to `docs/generation_demo_review12.csv` | Internal review checklist |
| KEEP columns | demo_id, task_id, approved |
| DROP | reviewer_kind, task_match, output_valid, schema_valid, source_verified, not_test_paraphrase, notes |

---

## 8. `data/demonstrations/main_fewshot_demo_audit_manifest.csv`

| Field | Action | Reason |
|---|---|---|
| sample_id | RENAME values optional | Internal hash ids; KEEP column as `demo_sample_id` or leave (3-col short table OK) — KEEP as-is (stable audit keys; not PII) |
| task_id, role | KEEP | Short table |

---

## 9. Experiment plans

### `cross_task_ablation_prompt_plan.jsonl.gz`

| Field | Action | Reason |
|---|---|---|
| condition_id, demo_ids, demo_variant, item_id, seed, task_id | KEEP | Reproduction |
| demo_subtypes, target_subtype, neutral_filler_id | KEEP | Used in ablation design |
| selection_pre_outcome | DROP | Procedural justice memo |

### `generation_sensitivity_prompt_plan.jsonl.gz`

All fields KEEP (already lean: demo_ids, item_id, model_id, repeat_seed, rng_seed, shot, task_id).

### `matched_order_plan.jsonl.gz`

| Field | Action | Reason |
|---|---|---|
| condition_id, experiment, generation_seed, item_id, model_id, permutation, permutation_index, reuse, task_id | KEEP | Needed |
| cell_id | DROP | Long pipe key; reconstructible from model+task+item+condition+perm |
| generation_config | DROP | Constant per row; lift note to protocol if needed — values do_sample/use_cache/max_new_tokens are model-level |
| ranking_eligible | DROP | Process |
| selection_policy | DROP | Long prose |

### `matched_order_budget.csv` — KEEP all columns (numeric budget).

### `robustness_run_plan.csv`

| Field | Action | Reason |
|---|---|---|
| job_id, model, setting, repeat_index, seed, tasks, task_count, expected_responses, generation_policy | KEEP | Plan |
| python_exec | DROP | Local path (`runtime_envs/...`) |
| ranking_role | DROP | Internal role tag |

### `generation_sensitivity_protocol.json` / `runtime.json` / `rubric.json`

| Field | Action | Reason |
|---|---|---|
| experiment_id | RENAME | `generation_fewshot_convergence_v3_formal11` → `generation_fewshot` |
| Long notes / self-explanatory prose | DROP or slim | Move limits to KNOWN_LIMITATIONS |
| Numeric protocol facts | KEEP | |

### `robustness_sampling_manifest.json`

KEEP sampling facts; DROP selection_timestamp_policy / self-memo prose if present.

---

## 10. Configs

### `model_inference_configurations.csv`

| Field | Action | Reason |
|---|---|---|
| model_id, source_id, deployment, provider_model_id, source_revision, checkpoint_fingerprint_sha256, reasoning_mode, dtype, transformers_version, torch_version, do_sample, temperature, top_p, top_k, min_p, repetition_penalty, max_output_tokens, context_limit, main_system_prompt_policy | KEEP | Inference config |
| access_or_load_utc, main_run_start_utc, main_run_end_utc, completed_at_utc | DROP | Microsecond run archaeology (or truncate to date-only — prefer DROP for public) |

### `configs/model_manifests/*/model_manifest.json`

| Field | Action | Reason |
|---|---|---|
| Core model/deployment/generation/runtime | KEEP | |
| *_utc timestamps | DROP or date-only | Prefer DROP |
| note (revision apology) | DROP | Self-defense prose |

### `protocol_manifest.json`

| Field | Action | Reason |
|---|---|---|
| protocol_version | RENAME value | `4.2-reviewer-ready` → `1.0.3` |
| created_at_utc | DROP | |
| benchmark_version, seeds, token limits, system_prompt_policy, conditions | KEEP | |
| models_config_sha256_at_creation | KEEP | Integrity pointer |

### `qa_shot_conditions.json`

KEEP: condition_id, n_shot/shot, demo_ids. DROP: purpose prose, rationale_policy long, redundant name_zh if duplicate of condition_id. KEEP short demo_policy if useful.

### `qa_shot_protocol_metadata.json`

KEEP counts and fixed_demonstration_ids and constraints list (factual). DROP diagnostic_scope_note prose if self-memo.

### `generation_rubrics.json`

KEEP weights and aggregation. DROP `note` footnote → KNOWN_LIMITATIONS. RENAME version string away from internal milestone if needed → `1.0.3`.

### `system_prompt_policy.json`

KEEP paths; DROP `note`.

### `diagnostic_system_prompts.json`, `qa_system_prompt.txt`, `robustness_settings.json`

KEEP (frozen prompts/settings).

### NEW `configs/qa_response_schema.json`

MOVE target for shared QA response_schema.

---

## 11. `code/analysis_spec_4_2.json` / `analysis_spec_4_3.json`

| Field | Action | Reason |
|---|---|---|
| bootstrap/signflip/seed/endpoints/tests/family sizes | KEEP | Stats protocol |
| policy_id | RENAME | Short id e.g. `methods_3_5` / `methods_3_5_qwen3` |
| Long narrative notes inside nested objects | DROP where pure prose | |

---

## 12. Human validation

| File / Field | Action | Reason |
|---|---|---|
| blinded_* candidate/input/instruction/reference/correct_output | KEEP | Blind materials |
| calibration_split | DROP or RENAME | `heldout_validation` → DROP |
| endpoint_definition | DROP | Guidelines cover scoring |
| sample_id | KEEP | Short public ids; strip internal module codes where easy (`P2BPLUS-CLS-037` → prefer item_id already present; KEEP sample_id as secondary) — for reference audit KEEP item_id, DROP redundant module-coded sample_id OR RENAME to item_id-based. Prefer: keep sample_id but no rewrite of candidate text. Minimal: DROP endpoint_definition & calibration_split only. |
| gold_record nested process fields | DROP nested evidence_key/diagnostic_role/truth_mask/response_schema/gold_truth_mask if present | Align with public QA |
| human_validation/README | REWRITE | Remove historical `human_validation_NOT_COMPLETED` paths |
| validation_design_manifest / scorer_sampling_manifest | KEEP | Design facts |
| annotation_guidelines_zh.md | KEEP | |

---

## 13. Results CSVs

### Keep numeric cores; DROP interpretive/pipeline columns

Common DROP across contrast tables:
- `analysis_role`
- `interpretation` / `interpretation_limit`
- `note` (method soliloquy)
- `holm_incomplete_family_conservative`
- `is_independent_setting_evidence` (move audit tables under `results/audit/` if purely audit)

### Paper-named files — **do not rename**
- `results/zero_shot/Table_V_panel_A.csv`
- `results/zero_shot/Table_V_panel_B.csv`
- `results/zero_shot/Supplementary_Table_S3_diagnostics.csv`

Slim dirty columns in place; **do not change numeric values**.

### `paired_main_3600_latest.csv`
KEEP all score columns (task-specific empties are structural, not always-empty globally). No numeric changes.

### Audit tables MOVE to `results/audit/`:
- `results/fewshot/holm_family_audit.csv`
- `results/qwen3/robustness_duplicate_setting_audit.csv`
- `results/cnhi/MASTER_CNHI_ZERO_AUDIT_METHODS_V2.csv` (DROP `interpretation` column)

### CNHI / fewshot / qwen3 / zero_shot summary tables
KEEP estimate/CI/p/Holm/n columns; DROP analysis_role, interpretation*, note where present.

---

## 14. Docs / root hygiene (file-level)

| File | Action |
|---|---|
| README.md | REWRITE public eval-repo structure |
| DATA_AND_SOURCE_NOTICE.md | REWRITE; remove author TODO; confirmed facts only |
| KNOWN_LIMITATIONS.md | REWRITE ≤5 short bullets |
| LICENSE | ADD draft (author-must-confirm; suggest Apache-2.0 or MIT) |
| CITATION.cff | ADD draft; blank author/year/DOI |
| CHANGELOG.md | ADD |
| CHANGELOG_CLEANING.md | ADD (cleaning log) |
| requirements.txt | ADD `threadpoolctl` |
| .gitignore | KEEP / ensure venv,pyc,logs |
| MANIFEST_SHA256.csv | RECOMPUTE after edits |
| release_assets/README.md | REWRITE short pointer to GitHub Release |

---

## 15. Scripts (path alignment) — plan before data drops that scripts need

| Script | Action |
|---|---|
| recompute_zero_shot.py | KEEP `--data-dir` + `scored_records/`; ensure requirements |
| recompute_fewshot_methods35.py | BREAKING path change: `--data-dir` → `scored_records/`; optional legacy refs |
| recompute_qwen3_methods35.py | BREAKING path change: `--data-dir` → `scored_records/`; make `robustness_120_...` and `mode_paired_contrasts_...` **optional** |
| validate_fewshot_inputs.py | BREAKING: `--data-dir` + scored_records |
| validate_qwen3_inputs.py | BREAKING: `--data-dir` + scored_records; missing CSVs optional |
| verify_package.py | KEEP; will pass after manifest recompute |
| Package A result paths for paired table | KEEP under `results/dual_judge/` (zero_shot already uses package_root) |

Missing files (both packages): 
- `robustness_120_task_setting_results_methods_v2.csv`
- `reference_legacy/mode_paired_contrasts_methods_v2.csv`
→ internal-only; do **not** invent; document in KNOWN_LIMITATIONS.

Do **not** copy package B large files into cleaned/.

---

## 16. Fields intentionally NOT dropped

- All Chinese task text (source_text, instruction, input, family-rule quotes, candidate_text)
- Gold correctness (answer, reference, statements[].truth)
- Rubric dimension names and weights
- Model output / blinded candidate / reference body text
- item_id / demo_id values (except sample_id hygiene where noted)

---

## Audit completeness

Schema sampled for all 71 json/jsonl/csv files under package A before edits. Gzip plans decompressed for samples. Package B used only for path alignment (`scored_records/`, `raw_outputs/`).
