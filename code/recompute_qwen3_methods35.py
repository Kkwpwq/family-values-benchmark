#!/usr/bin/env python3
"""Methods-3.5-aligned recalculation and audit patch for ASLIB Results 4.3.

Scope
-----
1) Recalculate the 15 Qwen3 Thinking vs Non-Thinking constrained-task contrasts.
2) Rebuild the complete Qwen3 zero-shot profile, replacing the six stale generation
   cells with the latest GPT-5.5/Kimi K2.6 dual-LLM scores.
3) Audit and normalize repeated-sampling evidence: duplicate setting, semantic-pair
   coverage, final-delivery failures, and the actual 99-item diagnostic panel.

No model inference, LLM judging, gold editing, BERTScore rescoring, or CNHI
recalculation is performed. Existing Methods-V2 item scores are the scoring input.
"""
from __future__ import annotations

import argparse, csv, gzip, json, math, zlib
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

MODE_A='Qwen3-8B-Thinking'
MODE_B='Qwen3-8B-NonThinking'
TASKS=['classification','reasoning','structuring','relationship','qa_v4_5']
GEN_TASKS=['story_generation','rewriting','continuation']
ALL_TASKS=['classification','reasoning','structuring','relationship','qa_v4_5','story_generation','rewriting','continuation']
PRIMARY_ENDPOINT={
 'classification':'accuracy',
 'reasoning':'judgment_accuracy',
 'structuring':'cnhi_v2',
 'relationship':'micro_f1',
 'qa_v4_5':'recoverable_accuracy',
}
EXPECTED_ITEMS={'classification':100,'reasoning':100,'structuring':100,'relationship':50,'qa_v4_5':100}
ROBUST_EXPECTED_ITEMS={'classification':11,'reasoning':12,'structuring':15,'relationship':12,'qa_v4_5':15,'story_generation':11,'rewriting':12,'continuation':11}


def read_csv(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write_csv(p,rows):
    rows=list(rows); p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ['status']
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def read_gz(p):
    with gzip.open(p,'rt',encoding='utf-8-sig') as f:return [json.loads(x) for x in f if x.strip()]

def write_json(p,obj):
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def stable_seed(base,*parts):
    return (base+zlib.crc32('|'.join(map(str,parts)).encode()))%(2**32-1)

def holm(rows,p_col='p_raw',out_col='p_holm'):
    ix=[i for i,r in enumerate(rows) if r.get(p_col) not in (None,'') and np.isfinite(float(r[p_col]))]
    order=sorted(ix,key=lambda i:float(rows[i][p_col]));m=len(ix);run=0.0
    for rank,i in enumerate(order):
        cand=min(1.0,(m-rank)*float(rows[i][p_col]));run=max(run,cand)
        rows[i][out_col]=run;rows[i]['significant_holm_0_05']=run<0.05
    for r in rows:
        r['holm_family_size']=m
        if out_col not in r:r[out_col]=None;r['significant_holm_0_05']=None
    return rows

def exact_mcnemar(a,b):
    a=np.asarray(a,int);b=np.asarray(b,int)
    ao=int(np.sum((a==1)&(b==0)));bo=int(np.sum((a==0)&(b==1)));n=ao+bo
    if n==0:p=1.0
    else:
        k=min(ao,bo); lower=sum(math.comb(n,i) for i in range(k+1))/(2**n);p=min(1.0,2*lower)
    return ao,bo,n,p

def micro_f1(v):
    tp,fp,fn=v[...,0],v[...,1],v[...,2];den=2*tp+fp+fn
    return np.divide(2*tp,den,out=np.zeros_like(tp,dtype=float),where=den>0)

def mean_stat(v):
    return np.divide(v[...,0],v[...,1],out=np.zeros_like(v[...,0],dtype=float),where=v[...,1]>0)

def sufficient(r,metric):
    if metric in ('accuracy','judgment_accuracy','recoverable_accuracy'):
        return np.array([float(r['accuracy']),1.0])
    if metric=='cnhi_v2': return np.array([float(r['cnhi_v2']),1.0])
    if metric=='micro_f1': return np.array([float(r['tp']),float(r['fp']),float(r['fn'])])
    raise KeyError(metric)

def stat(metric): return micro_f1 if metric=='micro_f1' else mean_stat

def item_matrix(rows,metric):
    g=defaultdict(list)
    for r in rows:g[r['item_id']].append(r)
    ids=sorted(g);vals=[];clusters=[]
    for iid in ids:
        rr=g[iid]
        if len(rr)!=1:raise ValueError(f'mode item {iid} has {len(rr)} rows')
        cs={str(x['source_cluster']) for x in rr}
        if len(cs)!=1:raise ValueError(f'cluster mismatch {iid}')
        vals.append(sufficient(rr[0],metric));clusters.append(next(iter(cs)))
    return ids,np.stack(vals),clusters

def aggregate_cluster(x,clusters):
    units=sorted(set(clusters));idx={u:i for i,u in enumerate(units)};out=np.zeros((len(units),x.shape[1]))
    for i,c in enumerate(clusters):out[idx[c]]+=x[i]
    return units,out

def paired_boot(a,b,metric,B,seed):
    ai,ax,ac=item_matrix(a,metric);bi,bx,bc=item_matrix(b,metric)
    if ai!=bi or ac!=bc:raise ValueError('paired item/source sets differ')
    units,aa=aggregate_cluster(ax,ac);ub,bb=aggregate_cluster(bx,bc)
    if units!=ub:raise ValueError('paired clusters differ')
    fn=stat(metric);ma=float(fn(aa.sum(0)));mb=float(fn(bb.sum(0)));obs=ma-mb
    rng=np.random.default_rng(seed);counts=rng.multinomial(len(units),np.full(len(units),1/len(units)),size=B)
    boots=fn(counts@aa)-fn(counts@bb);lo,hi=np.quantile(boots,[.025,.975])
    return {'items':ai,'clusters':ac,'a_cluster':aa,'b_cluster':bb,'mean_a':ma,'mean_b':mb,'effect':obs,'boots':boots,'lo':float(lo),'hi':float(hi),'n_items':len(ai),'n_clusters':len(units)}

def centered_boot_p(info):
    obs=info['effect'];null=info['boots']-obs
    return (1+int(np.sum(np.abs(null)>=abs(obs)-1e-15)))/(len(null)+1)

def signflip_p(info,S,seed):
    aa,bb=info['a_cluster'],info['b_cluster'];diff=aa[:,0]-bb[:,0];den=float(aa[:,1].sum())
    rng=np.random.default_rng(seed);signs=rng.choice(np.array([-1.0,1.0]),size=(S,len(diff)));null=(signs@diff)/den
    return (1+int(np.sum(np.abs(null)>=abs(info['effect'])-1e-15)))/(S+1)

def bootstrap_mean_cluster(values,clusters,B,seed):
    units=sorted(set(clusters));idx={u:i for i,u in enumerate(units)};s=np.zeros(len(units));n=np.zeros(len(units))
    for v,c in zip(values,clusters):s[idx[c]]+=float(v);n[idx[c]]+=1
    obs=s.sum()/n.sum();rng=np.random.default_rng(seed);counts=rng.multinomial(len(units),np.full(len(units),1/len(units)),size=B)
    bs=(counts@s)/(counts@n);lo,hi=np.quantile(bs,[.025,.975]);return obs,float(lo),float(hi),len(units)

def recalc_mode(main,outdir,B,S,seed):
    g=defaultdict(list)
    for r in main:
        if r['model_id'] in (MODE_A,MODE_B) and r['task_id'] in TASKS and r.get('shot') in (0,1,3):g[(r['model_id'],r['task_id'],int(r['shot']))].append(r)
    out=[]
    for task in TASKS:
        metric=PRIMARY_ENDPOINT[task]
        for shot in (0,1,3):
            a=g[(MODE_A,task,shot)];b=g[(MODE_B,task,shot)]
            if len(a)!=EXPECTED_ITEMS[task] or len(b)!=EXPECTED_ITEMS[task]:raise ValueError((task,shot,len(a),len(b)))
            info=paired_boot(a,b,metric,B,stable_seed(seed,'mode43',task,shot,metric))
            ao=bo=disc=None
            if task in ('classification','reasoning','qa_v4_5'):
                aa=np.array([int(round(float(r['accuracy']))) for r in sorted(a,key=lambda x:x['item_id'])]);bb=np.array([int(round(float(r['accuracy']))) for r in sorted(b,key=lambda x:x['item_id'])])
                ao,bo,disc,p=exact_mcnemar(aa,bb);test='two-sided exact McNemar on paired item correctness'
            elif task=='relationship':
                p=centered_boot_p(info);test='two-sided centered paired source-cluster bootstrap approximation; micro-F1 recomputed from TP/FP/FN in each replicate'
            else:
                p=signflip_p(info,S,stable_seed(seed,'mode43-sign',task,shot));test='two-sided paired sign-flip; one sign per source cluster'
            out.append({'task_id':task,'shot':shot,'contrast':'Thinking - NonThinking','metric':metric,'n_items':info['n_items'],'n_clusters':info['n_clusters'],'thinking_mean_100':100*info['mean_a'],'nonthinking_mean_100':100*info['mean_b'],'difference_thinking_minus_nonthinking_100':100*info['effect'],'ci95_low_100':100*info['lo'],'ci95_high_100':100*info['hi'],'p_raw':p,'test':test,'ci_method':f'paired percentile source-cluster bootstrap; {B} resamples','thinking_correct_nonthinking_wrong':ao,'thinking_wrong_nonthinking_correct':bo,'discordant_pairs':disc,'bootstrap_resamples':B,'signflip_resamples':S if task=='structuring' else None,'analysis_role':'PRESPECIFIED_WITHIN_MODEL_CONFIGURATION_CONTRAST','interpretation_limit':'configuration comparison; sampling settings and token budgets also differ, so this is not isolated mode causality'})
    if len(out)!=15:raise ValueError(len(out))
    holm(out)
    for r in out:r['holm_family_id']='qwen3_within_model_constrained_15'
    write_csv(outdir/'qwen3_mode_contrasts_methods35.csv',out)
    return out

def build_source_map(main):
    d={}
    for r in main:
        k=(r['task_id'],r['item_id']);c=str(r['source_cluster'])
        if k in d and d[k]!=c:raise ValueError(f'source cluster mismatch {k}: {d[k]} vs {c}')
        d[k]=c
    return d

def rebuild_profile(main,paired,outdir,B,seed):
    profile=[];src=build_source_map(main)
    # constrained from Methods-V2 item-level scores
    g=defaultdict(list)
    for r in main:
        if r['model_id'] in (MODE_A,MODE_B) and r['task_id'] in TASKS and r.get('shot')==0:g[(r['model_id'],r['task_id'])].append(r)
    for model in (MODE_B,MODE_A):
        for task in TASKS:
            rr=g[(model,task)];metric=PRIMARY_ENDPOINT[task]
            ids,x,c=item_matrix(rr,metric);units,agg=aggregate_cluster(x,c);fn=stat(metric);obs=float(fn(agg.sum(0)))
            rng=np.random.default_rng(stable_seed(seed,'profile',model,task));counts=rng.multinomial(len(units),np.full(len(units),1/len(units)),size=B);bs=fn(counts@agg);lo,hi=np.quantile(bs,[.025,.975])
            profile.append({'model_id':model,'task_id':task,'score_100':100*obs,'ci95_low_100':100*float(lo),'ci95_high_100':100*float(hi),'n_items':len(ids),'n_clusters':len(units),'score_source':'Methods-V2 constrained item scores','primary_judge':'DETERMINISTIC_OR_METHODS_V2','analysis_role':'QWEN3_ZERO_SHOT_PROFILE'})
    # generation latest dual judge
    pg=[r for r in paired if r['model_id'] in (MODE_A,MODE_B) and r['task_id'] in GEN_TASKS and int(r['shot'])==0]
    for model in (MODE_B,MODE_A):
        for task in GEN_TASKS:
            rr=sorted([r for r in pg if r['model_id']==model and r['task_id']==task],key=lambda x:x['item_id'])
            if len(rr)!=100:raise ValueError((model,task,len(rr)))
            vals=[float(r['dual_total']) for r in rr];clusters=[src[(task,r['item_id'])] for r in rr]
            obs,lo,hi,nc=bootstrap_mean_cluster(vals,clusters,B,stable_seed(seed,'profile-gen',model,task))
            profile.append({'model_id':model,'task_id':task,'score_100':obs,'ci95_low_100':lo,'ci95_high_100':hi,'n_items':100,'n_clusters':nc,'score_source':'latest GPT-5.5 + Kimi K2.6 dual-LLM item scores','primary_judge':'GPT-5.5_KIMI-K2.6_MEAN','analysis_role':'QWEN3_ZERO_SHOT_PROFILE'})
    order={t:i for i,t in enumerate(ALL_TASKS)};profile.sort(key=lambda r:(0 if r['model_id']==MODE_B else 1,order[r['task_id']]))
    write_csv(outdir/'qwen3_zero_shot_profile_latest.csv',profile)
    # generation config differences: descriptive only, no significance family is defined in current Methods.
    desc=[]
    for task in GEN_TASKS:
        a=sorted([r for r in pg if r['model_id']==MODE_A and r['task_id']==task],key=lambda x:x['item_id']);b=sorted([r for r in pg if r['model_id']==MODE_B and r['task_id']==task],key=lambda x:x['item_id'])
        if [r['item_id'] for r in a]!=[r['item_id'] for r in b]:raise ValueError('gen mode item mismatch')
        # cluster bootstrap paired mean difference
        by=defaultdict(list)
        for ra,rb in zip(a,b):by[src[(task,ra['item_id'])]].append(float(ra['dual_total'])-float(rb['dual_total']))
        units=sorted(by);s=np.array([sum(by[u]) for u in units]);n=np.array([len(by[u]) for u in units]);obs=s.sum()/n.sum();rng=np.random.default_rng(stable_seed(seed,'gen-mode-desc',task));counts=rng.multinomial(len(units),np.full(len(units),1/len(units)),size=B);bs=(counts@s)/(counts@n);lo,hi=np.quantile(bs,[.025,.975])
        desc.append({'task_id':task,'thinking_mean_100':sum(float(r['dual_total']) for r in a)/100,'nonthinking_mean_100':sum(float(r['dual_total']) for r in b)/100,'difference_100':obs,'ci95_low_100':float(lo),'ci95_high_100':float(hi),'n_items':100,'n_clusters':len(units),'analysis_role':'DESCRIPTIVE_CONFIGURATION_PROFILE_ONLY','p_value':'','note':'No formal p-value: current Methods define the separate 15-test Qwen3 Holm family for five constrained tasks x three prompting conditions.'})
    write_csv(outdir/'qwen3_generation_zero_shot_descriptive_latest.csv',desc)
    return profile,desc

def audit_robustness(robust,old_summary,outdir):
    models=sorted({r['model_id'] for r in robust});settings=sorted({r['setting_id'] for r in robust});tasks=sorted({r['task_id'] for r in robust})
    if len(robust)!=7425:raise ValueError(len(robust))
    if set(settings)!={'BASE_R5','T02_R5','T07_R5'}:raise ValueError(settings)
    # actual panel; assert same item sets across every model/setting
    panel=[];counts=[]
    baseline_items={}
    for task in tasks:
        sets=[]
        for m in models:
            for s in settings:sets.append({r['item_id'] for r in robust if r['model_id']==m and r['setting_id']==s and r['task_id']==task})
        if not all(x==sets[0] for x in sets):raise ValueError(f'panel item-set mismatch {task}')
        items=sorted(sets[0]);
        if len(items)!=ROBUST_EXPECTED_ITEMS[task]:raise ValueError((task,len(items)))
        baseline_items[task]=items
        for iid in items:
            rr=[r for r in robust if r['task_id']==task and r['item_id']==iid]
            cls={str(r['source_cluster']) for r in rr}
            if len(cls)!=1:raise ValueError((task,iid,cls))
            panel.append({'task_id':task,'item_id':iid,'source_cluster':next(iter(cls)),'models':len(models),'settings':len(settings),'repeats_per_model_setting':5,'expected_total_output_rows':len(models)*len(settings)*5,'actual_total_output_rows':len(rr)})
        counts.append({'task_id':task,'n_diagnostic_items':len(items),'n_source_clusters':len({r['source_cluster'] for r in robust if r['task_id']==task}),'models':len(models),'registered_settings':len(settings),'repeats_per_item_setting':5,'expected_output_rows':len(items)*len(models)*len(settings)*5,'actual_output_rows':sum(1 for r in robust if r['task_id']==task)})
    write_csv(outdir/'robustness_panel_items_99.csv',panel);write_csv(outdir/'robustness_panel_counts.csv',counts)
    if len(panel)!=99:raise ValueError(f'panel total {len(panel)}')
    # duplicate audit BASE vs T07 for Qwen3 NT
    dup=[];m=MODE_B
    for task in tasks:
        a=sorted([r for r in robust if r['model_id']==m and r['setting_id']=='BASE_R5' and r['task_id']==task],key=lambda r:(r['item_id'],int(r['repeat_index'])))
        b=sorted([r for r in robust if r['model_id']==m and r['setting_id']=='T07_R5' and r['task_id']==task],key=lambda r:(r['item_id'],int(r['repeat_index'])))
        keys_a=[(r['item_id'],int(r['repeat_index'])) for r in a];keys_b=[(r['item_id'],int(r['repeat_index'])) for r in b]
        if keys_a!=keys_b:raise ValueError('duplicate pair key mismatch')
        eh=sum(ra['raw_output_sha256']==rb['raw_output_sha256'] for ra,rb in zip(a,b));es=sum(str(ra.get('generation_seed'))==str(rb.get('generation_seed')) for ra,rb in zip(a,b))
        dup.append({'model_id':m,'task_id':task,'base_setting':'BASE_R5','duplicate_setting':'T07_R5','paired_outputs':len(a),'identical_raw_output_sha256':eh,'identical_generation_seed':es,'exact_output_duplicate':eh==len(a),'independent_evidence':False,'note':'T=0.7 is the default sampling profile for Qwen3-8B Non-Thinking; T07_R5 duplicates BASE_R5 and is not an independent condition.'})
    write_csv(outdir/'robustness_duplicate_setting_audit.csv',dup)
    if sum(int(r['paired_outputs']) for r in dup)!=495 or sum(int(r['identical_raw_output_sha256']) for r in dup)!=495:raise ValueError('Qwen3 NT duplicate audit != 495/495')
    # final delivery failures
    fail=[]
    for r in robust:
        if r.get('final_delivered') is False:
            fail.append({k:r.get(k) for k in ['model_id','setting_id','task_id','item_id','source_cluster','repeat_index','generation_seed','execution_status','budget_cap_flag','final_channel_status','final_delivered','raw_output_sha256']})
    fail.sort(key=lambda r:(r['model_id'],r['setting_id'],r['task_id'],r['item_id'],int(r['repeat_index'])))
    write_csv(outdir/'robustness_final_delivery_failures_10.csv',fail)
    if len(fail)!=10:raise ValueError(f'failures {len(fail)}')
    fc=Counter((r['model_id'],r['setting_id'],r['task_id']) for r in fail)
    expected={(MODE_A,'T02_R5','classification'):1,(MODE_A,'T02_R5','qa_v4_5'):7,(MODE_A,'T02_R5','relationship'):2}
    if dict(fc)!=expected:raise ValueError((fc,expected))
    # cleaned 120 summary and semantic coverage
    raw_fail_count=Counter((r['model_id'],r['setting_id'],r['task_id']) for r in robust if r.get('final_delivered') is False)
    clean=[];coverage=[];gaps=[]
    for r0 in old_summary:
        r=dict(r0);m=r['model_id'];s=r['setting'];task=r['task_id'];valid=int(r.get('semantic_valid_pair_n') or 0);total=int(r.get('semantic_total_pair_n') or 0);missing=total-valid
        r['setting_label']={'BASE_R5':'Default','T02_R5':'T=0.2','T07_R5':'T=0.7'}[s]
        r['is_independent_setting_evidence']=not (m==MODE_B and s=='T07_R5')
        r['duplicate_of_setting']='BASE_R5' if (m==MODE_B and s=='T07_R5') else ''
        r['duplicate_counterpart']='T07_R5' if (m==MODE_B and s=='BASE_R5') else ''
        r['semantic_pair_missing_n']=missing
        r['semantic_pair_coverage_rate']=(valid/total if total else '')
        r['semantic_pair_status']='PARTIAL' if total and missing else ('COMPLETE' if total else 'NOT_APPLICABLE')
        r['delivery_failure_outputs']=raw_fail_count[(m,s,task)]
        r['delivery_status']='FAILED_DELIVERY_RETAINED' if raw_fail_count[(m,s,task)] else 'COMPLETE_DELIVERY'
        clean.append(r)
        if task in ('story_generation','rewriting','continuation','structuring') and total:
            cr={'model_id':m,'setting':s,'setting_label':r['setting_label'],'task_id':task,'valid_pairs':valid,'total_pairs':total,'missing_pairs':missing,'coverage_rate':valid/total,'mean_pairwise_BERTScore':r.get('mean_pairwise_BERTScore',''),'is_independent_setting_evidence':r['is_independent_setting_evidence'],'duplicate_of_setting':r['duplicate_of_setting']}
            coverage.append(cr)
            if missing:gaps.append(cr)
    write_csv(outdir/'robustness_task_setting_summary_methods35_43.csv',clean);write_csv(outdir/'robustness_semantic_pair_coverage.csv',coverage);write_csv(outdir/'robustness_semantic_pair_gaps.csv',gaps)
    gen_missing=sum(int(r['missing_pairs']) for r in gaps if r['task_id'] in GEN_TASKS);struct_missing=sum(int(r['missing_pairs']) for r in gaps if r['task_id']=='structuring')
    if gen_missing!=26 or struct_missing!=8:raise ValueError((gen_missing,struct_missing))
    return {'models':models,'settings':settings,'panel_rows':len(panel),'failures':len(fail),'generation_semantic_missing_pairs':gen_missing,'structuring_semantic_missing_pairs':struct_missing,'duplicate_outputs_qwen3_nt_base_vs_t07':495}

def legacy_audit(new,legacy,outdir):
    old={(r['task_id'],int(r['shot'])):r for r in legacy};rows=[]
    for n in new:
        o=old[(n['task_id'],int(n['shot']))]
        rows.append({'task_id':n['task_id'],'shot':n['shot'],'effect_new_100':n['difference_thinking_minus_nonthinking_100'],'effect_old_100':o['difference_100'],'effect_delta':float(n['difference_thinking_minus_nonthinking_100'])-float(o['difference_100']),'ci_low_new_100':n['ci95_low_100'],'ci_low_old_100':o['ci95_low_100'],'ci_high_new_100':n['ci95_high_100'],'ci_high_old_100':o['ci95_high_100'],'p_raw_new':n['p_raw'],'p_raw_old':o['p_cluster_swap'],'p_holm_new':n['p_holm'],'p_holm_old':o['p_holm'],'test_new':n['test'],'test_old':'paired/source-cluster swap as archived','note':'Effect estimates are preserved; inferential p-values are recalculated to match current Methods 3.5.'})
    write_csv(outdir/'legacy_mode_comparison_audit.csv',rows);return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',type=Path,default=None,help='Optional extracted formal-records root. If omitted, packaged inputs/ are used.')
    ap.add_argument('--out',type=Path,default=None,help='Output dir (default: <repo>/results/qwen3_recomputed)')
    ap.add_argument('--package-root',default=str(Path(__file__).resolve().parents[1]),help=argparse.SUPPRESS)
    ap.add_argument('--bootstrap',type=int,default=10000)
    ap.add_argument('--signflips',type=int,default=10000)
    ap.add_argument('--seed',type=int,default=20260915)
    args=ap.parse_args()
    root=Path(args.package_root)
    data=Path(args.data_dir) if args.data_dir else None
    if data is None:
        scored=root/'inputs'
    else:
        scored=(data/'scored_records') if (data/'scored_records').is_dir() else data
    if not scored.is_dir():
        raise SystemExit(f'missing scored input directory: {scored}')
    out=args.out or (root/'results'/'qwen3_recomputed')
    out.mkdir(parents=True, exist_ok=True)

    ref_candidates=[]
    if data is not None:
        ref_candidates.append(data/'reference_legacy')
    ref_candidates.append(root/'reference_legacy')
    ref=next((r for r in ref_candidates if r.is_dir()),None)
    if ref is None:
        raise SystemExit('missing reference_legacy/ directory')

    mainrows=read_gz(scored/'main_scored_items_methods_v2.jsonl.gz')
    robust=read_gz(scored/'robustness_scored_items_methods_v2.jsonl.gz')

    paired_candidates=[root/'results'/'dual_judge'/'paired_main_3600_latest.csv',scored/'paired_main_3600_latest.csv',root/'inputs'/'paired_main_3600_latest.csv']
    paired_path=next((p for p in paired_candidates if p.is_file()),None)
    if paired_path is None:
        raise SystemExit('missing paired_main_3600_latest.csv')
    paired=read_csv(paired_path)

    oldsum_candidates=[scored/'robustness_120_task_setting_results_methods_v2.csv',root/'inputs'/'robustness_120_task_setting_results_methods_v2.csv']
    if data is not None:
        oldsum_candidates.insert(1,data/'robustness_120_task_setting_results_methods_v2.csv')
    oldsum_path=next((p for p in oldsum_candidates if p.is_file()),None)
    if oldsum_path is None:
        raise SystemExit('missing robustness_120_task_setting_results_methods_v2.csv')
    oldsum=read_csv(oldsum_path)

    legacy_path=ref/'mode_paired_contrasts_methods_v2.csv'
    if not legacy_path.is_file():
        raise SystemExit(f'missing {legacy_path}')
    legacy=read_csv(legacy_path)

    if len(mainrows)!=19800:raise ValueError(f'main rows {len(mainrows)}')
    if len(paired)!=3600:raise ValueError(f'paired main {len(paired)}')
    if len(robust)!=7425:raise ValueError(f'robustness rows {len(robust)}')
    if len(oldsum)!=120:raise ValueError(f'robustness summary rows {len(oldsum)}')
    if len(legacy)!=15:raise ValueError(f'legacy mode rows {len(legacy)}')

    mode=recalc_mode(mainrows,out,args.bootstrap,args.signflips,args.seed)
    profile,gdesc=rebuild_profile(mainrows,paired,out,args.bootstrap,args.seed)
    rob=audit_robustness(robust,oldsum,out)
    legacy_audit(mode,legacy,out)
    write_csv(out/'holm_family_audit.csv',[{'family_id':'qwen3_within_model_constrained_15','n_tests':15,'scope':'Qwen3 Thinking vs Non-Thinking across five constrained tasks and three prompting conditions','correction':'Holm','analysis_role':'PRESPECIFIED_WITHIN_MODEL_CONFIGURATION_FAMILY'}])
    status={'status':'COMPLETE','policy_id':'METHODS_3_5_ALIGNMENT_4_3_20260915','bootstrap_resamples':args.bootstrap,'signflip_resamples':args.signflips,'seed':args.seed,'qwen3_mode_contrasts':len(mode),'qwen3_mode_holm_family_size':15,'qwen3_zero_shot_profile_rows':len(profile),'qwen3_generation_profile_rows_latest':6,'qwen3_generation_descriptive_contrasts':len(gdesc),'robustness_scored_rows':len(robust),'robustness_task_setting_rows':len(oldsum),'robustness_panel_items':rob['panel_rows'],'robustness_final_delivery_failures':rob['failures'],'qwen3_nonthinking_base_t07_identical_outputs':rob['duplicate_outputs_qwen3_nt_base_vs_t07'],'generation_semantic_missing_pairs':rob['generation_semantic_missing_pairs'],'structuring_semantic_missing_pairs':rob['structuring_semantic_missing_pairs'],'notes':['No model inference or LLM judging was rerun.','No CNHI or BERTScore values were recomputed; current Methods-V2 item scores and archived semantic-pair results are reused.','The 15 constrained Qwen3 configuration contrasts are recalculated with Methods-3.5-consistent tests and one Holm family.','The six Qwen3 generation profile cells are replaced with the latest GPT-5.5/Kimi K2.6 dual-LLM means.','Qwen3-8B Non-Thinking T07_R5 is marked as duplicate of BASE_R5 and not independent evidence.','Ten Qwen3 Thinking T02_R5 records are retained as final-delivery failures, not missing observations.']}
    write_json(out/'RECALC_STATUS.json',status)
    print(json.dumps(status,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
