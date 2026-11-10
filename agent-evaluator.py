#!/usr/bin/env python3
"""Auditable evaluation. Does not infer correctness from source presence."""
import argparse, json, time, urllib.request, urllib.error, statistics, csv, pathlib, datetime
P=pathlib.Path(__file__).parent

def request(url,question,timeout):
 data=json.dumps({'messages':[{'role':'user','content':question}]}).encode()
 req=urllib.request.Request(url.rstrip('/')+'/chat',data=data,headers={'Content-Type':'application/json'},method='POST')
 started=time.perf_counter()
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r: payload=json.load(r);status=r.status
 except urllib.error.HTTPError as e:
  status=e.code;payload={'error':e.read(1024).decode('utf-8','replace')}
 except Exception as e: status=0;payload={'error':str(e)}
 return status,payload,round((time.perf_counter()-started)*1000,2)

def run(args):
 cases=json.loads((P/args.cases).read_text(encoding='utf-8'))['cases']
 rows=[]
 for case in cases[:args.limit or len(cases)]:
  status,payload,ms=request(args.url,case['question'],args.timeout)
  trace=payload.get('trace') or {};calls=trace.get('toolCalls') or []
  sources=payload.get('sources') or []
  row={'id':case['id'],'category':case['category'],'question':case['question'],'http_status':status,'elapsed_ms':ms,'trace_id':trace.get('id',''),'route':trace.get('route',''),'source_count':len(sources),'source_urls':[x.get('url') for x in sources],'tool_calls':calls,'tool_successes':sum(c.get('status')=='ok' for c in calls),'tool_failures':sum(c.get('status')!='ok' for c in calls),'retry_count':trace.get('retryCount',0),'human_escalation':bool(trace.get('needsHumanConfirmation',False)),'aborted':status!=200,'reply':str(payload.get('reply',''))[:5000],'correct':None,'task_success':None,'security_pass':None,'input_tokens':None,'output_tokens':None,'api_cost_usd':None,'error':payload.get('error','')}
  rows.append(row)
  print(f"{case['id']}: HTTP {status}, {ms:.0f} ms, {len(sources)} sources")
 out=P/args.output;out.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
 print(f'Wrote {len(rows)} unscored real execution records: {out}')
 print('Correctness, task success, and API cost remain null until verified.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:3000');ap.add_argument('--cases',default='evaluation-cases.json');ap.add_argument('--limit',type=int,default=0);ap.add_argument('--timeout',type=float,default=25);ap.add_argument('--output',default='evaluation-results.jsonl');run(ap.parse_args())
