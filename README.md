# GitHub Star Watch

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

Monitor fast-growing GitHub repositories by taking repeated star snapshots and
ranking repos by recent star velocity.

This is especially useful for watching fast-moving developer-tool trends such as
AI agents, MCP, coding-agent plugins, agent skills, and new open-source tools
before they become obvious on broader trending pages.

## Requirements

- Python 3.10 or newer.
- Python's standard library only; no additional packages are required.
- Internet access to the GitHub API.

The commands below use a macOS/Linux shell. On Windows, replace `python3` with
`py -3`; use the PowerShell token example below.

## What It Does

- Searches GitHub for recently active or newly created repositories above a star threshold.
- Stores repeated star snapshots in a local JSON database.
- Computes star growth over a recent time window.
- Prints a fastest-growing ranking with star delta, stars/hour, total stars, language, description, and URL.
- Can run once from a terminal or continuously as a background watcher.

## Quick Start

```bash
python3 github_star_watch.py --once
```

The first run establishes a baseline. Wait before running it again to calculate
star growth:

```bash
python3 github_star_watch.py --once
```

Run continuously:

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

## GitHub Token

The script can run without a token, but GitHub's unauthenticated API limit is
low. A token is recommended for reliable watch mode:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

On Windows PowerShell:

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

Replace the placeholder with your own token locally.
Do not commit tokens, logs, or snapshot databases.

## Common Commands

Run one collection cycle:

```bash
python3 github_star_watch.py --once
```

Watch every 30 minutes:

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

Filter by language:

```bash
python3 github_star_watch.py --watch --language Python
```

Lower the threshold to catch earlier projects:

```bash
python3 github_star_watch.py --watch --min-stars 20 --days 7
```

Show more rows:

```bash
python3 github_star_watch.py --once --limit 50
```

Use a custom local database path:

```bash
python3 github_star_watch.py --watch --db data/star_snapshots.json
```

## Ranking Logic

The ranking sorts primarily by star velocity:

```text
stars_per_hour = star_delta / elapsed_hours
```

The first time a repository is seen, the script stores a baseline snapshot. A
later run is needed before velocity can be calculated.

## Output Example

```text
Top 20 fastest-growing GitHub repos
------------------------------------------------------------------------------------------------
 1. owner/repo  +227 stars / 1.0h  (225.8/h, total 41920, JavaScript)
    Short repository description...
    https://github.com/owner/repo
```

See [`examples/sample_report.md`](examples/sample_report.md) for an example
daily report format built from the watcher data.

The watcher prints terminal rankings; generating a full dated daily report is a
separate workflow. The example is a template, not an automatic report generator.

## macOS LaunchAgent

For a background watcher on macOS, adapt the template in
[`launchd/com.example.github-star-watch.plist`](launchd/com.example.github-star-watch.plist).

Update the paths to match your local clone and log directory before loading it.

## Repository Hygiene

The repository contains source and examples only. The following are
runtime/private artifacts and are ignored by default:

- `star_snapshots.json`
- `*.log`
- `daily_reports/`
- local LaunchAgent files with personal paths
- Python caches

## Project Status

Small, practical, and intentionally simple. The script currently uses Python's
standard library only.

Search results are a candidate sample, not every GitHub repository. Each repo
retains up to 1,600 snapshots; useful history depends on collection frequency.
Missing or stale observations do not mean zero star growth.

These translations cover documentation only. Terminal messages remain in
English and Chinese.
