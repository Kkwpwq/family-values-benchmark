# Formal-records release asset

The matching large-output archive is distributed as a GitHub Release asset rather than committed to Git history.

- **Asset:** `aslib-formal-records-v1.0.4-reviewer-complete.zip`
- **SHA-256:** `9ac45eb83179f8e8978b1e633d2d264b1d110fb55b42b50355f917750081deb1`

The asset contains the raw model-output families used in the reported analyses and the complete item-level scored-record archive.

Example:

```bash
gh release download <tag> -p aslib-formal-records-v1.0.4-reviewer-complete.zip
unzip aslib-formal-records-v1.0.4-reviewer-complete.zip
python3 code/recompute_zero_shot.py \
  --data-dir path/to/aslib-formal-records-v1.0.4-reviewer-complete \
  --out results/recomputed_zero_shot
```

Do not commit the extracted formal-records tree into the Git repository.
