#!/usr/bin/env python3
"""Produce truthful auditable evidence. Missing observations stay null / not_measured."""
import argparse, csv, datetime, hashlib, json, os, pathlib, platform, statistics, subprocess, sys, collections
P=pathlib.Path(__file__).resolve().parent

def load_json(name, default=None):
 p=P/name
 return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else default

def load_jsonl(name):
 p=P/name
 if not p.exists():return []
 return [json.loads(s) for s in p.read_text(encoding='utf-8-sig').splitlines() if s.strip()]

def write_json(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ratio(num,den):return round(num/den,4) if den else None
def stat(rows,key):
 a=[r.get(key) for r in rows if isinstance(r.get(key),(float,int)) and not isinstance(r.get(key),bool)]
 return {'average':round(statistics.mean(a),2) if a else None,'maximum':max(a) if a else None}
def scored(rows,key):
 a=[r[key] for r in rows if type(r.get(key)) is bool]
 return {'rate':ratio(sum(a),len(a)),'reviewed':len(a),'total':len(rows)}
def sha(name):
 p=P/name
 return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

def run():
 cases=load_json('evaluation-cases.json',{}).get('cases',[])
 security_cases=load_json('security-cases.json',{}).get('cases',[])
 agent=load_jsonl('evaluation-results.jsonl')
 baseline=load_jsonl('baseline-results.jsonl')
 sec=load_jsonl('security-results.jsonl')
 traces=load_jsonl('agent-traces.jsonl')+load_jsonl('v11-traces.jsonl')
 try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,stderr=subprocess.DEVNULL,text=True).strip()
 except Exception:commit=None
 tools=sum(len(r.get('tool_calls') or []) for r in agent)
 successes=sum(int(r.get('tool_successes') or 0) for r in agent)
 failures=sum(int(r.get('tool_failures') or 0) for r in agent)
 lat=stat(agent,'elapsed_ms')
 measured_cost=[r.get('api_cost_usd') for r in agent]
 all_cost_known=bool(agent) and all(type(x) in (int,float) for x in measured_cost)
 errors=collections.Counter()
 for r in agent:
  if r.get('error'):errors['request_error']+=1
  if r.get('http_status') not in (200,):errors['http_'+str(r.get('http_status'))]+=1
  if r.get('tool_failures'):errors['tool_failure']+=1
 report={
 'report_type':'real_observation_only','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'observed' if agent else 'NOT_MEASURED',
 'task_definition':{'success':'Human-verified answer supported by official evidence, OR appropriate refusal/handoff when data is unavailable or restricted; HTTP 200 alone is NOT success.','accuracy':'Among manually reviewed substantive answers, correct and supported by official evidence; refusals scored separately.','gold_review':'Set correct/task_success explicitly true or false only after human review; null means unreviewed.'},
 'test_cases':{'planned':len(cases),'executed':len(agent),'security_planned':len(security_cases),'security_executed':len(sec),'gold_verified':sum(c.get('gold_verified') is True for c in cases)},
 'environment':{'os':platform.platform(),'python':platform.python_version(),'node':os.environ.get('NODE_VERSION','not_captured'),'timezone_policy':'Asia/Taipei for user-facing time','endpoint':os.environ.get('EVAL_ENDPOINT','not_recorded'),'git_commit':commit or os.environ.get('GIT_COMMIT','not_recorded'),'data_sha256':sha('school-crawl-data.json'),'cases_sha256':sha('evaluation-cases.json'),'security_cases_sha256':sha('security-cases.json'),'prompt_file_sha256':sha('llm-client-openai.js'),'strategy_file_sha256':sha('regulation-bridge.js'),'model':os.environ.get('OPENAI_MODEL','not_recorded'),'model_version':'provider-specific snapshot not captured unless pinned','source':'school-crawl-data.json; see version-manifest.json'},
 'comparisons':{'agent':{'executed':len(agent),'task_success':scored(agent,'task_success'),'answer_accuracy':scored(agent,'correct'),'latency_ms':lat},'keyword_fixed_workflow':{'executed':len(baseline),'candidate_found_rate':ratio(sum(bool(x.get('candidate_found')) for x in baseline),len(baseline)),'task_success':scored(baseline,'task_success'),'answer_accuracy':scored(baseline,'correct'),'latency_ms':stat(baseline,'latency_ms')},'human_manual':{'status':'NOT_MEASURED','records':0},'single_model':{'status':'NOT_MEASURED','records':0}},
 'metrics':{'http_200_rate':ratio(sum(r.get('http_status')==200 for r in agent),len(agent)),'task_success':scored(agent,'task_success'),'accuracy':scored(agent,'correct'),'average_latency_ms':lat['average'],'maximum_latency_ms':lat['maximum'],'model_api_cost_usd_total':round(sum(measured_cost),6) if all_cost_known else None,'cost_coverage':ratio(sum(type(x) in (int,float) for x in measured_cost),len(agent)),'tool_call_success_rate':ratio(successes,tools),'tool_calls':tools,'tool_successes':successes,'tool_failures':failures,'retry_count_reported':sum(int(r.get('retry_count') or 0) for r in agent),'retry_coverage':'partial; backend retries may not be instrumented','human_escalation_rate':ratio(sum(bool(r.get('human_escalation')) for r in agent),len(agent)),'abort_rate':ratio(sum(bool(r.get('aborted')) for r in agent),len(agent))},
 'errors':dict(errors), 'security':{'probes':len(sec),'review':scored(sec,'pass'),'categories':dict(collections.Counter(r.get('category','unknown') for r in sec)),'status':'manual_review_required' if sec else 'NOT_MEASURED'},
 'trace':{'trace_event_count':len(traces),'agent_request_trace_ids':sum(bool(r.get('trace_id')) for r in agent),'real_trace_files':['evaluation-results.jsonl','agent-traces.jsonl','v11-traces.jsonl'],'demo_trace_excluded':True},
 'known_limitations':['Current crawl snapshot may be stale and PDF full text may be absent','Agent evaluator does not automatically verify correctness','Model usage and API cost are null unless measured by backend','Human and single-model baselines require separately collected runs','Trace fields reflect only instrumented layers','Local logs on Render ephemeral storage may be lost after restart','Security probes need manual pass/fail review'],
 'worst_case_and_recovery':[{'scenario':'MCP startup failure','impact':'school search unavailable','recovery':'fail closed, alert operator, check Python module import, restart after fix'},{'scenario':'source missing or conflicting','impact':'unsupported answer','recovery':'state uncertainty, cite available source, refer to school office'},{'scenario':'API timeout / 429','impact':'latency or no answer','recovery':'bounded retry with backoff; safe fallback; log abort'},{'scenario':'prompt injection in crawled text','impact':'instruction hijack','recovery':'treat retrieved text as untrusted; block tool/secret access; security regression test'},{'scenario':'personal data request','impact':'privacy breach','recovery':'deny unauthorized access, redact logs, escalate to authorized staff'}]
 }
 write_json('audit-summary.json',report)
 with (P/'audit-metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['metric','value','status'])
  for k,v in report['metrics'].items():w.writerow([k,json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v,'measured' if v is not None and agent else 'not_measured'])
 md=['# V11.2 決賽 Agent 評測稽核報告','',f"產生時間 (UTC)：{report['generated_at_utc']}",'','**注意：未執行的評測一律標示 NOT_MEASURED；本報告不製造實測成功率或操作紀錄。**','','## 1. 任務判定、案例、環境',report['task_definition']['success'],f"預定案例：{len(cases)}；已執行：{len(agent)}；安全案例：{len(security_cases)}；已執行：{len(sec)}",f"環境：{report['environment']}",'','## 2. 比較基準','Agent 與 keyword-only 基準由各自結果檔讀取。人工與單模型尚未量測，不得宣稱比較改善。',f"Agent：{report['comparisons']['agent']}",f"固定關鍵字：{report['comparisons']['keyword_fixed_workflow']}",'','## 3. 成功率、正確率、延遲、成本',f"{report['metrics']}",'','## 4. 工具、重試、人工介入、中止','工具成功率依回傳 tool_calls 計算；底層重試尚可能未完整紀錄。','','## 5. 錯誤、限制與復原',f"錯誤：{report['errors']}"]
 md+=['- '+s for s in report['known_limitations']]
 md+=['- '+x['scenario']+'：'+x['recovery'] for x in report['worst_case_and_recovery']]
 md+=['','## 6. Trace 與事件紀錄',f"實際追蹤事件數：{len(traces)}；Agent 回應 trace_id 數：{report['trace']['agent_request_trace_ids']}",'若無真實執行紀錄，請先啟動服務並執行 agent-evaluator.py；示範 Trace 不得作為實測證據。','','## 7. 版本管理','檔案 SHA-256 與 Git commit 參見 audit-summary.json / version-manifest.json；部署時需記錄 OPENAI_MODEL、Git commit、Prompt 與策略檔案版本。','','## 8. 安全評測',f"安全測試執行數：{len(sec)}；人工審核：{report['security']['review']}",'須人工核對個資、權限、提示注入、不當輸出及資安測試的實際輸出，未審核不可標示通過。','']
 (P/'AUDIT_REPORT.md').write_text('\n\n'.join(md),encoding='utf-8')
 print('Created AUDIT_REPORT.md, audit-summary.json, audit-metrics.csv')
 print('Executed agent cases:',len(agent),'security cases:',len(sec))
if __name__=='__main__':run()
