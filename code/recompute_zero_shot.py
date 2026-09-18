"""Recompute Section 4.1 summaries from stored item scores and the public paired dual-judge table.
No model inference, parser change, gold edit, or LLM judging is performed.

Run:
    python code/recompute_zero_shot.py --data-dir <extracted-formal-records> --out <output-dir>

Dependencies: Python 3.10+, NumPy, SciPy, threadpoolctl.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, itertools, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
from threadpoolctl import threadpool_limits

MODELS=['Baichuan2-7B-Chat','chatglm3-6b','deepseek-llm-7b-chat',
 'DeepSeek-R1-Distill-Qwen-32B','glm-4-9b-chat','internlm2_5-7b-chat',
 'Mistral-7B-Instruct-v0.3','Qwen2.5-7B-Instruct','Qwen3-8B-NonThinking','QwQ-32B','Doubao']
PRIMARY={'classification':'macro_f1','qa_v4_5':'recoverable_accuracy',
 'reasoning':'judgment_accuracy','relationship':'micro_f1','structuring':'cnhi',
 'story_generation':'dual_judge_score','rewriting':'dual_judge_score','continuation':'dual_judge_score'}
WEIGHTS={'story_generation':{'family_value':.4,'plot_logic':.25,'characterization':.2,'emotion':.15},
 'rewriting':{'content_fidelity':.2,'style_fit':.5,'clarity':.2,'value_expression':.1},
 'continuation':{'family_value':.3,'context_fit':.15,'coherence':.35,'clarity':.2}}
LABELS=list('忠孝悌节养恕勇俭让慎省')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def writecsv(path, rows):
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        fields=list(dict.fromkeys(k for r in rows for k in r))
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def writejson(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def calculate(task, rs, w):
    def mean(k):
        v=np.array([r[k] for r in rs], float)
        if not np.isfinite(v).all(): raise ValueError(f'Missing {task}/{k}')
        return w@v/w.sum(1)
    result={}
    if task not in WEIGHTS:
        result.update(strict_format=mean('strict_format_v2' if task=='structuring' else 'strict_format'),
                      answer_recovery=mean('recoverable_parse_v2' if task=='structuring' else 'recoverable_parse'))
    if task=='classification':
        result['accuracy']=mean('accuracy'); mf=np.zeros(w.shape[0])
        gold=np.array([r['gold_label'] for r in rs]); pred=np.array([r.get('parsed_label') or '__INVALID__' for r in rs])
        for label in LABELS:
            num=2*(w@((gold==label)&(pred==label)).astype(float))
            den=w@((gold==label).astype(float)+(pred==label).astype(float))
            mf+=np.divide(num,den,out=np.zeros_like(num),where=den>0)/11
        result['macro_f1']=mf
    elif task=='qa_v4_5':
        result['recoverable_accuracy']=mean('accuracy'); result['strict_accuracy']=mean('strict_accuracy')
    elif task=='reasoning':
        result['judgment_accuracy']=mean('accuracy'); result['evidence_source_match']=mean('evidence_source_substring')
        result['evidence_bertscore']=mean('evidence_alignment_bertscore')
    elif task=='relationship':
        tp,fp,fn=(w@np.array([r[k] for r in rs],float) for k in ['tp','fp','fn'])
        for k,num,den in [('micro_f1',2*tp,2*tp+fp+fn),('micro_precision',tp,tp+fp),('micro_recall',tp,tp+fn)]:
            result[k]=np.divide(num,den,out=np.zeros_like(num),where=den>0)
        result['exact_set_match']=mean('exact_set_match')
    elif task=='structuring':
        result.update(cnhi=mean('cnhi_v2'),sc=mean('sc_v2'),sa=mean('sa_v2'),field_completeness=mean('field_completeness_v2'))
    else:
        result.update(dual_judge_score=mean('dual_judge_score')/100,gpt_score=mean('gpt_score')/100,kimi_score=mean('kimi_score')/100)
        for dim in WEIGHTS[task]: result['dual_dimension_'+dim]=mean('dual_dimension_'+dim)/100
    return result

def load_paired_scores(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        pairs=list(csv.DictReader(f))
    if len(pairs)!=3600: raise ValueError(f'paired rows: {len(pairs)}')
    joined={}
    for r in pairs:
        task=r['task_id']
        if task not in WEIGHTS: raise ValueError(task)
        if int(r['shot'])!=0: raise ValueError('paired main table must be zero-shot')
        gt=float(r['gpt_total']); kt=float(r['kimi_total']); dt=float(r['dual_total'])
        if abs((gt+kt)/2-dt)>1e-7: raise ValueError('dual total mismatch')
        dims={}
        for d,wgt in WEIGHTS[task].items():
            gv=float(r['gpt_'+d]); kv=float(r['kimi_'+d])
            dims['dual_dimension_'+d]=(gv+kv)/2
        for prefix,total in [('gpt_',gt),('kimi_',kt)]:
            calc=sum(wgt*float(r[prefix+d]) for d,wgt in WEIGHTS[task].items())
            if abs(calc-total)>1e-7: raise ValueError(f'weighted-total mismatch: {r["model_id"]}/{task}/{r["item_id"]}')
        key=(r['model_id'],task,r['item_id'])
        if key in joined: raise ValueError(f'duplicate paired key: {key}')
        joined[key]={'gpt_score':gt,'kimi_score':kt,'dual_judge_score':dt,**dims}
    return joined

def main(args):
    data=args.data_dir; out=args.out; out.mkdir(parents=True,exist_ok=True)
    package_root=Path(__file__).resolve().parents[1]
    item_path=data/'scored_records'/'main_scored_items_methods_v2.jsonl.gz'
    pair_path=package_root/'results'/'dual_judge'/'paired_main_3600_latest.csv'
    with gzip.open(item_path,'rt',encoding='utf-8-sig') as f:
        rows=[json.loads(x) for x in f if x.strip()]
    paired=load_paired_scores(pair_path)
    primary=[dict(r) for r in rows if r.get('shot')==0 and r['model_id'] in MODELS]
    assert len(primary)==8250
    assert len({(r['model_id'],r['task_id'],r['item_id']) for r in primary})==8250
    judgepairs=[]
    for r in primary:
        if r['task_id'] in WEIGHTS: r.update(paired[(r['model_id'],r['task_id'],r['item_id'])])
        if r['task_id']=='structuring':
            sc,sa,val=(r[k] for k in ['sc_v2','sa_v2','cnhi_v2'])
            assert sc in [0.,1.] and np.isfinite(val)
            assert abs(sa-np.mean([r['field_bertscore_v2_'+f] for f in ['前提条件','行为规范','主题类别']]))<1e-10
            assert abs(val-(2*sc*sa/(sc+sa) if sc+sa else 0))<1e-10
        if r['task_id'] in WEIGHTS:
            judgepairs.append({k:r[k] for k in ['model_id','task_id','item_id','source_cluster','gpt_score','kimi_score','dual_judge_score']})
    summaries=[]; comparisons=[]
    for ti,(task,metric) in enumerate(PRIMARY.items()):
        group={m:sorted([r for r in primary if r['model_id']==m and r['task_id']==task],key=lambda r:r['item_id']) for m in MODELS}
        first=group[MODELS[0]]; ids=[r['item_id'] for r in first]; clusters=[str(r['source_cluster']) for r in first]
        assert len(ids)==(50 if task=='relationship' else 100)
        for m,rs in group.items():
            assert [r['item_id'] for r in rs]==ids
            assert [str(r['source_cluster']) for r in rs]==clusters
        units=sorted(set(clusters)); uid={u:i for i,u in enumerate(units)}; where=np.array([uid[c] for c in clusters])
        rng=np.random.default_rng(args.seed+ti*1000)
        counts=rng.multinomial(len(units),np.full(len(units),1/len(units)),size=args.bootstrap)
        w=np.vstack([np.ones(len(ids)),counts[:,where]]).astype(float)
        results={m:calculate(task,group[m],w) for m in MODELS}
        for m,metrics in results.items():
            for met,v in metrics.items():
                lo,hi=np.quantile(v[1:],[.025,.975])
                summaries.append({'model_id':m,'task_id':task,'metric':met,'n_items':len(ids),'n_clusters':len(units),
                    'estimate_100':float(v[0]*100),'ci95_low_100':float(lo*100),'ci95_high_100':float(hi*100),
                    'bootstrap_resamples':args.bootstrap,'bootstrap_seed':args.seed+ti*1000,
                    'source':'paired_dual_judge_scores' if task in WEIGHTS else 'stored_item_scores'})
        fam=[]; sign=None
        if task in WEIGHTS or task=='structuring': sign=rng.choice([-1.,1.],size=(args.signflips,len(units)))
        for ma,mb in itertools.combinations(MODELS,2):
            dv=results[ma][metric]-results[mb][metric]; delta=float(dv[0]); lo,hi=np.quantile(dv[1:],[.025,.975])
            ab=ba=None
            if task in ['reasoning','qa_v4_5']:
                av=np.array([r['accuracy'] for r in group[ma]]); bv=np.array([r['accuracy'] for r in group[mb]])
                ab=int(np.sum((av==1)&(bv==0))); ba=int(np.sum((av==0)&(bv==1)))
                p=1. if not ab+ba else float(binomtest(ab,ab+ba,.5).pvalue)
                test='two-sided exact McNemar on paired item correctness'
            elif task in ['classification','relationship']:
                p=(1+int(np.sum(np.abs(dv[1:]-delta)>=abs(delta)-1e-12)))/(args.bootstrap+1)
                test='two-sided centered paired source-cluster bootstrap approximation'
            else:
                key='cnhi_v2' if task=='structuring' else 'dual_judge_score'; scale=1. if task=='structuring' else 100.
                diff=np.array([(a[key]-b[key])/scale for a,b in zip(group[ma],group[mb])])
                cluster_diffs=np.bincount(where,weights=diff,minlength=len(units))
                null=sign@cluster_diffs/len(ids)
                p=(1+int(np.sum(np.abs(null)>=abs(delta)-1e-12)))/(args.signflips+1)
                test='two-sided paired sign-flip; one sign per source cluster'
            fam.append({'task_id':task,'metric':metric,'model_a':ma,'model_b':mb,
              'n_items':len(ids),'n_clusters':len(units),'estimate_a_minus_b_100':delta*100,
              'ci95_low_100':float(lo*100),'ci95_high_100':float(hi*100),'p_raw':p,
              'p_holm':None,'family_id':'primary_11_zero_shot_'+task,'family_size':55,'test':test,
              'a_correct_b_wrong':ab,'a_wrong_b_correct':ba,'bootstrap_resamples':args.bootstrap,
              'signflip_resamples':args.signflips if sign is not None else None})
        order=sorted(range(len(fam)),key=lambda i:fam[i]['p_raw']); last=0
        for pos,i in enumerate(order):
            last=max(last,min(1.,(len(fam)-pos)*fam[i]['p_raw'])); fam[i]['p_holm']=last
            fam[i]['significant_holm_0_05']=last<.05
        comparisons+=fam
    writecsv(out/'zero_shot_summary_ci_latest.csv',summaries)
    writecsv(out/'zero_shot_pairwise_latest.csv',comparisons)
    writecsv(out/'generation_dual_judge_item_scores_latest.csv',judgepairs)
    with gzip.open(out/'primary_item_scores_used.jsonl.gz','wt',encoding='utf-8') as f:
        for r in primary: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    provenance={'status':'RECOMPUTED_FROM_PUBLIC_MINIMAL_RECORDS',
      'inputs':[{'filename':item_path.name,'sha256':sha(item_path)},{'filename':pair_path.name,'sha256':sha(pair_path)}],
      'models':MODELS,'n_primary_output_records':len(primary),'paired_main_judge_records_all_configurations':len(paired),
      'paired_main_judge_records_primary':len(judgepairs),'all_dimension_weights_validated':True,
      'all_primary_CNHI_formulas_validated':True,'no_parser_change':True,'no_gold_change':True,'no_model_inference':True,'no_llm_judging':True,
      'primary_hypothesis_endpoints':PRIMARY,'family_size_per_task':55,
      'bootstrap':args.bootstrap,'signflip_resamples':args.signflips,'seed':args.seed,
      'score_units':'All exported estimates are on a 0-100 scale. F1 and CNHI may be divided by 100 for 0-1 presentation.'}
    writejson(out/'provenance.json',provenance)
    print(json.dumps({'summaries':len(summaries),'comparisons':len(comparisons),'significant_by_task':{t:sum(r['significant_holm_0_05'] for r in comparisons if r['task_id']==t) for t in PRIMARY}},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--bootstrap',type=int,default=10000); ap.add_argument('--signflips',type=int,default=100000)
    ap.add_argument('--seed',type=int,default=20260914); args=ap.parse_args()
    with threadpool_limits(limits=1): main(args)
