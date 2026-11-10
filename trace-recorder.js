import fs from 'node:fs';
import crypto from 'node:crypto';
const file=process.env.V11_TRACE_FILE || '/tmp/v11-traces.jsonl';
export function traceEvent(event){
 const allowed=['traceId','stage','route','elapsedMs','status','tool','toolCalls','sourceCount','retryCount','humanEscalation','aborted','errorCode','model','promptVersion','strategyVersion','usage','costUsd'];
 const row={timestamp:new Date().toISOString(),type:'agent_trace',version:'v11.0'};
 for(const k of allowed)if(event[k]!==undefined)row[k]=event[k];
 try{fs.appendFileSync(file,JSON.stringify(row)+'\n',{encoding:'utf8',mode:0o600})}catch(e){console.error('[TRACE_WRITE_ERROR]',e.message)}
 return row;
}
export function safeTraceId(){return crypto.randomUUID()}
