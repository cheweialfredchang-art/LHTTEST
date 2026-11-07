# Mini AI Campus Assistant V6 — Evidence-first retrieval

## 保留原始首頁
`index.html` 保留 V5 的版面、配色、快速分類、小型按鈕、聊天區及點擊帶入問題的方式。只在聊天文字後附上短版 Trace ID；沒有重做版型。

## 主要修正
- 原版 `additional_regulations.json` 有重修、補修、學期補考資料，`hello_tool.py` 卻沒有檢索它。本版加入 `regulation_search.py` 及 `search_regulations` MCP 工具。
- 重修／補修、學分不足、被當、補學分等口語問法，優先查校方規定索引，並以確定性模板回答已收錄的內容。
- 文件摘要不包含本學期報名時間、費用、開班與申請表，不編造；建議向教務處註冊組確認。
- 回傳 `trace`（匿名請求 ID、路由、耗時、命中文件 ID），伺服器僅記錄技術摘要，不記錄完整問題與個資。
- 加入 `test_regulations.py` 測試別名檢索、文件來源及不虛構報名資訊。
- 原本 `school-ui-config.json` 繼續獨立管理學校網址與快速分類；增加一個「重修規定來源」小按鈕。

## 對應簡報及審查建議
- 第 4–5 頁：口語查詢改寫、MCP 證據、查無與轉介。
- 第 7 頁：不臆測未驗證校務資訊；個案須人工確認。
- 第 9–10 頁：補強可量測的 Trace、重試與後續正式評測的基礎。
- 審查意見：強化 Agent 來源正確性、查詢改寫與操作紀錄，避免只是單一工具問答。

## 本版的限制（請在競賽中如實說明）
- 校方來源連結來自既有 `additional_regulations.json`，本次未即時重新核驗 PDF 內容與現行效力。
- 專案已有的 2025 學習評量文件摘要僅能支持概括規則，不能視為完整的重修補修程序。
- 尚未實作身分驗證、成績查詢、正式請假申請或校務系統寫入。
- 新增 Trace 不是完整、持久化的審計日誌；Render 重啟後不保留記錄。
- 自動測試僅涵蓋檢索行為，尚未完成評審所要求的多題官方答案逐題核對及真實場域試辦。

## 部署
全部檔案直接上傳 GitHub 根目錄，沒有子資料夾。Render Docker 部署：`Dockerfile` 自動安裝 Node.js 與 Python。設定 `OPENAI_API_KEY`、`OPENAI_MODEL=gpt-4.1-mini`、`PYTHON_BIN=python3`、`MAX_AGENT_STEPS=4`。勿將金鑰上傳 GitHub。部署後測 `/healthz`、首頁及「重修／補修」按鈕。

## 測試
`python3 -m unittest -v test_regulations.py`
`node --check server.js`
