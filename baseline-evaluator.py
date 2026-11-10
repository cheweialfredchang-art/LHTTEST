#!/usr/bin/env python3
"""Produce reproducible deterministic keyword baseline, never pretend it is an LLM."""
import json,re,pathlib,datetime
P=pathlib.Path(__file__).parent
D=json.loads((P/'school-crawl-data.json').read_text(encoding='utf8'))
C=json.loads((P/'evaluation-cases.json').read_text(encoding='utf8'))['cases']
rows=[]
for c in C:
 q=c['question'];tokens=set(re.findall(r'[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}',q));scores=[]
 for r in D.get('records',[]):
  hay=str(r.get('title',''))+' '+str(r.get('content',''))[:2000];score=sum(1 for x in tokens if x in hay)
  if score:scores.append((score,r))
 scores.sort(key=lambda x:-x[0]);top=scores[0][1] if scores else {}
 rows.append({'id':c['id'],'baseline':'keyword-only','source_url':top.get('url'),'candidate_found':bool(top),'correct':None,'task_success':None,'latency_ms':None,'cost_usd':0,'note':'offline deterministic retrieval only; no measured end-to-end latency'})
(P/'baseline-results.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
print('Wrote',len(rows),'keyword-only baseline rows; correctness remains unscored')
