# Known reproducibility limits

1. Provider-side API revisions are not exposed for every API call. Where a concrete provider model identifier was retained, it is reported; no unobserved provider revision is inferred.
2. Some local model records do not contain immutable weight-byte hashes or repository commit revisions. The retained checkpoint/inventory fingerprint and recorded access/load time are reported instead; blank revision fields are not back-filled.
3. Completed H1/H2 individual ratings are not included in the public package. Human-validation design, guidelines, blinded materials, and sampling manifests are public; aggregate reliability results are reported in the manuscript.
4. Automatic-analysis reproducibility is stronger than provider-side model-weight reproducibility: an API provider may change infrastructure behind a stable model alias, and this package cannot reconstruct provider-side state that was not exposed at execution time.
5. Length/structure compliance checks are separate diagnostics and are not additional weighted generation-quality dimensions; see `configs/generation_rubrics.json`.
