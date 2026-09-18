# Data and source-material notice

## What this package contains

- Researcher-constructed and adapted evaluation items for eight Chinese-language tasks on traditional family values / family rules.
- Historically grounded source passages used inside some items.
- Model identifiers and retained inference metadata under `configs/` (model weights are not redistributed).

## Rights boundary

This repository does **not** grant new rights over third-party source resources. Where an originating resource imposes access or reuse restrictions, those terms remain controlling.

## Redistribution rule for source-derived passages

Redistribution rights for every third-party source-derived passage in
`data/benchmark/canonical_gold_750.jsonl` are **not confirmed** in this package.

Until the authors confirm redistribution is permitted for a passage:

1. Do **not** treat the embedded source text as freely redistributable.
2. If a passage cannot be redistributed, replace **only** that `source_text` (or equivalent source field) with an access pointer and content hash.
3. Preserve the stable `item_id` and all gold labels / scoring keys.
4. Document the restriction in this file.

Do not silently substitute a different benchmark item.

## Canonical record

`data/benchmark/canonical_gold_750.jsonl` is the versioned 750-item public benchmark record used by the study (task counts: 100/100/100/50/100/100/100/100).
