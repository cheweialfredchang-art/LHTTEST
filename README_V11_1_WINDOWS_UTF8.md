# V11.1 Windows UTF-8 修正版

本版本以 V11 為基礎，保留首頁、單層目錄、校網資料及決賽評測功能。

## 修正

- `test_v11.py` 的 JSON 讀取明確指定 `encoding="utf-8"`，避免 Windows Python 3.13 使用 cp1252 時發生 UnicodeDecodeError。
- 其餘評測 Python 檔案已檢查，原本即明確使用 UTF-8。

## Windows PowerShell

```powershell
python3 -m pip install -r requirements.txt
npm.cmd install
python3 -m unittest -v test_v11.py
python3 -m unittest -v test_v9.py
npm.cmd start
```

另外開一個 PowerShell 視窗進行評測：

```powershell
python3 baseline-evaluator.py
python3 agent-evaluator.py --limit 10
python3 evaluation-report.py
python3 security-tests.py
```

`agent-evaluator.py` 需要本機服務啟動，測試結果不是人工核定的答案正確率。

## Render

將 ZIP 中所有檔案直接放入 GitHub 指定部署分支根目錄，Render Runtime 選 Docker、Root Directory 留空。設定 `OPENAI_API_KEY` 與其他必要環境變數。部署後檢查 `/healthz`、`/api/time`。

## 資料與安全

`school-crawl-data.json` 為先前爬取快照；不代表已擷取完整 PDF 法規。不要將 API Key 寫入 GitHub。
