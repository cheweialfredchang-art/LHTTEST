# V11 決賽 Agent 評測與稽核框架

此版本在 V10 原首頁及單層目錄基礎上新增評測程式，**不代表已完成真實場域測試**。

## 本機啟動

```bash
npm install
python3 -m pip install -r requirements.txt
npm start
```

另一終端機：

```bash
python3 -m unittest -v test_v11.py
python3 baseline-evaluator.py
python3 agent-evaluator.py --url http://localhost:3000 --limit 10
python3 evaluation-report.py
python3 security-tests.py http://localhost:3000
```

完整 120 題測試：`python3 agent-evaluator.py --url http://localhost:3000`。

## 八項揭露對應

1. `evaluation-cases.json`：120 個**合成草案**案例，含分類與判定準則；正式評分前需補人工核定 gold answer。環境：Node 22、Python 3、Render Docker；實際 commit、模型、資料 SHA 見 `version-manifest.json`。
2. `baseline-evaluator.py`：固定關鍵字基準；人工與單模型比較需要另外真實執行並填入同一評分表，**不可將此腳本當成人工基準**。
3. `evaluation-report.py`：成功率、正確率、平均／最大延遲、成本；無資料回傳 null，不編造。
4. 工具成功率、重試、人工介入與中止：見 `evaluation-results.jsonl`。重試若未由工具層上報，僅顯示 0 的觀察值，不代表沒有隱含重試。
5. `failure-analysis-template.csv`：故障分類、最壞情境與回復策略。
6. `trace-recorder.js`：`/tmp/v11-traces.jsonl` 匿名事件紀錄，正式試辦須安全持久化匯出，Render 預設暫存檔不保證保留。
7. `version-manifest.json`：資料 SHA256、Prompt／策略／模型版本，部署時補 Git commit。
8. `security-cases.json` / `security-tests.py`：10 項安全探測，**pass=null 直到人工判定**。

## 安全與隱私

追蹤紀錄不保存問題原文或個資。`evaluation-results.jsonl` 會保存測試問題及回答，請勿使用真實個人資料；管理金鑰、API Key 僅存 Render Secret。公開測試環境不要開放未經授權的 trace 下載。爬蟲 SSL 例外只能在受控測試下啟用。

## 重要限制

目前校網 JSON 含 HTML 快照，PDF 內文可能缺漏；不能把「找到來源」當成「回答正確」。模型費用需使用供應商實際 usage 計算，現有 `/chat` 回應未完整回傳 token usage，故報表成本為 null。此版的 trace 主要記錄完成的 Agent 工具呼叫，尚不涵蓋所有 MCP 底層重試。正式決賽前應補齊此部分。
