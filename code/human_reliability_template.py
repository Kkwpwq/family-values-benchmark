#!/usr/bin/env python3
"""Generic two-rater reliability analysis used for human-validation replication.
Raw human ratings are not distributed in the public minimal package.
Input CSV columns: item_id, cluster_id, rater_a, rater_b.
"""
import argparse, csv, math, random, statistics
try:
    from scipy.stats import spearmanr
except Exception:
    spearmanr=None

def icc_a1(a,b):
    # McGraw & Wong / Shrout-Fleiss absolute-agreement single-measure, k=2.
    n=len(a); k=2
    if n<2: return float('nan')
    rows=[(float(x),float(y)) for x,y in zip(a,b)]
    grand=sum(x+y for x,y in rows)/(n*k)
    rowmeans=[(x+y)/2 for x,y in rows]
    colmeans=[sum(x for x,y in rows)/n, sum(y for x,y in rows)/n]
    ssr=k*sum((m-grand)**2 for m in rowmeans)
    ssc=n*sum((m-grand)**2 for m in colmeans)
    sse=sum((x-rowmeans[i]-colmeans[0]+grand)**2 + (y-rowmeans[i]-colmeans[1]+grand)**2 for i,(x,y) in enumerate(rows))
    msr=ssr/(n-1); msc=ssc/(k-1); mse=sse/((n-1)*(k-1))
    den=msr+(k-1)*mse+k*(msc-mse)/n
    return (msr-mse)/den if den else float('nan')

def metrics(a,b):
    dif=[y-x for x,y in zip(a,b)]
    rho=float(spearmanr(a,b).statistic) if spearmanr else float('nan')
    bias=statistics.mean(dif); sd=statistics.stdev(dif) if len(dif)>1 else 0.0
    return {'n':len(a),'icc_a1':icc_a1(a,b),'spearman':rho,'mae':statistics.mean(abs(d) for d in dif),'bias_b_minus_a':bias,'loa_low':bias-1.96*sd,'loa_high':bias+1.96*sd}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv'); a=ap.parse_args()
    rows=list(csv.DictReader(open(a.csv,encoding='utf-8-sig')))
    x=[float(r['rater_a']) for r in rows]; y=[float(r['rater_b']) for r in rows]
    print(metrics(x,y))
if __name__=='__main__': main()
