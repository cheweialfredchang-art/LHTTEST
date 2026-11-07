# Mini AI Campus Assistant — V5 單層設定版

## 編輯學校與按鈕（不需修改 HTML）

只需要修改根目錄的 `school-ui-config.json`：
- `school`：學校名稱、官方網站、標題、提醒文字。
- `quickCategories`：快速分類、圓角小按鈕、預填問題、顏色樣式。
- `webButtons`：外部連結按鈕（網址須為 http/https）。
- `ui`：歡迎標題、引導文字。點按分類只帶入問題，不會自動發送。

請勿將 API Key 放進這個公開 JSON。OpenAI 金鑰只設定在 Render 的 `OPENAI_API_KEY` 環境變數。

## 單層部署

將 ZIP 解壓後的所有檔案上傳 GitHub 根目錄；不需建立 `public` 或 `data` 資料夾。
Render 使用 Dockerfile，Root Directory 留空；檢查 `/healthz` 的 `mcpReady` 和 `openaiConfigured`。

## 評審要求對應

保留自然語言提問、校務資料 MCP、來源提示、查無依據時不猜測、快速查詢與跨資料／未知問題測試範例。
本次改動主要為 UI 設定外部化與單層部署；並未宣稱完成新的量化評測或人工確認所有外部網址。

## 官方網址

校方首頁採用原始簡報與資料來源提供的 https://www.ykvs.ntpc.edu.tw/ 。其他連結取自原專案資料，正式展示前應人工檢查是否仍有效及標籤是否相符。
