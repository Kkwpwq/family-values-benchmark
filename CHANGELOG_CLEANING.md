# CHANGELOG_CLEANING

Per-edit cleaning log for the public package.

| File | Field | Reason | Reproduction affected |
|---|---|---|---|
| `configs/qa_response_schema.json` | `(new)` | Moved shared QA response_schema from per-item records | no |
| `data/benchmark/canonical_gold_750.jsonl` | `statements[].evidence_key` | Process/authoring field; schema moved to configs | no |
| `data/benchmark/canonical_gold_750.jsonl` | `options[].diagnostic_role` | Process/authoring field; schema moved to configs | no |
| `data/benchmark/canonical_gold_750.jsonl` | `options[].truth_mask` | Process/authoring field; schema moved to configs | no |
| `data/benchmark/canonical_gold_750.jsonl` | `gold_truth_mask` | Process/authoring field; schema moved to configs | no |
| `data/benchmark/canonical_gold_750.jsonl` | `response_schema` | Process/authoring field; schema moved to configs | no |
| `data/benchmark/source_record_manifest.json` | `note` | Prose fluff | no |
| `data/qa/development_gold_20.jsonl` | `dataset_version` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `scored` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `source_unit_id` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `template_family` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `ability` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `gold_rationale` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `gold_truth_mask` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `split` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `response_schema` | Process field per §3.2 | no |
| `data/qa/development_gold_20.jsonl` | `options[].truth_mask` | Process field per §3.2 | no |
| `data/qa/development_inference_20.jsonl` | `dataset_version` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `scored` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `source_unit_id` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `template_family` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `ability` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `release_role` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `split` | Process field; no answer leakage | no |
| `data/qa/development_inference_20.jsonl` | `response_schema` | Process field; no answer leakage | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `corruption_type` | Process/demo authoring field | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `evidence_key` | Process/demo authoring field | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `diagnostic_role` | Process/demo authoring field | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `truth_mask` | Process/demo authoring field | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `gold_truth_mask` | Process/demo authoring field | no |
| `data/demonstrations/constrained_demo_pool.jsonl` | `response_schema` | Process/demo authoring field | no |
| `data/demonstrations/qa_fixed_examples.jsonl` | `gold_truth_mask` | Align with public QA fields | no |
| `data/demonstrations/qa_fixed_examples.jsonl` | `response_schema` | Align with public QA fields | no |
| `data/demonstrations/qa_fixed_examples.jsonl` | `evidence_key` | Align with public QA fields | no |
| `data/demonstrations/qa_fixed_examples.jsonl` | `diagnostic_role` | Align with public QA fields | no |
| `data/demonstrations/qa_fixed_examples.jsonl` | `truth_mask` | Align with public QA fields | no |
| `data/demonstrations/generation_demo_review12.csv` | `(moved slim)` | Internal review checklist → docs/; dropped review checklist cols | no |
| `data/experiment_plans/cross_task_ablation_prompt_plan.jsonl.gz` | `selection_pre_outcome` | Procedural justice memo | no |
| `data/experiment_plans/matched_order_plan.jsonl.gz` | `cell_id` | Process/reconstructible/repeated config | no |
| `data/experiment_plans/matched_order_plan.jsonl.gz` | `selection_policy` | Process/reconstructible/repeated config | no |
| `data/experiment_plans/matched_order_plan.jsonl.gz` | `generation_config` | Process/reconstructible/repeated config | no |
| `data/experiment_plans/matched_order_plan.jsonl.gz` | `ranking_eligible` | Process/reconstructible/repeated config | no |
| `data/experiment_plans/robustness_run_plan.csv` | `python_exec` | Local runtime path | no |
| `data/experiment_plans/robustness_run_plan.csv` | `ranking_role` | Internal role tag | no |
| `data/experiment_plans/generation_sensitivity_protocol.json` | `experiment_id` | Renamed generation_fewshot_convergence_v3_formal11 → generation_fewshot | no |
| `data/experiment_plans/generation_sensitivity_protocol.json` | `scoring_note` | Long self-explanatory note | no |
| `data/experiment_plans/robustness_sampling_manifest.json` | `selection_timestamp_policy` | Procedural memo | no |
| `configs/model_inference_configurations.csv` | `access_or_load_utc` | Microsecond run timestamps | no |
| `configs/model_inference_configurations.csv` | `main_run_start_utc` | Microsecond run timestamps | no |
| `configs/model_inference_configurations.csv` | `main_run_end_utc` | Microsecond run timestamps | no |
| `configs/model_inference_configurations.csv` | `completed_at_utc` | Microsecond run timestamps | no |
| `configs/model_manifests/Qwen3-8B-Thinking/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-Thinking/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-Thinking/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-Thinking/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-Thinking/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/deepseek-llm-7b-chat/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/deepseek-llm-7b-chat/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/deepseek-llm-7b-chat/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/deepseek-llm-7b-chat/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/deepseek-llm-7b-chat/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Doubao/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Doubao/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Doubao/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Doubao/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Doubao/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Mistral-7B-Instruct-v0.3/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Mistral-7B-Instruct-v0.3/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Mistral-7B-Instruct-v0.3/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Mistral-7B-Instruct-v0.3/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Mistral-7B-Instruct-v0.3/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Baichuan2-7B-Chat/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Baichuan2-7B-Chat/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Baichuan2-7B-Chat/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Baichuan2-7B-Chat/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Baichuan2-7B-Chat/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/chatglm3-6b/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/chatglm3-6b/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/chatglm3-6b/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/chatglm3-6b/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/chatglm3-6b/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/QwQ-32B/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/QwQ-32B/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/QwQ-32B/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/QwQ-32B/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/QwQ-32B/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/glm-4-9b-chat/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/glm-4-9b-chat/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/glm-4-9b-chat/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/glm-4-9b-chat/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/glm-4-9b-chat/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/internlm2_5-7b-chat/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/internlm2_5-7b-chat/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/internlm2_5-7b-chat/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/internlm2_5-7b-chat/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/internlm2_5-7b-chat/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-NonThinking/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-NonThinking/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-NonThinking/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-NonThinking/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen3-8B-NonThinking/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen2.5-7B-Instruct/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen2.5-7B-Instruct/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen2.5-7B-Instruct/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen2.5-7B-Instruct/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/Qwen2.5-7B-Instruct/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/model_manifests/DeepSeek-R1-Distill-Qwen-32B/model_manifest.json` | `access_or_load_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/DeepSeek-R1-Distill-Qwen-32B/model_manifest.json` | `main_run_start_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/DeepSeek-R1-Distill-Qwen-32B/model_manifest.json` | `main_run_end_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/DeepSeek-R1-Distill-Qwen-32B/model_manifest.json` | `completed_at_utc` | Timestamp or revision-apology note | no |
| `configs/model_manifests/DeepSeek-R1-Distill-Qwen-32B/model_manifest.json` | `note` | Timestamp or revision-apology note | no |
| `configs/protocol_manifest.json` | `created_at_utc` | Timestamp | no |
| `configs/protocol_manifest.json` | `protocol_version` | 4.2-reviewer-ready → 1.0.3 | no |
| `configs/qa_shot_conditions.json` | `purpose/rationale_policy/name_zh` | Prose / redundant | no |
| `configs/qa_shot_protocol_metadata.json` | `diagnostic_scope_note` | Prose memo | no |
| `configs/generation_rubrics.json` | `note` | Footnote → KNOWN_LIMITATIONS | no |
| `configs/generation_rubrics.json` | `version` | Internal milestone → 1.0.3 | no |
| `configs/system_prompt_policy.json` | `note` | Prose | no |
| `code/analysis_spec_4_2.json` | `policy_id` | METHODS_3_5_ALIGNMENT_20260915 → methods_3_5 | no |
| `code/analysis_spec_4_2.json` | `matched_order.binary_endpoint_note` | Narrative note | no |
| `code/analysis_spec_4_3.json` | `policy_id` | METHODS_3_5_ALIGNMENT_4_3_20260915 → methods_3_5_qwen3 | no |
| `results/fewshot/holm_family_audit.csv` | `(moved)` | Moved to results/audit/holm_family_audit.csv | no |
| `results/qwen3/robustness_duplicate_setting_audit.csv` | `(moved)` | Moved to results/audit/robustness_duplicate_setting_audit.csv | no |
| `results/cnhi/MASTER_CNHI_ZERO_AUDIT_METHODS_V2.csv` | `(moved)` | Moved to results/audit/MASTER_CNHI_ZERO_AUDIT_METHODS_V2.csv | no |
| `results/audit/MASTER_CNHI_ZERO_AUDIT_METHODS_V2.csv` | `interpretation` | Interpretive/pipeline column | no |
| `results/audit/robustness_duplicate_setting_audit.csv` | `note` | Interpretive/pipeline column | no |
| `results/cnhi/main_shot_paired_contrasts_methods_v2.csv` | `interpretation` | Interpretive/pipeline column | no |
| `results/cnhi/main_shot_paired_contrasts_methods_v2.csv` | `holm_incomplete_family_conservative` | Interpretive/pipeline column | no |
| `results/fewshot/classification_macro_f1_shot_contrasts_methods35.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/fewshot/generation_sensitivity_contrasts_methods35.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/fewshot/main_primary_shot_contrasts_methods35.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/fewshot/matched_order_primary_contrasts_methods35.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/qwen3/qwen3_generation_zero_shot_descriptive_latest.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/qwen3/qwen3_generation_zero_shot_descriptive_latest.csv` | `note` | Interpretive/pipeline column | no |
| `results/qwen3/qwen3_mode_contrasts_methods35.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/qwen3/qwen3_mode_contrasts_methods35.csv` | `interpretation_limit` | Interpretive/pipeline column | no |
| `results/qwen3/qwen3_zero_shot_profile_latest.csv` | `analysis_role` | Interpretive/pipeline column | no |
| `results/qwen3/robustness_semantic_pair_coverage.csv` | `is_independent_setting_evidence` | Interpretive/pipeline column | no |
| `results/qwen3/robustness_task_setting_summary_methods35_43.csv` | `interpretation` | Interpretive/pipeline column | no |
| `results/qwen3/robustness_task_setting_summary_methods35_43.csv` | `is_independent_setting_evidence` | Interpretive/pipeline column | no |
| `results/zero_shot/Supplementary_Table_S3_diagnostics.csv` | `source` | Interpretive/pipeline column | no |
| `results/zero_shot/zero_shot_summary_ci_latest.csv` | `source` | Interpretive/pipeline column | no |
| `human_validation/blinded_generation_outputs_180.jsonl` | `calibration_split` | heldout_validation process tag | no |
| `human_validation/blinded_scorer_positive_audit_60.jsonl` | `endpoint_definition` | Scoring prose; guidelines cover this | no |
| `human_validation/blinded_controlled_output_audit_100.jsonl` | `gold_record.* process` | Align nested gold with public schema | no |
| `code/recompute_fewshot_methods35.py` | `CLI paths` | BREAKING: --data-dir + scored_records/; legacy refs optional | yes |
| `code/recompute_qwen3_methods35.py` | `CLI paths` | BREAKING: --data-dir + scored_records/; missing internal CSVs optional | yes |
| `code/validate_fewshot_inputs.py` | `CLI paths` | BREAKING: --data-dir + scored_records/ | yes |
| `code/validate_qwen3_inputs.py` | `CLI paths` | BREAKING: --data-dir + scored_records/; optional internal CSVs | yes |
| `requirements.txt` | `threadpoolctl` | Add dependency used by recompute_zero_shot.py | no |
| `LICENSE` | `(new)` | Draft only; author must confirm OSI license | no |
| `CITATION.cff` | `(new)` | Draft; blank author/year/DOI | no |
| `DATA_AND_SOURCE_NOTICE.md` | `(rewrite)` | Remove author TODO; state unconfirmed redistribution rule | no |
| `README.md` | `(rewrite)` | Public eval-repo structure | no |
| `KNOWN_LIMITATIONS.md` | `(rewrite)` | ≤5 short bullets; document optional missing CSVs | no |
| `human_validation/README.md` | `(rewrite)` | Remove historical internal path memo | no |
| `CHANGELOG.md` | `(new)` | Public changelog | no |
| `LICENSE` | `(finalized)` | Author confirmed Apache-2.0; draft placeholder replaced with full license text | no |
