# V11.3 Render Logs 與決賽可稽核 Trace

## 新增功能

- 所有 `/chat` 請求產生 `request_start`、`tool_call`、`model_call`、`request_complete` 事件，印至 **Render Logs**，前綴為 `[AGENT_AUDIT]`。
- 每個事件有 UTC ISO8601 時間與同一個 `traceId`，可串接整次操作。
- 完成事件記錄端到端延遲、工具成功/總次數、重試、人工確認、是否中止、模型 token 與估算費用。
- 模型呼叫事件含模型名稱、token、模型呼叫延遲、finish reason。無法取得的成本為 `null`。
- `/api/admin/audit`：本次 Node 進程的統計（平均/最大延遲、工具成功率、重試數、人工介入率、中止率、已知成本）。
- `/api/admin/traces?limit=50`：最近事件；`/api/admin/versions`：模型、Prompt/策略版本、Git commit 與來源檔 SHA256。均須 `ADMIN_TOKEN`。
- `AUDIT_JSONL_FILE` 可選擇本地 JSONL 落盤；Render 一般容器檔案非持久儲存，請以 Render Logs 或外部日誌系統保存查核資料。

## Render Environment Variables

| 名稱 | 建議 | 說明 |
| --- | --- | --- |
| `ADMIN_TOKEN` | 強隨機值 | 啟用管理 API，切勿放入 Git |
| `AUDIT_LOG_CONTENT` | `0` | 預設僅記錄問答 SHA-256 與長度；`1` 記錄基本遮蔽後文字，需同意及權限管理 |
| `OPENAI_MODEL` | `gpt-4.1-mini` | 使用模型 |
| `OPENAI_INPUT_USD_PER_1M` | 不預填 | 依當時官方價格自行設定每百萬輸入 tokens 的美元價格 |
| `OPENAI_OUTPUT_USD_PER_1M` | 不預填 | 依當時官方價格自行設定每百萬輸出 tokens 的美元價格 |
| `AUDIT_JSONL_FILE` | 留空 | 非必要；若設定可同步寫入 JSONL |
| `RENDER_GIT_COMMIT` | Render 提供時自動讀取 | 程式版本資訊 |

**注意**：成本為依設定單價及 API 回傳 token 用量的估算，不等於帳單實付金額。未涵蓋其他付費 API、快取優惠等特殊計費情況。固定工作流與 evidence agent 不呼叫 OpenAI 時，模型費用為 0；但不代表 Render 主機免費。

## 在 Render Logs 查看

搜尋 `AGENT_AUDIT`、`request_start`、`tool_call`、`model_call`、`request_complete`，並用 `traceId` 串起單次操作。範例：

```json
{"eventType":"agent_audit","event":"request_complete","traceId":"example","elapsedMs":1200,"toolCalls":2,"toolSuccess":2,"retryCount":0,"manualIntervention":false,"aborted":false,"costUsd":null,"costKnown":false}
```

以上是格式範例，非真實測試數據。實際 `costKnown` 取決於路由和單價設定。

## Windows 測試

```powershell
npm.cmd install
node test_render_audit.mjs
python3 -m unittest -v test_v11.py
npm.cmd start
```

請在另一視窗呼叫聊天 API，並檢查輸出的 `AGENT_AUDIT`。正式驗證需實際測試 MCP 正常/異常、API 超時、人工轉介及 Prompt 注入情境。

## 已知限制

1. `/api/admin/audit` 是單一 Node 進程、最近 1000 筆事件的統計，重啟後歸零；正式跨日報表需匯出 Render Logs 或外部資料庫。
2. 問答遮蔽僅為基本正規式，不能保證完整去識別；正式環境不建議啟用原文紀錄。
3. `manualIntervention` 是「系統判定需要人工確認」，不是已完成真人介入。
4. `aborted` 是服務端辨識的失敗/中止，不等於使用者主動取消。
5. 重試次數只統計經程式明確回報的工具重試；MCP 啟動重試另以 `mcp_startup_error` 事件記錄。
6. 本版不會自動宣稱任務成功率或答案正確率，這兩者需搭配人工核定題庫。
7. 本版記錄的是**主要 Prompt 的版本與檔案雜湊**，不預設把含機密的完整系統 Prompt 寫入公開日誌。
