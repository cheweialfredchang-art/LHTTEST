#!/usr/bin/env python3
import json,statistics,pathlib,collections,sys
P=pathlib.Path(__file__).parent
src=P/(sys.argv[1] if len(sys.argv)>1 else 'evaluation-results.jsonl')
if not src.exists():raise SystemExit('Run agent-evaluator.py first')
rows=[json.loads(x) for x in src.read_text(encoding='utf8').splitlines() if x.strip()]
def rate(key):
 eligible=[r[key] for r in rows if r.get(key) is not None]
 return round(sum(x is True for x in eligible)/len(eligible),4) if eligible else None
ms=[r['elapsed_ms'] for r in rows if isinstance(r.get('elapsed_ms'),(int,float))]
tools=sum(len(r.get('tool_calls',[])) for r in rows)
summary={'sample_count':len(rows),'http_success_rate':round(sum(r.get('http_status')==200 for r in rows)/len(rows),4) if rows else None,'task_success_rate':rate('task_success'),'answer_accuracy':rate('correct'),'security_pass_rate':rate('security_pass'),'average_latency_ms':round(statistics.mean(ms),2) if ms else None,'maximum_latency_ms':max(ms) if ms else None,'tool_call_success_rate':round(sum(r.get('tool_successes',0) for r in rows)/tools,4) if tools else None,'tool_call_count':tools,'retry_count':sum(r.get('retry_count',0) for r in rows),'human_intervention_rate':round(sum(r.get('human_escalation',False) for r in rows)/len(rows),4) if rows else None,'abort_rate':round(sum(r.get('aborted',False) for r in rows)/len(rows),4) if rows else None,'api_cost_usd_total':round(sum(r['api_cost_usd'] for r in rows),6) if rows and all(isinstance(r.get('api_cost_usd'),(float,int)) for r in rows) else None,'error_classes':dict(collections.Counter('HTTP_'+str(r['http_status']) for r in rows if r.get('http_status')!=200)),'limitations':['Correctness and success require human gold-answer annotation','Token usage/cost unavailable unless server records provider usage','Keyword baseline is not human or LLM baseline','Render ephemeral filesystem: export logs to persistent secure storage']}
(P/'evaluation-summary-v11.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
