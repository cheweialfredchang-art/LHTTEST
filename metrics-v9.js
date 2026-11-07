import fs from 'node:fs';import path from 'node:path';
const file=process.env.V9_METRICS_FILE||path.join(process.cwd(),'v9-metrics.jsonl');
const buffer=[];const MAX=500;
function write(event){const row={at:new Date().toISOString(),...event};buffer.push(row);if(buffer.length>MAX)buffer.shift();
 if(process.env.V9_PERSIST_METRICS==='1'){try{fs.appendFileSync(file,JSON.stringify(row)+'\n',{encoding:'utf8',flag:'a'})}catch(e){console.error('[METRICS]',e.message)}}}
export function recordEvent(e){write({type:'query',...e})}
export function recordFeedback(e){write({type:'feedback',...e})}
export function summary(){const queries=buffer.filter(x=>x.type==='query'),feedback=buffer.filter(x=>x.type==='feedback');return {scope:'current_process_only',persistent:process.env.V9_PERSIST_METRICS==='1',queryCount:queries.length,averageLatencyMs:queries.length?Math.round(queries.reduce((s,x)=>s+x.elapsedMs,0)/queries.length):null,withSources:queries.filter(x=>x.sourceCount>0).length,escalations:queries.filter(x=>x.needsHumanConfirmation).length,toolErrors:queries.flatMap(x=>x.toolCalls||[]).filter(x=>x.status==='error').length,feedback:{helpful:feedback.filter(x=>x.rating==='helpful').length,incorrect:feedback.filter(x=>x.rating==='incorrect').length,incomplete:feedback.filter(x=>x.rating==='incomplete').length},recent:queries.slice(-20).map(x=>({at:x.at,id:x.id,route:x.route,sourceCount:x.sourceCount,elapsedMs:x.elapsedMs}))};}
