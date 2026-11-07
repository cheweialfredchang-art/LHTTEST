# Mini AI Campus Assistant V9 — 完整競賽開發版

## 與 V8 的差異
- **原始 index.html、school-ui.js、school-ui-config.json 原樣保留**。
- 整合使用者實際上傳的 `school-crawl-data.json`：150 筆 HTML、172 個文件連結，**0 筆成功 PDF 內文**。本版不虛構 PDF 擷取成果。
- `agent-v9.js`：多輪簡單上下文補全、同義詞查詢改寫、MCP 多工具檢索、來源 URL 白名單驗證、缺資料轉人工。**非任意多步自主規劃 Agent**。
- `school_crawl_search.py`：HTML 長文切段、關鍵字擴展、來源排序、回傳片段位置。
- `/admin`：管理儀表板；`/api/admin/metrics` 需設定 `ADMIN_TOKEN` 並在 header 傳 `x-admin-token`；預設匿名化且僅記憶體暫存。
- `crawl-diff-v9.py`：兩次快照的新增、修改、缺漏比較；**不是排程爬蟲**。
- `evaluation-100-v9.json`：100 題合成情境測試；**尚無人工核對標準答案，不能宣稱 90% 正確率**。

## Windows 本機測試
```powershell
python3 -m pip install -r requirements.txt
python3 -m unittest -v test_v9.py test_regulations.py test_school_crawl.py test_crawler_v8.py
python3 evaluate-v9.py
npm install
$env:OPENAI_API_KEY='你的金鑰'  # 若需一般問題 LLM；校務 V9 檢索可不設
$env:ADMIN_TOKEN='請設定強密碼'
npm start
```
開啟 `http://localhost:3000`；管理頁 `http://localhost:3000/admin`，在頁面輸入金鑰。勿將金鑰提交 GitHub。

## Render 部署
1. 將 ZIP 解壓後的檔案放 GitHub repository 根目錄，**不要上傳 `.env`**。
2. Render 使用 `render.yaml` Docker Web Service。環境變數 `OPENAI_API_KEY`（可選）、`OPENAI_MODEL`、`ADMIN_TOKEN`（管理功能必需）。
3. `GET /healthz` 檢查 MCP；若啟動尚未完成請稍後重試。
4. `school-crawl-data.json` 為已上傳快照，**不會自動刷新**。重新爬取後請人工審核再提交。
5. Render 免費實例的記憶體與檔案系統可能重置；本版匿名指標預設只在記憶體中保存。正式持久化請用外部資料庫並訂資料保留政策。

## 限制與風險
- 上傳的快照使用 `insecure_school_ssl=true`，僅供資料蒐集測試；正式請修復學校端 SSL 憑證。V9 不會在 Web 啟動時停用 SSL 驗證。
- PDF 下載與擷取能力保留 V8 原始爬蟲，但這份 JSON 尚未成功取得 PDF 條文；需要安裝 `pypdf` 後重爬、檢查 errors，再審核更新。
- V9 的證據回答**展示原始摘錄而非保證語義正確的規則解讀**；多輪補全為簡單啟發式，沒有帳號、跨裝置會話或寫入學籍功能。
- 評測目前只可量測「是否有候選來源」，不可當作真實答案正確率。競賽前需校方人工建立標準答案及驗證樣本。
- 管理回饋端點只開放管理員；學生端回報 UI 尚未加入，以免更動首頁。
- JSON 有 HTML 選單雜訊；檢索品質需後續去除共用導覽區塊及增量擷取。
