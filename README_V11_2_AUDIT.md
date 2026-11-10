# V11.2 決賽評測與稽核紀錄

本版本新增 `audit-report.py`，產生 `AUDIT_REPORT.md`、`audit-summary.json`、`audit-metrics.csv`。沒有實際測試資料時，數值會是 null 或 NOT_MEASURED，不會生成虛構 log。

## Windows PowerShell

```powershell
python3 -m unittest -v test_v11.py
npm.cmd install
npm.cmd start
```

在另一個 PowerShell 視窗：

```powershell
python3 baseline-evaluator.py
python3 agent-evaluator.py --limit 10 --url http://127.0.0.1:3000
python3 security-tests.py http://127.0.0.1:3000
python3 audit-report.py
```

請先人工審核 `evaluation-results.jsonl` 的 `correct` / `task_success` 與 `security-results.jsonl` 的 `pass`，未核定保持 null。再次執行 `python3 audit-report.py` 可更新報表。

## 八項查核證據

1. 任務成功規則、案例數、環境：`audit-summary.json`
2. Agent / keyword 基準：`evaluation-results.jsonl` / `baseline-results.jsonl`；人工與單模型需另外量測
3. 成功率、正確率、延遲、成本：`audit-metrics.csv`（無量測值保持空白）
4. 工具成功、重試、人工介入、中止：`audit-summary.json` 的 metrics
5. 錯誤、已知限制、最壞情境與復原：`AUDIT_REPORT.md`
6. Trace：實際執行的 `evaluation-results.jsonl` 與服務 trace 檔
7. 資料、模型、Prompt、策略版本：`version-manifest.json` + SHA-256 + Git commit
8. 個資、資安、權限、提示注入、不當輸出：`security-results.jsonl`（人工審核）

**注意**：Render 檔案系統可能是暫存，需安全匯出操作紀錄；不可將含敏感資料的日誌提交公開 GitHub。
