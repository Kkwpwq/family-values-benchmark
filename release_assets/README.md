# Release asset

Large formal outputs and item-level scored records are distributed as the
version-linked GitHub Release asset:

- **Asset:** `aslib-formal-records-v1.0.3-reviewer-complete.zip`
- **SHA-256:** `cd6e4de69b829e6d05969fe4612a5e48ac2a4c4f7e046e6832778e5e8636563b`

After download:

```bash
gh release download <tag> -p aslib-formal-records-v1.0.3-reviewer-complete.zip
unzip aslib-formal-records-v1.0.3-reviewer-complete.zip
python code/recompute_zero_shot.py \
  --data-dir path/to/aslib-formal-records-v1.0.3-reviewer-complete \
  --out results/recomputed_zero_shot
```

Do not commit the extracted formal-records tree into the Git repository.
