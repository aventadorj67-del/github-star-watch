#!/usr/bin/env python3
"""
Monitor fast-growing GitHub repositories by comparing star snapshots over time.

Usage:
  python3 github_star_watch.py --once
  python3 github_star_watch.py --watch --interval-minutes 30

Optional:
  export GITHUB_TOKEN=ghp_xxx
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import http.client
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_ROOT = "https://api.github.com"
DEFAULT_DB = Path("star_snapshots.json")


@dataclass
class Repo:
    full_name: str
    html_url: str
    description: str
    language: str
    stars: int
    forks: int
    open_issues: int
    pushed_at: str
    created_at: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def github_get(path: str, token: str | None, retries: int = 3) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-star-watch/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read()
            return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in {403, 429, 500, 502, 503, 504} and attempt < retries:
                last_error = RuntimeError(f"GitHub API error {exc.code}: {body}")
                time.sleep(2 * attempt)
                continue
            raise RuntimeError(f"GitHub API error {exc.code}: {body}") from exc
        except (
            http.client.IncompleteRead,
            json.JSONDecodeError,
            TimeoutError,
            urllib.error.URLError,
        ) as exc:
            last_error = exc
            if attempt < retries:
                print(f"GitHub API 讀取中斷，{2 * attempt} 秒後重試 ({attempt}/{retries})...")
                time.sleep(2 * attempt)
                continue
            if isinstance(exc, urllib.error.URLError):
                raise RuntimeError(f"Network error: {exc.reason}") from exc
            raise RuntimeError(f"GitHub API response was incomplete after {retries} attempts: {exc}") from exc

    raise RuntimeError(f"GitHub API request failed: {last_error}")


def search_repos(query: str, token: str | None, per_page: int) -> list[Repo]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
        }
    )
    payload = github_get(f"/search/repositories?{params}", token)
    repos: list[Repo] = []

    for item in payload.get("items", []):
        repos.append(
            Repo(
                full_name=item["full_name"],
                html_url=item["html_url"],
                description=item.get("description") or "",
                language=item.get("language") or "",
                stars=int(item.get("stargazers_count") or 0),
                forks=int(item.get("forks_count") or 0),
                open_issues=int(item.get("open_issues_count") or 0),
                pushed_at=item.get("pushed_at") or "",
                created_at=item.get("created_at") or "",
            )
        )
    return repos


def build_queries(min_stars: int, days: int, language: str | None) -> list[str]:
    since = datetime.now(timezone.utc).date().toordinal() - days
    since_date = datetime.fromordinal(since).date().isoformat()
    language_part = f" language:{language}" if language else ""

    return [
        f"stars:>={min_stars} pushed:>={since_date}{language_part}",
        f"stars:>={max(10, min_stars // 2)} created:>={since_date}{language_part}",
    ]


def dedupe_repos(repos: list[Repo]) -> list[Repo]:
    seen: set[str] = set()
    deduped: list[Repo] = []
    for repo in repos:
        if repo.full_name in seen:
            continue
        seen.add(repo.full_name)
        deduped.append(repo)
    return deduped


def load_db(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"repos": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_db(path: Path, db: dict[str, Any]) -> None:
    path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def update_snapshots(db: dict[str, Any], repos: list[Repo], timestamp: str) -> None:
    db.setdefault("repos", {})
    for repo in repos:
        entry = db["repos"].setdefault(
            repo.full_name,
            {
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "description": repo.description,
                "language": repo.language,
                "forks": repo.forks,
                "open_issues": repo.open_issues,
                "pushed_at": repo.pushed_at,
                "created_at": repo.created_at,
                "snapshots": [],
            },
        )
        entry.update(
            {
                "html_url": repo.html_url,
                "description": repo.description,
                "language": repo.language,
                "forks": repo.forks,
                "open_issues": repo.open_issues,
                "pushed_at": repo.pushed_at,
                "created_at": repo.created_at,
            }
        )
        entry["snapshots"].append({"time": timestamp, "stars": repo.stars})
        entry["snapshots"] = entry["snapshots"][-1600:]


def rank_repos(db: dict[str, Any], max_age_hours: float) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for entry in db.get("repos", {}).values():
        snapshots = entry.get("snapshots", [])
        if len(snapshots) < 2:
            continue

        latest = snapshots[-1]
        latest_time = parse_iso(latest["time"])
        if (now - latest_time).total_seconds() > max_age_hours * 3600:
            continue

        baseline = snapshots[0]
        for snap in reversed(snapshots[:-1]):
            hours = (latest_time - parse_iso(snap["time"])).total_seconds() / 3600
            if hours >= 1:
                baseline = snap
                break

        hours = max(
            (latest_time - parse_iso(baseline["time"])).total_seconds() / 3600,
            1 / 60,
        )
        delta = int(latest["stars"]) - int(baseline["stars"])
        ranked.append(
            {
                **entry,
                "stars": int(latest["stars"]),
                "delta": delta,
                "stars_per_hour": delta / hours,
                "window_hours": hours,
            }
        )

    return sorted(
        ranked,
        key=lambda item: (item["stars_per_hour"], item["delta"], item["stars"]),
        reverse=True,
    )


def print_ranking(rows: list[dict[str, Any]], limit: int) -> None:
    if not rows:
        print("未有足夠快照計算升速。請隔一段時間再跑一次，或用 --watch 連續監測。")
        return

    print(f"\nTop {min(limit, len(rows))} fastest-growing GitHub repos")
    print("-" * 96)
    for index, repo in enumerate(rows[:limit], start=1):
        language = repo.get("language") or "-"
        desc = (repo.get("description") or "").replace("\n", " ").strip()
        if len(desc) > 90:
            desc = desc[:87] + "..."
        print(
            f"{index:>2}. {repo['full_name']}  "
            f"+{repo['delta']} stars / {repo['window_hours']:.1f}h  "
            f"({repo['stars_per_hour']:.2f}/h, total {repo['stars']}, {language})"
        )
        if desc:
            print(f"    {desc}")
        print(f"    {repo['html_url']}")


def collect_once(args: argparse.Namespace) -> None:
    token = os.getenv("GITHUB_TOKEN")
    queries = build_queries(args.min_stars, args.days, args.language)
    repos: list[Repo] = []

    for query in queries:
        repos.extend(search_repos(query, token, args.per_page))

    repos = dedupe_repos(repos)
    timestamp = utc_now_iso()
    db = load_db(args.db)
    update_snapshots(db, repos, timestamp)
    save_db(args.db, db)

    ranked = rank_repos(db, args.max_age_hours)
    print(f"已更新 {len(repos)} 個 repo 快照：{timestamp}")
    print_ranking(ranked, args.limit)


def sleep_with_countdown(seconds: float, label: str) -> None:
    minutes = seconds / 60
    print(f"\n{label}：等 {minutes:.0f} 分鐘...\n", flush=True)
    time.sleep(seconds)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor GitHub repositories with the fastest star growth."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Run one collection cycle.")
    mode.add_argument("--watch", action="store_true", help="Keep monitoring.")
    parser.add_argument("--interval-minutes", type=float, default=30)
    parser.add_argument("--days", type=int, default=14, help="Candidate activity window.")
    parser.add_argument("--min-stars", type=int, default=100)
    parser.add_argument("--language", help="Filter by language, e.g. Python, Go, Rust.")
    parser.add_argument("--per-page", type=int, default=50)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-age-hours", type=float, default=48)
    parser.add_argument(
        "--retry-delay-minutes",
        type=float,
        default=5,
        help="Watch mode delay after a failed collection cycle.",
    )
    parser.add_argument(
        "--max-retry-delay-minutes",
        type=float,
        default=60,
        help="Maximum retry delay after repeated failures in watch mode.",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    if not args.once and not args.watch:
        args.once = True

    failures = 0
    while True:
        try:
            collect_once(args)
            failures = 0
            if not args.watch:
                return 0
            sleep_with_countdown(
                max(args.interval_minutes * 60, 60),
                "下一輪檢查",
            )
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            if not args.watch:
                raise
            failures += 1
            retry_seconds = min(
                max(args.retry_delay_minutes * 60, 60) * failures,
                max(args.max_retry_delay_minutes * 60, 60),
            )
            print(
                f"\n監測出錯但會自動重試：{exc}\n"
                f"連續失敗次數：{failures}",
                file=sys.stderr,
                flush=True,
            )
            sleep_with_countdown(retry_seconds, "自動重試")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已停止。")
        raise SystemExit(130)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
