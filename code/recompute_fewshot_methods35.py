#!/usr/bin/env python3
"""Recalculate Methods 3.5-aligned statistics for ASLIB Results 4.2.

Scope
-----
1) Main constrained 0/1/3-shot, 11 primary configurations only.
2) Classification macro-F1 secondary shot contrasts.
3) Matched six-order controlled contrasts, preserving all six orders within item.
4) Generation 24-item sensitivity validation/recalculation from the complete 2376 dual-LLM item scores.
5) Optional earlier ablation contrasts as a separate exploratory family.

No model inference, rescoring, CNHI recomputation, or gold modification is performed.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import zlib
from collections import defaultdict
from pathlib import Path
from typing import Callable

import numpy as np

PRIMARY_MODELS = [
    'Baichuan2-7B-Chat',
    'chatglm3-6b',
    'deepseek-llm-7b-chat',
    'DeepSeek-R1-Distill-Qwen-32B',
    'glm-4-9b-chat',
    'internlm2_5-7b-chat',
    'Mistral-7B-Instruct-v0.3',
    'Qwen2.5-7B-Instruct',
    'Qwen3-8B-NonThinking',
    'QwQ-32B',
    'Doubao',
]
LABELS = list('忠孝悌节养恕勇俭让慎省')
TASKS = ['classification', 'reasoning', 'structuring', 'relationship', 'qa_v4_5']
GEN_TASKS = ['story_generation', 'rewriting', 'continuation']
PRIMARY_ENDPOINT = {
    'classification': 'accuracy',
    'reasoning': 'judgment_accuracy',
    'structuring': 'cnhi_v2',
    'relationship': 'micro_f1',
    'qa_v4_5': 'recoverable_accuracy',
}


def read_jsonl_gz(path: Path):
    out = []
    with gzip.open(path, 'rt', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f'{path}:{i}: invalid JSONL') from e
    return out


def read_jsonl(path: Path):
    out = []
    with path.open(encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f'{path}:{i}: invalid JSONL') from e
    return out


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows):
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r)) if rows else ['status']
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def stable_seed(base: int, *parts) -> int:
    key = '|'.join(map(str, parts)).encode('utf-8')
    return (base + zlib.crc32(key)) % (2**32 - 1)


def holm_adjust(rows, p_col='p_raw', out_col='p_holm'):
    idx = [i for i, r in enumerate(rows) if r.get(p_col) is not None and np.isfinite(float(r[p_col]))]
    order = sorted(idx, key=lambda i: float(rows[i][p_col]))
    m = len(idx)
    running = 0.0
    for rank, i in enumerate(order):
        candidate = min(1.0, (m - rank) * float(rows[i][p_col]))
        running = max(running, candidate)
        rows[i][out_col] = running
        rows[i]['significant_holm_0_05'] = running < 0.05
    for r in rows:
        r['holm_family_size'] = m
        if out_col not in r:
            r[out_col] = None
            r['significant_holm_0_05'] = None
    return rows


def exact_mcnemar(a: np.ndarray, b: np.ndarray):
    a = np.asarray(a, int)
    b = np.asarray(b, int)
    if len(a) != len(b):
        raise ValueError('McNemar arrays differ in length')
    a_only = int(np.sum((a == 1) & (b == 0)))
    b_only = int(np.sum((a == 0) & (b == 1)))
    n = a_only + b_only
    if n == 0:
        p = 1.0
    else:
        k = min(a_only, b_only)
        lower = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        p = min(1.0, 2 * lower)
    return a_only, b_only, n, p


def macro_f1_stat(v: np.ndarray) -> np.ndarray:
    """v [...,33] = tp[11], gold_count[11], pred_count[11]."""
    tp = v[..., :11]
    gold = v[..., 11:22]
    pred = v[..., 22:33]
    den = gold + pred
    f = np.divide(2 * tp, den, out=np.zeros_like(tp, dtype=float), where=den > 0)
    return f.mean(axis=-1)


def micro_f1_stat(v: np.ndarray) -> np.ndarray:
    tp, fp, fn = v[..., 0], v[..., 1], v[..., 2]
    den = 2 * tp + fp + fn
    return np.divide(2 * tp, den, out=np.zeros_like(tp, dtype=float), where=den > 0)


def mean_stat(v: np.ndarray) -> np.ndarray:
    return np.divide(v[..., 0], v[..., 1], out=np.zeros_like(v[..., 0], dtype=float), where=v[..., 1] > 0)


def row_sufficient(row, metric):
    if metric in ('accuracy', 'judgment_accuracy', 'recoverable_accuracy'):
        return np.array([float(row['accuracy']), 1.0])
    if metric == 'cnhi_v2':
        x = row.get('cnhi_v2')
        if x is None:
            raise ValueError('Missing cnhi_v2')
        return np.array([float(x), 1.0])
    if metric == 'macro_f1':
        gold = row.get('gold_label')
        pred = row.get('parsed_label') or '__INVALID__'
        tp = np.array([1.0 if gold == lab and pred == lab else 0.0 for lab in LABELS])
        gc = np.array([1.0 if gold == lab else 0.0 for lab in LABELS])
        pc = np.array([1.0 if pred == lab else 0.0 for lab in LABELS])
        return np.concatenate([tp, gc, pc])
    if metric == 'micro_f1':
        return np.array([float(row['tp']), float(row['fp']), float(row['fn'])])
    raise KeyError(metric)


def stat_func(metric) -> Callable[[np.ndarray], np.ndarray]:
    if metric == 'macro_f1':
        return macro_f1_stat
    if metric == 'micro_f1':
        return micro_f1_stat
    return mean_stat


def item_matrix(rows, metric, expected_repeats=None):
    """Average repeated order rows within item BEFORE nonlinear task statistic."""
    g = defaultdict(list)
    for r in rows:
        g[r['item_id']].append(r)
    ids = sorted(g)
    vals = []
    clusters = []
    repeat_counts = []
    for iid in ids:
        rr = g[iid]
        clusters_here = {str(r['source_cluster']) for r in rr}
        if len(clusters_here) != 1:
            raise ValueError(f'source_cluster changed within item {iid}: {clusters_here}')
        if expected_repeats is not None and len(rr) != expected_repeats:
            raise ValueError(f'{iid}: expected {expected_repeats} rows, got {len(rr)}')
        vv = np.stack([row_sufficient(r, metric) for r in rr])
        vals.append(vv.mean(axis=0))
        clusters.append(next(iter(clusters_here)))
        repeat_counts.append(len(rr))
    return ids, np.stack(vals), clusters, repeat_counts


def aggregate_by_cluster(x: np.ndarray, clusters):
    units = sorted(set(clusters))
    uidx = {u: i for i, u in enumerate(units)}
    out = np.zeros((len(units), x.shape[1]), float)
    for i, c in enumerate(clusters):
        out[uidx[c]] += x[i]
    return units, out


def paired_bootstrap_effect(a_rows, b_rows, metric, n_boot, seed, expected_repeats=None):
    ai, ax, ac, ar = item_matrix(a_rows, metric, expected_repeats)
    bi, bx, bc, br = item_matrix(b_rows, metric, expected_repeats)
    if ai != bi or ac != bc:
        raise ValueError('Paired item/source sets do not match')
    units, aa = aggregate_by_cluster(ax, ac)
    units_b, bb = aggregate_by_cluster(bx, bc)
    if units != units_b:
        raise ValueError('Cluster sets do not match')
    stat = stat_func(metric)
    obs_a = float(stat(aa.sum(axis=0)))
    obs_b = float(stat(bb.sum(axis=0)))
    obs = obs_a - obs_b
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(len(units), np.full(len(units), 1 / len(units)), size=n_boot)
    boot_a = stat(counts @ aa)
    boot_b = stat(counts @ bb)
    boots = boot_a - boot_b
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return {
        'ids': ai,
        'clusters': ac,
        'repeat_counts': ar,
        'a_items': ax,
        'b_items': bx,
        'a_cluster': aa,
        'b_cluster': bb,
        'mean_a': obs_a,
        'mean_b': obs_b,
        'effect': obs,
        'boot_effects': boots,
        'ci_low': float(lo),
        'ci_high': float(hi),
        'n_items': len(ai),
        'n_clusters': len(units),
        'units': units,
    }


def centered_bootstrap_p(info):
    obs = info['effect']
    null = info['boot_effects'] - obs
    return (1 + int(np.sum(np.abs(null) >= abs(obs) - 1e-15))) / (len(null) + 1)


def signflip_p_mean(info, n_flip, seed):
    """Sign flip cluster-level score differences for mean endpoints only."""
    aa, bb = info['a_cluster'], info['b_cluster']
    if aa.shape[1] != 2 or bb.shape[1] != 2:
        raise ValueError('signflip_p_mean only supports [sum,count] sufficient stats')
    total_count = float(aa[:, 1].sum())
    if abs(total_count - float(bb[:, 1].sum())) > 1e-12:
        raise ValueError('Paired counts differ')
    diffs = aa[:, 0] - bb[:, 0]
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_flip, len(diffs)))
    null = (signs @ diffs) / total_count
    obs = info['effect']
    return (1 + int(np.sum(np.abs(null) >= abs(obs) - 1e-15))) / (n_flip + 1)


def group_main(rows):
    out = defaultdict(list)
    for r in rows:
        if r.get('is_primary_model') is True and r['model_id'] in PRIMARY_MODELS and r['task_id'] in TASKS and r.get('shot') in (0, 1, 3):
            out[(r['model_id'], r['task_id'], int(r['shot']))].append(r)
    return out


def recalc_main(rows, outdir: Path, B: int, S: int, seed: int):
    groups = group_main(rows)
    expected = {'classification': 100, 'reasoning': 100, 'structuring': 100, 'relationship': 50, 'qa_v4_5': 100}
    summary = []
    primary = []
    secondary_macro = []
    for model in PRIMARY_MODELS:
        for task in TASKS:
            for shot in (0, 1, 3):
                rr = groups[(model, task, shot)]
                if len(rr) != expected[task]:
                    raise ValueError(f'{model}/{task}/{shot}: {len(rr)} != {expected[task]}')
                metrics = [PRIMARY_ENDPOINT[task]] + (['macro_f1'] if task == 'classification' else [])
                for metric in metrics:
                    _, xx, cc, _ = item_matrix(rr, metric, expected_repeats=1)
                    _, agg = aggregate_by_cluster(xx, cc)
                    val = float(stat_func(metric)(agg.sum(axis=0)))
                    summary.append({'model_id': model, 'task_id': task, 'shot': shot, 'metric': metric,
                                    'n_items': len(xx), 'n_clusters': len(set(cc)), 'estimate_100': 100 * val})
            for shot in (1, 3):
                a = groups[(model, task, shot)]
                b = groups[(model, task, 0)]
                metric = PRIMARY_ENDPOINT[task]
                info = paired_bootstrap_effect(a, b, metric, B, stable_seed(seed, 'main', model, task, shot, metric), 1)
                if task in ('classification', 'reasoning', 'qa_v4_5'):
                    aa = np.array([int(round(float(r['accuracy']))) for r in sorted(a, key=lambda r: r['item_id'])])
                    bb = np.array([int(round(float(r['accuracy']))) for r in sorted(b, key=lambda r: r['item_id'])])
                    a_only, b_only, disc, p = exact_mcnemar(aa, bb)
                    test = 'two-sided exact McNemar on paired item correctness'
                elif task == 'relationship':
                    p = centered_bootstrap_p(info)
                    a_only = b_only = disc = None
                    test = 'two-sided centered paired source-cluster bootstrap approximation; micro-F1 recomputed in each replicate'
                elif task == 'structuring':
                    p = signflip_p_mean(info, S, stable_seed(seed, 'main-sign', model, task, shot))
                    a_only = b_only = disc = None
                    test = 'two-sided paired sign-flip; one sign per source cluster'
                else:
                    raise AssertionError(task)
                primary.append({
                    'model_id': model, 'task_id': task, 'contrast': f'{shot}-0', 'metric': metric,
                    'n_items': info['n_items'], 'n_clusters': info['n_clusters'],
                    'mean_a_100': 100 * info['mean_a'], 'mean_b_100': 100 * info['mean_b'],
                    'difference_a_minus_b_100': 100 * info['effect'],
                    'ci95_low_100': 100 * info['ci_low'], 'ci95_high_100': 100 * info['ci_high'],
                    'p_raw': p, 'test': test, 'ci_method': f'paired percentile source-cluster bootstrap; {B} resamples',
                    'a_correct_b_wrong': a_only, 'a_wrong_b_correct': b_only, 'discordant_pairs': disc,
                    'bootstrap_resamples': B, 'signflip_resamples': S if task == 'structuring' else None,
                    'analysis_role': 'PRIMARY_TASK_ENDPOINT',
                })
                if task == 'classification':
                    minfo = paired_bootstrap_effect(a, b, 'macro_f1', B, stable_seed(seed, 'main', model, task, shot, 'macro_f1'), 1)
                    mp = centered_bootstrap_p(minfo)
                    secondary_macro.append({
                        'model_id': model, 'task_id': task, 'contrast': f'{shot}-0', 'metric': 'macro_f1',
                        'n_items': minfo['n_items'], 'n_clusters': minfo['n_clusters'],
                        'mean_a_100': 100 * minfo['mean_a'], 'mean_b_100': 100 * minfo['mean_b'],
                        'difference_a_minus_b_100': 100 * minfo['effect'],
                        'ci95_low_100': 100 * minfo['ci_low'], 'ci95_high_100': 100 * minfo['ci_high'],
                        'p_raw': mp,
                        'test': 'two-sided centered paired source-cluster bootstrap approximation; fixed 11-class macro-F1 recomputed in each replicate',
                        'ci_method': f'paired percentile source-cluster bootstrap; macro-F1 recomputed in each replicate; {B} resamples',
                        'bootstrap_resamples': B, 'analysis_role': 'SECONDARY_CLASSIFICATION_ENDPOINT',
                    })
    # One 22-comparison primary family per task.
    for task in TASKS:
        fam = [r for r in primary if r['task_id'] == task]
        if len(fam) != 22:
            raise ValueError(f'{task}: primary family size {len(fam)} != 22')
        holm_adjust(fam)
        for r in fam:
            r['holm_family_id'] = f'main_{task}_primary_22'
    # Classification macro-F1 is a separate secondary 22-comparison family.
    if len(secondary_macro) != 22:
        raise ValueError('classification macro-F1 family must contain 22 contrasts')
    holm_adjust(secondary_macro)
    for r in secondary_macro:
        r['holm_family_id'] = 'main_classification_macro_f1_secondary_22'
    write_csv(outdir/'main_condition_summary_methods35.csv', summary)
    write_csv(outdir/'main_primary_shot_contrasts_methods35.csv', primary)
    write_csv(outdir/'classification_macro_f1_shot_contrasts_methods35.csv', secondary_macro)
    return primary, secondary_macro, summary


def group_generic(rows):
    d = defaultdict(list)
    for r in rows:
        d[(r['model_id'], r['task_id'], r['condition_id'])].append(r)
    return d


def matched_specs(rows):
    models = sorted({r['model_id'] for r in rows})
    specs = []
    for m in models:
        for t in TASKS:
            if t == 'qa_v4_5':
                specs += [(m, t, 'W3', 'G3'), (m, t, 'L3', 'G3')]
            else:
                specs += [(m, t, 'W3', 'G3')]
    return specs


def recalc_matched(rows, outdir: Path, B: int, S: int, seed: int):
    groups = group_generic(rows)
    result = []
    macro_secondary = []
    orderdiag = []
    for model, task, a_cond, b_cond in matched_specs(rows):
        a = groups[(model, task, a_cond)]
        b = groups[(model, task, b_cond)]
        if len(a) != 120 or len(b) != 120:
            raise ValueError(f'{model}/{task}/{a_cond}-{b_cond}: expected 120 rows per condition')
        metric = PRIMARY_ENDPOINT[task]
        info = paired_bootstrap_effect(a, b, metric, B, stable_seed(seed, 'matched', model, task, a_cond, b_cond, metric), 6)
        # Six repeated orders are averaged within item before inference. Therefore binary
        # endpoints become item-level proportions and are mean-score comparisons, not
        # independent binary McNemar pairs.
        if task == 'relationship':
            p = centered_bootstrap_p(info)
            test = 'two-sided centered paired source-cluster bootstrap approximation after six-order within-item averaging; micro-F1 recomputed in each replicate'
        else:
            p = signflip_p_mean(info, S, stable_seed(seed, 'matched-sign', model, task, a_cond, b_cond))
            test = 'two-sided paired sign-flip on six-order-averaged item score; one sign per source cluster'
        row = {
            'model_id': model, 'task_id': task, 'contrast': f'{a_cond}-{b_cond}', 'metric': metric,
            'orders_per_item': 6, 'n_items': info['n_items'], 'n_clusters': info['n_clusters'],
            'mean_a_100': 100*info['mean_a'], 'mean_b_100': 100*info['mean_b'],
            'difference_a_minus_b_100': 100*info['effect'],
            'ci95_low_100': 100*info['ci_low'], 'ci95_high_100': 100*info['ci_high'],
            'p_raw': p, 'test': test,
            'ci_method': f'paired percentile source-cluster bootstrap after six-order within-item averaging; {B} resamples',
            'bootstrap_resamples': B, 'signflip_resamples': None if task=='relationship' else S,
            'analysis_role': 'MATCHED_ORDER_PRIMARY_PRESPECIFIED',
        }
        result.append(row)
        # Order-wise descriptive effect audit (not independent tests).
        for perm in range(1, 7):
            aa = [r for r in a if int(r['permutation_index']) == perm]
            bb = [r for r in b if int(r['permutation_index']) == perm]
            oi = paired_bootstrap_effect(aa, bb, metric, B, stable_seed(seed, 'orderdiag', model, task, a_cond, b_cond, perm), 1)
            orderdiag.append({'model_id': model, 'task_id': task, 'contrast': f'{a_cond}-{b_cond}', 'permutation_index': perm,
                              'metric': metric, 'difference_a_minus_b_100': 100*oi['effect'], 'descriptive_only': True})
        if task == 'classification':
            mi = paired_bootstrap_effect(a, b, 'macro_f1', B, stable_seed(seed, 'matched', model, task, a_cond, b_cond, 'macro_f1'), 6)
            mp = centered_bootstrap_p(mi)
            macro_secondary.append({
                'model_id': model, 'task_id': task, 'contrast': f'{a_cond}-{b_cond}', 'metric': 'macro_f1',
                'orders_per_item': 6, 'n_items': mi['n_items'], 'n_clusters': mi['n_clusters'],
                'mean_a_100': 100*mi['mean_a'], 'mean_b_100': 100*mi['mean_b'],
                'difference_a_minus_b_100': 100*mi['effect'], 'ci95_low_100': 100*mi['ci_low'], 'ci95_high_100': 100*mi['ci_high'],
                'p_raw': mp,
                'test': 'two-sided centered paired source-cluster bootstrap approximation after six-order within-item averaging; fixed 11-class macro-F1 recomputed in each replicate',
                'ci_method': f'paired percentile source-cluster bootstrap; {B} resamples',
                'analysis_role': 'MATCHED_ORDER_SECONDARY_CLASSIFICATION_ENDPOINT',
            })
    if len(result) != 30:
        raise ValueError(f'matched-order primary family must contain 30 contrasts, got {len(result)}')
    holm_adjust(result)
    for r in result:
        r['holm_family_id'] = 'matched_order_prespecified_30'
    if len(macro_secondary) != 5:
        raise ValueError(f'matched-order classification macro-F1 family must contain 5 contrasts, got {len(macro_secondary)}')
    holm_adjust(macro_secondary)
    for r in macro_secondary:
        r['holm_family_id'] = 'matched_order_classification_macro_f1_secondary_5'
    write_csv(outdir/'matched_order_primary_contrasts_methods35.csv', result)
    write_csv(outdir/'matched_order_classification_macro_f1_secondary.csv', macro_secondary)
    write_csv(outdir/'matched_order_orderwise_diagnostics.csv', orderdiag)
    return result, macro_secondary, orderdiag


def recalc_generation(item_csv: Path, panel_jsonl: Path, outdir: Path, B: int, S: int, seed: int):
    items = read_csv(item_csv)
    panel = {r['item_id']: r for r in read_jsonl(panel_jsonl)}
    if len(items) != 2376:
        raise ValueError(f'generation item scores: expected 2376, got {len(items)}')
    d = defaultdict(list)
    for r in items:
        r = dict(r)
        r['shot'] = int(r['shot'])
        r['dual_total'] = float(r['dual_total'])
        if r['task_id'] == 'rewriting':
            src = panel[r['item_id']]['metadata']['source_index']
            r['source_cluster'] = f'REW-SRC-{src}'
        else:
            r['source_cluster'] = r['item_id']
        r['accuracy'] = r['dual_total'] / 100.0  # reuse mean-score sufficient handler
        d[(r['model_id'], r['task_id'], r['shot'])].append(r)
    models = sorted({r['model_id'] for r in items})
    if len(models) != 11:
        raise ValueError(f'generation models != 11: {models}')
    out = []
    for model in models:
        for task in GEN_TASKS:
            for shot in (1, 3):
                a, b = d[(model, task, shot)], d[(model, task, 0)]
                if len(a) != 24 or len(b) != 24:
                    raise ValueError(f'{model}/{task}: expected 24 paired items')
                info = paired_bootstrap_effect(a, b, 'accuracy', B, stable_seed(seed, 'gen', model, task, shot), 1)
                p = signflip_p_mean(info, S, stable_seed(seed, 'gen-sign', model, task, shot))
                out.append({'model_id': model, 'task_id': task, 'contrast': f'{shot}-0', 'metric': 'dual_llm_weighted_total',
                            'n_items': info['n_items'], 'n_clusters': info['n_clusters'],
                            'mean_a_100': 100*info['mean_a'], 'mean_b_100': 100*info['mean_b'],
                            'difference_a_minus_b_100': 100*info['effect'],
                            'ci95_low_100': 100*info['ci_low'], 'ci95_high_100': 100*info['ci_high'],
                            'p_raw': p, 'test': 'two-sided paired sign-flip; one sign per source cluster',
                            'ci_method': f'paired percentile source-cluster bootstrap; {B} resamples',
                            'bootstrap_resamples': B, 'signflip_resamples': S,
                            'analysis_role': 'GENERATION_SENSITIVITY_24_ITEM'})
    if len(out) != 66:
        raise ValueError(f'generation contrasts != 66: {len(out)}')
    for task in GEN_TASKS:
        fam = [r for r in out if r['task_id'] == task]
        if len(fam) != 22:
            raise ValueError(f'{task}: expected 22 contrasts')
        holm_adjust(fam)
        for r in fam:
            r['holm_family_id'] = f'generation_{task}_22'
    write_csv(outdir/'generation_sensitivity_contrasts_methods35.csv', out)
    return out


def recalc_ablation_exploratory(rows, legacy_csv: Path, outdir: Path, B: int, S: int, seed: int):
    """Optional: endpoint-correct reanalysis, still labeled exploratory/earlier phase.

    The original 125 planned contrasts are retained as a SEPARATE global family.
    This does not replace the later matched-order family for order-sensitive causal interpretation.
    """
    groups = group_generic(rows)
    specs = read_csv(legacy_csv)
    out = []
    for old in specs:
        model, task = old['model_id'], old['task_id']
        a_cond, b_cond = old['contrast'].split('-', 1)
        a, b = groups[(model, task, a_cond)], groups[(model, task, b_cond)]
        metric = PRIMARY_ENDPOINT[task]
        info = paired_bootstrap_effect(a, b, metric, B, stable_seed(seed, 'abl', model, task, a_cond, b_cond), None)
        if task in ('classification','reasoning','qa_v4_5'):
            # Earlier ablation conditions contain repeated runs for some conditions.
            # Average repeats within item first, then use a paired sign-flip on the
            # resulting item-level mean score rather than pseudo-replicating McNemar pairs.
            p=signflip_p_mean(info,S,stable_seed(seed,'abl-sign',model,task,a_cond,b_cond));a_only=b_only=disc=None
            test='two-sided paired sign-flip on repeat-averaged item accuracy; one sign per source cluster'
        elif task=='relationship':
            p=centered_bootstrap_p(info);a_only=b_only=disc=None
            test='two-sided centered paired source-cluster bootstrap approximation; micro-F1 recomputed in each replicate'
        else:
            p=signflip_p_mean(info,S,stable_seed(seed,'abl-sign',model,task,a_cond,b_cond));a_only=b_only=disc=None
            test='two-sided paired sign-flip; one sign per source cluster'
        out.append({'model_id':model,'task_id':task,'contrast':old['contrast'],'metric':metric,
                    'n_items':info['n_items'],'n_clusters':info['n_clusters'],'mean_a_100':100*info['mean_a'],'mean_b_100':100*info['mean_b'],
                    'difference_a_minus_b_100':100*info['effect'],'ci95_low_100':100*info['ci_low'],'ci95_high_100':100*info['ci_high'],
                    'p_raw':p,'test':test,'a_correct_b_wrong':a_only,'a_wrong_b_correct':b_only,'discordant_pairs':disc,
                    'analysis_role':'EARLIER_ABLATION_EXPLORATORY','caveat':old.get('caveat','')})
    if len(out)!=125: raise ValueError(f'ablation contrasts !=125: {len(out)}')
    holm_adjust(out)
    for r in out:r['holm_family_id']='earlier_ablation_global_125_exploratory'
    write_csv(outdir/'ablation_125_endpoint_correct_exploratory.csv',out)
    return out


def comparison_audit(new_rows, old_rows, keys, old_effect_col, old_p_col, label):
    om = {tuple(r[k] for k in keys): r for r in old_rows}
    out=[]
    for r in new_rows:
        key=tuple(str(r[k]) for k in keys)
        o=om.get(key)
        if not o: continue
        oldeff=float(o[old_effect_col]) if o.get(old_effect_col) not in (None,'') else None
        oldp=float(o[old_p_col]) if o.get(old_p_col) not in (None,'') else None
        out.append({**{k:r[k] for k in keys},'comparison_set':label,
                    'new_effect_100':r['difference_a_minus_b_100'],'old_effect_100':oldeff,
                    'effect_difference_100':None if oldeff is None else r['difference_a_minus_b_100']-oldeff,
                    'new_p_raw':r['p_raw'],'old_p_raw':oldp,'new_test':r['test']})
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',type=Path,default=None,help='Optional extracted formal-records root. If omitted, packaged inputs/ are used.')
    ap.add_argument('--out',type=Path,default=None,help='Output dir (default: <repo>/results/fewshot_recomputed)')
    ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1],help=argparse.SUPPRESS)
    ap.add_argument('--bootstrap',type=int,default=10000)
    ap.add_argument('--signflips',type=int,default=10000)
    ap.add_argument('--seed',type=int,default=20260915)
    args=ap.parse_args()
    root=args.package_root
    data=Path(args.data_dir) if args.data_dir else None
    if data is None:
        scored=root/'inputs'
    else:
        scored=(data/'scored_records') if (data/'scored_records').is_dir() else data
    if not scored.is_dir():
        raise SystemExit(f'missing scored input directory: {scored}')
    out=args.out or (root/'results'/'fewshot_recomputed')
    out.mkdir(parents=True,exist_ok=True)

    ref_candidates=[]
    if data is not None:
        ref_candidates.append(data/'reference_legacy')
    ref_candidates.append(root/'reference_legacy')
    ref=next((r for r in ref_candidates if r.is_dir()),None)
    if ref is None:
        raise SystemExit('missing reference_legacy/ directory')

    mainrows=read_jsonl_gz(scored/'main_scored_items_methods_v2.jsonl.gz')
    matched=read_jsonl_gz(scored/'matched_order_scored_items_methods_v2.jsonl.gz')
    ablation=read_jsonl_gz(scored/'ablation_scored_items_methods_v2.jsonl.gz')
    prim,macro,summary=recalc_main(mainrows,out,args.bootstrap,args.signflips,args.seed)
    mprim,mmacro,orderdiag=recalc_matched(matched,out,args.bootstrap,args.signflips,args.seed)

    panel_candidates=[scored/'panel72_scoring.jsonl',root/'inputs'/'panel72_scoring.jsonl']
    if data is not None:
        panel_candidates.insert(1,data/'panel72_scoring.jsonl')
    panel72=next((p for p in panel_candidates if p.is_file()),None)
    if panel72 is None:
        raise SystemExit('missing panel72_scoring.jsonl')
    gen_score_path=scored/'dual_2376_item_scores.csv'
    if not gen_score_path.is_file():
        gen_score_path=root/'inputs'/'dual_2376_item_scores.csv'
    if not gen_score_path.is_file():
        raise SystemExit('missing dual_2376_item_scores.csv')
    gen=recalc_generation(gen_score_path,panel72,out,args.bootstrap,args.signflips,args.seed)

    required_refs={
        'ablation':ref/'ablation_paired_contrasts_methods_v2.csv',
        'main':ref/'main_shot_paired_contrasts_methods_v2.csv',
        'matched':ref/'matched_order_paired_contrasts_methods_v2.csv',
    }
    missing=[str(p) for p in required_refs.values() if not p.is_file()]
    if missing:
        raise SystemExit('missing legacy reference files: '+', '.join(missing))
    abl=recalc_ablation_exploratory(ablation,required_refs['ablation'],out,args.bootstrap,args.signflips,args.seed)
    audit=[]
    audit += comparison_audit(prim,read_csv(required_refs['main']),['model_id','task_id','contrast'],'difference_100','p_cluster_swap','main_primary_vs_legacy')
    audit += comparison_audit(mprim,read_csv(required_refs['matched']),['model_id','task_id','contrast'],'difference_100','p_cluster_swap','matched_order_vs_legacy')
    write_csv(out/'legacy_comparison_audit.csv',audit)

    families=[]
    for family_id, rows in [(f'main_{t}_primary_22',[r for r in prim if r['task_id']==t]) for t in TASKS]:
        families.append({'family_id':family_id,'n_tests':len(rows),'role':'formal primary shot-vs-zero family'})
    families.append({'family_id':'main_classification_macro_f1_secondary_22','n_tests':len(macro),'role':'secondary classification endpoint'})
    families.append({'family_id':'matched_order_prespecified_30','n_tests':len(mprim),'role':'formal controlled matched-order family'})
    families.append({'family_id':'matched_order_classification_macro_f1_secondary_5','n_tests':len(mmacro),'role':'secondary classification endpoint'})
    for t in GEN_TASKS:families.append({'family_id':f'generation_{t}_22','n_tests':len([r for r in gen if r['task_id']==t]),'role':'formal generation sensitivity family'})
    families.append({'family_id':'earlier_ablation_global_125_exploratory','n_tests':len(abl),'role':'earlier diagnostic experiment; separate from matched-order'})
    write_csv(out/'holm_family_audit.csv',families)
    status={
        'status':'COMPLETE',
        'policy':'METHODS_3_5_ALIGNMENT_20260915',
        'bootstrap_resamples':args.bootstrap,'signflip_resamples':args.signflips,'seed':args.seed,
        'counts':{
            'main_item_rows_total':len(mainrows),
            'main_primary_constrained_rows':sum(1 for r in mainrows if r.get('is_primary_model') is True and r['task_id'] in TASKS),
            'main_primary_formal_contrasts':len(prim),
            'classification_macro_f1_secondary_contrasts':len(macro),
            'matched_order_rows':len(matched),
            'matched_order_formal_contrasts':len(mprim),
            'matched_order_macro_f1_secondary_contrasts':len(mmacro),
            'generation_item_rows':len(read_csv(gen_score_path)),
            'generation_contrasts':len(gen),
            'earlier_ablation_rows':len(ablation),
            'earlier_ablation_contrasts':len(abl),
        },
        'main_primary_models':PRIMARY_MODELS,
        'notes':[
            'No model inference, scoring, CNHI recomputation, or gold edits are performed.',
            'Main classification accuracy uses exact McNemar; macro-F1 is separately recomputed in paired source-cluster bootstrap replicates.',
            'Main reasoning and QA accuracy use exact McNemar.',
            'Relationship micro-F1 uses a centered paired source-cluster bootstrap approximation with TP/FP/FN recomputed in each replicate.',
            'Structuring CNHI uses paired sign-flip inference with one sign per source cluster.',
            'Primary main Holm correction is task-specific: 22 shot-vs-zero contrasts per task.',
            'Matched-order repeats are averaged within item before inference; therefore aggregated binary endpoints are proportions and use sign-flip rather than McNemar. All 30 prespecified matched-order primary contrasts form one Holm family.',
            'Earlier 125 ablation contrasts remain a separate exploratory family and are not combined with the matched-order family.',
        ]
    }
    write_json(out/'RECALC_STATUS.json',status)
    print(json.dumps(status,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
