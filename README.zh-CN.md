# GitHub Star Watch

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

定期采集 GitHub 仓库的星标快照，按照近期增长速度发现快速成长的项目。

适合跟踪 AI 智能体、MCP、编程智能体插件、agent skills 和新开源工具等快速变化的开发者工具趋势。

## 运行要求

- Python 3.10 或更新版本。
- 仅使用 Python 标准库，无需额外安装依赖。
- 能够访问 GitHub API 的网络连接。

以下命令以 macOS／Linux shell 为例。Windows 请将 `python3` 替换为 `py -3`，Token 设置使用下方 PowerShell 写法。

## 功能

- 搜索近期活跃或新创建、达到星标门槛的仓库。
- 将多次快照保存在本地 JSON 数据库。
- 计算近期时间窗口内的星标增长。
- 输出增长排行，包括新增星标数、每小时增速、总星标数、编程语言、描述和链接。
- 支持单次执行或持续后台监控。

## 快速开始

```bash
python3 github_star_watch.py --once
```

首次运行建立基准快照。等待一段时间后再次运行，才能计算增长：

```bash
python3 github_star_watch.py --once
```

持续监控：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

## GitHub Token

不提供 token 也能运行，但未认证 API 的调用限额较低。持续监控建议使用自己的 token：

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Windows PowerShell 写法：

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

这只是占位符，请在本地设置自己的 token。不要将 token、日志或快照数据库提交到 Git。

## 常用命令

执行一轮采集：

```bash
python3 github_star_watch.py --once
```

每 30 分钟监控一次：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

按编程语言筛选：

```bash
python3 github_star_watch.py --watch --language Python
```

降低星标门槛，发现更早期的项目：

```bash
python3 github_star_watch.py --watch --min-stars 20 --days 7
```

显示更多项目：

```bash
python3 github_star_watch.py --once --limit 50
```

自定义本地数据库路径：

```bash
python3 github_star_watch.py --watch --db data/star_snapshots.json
```

## 排名逻辑

主要按照每小时星标增长速度排序：

```text
stars_per_hour = star_delta / elapsed_hours
```

首次发现仓库时只会保存基准快照；需要后续快照才能计算增长速度。

## 输出示例

```text
Top 20 fastest-growing GitHub repos
------------------------------------------------------------------------------------------------
 1. owner/repo  +227 stars / 1.0h  (225.8/h, total 41920, JavaScript)
    Short repository description...
    https://github.com/owner/repo
```

每日报告格式见 [`examples/sample_report.md`](examples/sample_report.md)。

监控程序只输出终端排行；完整的日期日报需要由独立流程生成。示例是模板，不是自动日报生成器。

## macOS LaunchAgent

如需在 macOS 后台运行，可修改 [`launchd/com.example.github-star-watch.plist`](launchd/com.example.github-star-watch.plist) 模板。

加载前，请将程序、工作目录和日志路径替换为自己的实际路径。

## 仓库数据管理

仓库只包含源码和示例。以下运行数据及私人文件默认不会加入 Git：

- `star_snapshots.json`
- `*.log`
- `daily_reports/`
- 包含个人路径的本地 LaunchAgent 配置
- Python 缓存

## 项目状态

小巧、实用，刻意保持简单，仅依赖 Python 标准库。

搜索结果只是候选样本，不代表所有 GitHub 仓库。每个仓库最多保留 1,600 个快照；实际历史长度取决于采集频率。数据缺失或过期不代表零增长。

多语言版本仅翻译文档；终端消息仍使用英文和中文。
