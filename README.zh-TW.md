# GitHub Star Watch

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

定期擷取 GitHub repository 嘅星數快照，按近期增星速度找出快速成長嘅項目。

適合追蹤 AI agents、MCP、coding-agent plugins、agent skills 同新開源工具等變化快嘅開發者工具趨勢。

## 執行要求

- Python 3.10 或以上。
- 只用 Python 標準函式庫，唔需要額外套件。
- 可以連接 GitHub API 嘅網絡。

以下指令以 macOS／Linux shell 為例。Windows 請將 `python3` 換成 `py -3`，Token 設定用下方 PowerShell 寫法。

## 功能

- 搜尋近期活躍或新建立、達到星數門檻嘅 repository。
- 將多次快照儲存喺本機 JSON 資料庫。
- 計算近期時間窗口嘅星數增長。
- 輸出增長排行，包括增星數、每小時增星、總星數、程式語言、描述及網址。
- 支援單次執行，或者持續喺背景監察。

## 快速開始

```bash
python3 github_star_watch.py --once
```

第一次執行只會建立基準快照；等一段時間再執行，先可以計算增星：

```bash
python3 github_star_watch.py --once
```

持續監察：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

## GitHub Token

唔提供 token 亦可以執行，但未認證 API 嘅限額較低。持續監察建議使用自己嘅 token：

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Windows PowerShell 寫法：

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

以上只係佔位符，請喺本機設定自己嘅 token。唔好將 token、日誌或快照資料庫提交到 Git。

## 常用指令

執行一輪採集：

```bash
python3 github_star_watch.py --once
```

每 30 分鐘監察一次：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

按程式語言篩選：

```bash
python3 github_star_watch.py --watch --language Python
```

降低星數門檻，尋找較早期嘅項目：

```bash
python3 github_star_watch.py --watch --min-stars 20 --days 7
```

顯示更多項目：

```bash
python3 github_star_watch.py --once --limit 50
```

自訂本機資料庫路徑：

```bash
python3 github_star_watch.py --watch --db data/star_snapshots.json
```

## 排名邏輯

主要按每小時增星速度排序：

```text
stars_per_hour = star_delta / elapsed_hours
```

首次見到 repository 時只會儲存基準快照；要有之後嘅快照，先可以計算增長速度。

## 輸出範例

```text
Top 20 fastest-growing GitHub repos
------------------------------------------------------------------------------------------------
 1. owner/repo  +227 stars / 1.0h  (225.8/h, total 41920, JavaScript)
    Short repository description...
    https://github.com/owner/repo
```

每日報告格式可參考 [`examples/sample_report.md`](examples/sample_report.md)。

Watcher 只輸出終端排行；完整嘅日期日報由另一個流程生成。範例係模板，唔係自動日報產生器。

## macOS LaunchAgent

要喺 macOS 背景執行，可以修改 [`launchd/com.example.github-star-watch.plist`](launchd/com.example.github-star-watch.plist) 模板。

載入前，請將程式、工作目錄及日誌路徑改成自己嘅實際路徑。

## Repository 資料管理

Repository 只包含原始碼同範例。以下執行資料及私人檔案預設唔會加入 Git：

- `star_snapshots.json`
- `*.log`
- `daily_reports/`
- 包含個人路徑嘅本機 LaunchAgent 設定
- Python 快取

## 項目狀態

小型、實用，刻意保持簡單，只依賴 Python 標準函式庫。

搜尋結果只係候選樣本，唔代表全部 GitHub repository。每個 repo 最多保留 1,600 個快照；實際歷史長度取決於採集頻率。缺資料或資料過期，唔代表零增長。

多語版本只翻譯文件；終端訊息仍然使用英文同中文。
