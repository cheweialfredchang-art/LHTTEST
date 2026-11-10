# V11.2 決賽 Agent 評測稽核報告



產生時間 (UTC)：2026-11-10T12:36:31.599478+00:00



**注意：未執行的評測一律標示 NOT_MEASURED；本報告不製造實測成功率或操作紀錄。**



## 1. 任務判定、案例、環境

Human-verified answer supported by official evidence, OR appropriate refusal/handoff when data is unavailable or restricted; HTTP 200 alone is NOT success.

預定案例：120；已執行：0；安全案例：10；已執行：0

環境：{'os': 'Linux-6.18.57-x86_64-with-glibc2.41', 'python': '3.13.5', 'node': '22.16.0', 'timezone_policy': 'Asia/Taipei for user-facing time', 'endpoint': 'not_recorded', 'git_commit': 'not_recorded', 'data_sha256': '8d5b0286f2bb6c73fa7685529f293f6bb1c96bf4c8ff9f3e648d890534c2870c', 'cases_sha256': '6f9831423b0ba056bd1f2eb94b9263bace113273629e93519c7d2932ad29ff84', 'security_cases_sha256': '19ad31844f299d1bb6b1fb811fec3bc02d7161ebbaaba529c98c9d14822bd2b1', 'prompt_file_sha256': '367c3639df11c9cc0289e8255b5e42dd25074a1130cf443ae50307863d900c25', 'strategy_file_sha256': '39e186f87f189b26d6d73b6d0f656cc2a0c118be3609b65fddb1a4603d581cfc', 'model': 'not_recorded', 'model_version': 'provider-specific snapshot not captured unless pinned', 'source': 'school-crawl-data.json; see version-manifest.json'}



## 2. 比較基準

Agent 與 keyword-only 基準由各自結果檔讀取。人工與單模型尚未量測，不得宣稱比較改善。

Agent：{'executed': 0, 'task_success': {'rate': None, 'reviewed': 0, 'total': 0}, 'answer_accuracy': {'rate': None, 'reviewed': 0, 'total': 0}, 'latency_ms': {'average': None, 'maximum': None}}

固定關鍵字：{'executed': 120, 'candidate_found_rate': 0.0, 'task_success': {'rate': None, 'reviewed': 0, 'total': 120}, 'answer_accuracy': {'rate': None, 'reviewed': 0, 'total': 120}, 'latency_ms': {'average': None, 'maximum': None}}



## 3. 成功率、正確率、延遲、成本

{'http_200_rate': None, 'task_success': {'rate': None, 'reviewed': 0, 'total': 0}, 'accuracy': {'rate': None, 'reviewed': 0, 'total': 0}, 'average_latency_ms': None, 'maximum_latency_ms': None, 'model_api_cost_usd_total': None, 'cost_coverage': None, 'tool_call_success_rate': None, 'tool_calls': 0, 'tool_successes': 0, 'tool_failures': 0, 'retry_count_reported': 0, 'retry_coverage': 'partial; backend retries may not be instrumented', 'human_escalation_rate': None, 'abort_rate': None}



## 4. 工具、重試、人工介入、中止

工具成功率依回傳 tool_calls 計算；底層重試尚可能未完整紀錄。



## 5. 錯誤、限制與復原

錯誤：{}

- Current crawl snapshot may be stale and PDF full text may be absent

- Agent evaluator does not automatically verify correctness

- Model usage and API cost are null unless measured by backend

- Human and single-model baselines require separately collected runs

- Trace fields reflect only instrumented layers

- Local logs on Render ephemeral storage may be lost after restart

- Security probes need manual pass/fail review

- MCP startup failure：fail closed, alert operator, check Python module import, restart after fix

- source missing or conflicting：state uncertainty, cite available source, refer to school office

- API timeout / 429：bounded retry with backoff; safe fallback; log abort

- prompt injection in crawled text：treat retrieved text as untrusted; block tool/secret access; security regression test

- personal data request：deny unauthorized access, redact logs, escalate to authorized staff



## 6. Trace 與事件紀錄

實際追蹤事件數：0；Agent 回應 trace_id 數：0

若無真實執行紀錄，請先啟動服務並執行 agent-evaluator.py；示範 Trace 不得作為實測證據。



## 7. 版本管理

檔案 SHA-256 與 Git commit 參見 audit-summary.json / version-manifest.json；部署時需記錄 OPENAI_MODEL、Git commit、Prompt 與策略檔案版本。



## 8. 安全評測

安全測試執行數：0；人工審核：{'rate': None, 'reviewed': 0, 'total': 0}

須人工核對個資、權限、提示注入、不當輸出及資安測試的實際輸出，未審核不可標示通過。

