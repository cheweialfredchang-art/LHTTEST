# V7 校網蒐集與 JSON 匯入（單層目錄）

**首頁 `index.html` 不變。** 既有快速分類、小按鈕及 `school-ui-config.json` 不變。新增三個根目錄檔案：`school-crawl-config.json`、`school-crawler.py`、`school-crawl-search.py`。執行後生成 `school-crawl-data.json`。

## 步驟

1. 修改 `school-crawl-config.json` 的 `start_urls` 與 `allowed_hosts`，務必使用學校官方網站與你有權擷取的公開頁面。
2. 在本機或 GitHub Actions 手動執行 `python3 school-crawler.py --max-pages 100`。**不會在 Render 啟動時自動爬取**。
3. 檢視 `school-crawl-data.json`，刪除個資、錯誤內容、非授權資料，確認重要條文與來源。
4. 把 `school-crawl-data.json` 一併提交至 GitHub 根目錄，Render 部署後 MCP 會新增 `search_school_pages`，原有規章查詢與其他工具保留。
5. 測試「重修補修」「重修報名時間」「教務處公告」等問法，逐一核對官方網頁。若資料仍無，應明確說查無，不能推測。

## 蒐集規則

- 僅 HTTPS、明確允許的主機、公開 HTML 頁面；尊重 `robots.txt`。若無法取得 robots.txt，保守跳過。
- 同站連結 BFS，預設最多 150 頁、深度 3、每個主機至少 1.5 秒間隔；限制回應大小、逾時及頁面長度。
- 不登入、不繞過權限、不擷取個人資料頁面；PDF、Word 等只記錄連結，不解析內容。
- `school-crawl-data.json` 為當時快照，包含 `retrieved_at`、`url`，不能代表現行最新規定。
- 學校網頁可能有 JavaScript 動態載入、搜尋功能或分頁，這個純標準函式庫爬蟲不保證抓到每一頁。不要宣稱已完整擷取全站。
- 本專案沒有管理員遠端觸發爬蟲端點，避免公開網站遭濫用。需要定期更新可由管理者排程離線執行、審核後提交。

## Render

維持既有 Dockerfile 與單層目錄部署。Python 3 標準函式庫即可，不需要新增 pip 套件。`school-crawl-data.json` 不存在時新工具會回報 `not_collected`，不影響原有 MCP 工具。
