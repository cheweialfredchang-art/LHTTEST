# V8 校網爬蟲：SSL 診斷、重試、PDF 文字擷取

原有 `index.html`、`school-ui-config.json`、快速分類與小按鈕均未修改。所有檔案位於同一層，維持 Render 的 FLAT 部署方式。

## Windows PowerShell

```powershell
cd C:\Users\chewe\Downloads\Mini_AI_Campus_Assistant_V8_Crawler_SSL_PDF_FLAT
python3 -m pip install -r requirements.txt
python3 school-crawler.py --max-pages 150 --max-documents 30
```

若目標校網憑證已過期，先向網站管理員反映，確認主機及電腦時間。**僅開發測試**可使用：

```powershell
python3 school-crawler.py --insecure-school-ssl --max-pages 150 --max-documents 30
```

此旗標僅對 `school-crawl-config.json` 的 `allowed_hosts` 生效，且 HTTPS 跳轉會重新驗證網域；**不會略過 robots.txt**。它會使下載內容失去 TLS 身分驗證保障，不適合正式生產或未受信任網路。

## 設定檔

`school-crawl-config.json`：`start_urls`、`allowed_hosts`、`max_pages`、`max_depth`、`max_documents`、`max_pdf_bytes`、`retries`、`delay_seconds`、`output_file`。若有可信 CA 檔，可選擇設定 `ca_bundle`（相對專案根目錄）。

## 行為與限制

- 每個主機先取得並解析 `robots.txt`；404/410 視為沒有發布規則；403、5xx、SSL/網路錯誤均保守停止該主機的爬取。
- 對暫時性 HTTP 408、429、5xx 和網路錯誤重試，間隔退避；尊重基本請求延遲。
- 巡覽 HTML 連結，找到 PDF 時下載到記憶體並用 pypdf 擷取文字，與網頁文字一起寫入 `school-crawl-data.json` 的 `records`，供既有 `search_school_pages` 使用。
- 只支援同網域公開 HTTPS 網頁與可擷取文字的 PDF；掃描影像 PDF 不會自動 OCR。PDF 頁數及大小有上限；動態 JS 頁面、非 PDF 文件不擷取文字。
- `document_links` 包含每個文件的擷取狀態；`errors` 包含 robots、TLS、HTTP、PDF 錯誤。`insecure_school_ssl` 記錄在 JSON 中。
- 爬蟲不會隨 Render 啟動而自動執行。請本機爬取、審核 JSON、再提交到 GitHub。校方來源可能過期，對報名期限、資格與費用仍須核對官方原文。

## 測試

```powershell
python3 -m unittest test_crawler_v8.py test_school_crawl.py
```
