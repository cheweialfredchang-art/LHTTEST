import {taiwanCalendar} from './taiwan-time.js';
import crypto from 'node:crypto';
const CREDIT=/重修|補修|重補修|學分|被當|補考|畢業條件|畢業門檻/;
const LEAVE=/請假|病假|事假|補假|喪假/;
const SCHOOL=/重修|補修|學分|補考|畢業|請假|病假|獎懲|校規|規定|公告|行事曆|日期|分機|教務|學務|學習歷程|老師|教師|學校|報名|開學|成績|手機|載具|獎學金/;
const HIGH_RISK=/我(的)?成績|我的學分|我能不能|我是否符合|我的出缺勤|個人資料|帳號|密碼|身分證|學號|繳費|費用|報名截止|今天|明天|最新|這學期|本學期/;
export function isSchool(q){return SCHOOL.test(q)}
export function rewriteQuery(query,history=[]){
 let q=String(query||'').trim();const previous=history.slice(-8).reverse().find(m=>m?.role==='user' && m.content!==query)?.content||'';
 if(/^(那|所以|這個|那個|費用|多少錢|什麼時候|怎麼報名|在哪裡|要去哪)/.test(q)&&previous){q=String(previous).slice(0,120)+'；'+q}
 const variants=[q];if(CREDIT.test(q))variants.push('重補修 辦理期程 法規 報名 Q&A 學習評量');
 if(LEAVE.test(q))variants.push('學生請假規則 請假期限');
 return [...new Set(variants)].slice(0,3);
}
function parse(raw){try{return JSON.parse(raw)}catch{return {matches:[]}}}
function validUrl(u){try{const x=new URL(u);return x.protocol==='https:'&&['www.ykvs.ntpc.edu.tw','ykvs.ntpc.edu.tw'].includes(x.hostname)}catch{return false}}
export function selectEvidence(results){
 const rows=[];const seen=new Set();
 for(const result of results){for(const item of result.matches||[]){const url=item.url||item.source_url;if(!validUrl(url))continue;
 const key=url+'|'+String(item.chunk_offset??'');if(seen.has(key))continue;seen.add(key);
 const excerpt=String(item.excerpt||item.content||item.summary||'').slice(0,900);
 if(!excerpt.trim())continue;
 rows.push({title:String(item.title||'校方文件'),url,excerpt,retrieved_at:item.retrieved_at||item.last_verified_date||null,score:Number(item.score||0)});
 }}return rows.sort((a,b)=>b.score-a.score).slice(0,5);
}
export async function runEvidenceAgent({question,messages,mcp,traceId=crypto.randomUUID()}){
 const calendar=taiwanCalendar();
 const started=Date.now(),rewrites=rewriteQuery(question,messages.slice(0,-1));const calls=[];const results=[];
 const run=async(name,q)=>{const t=Date.now();try{const result=parse(await mcp.callTool(name,{query:q}));calls.push({tool:name,query:q,status:'ok',ms:Date.now()-t,matches:result.matches?.length||0});results.push(result);return result}catch(e){calls.push({tool:name,query:q,status:'error',ms:Date.now()-t,error:String(e.message).slice(0,100)});return {matches:[]}}};
 if(CREDIT.test(question))await run('search_regulations',rewrites[0]);
 let result=await run('search_school_pages',rewrites[0]);
 if(!result.matches?.length || result.matches.length<2){if(rewrites.length>1)await run('search_school_pages',rewrites[1]);}
 if(!results.some(r=>r.matches?.length))await run('search_school_info',rewrites[0]);
 const evidence=selectEvidence(results),human=HIGH_RISK.test(question),confidence=evidence.length>=2?'partial':evidence.length?'partial':'none';
 const lines=[];
 if(/本週|這週|本周|這周/.test(question))lines.push(`🗓️ 台灣時間本週：${calendar.weekLabel}（星期一至星期日）。\n注意：以下校網資料是歷史快照，不能據此推定本週一定有活動。`);
 if(!evidence.length)lines.push('目前已收錄的公開資料中，找不到足以直接回答的校方條文或公告。');
 else {lines.push('📚 查到以下校方公開資料（摘錄，不等同於最新正式決定）：');evidence.slice(0,3).forEach((x,i)=>lines.push(`${i+1}. ${x.title}\n${x.excerpt.slice(0,380)}\n🔗 ${x.url}${x.retrieved_at?'\n擷取：'+x.retrieved_at:''}`));}
 if(human||!evidence.length)lines.push('⚠️ 具體報名資格、個人成績、最新期限及費用，仍需向校方承辦單位確認；本系統無權查詢或更改個人紀錄。');
 else lines.push('⚠️ 以上為校網快照，請點擊原始公告核對最新版本。');
 return {reply:lines.join('\n\n'),trace:{id:traceId,route:'v9-evidence-agent',rewrites,toolCalls:calls,sourceCount:evidence.length,confidence,needsHumanConfirmation:human||!evidence.length,elapsedMs:Date.now()-started},sources:evidence.map(x=>({title:x.title,url:x.url,retrieved_at:x.retrieved_at}))};
}
