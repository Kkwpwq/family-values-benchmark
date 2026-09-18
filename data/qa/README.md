# QA development split

`development_gold_20.jsonl` contains the 20-item QA development split. These items are not part of the 100-item QA test set and are not included in the primary reported test results.

`development_inference_20.jsonl` is the corresponding no-gold inference view. The three fixed demonstrations used by the main QA 0/1/3-shot protocol are stored in `../demonstrations/qa_fixed_examples.jsonl` and are disjoint from both development and test items. A subset of development items is used separately as demonstrations in the diagnostic ablation experiments.
