#!/usr/bin/env python3
import csv, hashlib, json, os, sys
from collections import Counter
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

bench=os.path.join(ROOT,'data','benchmark','canonical_gold_750.jsonl')
rows=[json.loads(x) for x in open(bench,encoding='utf-8') if x.strip()]
assert len(rows)==750, len(rows)
c=Counter(r.get('task_id','qa_v4_5') for r in rows)
expected={'classification':100,'reasoning':100,'structuring':100,'relationship':50,'story_generation':100,'rewriting':100,'continuation':100,'qa_v4_5':100}
assert c==expected,(c,expected)
manifest=os.path.join(ROOT,'MANIFEST_SHA256.csv')
if os.path.exists(manifest):
    for r in csv.DictReader(open(manifest,encoding='utf-8')):
        p=os.path.join(ROOT,r['path'])
        if not os.path.isfile(p): raise SystemExit('missing '+r['path'])
        if sha(p)!=r['sha256']: raise SystemExit('hash mismatch '+r['path'])
print('OK: benchmark counts and SHA-256 manifest verified')
