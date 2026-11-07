import 'dotenv/config';
import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { MCPClient } from './mcp-client.js';
import { OpenAILLMClient } from './llm-client-openai.js';
import { getQuickReply } from './quick-reply.js';
import crypto from 'node:crypto';
import {searchRegulationFallback} from './regulation-bridge.js';

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

app.get('/healthz', (req, res) => {
  res.json({ ok: true, mcpReady: mcp.ready, mcpTools: mcp.tools.map(x => x.name), mcpError, openaiConfigured: llm.enabled });
});

app.post('/chat', async (req, res) => {
  const started = Date.now();
  const traceId = crypto.randomUUID();
  let route = 'agent';
  try {
    const { messages } = req.body || {};
    if (!Array.isArray(messages) || !messages.length) return res.status(400).json({error:'messages (array) is required'});
    const q = String([...messages].reverse().find(x => x?.role === 'user')?.content || '');
    if (q.length > 2000) return res.status(400).json({error:'問題過長，請縮短至 2000 字以內。'});
    const quick = await getQuickReply(q);
    if (quick !== null) { route='quick-reply'; return res.json({ reply: quick, messages: [...messages, {role:'assistant', content:quick}], trace:{id:traceId,route,elapsedMs:Date.now()-started} }); }
    if (CREDIT.test(q) && mcp.ready) {
      route='verified-credit-retrieval';
      const raw=await mcp.callTool('search_regulations',{query:q});
      const result=JSON.parse(raw);
      const response=searchRegulationFallback(q,result);
      if(response) return res.json({reply:response,messages:[...messages,{role:'assistant',content:response}],trace:{id:traceId,route,tool:'search_regulations',matchedDocuments:result.matches?.map(x=>x.data_id)||[],elapsedMs:Date.now()-started,needsHumanConfirmation:true}});
    }
    if (SCHOOL.test(q) && !mcp.ready) {
      return res.status(503).json({error:'校務資料服務尚未完成啟動，請稍後再試。', detail:mcpError});
    }
    const result = await llm.chat(messages, { forceTool: SCHOOL.test(q) });
    res.json({...result,trace:{id:traceId,route,elapsedMs:Date.now()-started}});
  } catch (e) {
    console.error('[CHAT_ERROR]',traceId,e?.message);
    res.status(500).json({error:'查詢暫時失敗，請稍後再試或洽詢校方承辦單位。',traceId});
  } finally {
    console.log(JSON.stringify({event:'chat',traceId,route,elapsedMs:Date.now()-started}));
  }
});

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
      console.error('[MCP STARTUP ERROR]', err);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay = Math.min(delay * 2, 30000);
    }
  }
}

startMcp();
