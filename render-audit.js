import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const LIMIT = 1000;
const history = [];
const sessions = new Map();
const start = Date.now();
const enabledRaw = process.env.AUDIT_LOG_CONTENT === '1';
const file = process.env.AUDIT_JSONL_FILE || '';
const mask = (value) => String(value ?? '')
  .replace(/sk-(?:proj-)?[A-Za-z0-9_-]{12,}/g,'[REDACTED_API_KEY]')
  .replace(/(?:Bearer\s+)[A-Za-z0-9._-]+/gi,'Bearer [REDACTED]')
  .replace(/\b[A-Z][12]\d{8}\b/g,'[REDACTED_ID]')
  .replace(/\b09\d{8}\b/g,'[REDACTED_PHONE]')
  .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi,'[REDACTED_EMAIL]')
  .replace(/(?:密碼|password|token|api[_ -]?key)\s*[:：=]\s*\S+/gi,'[REDACTED_SECRET]');
function scrub(obj, depth=0) {
  if(depth>7) return '[DEPTH_LIMIT]';
  if(typeof obj==='string') return mask(obj).slice(0,3000);
  if(Array.isArray(obj)) return obj.slice(0,30).map(v=>scrub(v,depth+1));
  if(obj && typeof obj==='object') return Object.fromEntries(Object.entries(obj).filter(([k])=>!/(authorization|api.?key|secret|password|cookie)/i.test(k)).map(([k,v])=>[k,scrub(v,depth+1)]));
  return obj;
}
export function contentAudit(value) {
  const s=String(value??'');
  return enabledRaw ? {text:mask(s).slice(0,2000),truncated:s.length>2000,redacted:true} : {sha256:crypto.createHash('sha256').update(s).digest('hex'),characters:s.length,contentLogged:false};
}
export function auditLog(event) {
  const row=scrub({timestamp:new Date().toISOString(),eventType:'agent_audit',schemaVersion:'1.0',...event});
  console.log('[AGENT_AUDIT] '+JSON.stringify(row));
  history.push(row);if(history.length>LIMIT)history.shift();
  if(file){try{fs.appendFileSync(file,JSON.stringify(row)+'\n',{encoding:'utf8',mode:0o600})}catch(e){console.error('[AUDIT_FILE_ERROR]',e.message)}}
  return row;
}
export function beginAudit({traceId,route,question,model,promptVersion,strategyVersion}) {
  const entry={traceId,route,model,promptVersion,strategyVersion,startedAt:Date.now(),toolCalls:0,toolSuccess:0,retries:0,manualIntervention:false,aborted:false,inputTokens:0,outputTokens:0,costUsd:0,costKnown:true,errors:[],sourceCount:0};
  sessions.set(traceId,entry);
  auditLog({event:'request_start',traceId,route,model,promptVersion,strategyVersion,question:contentAudit(question)});
  return entry;
}
export function recordTool(traceId,{name,success,latencyMs,retryCount=0,error=null}) {
  const x=sessions.get(traceId);if(x){x.toolCalls++;if(success)x.toolSuccess++;x.retries+=retryCount;if(error)x.errors.push(String(error).slice(0,120));}
  auditLog({event:'tool_call',traceId,tool:name,success,latencyMs,retryCount,error:error?mask(error):null});
}
export function recordModel(traceId,{model,latencyMs,usage,costUsd,costKnown,finishReason}) {
  const x=sessions.get(traceId);if(x){x.inputTokens+=usage?.prompt_tokens||0;x.outputTokens+=usage?.completion_tokens||0;if(costKnown)x.costUsd+=costUsd||0;else x.costKnown=false;}
  auditLog({event:'model_call',traceId,model,latencyMs,usage:usage||null,costUsd:costKnown?costUsd:null,costKnown,finishReason});
}
export function completeAudit(traceId,{route,answer,status='ok',elapsedMs,sourceCount=0,manualIntervention=false,aborted=false,errorCode=null,model=null,promptVersion=null,strategyVersion=null}) {
  const x=sessions.get(traceId);
  const result={event:'request_complete',traceId,route:route||x?.route,status,elapsedMs,model:model||x?.model,promptVersion:promptVersion||x?.promptVersion,strategyVersion:strategyVersion||x?.strategyVersion,answer:contentAudit(answer),sourceCount,toolCalls:x?.toolCalls??0,toolSuccess:x?.toolSuccess??0,toolSuccessRate:x?.toolCalls?x.toolSuccess/x.toolCalls:null,retryCount:x?.retries??0,manualIntervention,aborted,errorCode,usage:{prompt_tokens:x?.inputTokens??0,completion_tokens:x?.outputTokens??0},costUsd:x?.costKnown?(x?.costUsd??0):null,costKnown:x?.costKnown??false};
  auditLog(result);sessions.delete(traceId);return result;
}
export function auditSummary() {
  const completed=history.filter(x=>x.event==='request_complete');const tools=history.filter(x=>x.event==='tool_call');
  const sum=(arr,key)=>arr.reduce((a,x)=>a+(Number(x[key])||0),0);
  const errors=completed.filter(x=>x.status!=='ok');
  return {scope:'current_process_only',since:new Date(start).toISOString(),requests:completed.length,avgLatencyMs:completed.length?sum(completed,'elapsedMs')/completed.length:null,maxLatencyMs:completed.length?Math.max(...completed.map(x=>x.elapsedMs)):null,toolCalls:tools.length,toolSuccessRate:tools.length?tools.filter(x=>x.success).length/tools.length:null,retries:sum(tools,'retryCount'),manualInterventionRate:completed.length?completed.filter(x=>x.manualIntervention).length/completed.length:null,abortRate:completed.length?completed.filter(x=>x.aborted).length/completed.length:null,errorRate:completed.length?errors.length/completed.length:null,totalKnownCostUsd:sum(completed.filter(x=>x.costKnown),'costUsd'),unknownCostRequests:completed.filter(x=>!x.costKnown).length,contentLogging:enabledRaw?'redacted_opt_in':'hash_only',recent:completed.slice(-20).map(({traceId,route,status,elapsedMs,toolCalls,retryCount,costUsd})=>({traceId,route,status,elapsedMs,toolCalls,retryCount,costUsd}))};
}
export function auditRecent(limit=50){return history.slice(-Math.min(200,Math.max(1,Number(limit)||50)));}
export function versionInfo({model,promptVersion,strategyVersion}) {
  const hash=(f)=>{try{return crypto.createHash('sha256').update(fs.readFileSync(path.join(process.cwd(),f))).digest('hex')}catch{return null}};
  return {model,modelProvider:'OpenAI',promptVersion,strategyVersion,gitCommit:process.env.RENDER_GIT_COMMIT||process.env.GIT_COMMIT||null,gitBranch:process.env.RENDER_GIT_BRANCH||null,sourceFiles:{'school-crawl-data.json':hash('school-crawl-data.json'),'additional_regulations.json':hash('additional_regulations.json')},promptFileHash:hash('llm-client-openai.js'),strategyFileHash:hash('agent-v9.js'),note:'Model name is configured; provider snapshot revision may not be available.'};
}
