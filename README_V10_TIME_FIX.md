# V10 台灣本週時間修正（V9 完整競賽版延伸）

## 修正內容
- 全部日期以 `Asia/Taipei` 時區計算，不依賴 Render 伺服器 UTC 時區。
- 本週採 **星期一 00:00 至星期日 23:59:59（台灣時間）**；支援「本週／本周／這週／這周／上週／下週」。
- 跨日、跨週以台灣日曆日期判定，不使用 7×24 小時滑動視窗。
- `/api/time` 提供 today、weekStart、weekEnd、time 等欄位，便於檢查。
- 對「本週學校活動」只給正確日期範圍與資料時效警告；**不將舊公告當成本週活動**。
- OpenAI 系統提示注入台灣當日日期與本週區間。
- Docker build 加入 Python MCP 模組及 Node 語法檢查。
- 保留 V9 原始 `index.html`、按鈕、單層目錄及使用者上傳的 `school-crawl-data.json`。

## Windows 本機測試
```powershell
npm install
node test-time-v10.mjs
python3 -m unittest -v test_v9.py
npm start
```
瀏覽 `http://localhost:3000/api/time` 驗證台灣日期與週區間。

## Render
GitHub 上傳 ZIP **解壓後的根目錄全部檔案**，包括 `school_crawl_search.py`、`taiwan-time.js`、`school-crawl-data.json`。
Render 使用 Docker runtime，Root Directory 留空，Dockerfile Path 為 `./Dockerfile`；部署最新 commit。
設定 `OPENAI_API_KEY`、`OPENAI_MODEL=gpt-4.1-mini`、`PYTHON_BIN=python3`，管理功能另設 `ADMIN_TOKEN`。
健康檢查 `/healthz` 應顯示 `mcpReady: true`；`/api/time` 顯示本週時間。

注意：校網資料為 2026-11-07 快照，不能以此確認即時校園活動。PDF 內文仍需完成擷取與驗證。
