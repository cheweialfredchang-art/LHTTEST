import 'dotenv/config';
import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { MCPClient } from './mcp-client.js';
import { OpenAILLMClient } from './llm-client-openai.js';
import { getQuickReply } from './quick-reply.js';
import {taiwanCalendar} from './taiwan-time.js';
import crypto from 'node:crypto';
import {traceEvent} from './trace-recorder.js';
import {searchRegulationFallback} from './regulation-bridge.js';
import {runEvidenceAgent,isSchool} from './agent-v9.js';
import {recordEvent,summary,recordFeedback} from './metrics-v9.js';
import {beginAudit,completeAudit,auditSummary,auditRecent,versionInfo,auditLog} from './render-audit.js';
import {PROMPT_VERSION} from './llm-client-openai.js';

const app = express();
app.use(express.json({ limit: '1mb' }));
const ROOT = path.dirname(fileURLToPath(import.meta.url));
app.get('/', (req,res)=>res.sendFile(path.join(ROOT,'index.html')));
app.get('/index.html', (req,res)=>res.sendFile(path.join(ROOT,'index.html')));
app.get('/school-ui.js', (req,res)=>res.sendFile(path.join(ROOT,'school-ui.js')));
app.get('/school-ui-config.json', (req,res)=>res.sendFile(path.join(ROOT,'school-ui-config.json')));

const mcp = new MCPClient();
const llm = new OpenAILLMClient(mcp);
let mcpError = null;

const CREDIT = /重修|補修|重補修|學分沒過|學分不足|學分不夠|補學分|被當|學分未取得/;
const SCHOOL = /分機|電話|教室|場館|老師|教師|主任|組長|職稱|單位|姓名|行事曆|行程|校規|規定|法規|條文|請假|行動載具|手機|獎懲|成績|考試|補考|學分|編班|轉班|抵免|學習歷程|班級|重修|補修|重補修|學分不足|學分不夠|被當/;

app.get('/api/time', (req,res) => res.json(taiwanCalendar()));
app.get('/healthz', (req, res) => {
  res.json({ ok: true, mcpReady: mcp.ready, mcpTools: mcp.tools.map(x => x.name), mcpError, openaiConfigured: llm.enabled, taiwanTime: taiwanCalendar() });
});

app.post('/chat', async (req, res) => {
  const started = Date.now();
  const traceId = crypto.randomUUID();
  traceEvent({traceId,stage:'received',status:'ok'});
  let route = 'agent';
  let finalized=false;
  const finish=(args)=>{if(!finalized){finalized=true;completeAudit(traceId,{route,elapsedMs:Date.now()-started,...args});}};
  try {
    const { messages } = req.body || {};
    if (!Array.isArray(messages) || !messages.length){beginAudit({traceId,route,question:'',model:llm.model,promptVersion:PROMPT_VERSION,strategyVersion:'v11.3'});finish({status:'invalid_request',aborted:true,errorCode:'INVALID_MESSAGES',answer:''});return res.status(400).json({error:'messages (array) is required'});}
    const q = String([...messages].reverse().find(x => x?.role === 'user')?.content || '');
    beginAudit({traceId,route,question:q,model:llm.model,promptVersion:PROMPT_VERSION,strategyVersion:'v11.3'});
    if (q.length > 2000){finish({status:'invalid_request',aborted:true,errorCode:'QUESTION_TOO_LONG',answer:''});return res.status(400).json({error:'問題過長，請縮短至 2000 字以內。'});}
    const quick = await getQuickReply(q);
    if (quick !== null) { route='quick-reply';finish({answer:quick}); return res.json({ reply: quick, messages: [...messages, {role:'assistant', content:quick}], trace:{id:traceId,route,elapsedMs:Date.now()-started} }); }
    if (isSchool(q) && mcp.ready) {
      route='v9-evidence-agent';
      const result=await runEvidenceAgent({question:q,messages,mcp,traceId});
      recordEvent({id:traceId,route,elapsedMs:Date.now()-started,sourceCount:result.sources.length,needsHumanConfirmation:result.trace.needsHumanConfirmation,toolCalls:result.trace.toolCalls.map(x=>({tool:x.tool,status:x.status,ms:x.ms}))});
      traceEvent({traceId,stage:'completed',route,status:'ok',elapsedMs:Date.now()-started,sourceCount:result.sources.length,humanEscalation:result.trace.needsHumanConfirmation,toolCalls:result.trace.toolCalls.map(x=>({tool:x.tool,status:x.status,elapsedMs:x.ms})),retryCount:0,strategyVersion:'evidence-v9'});
      finish({answer:result.reply,sourceCount:result.sources.length,manualIntervention:result.trace.needsHumanConfirmation});
      return res.json({reply:result.reply,messages:[...messages,{role:'assistant',content:result.reply}],trace:result.trace,sources:result.sources});
    }
    if (SCHOOL.test(q) && !mcp.ready) {
      finish({status:'unavailable',aborted:true,errorCode:'MCP_NOT_READY',answer:'校務資料服務尚未完成啟動'});
      return res.status(503).json({error:'校務資料服務尚未完成啟動，請稍後再試。', detail:mcpError});
    }
    const result = await llm.chat(messages, { forceTool: SCHOOL.test(q),traceId });
    finish({answer:result.reply});
    res.json({...result,trace:{id:traceId,route,elapsedMs:Date.now()-started}});
  } catch (e) {
    console.error('[CHAT_ERROR]',traceId,e?.message);
    finish({status:'error',aborted:true,errorCode:'CHAT_ERROR',answer:'查詢暫時失敗'});
    traceEvent({traceId,stage:'failed',route,status:'error',elapsedMs:Date.now()-started,errorCode:'CHAT_ERROR',aborted:true});
    res.status(500).json({error:'查詢暫時失敗，請稍後再試或洽詢校方承辦單位。',traceId});
  } finally {
    console.log(JSON.stringify({event:'chat',traceId,route,elapsedMs:Date.now()-started}));
    traceEvent({traceId,stage:'finished',route,elapsedMs:Date.now()-started,status:'finished'});
  }
});

// Management endpoints are disabled unless an admin token is configured.
function requireAdmin(req,res,next){const token=process.env.ADMIN_TOKEN;if(!token)return res.status(404).json({error:'disabled'});
 const value=String(req.get('x-admin-token')||'');const a=Buffer.from(value),b=Buffer.from(token);
 if(a.length!==b.length||!crypto.timingSafeEqual(a,b))return res.status(403).json({error:'forbidden'});next();}
app.get('/api/admin/metrics',requireAdmin,(req,res)=>res.json(summary()));
app.get('/api/admin/audit',requireAdmin,(req,res)=>res.json(auditSummary()));
app.get('/api/admin/traces',requireAdmin,(req,res)=>res.json({events:auditRecent(req.query.limit)}));
app.get('/api/admin/versions',requireAdmin,(req,res)=>res.json(versionInfo({model:llm.model,promptVersion:PROMPT_VERSION,strategyVersion:'v11.3'})));
app.post('/api/admin/feedback',requireAdmin,(req,res)=>{const {traceId,rating,category}=req.body||{};
 if(typeof traceId!=='string'||traceId.length>100||!['helpful','incorrect','incomplete'].includes(rating))return res.status(400).json({error:'invalid feedback'});
 recordFeedback({traceId,rating,category:String(category||'').slice(0,40)});res.json({ok:true});});
app.get('/admin',(req,res)=>res.sendFile(path.join(ROOT,'admin-v9.html')));
const port = Number(process.env.PORT || 3000);
app.listen(port, () => console.log(`YKVS AI Assistant listening on ${port}`));

async function startMcp() {
  let delay = 1000;
  while (!mcp.ready) {
    try {
      await mcp.connect();
      mcpError = null;
      return;
    } catch (err) {
      mcpError = err.message;
      auditLog({event:'mcp_startup_error',errorCode:'MCP_STARTUP',message:err.message,retryDelayMs:delay});
      console.error('[MCP STARTUP ERROR]', err);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay = Math.min(delay * 2, 30000);
    }
  }
}

startMcp();
