# YKVS AI Assistant — OpenAI / Render 版本

使用 Node.js Express + OpenAI `gpt-4.1-mini` + Python MCP 校務資料查詢。

## Render 部署

- Runtime: Node
- Build Command: `npm install`
- Start Command: `node server.js`
- Health Check Path: `/healthz`

在 Render → Environment 設定（請使用**新產生**的 API Key）：

```text
OPENAI_API_KEY=<your-new-secret-key>
OPENAI_MODEL=gpt-4.1-mini
PYTHON_BIN=python3
MAX_AGENT_STEPS=4
```

不要設定舊的 `OPENAI_BASE_URL` 或 `GEMINI_API_KEY`。API Key 不應寫進程式、README 或 GitHub。

`MAX_AGENT_STEPS` 限制每次對話中模型工具迴圈的最大次數（1–10）；若最後一次仍有工具呼叫，會額外進行一次不允許工具呼叫的回答生成。

## 本機執行

```bash
npm install
cp env.example .env
# 在本機 .env 填入自己的新 API Key
npm start
```

開啟 `http://localhost:3000`，健康檢查路徑為 `/healthz`。

Python MCP 透過 `PYTHON_BIN` 指定的執行檔啟動，Node 執行環境必須能找到 Python 3。若 Render 的 Node Runtime 未提供 Python，需使用含 Node + Python 的 Docker 部署環境。
