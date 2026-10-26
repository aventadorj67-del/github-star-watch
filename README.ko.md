# GitHub Star Watch

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

GitHub 저장소의 스타 수를 주기적으로 기록하고 최근 증가 속도로 빠르게 성장하는 프로젝트를 찾습니다.

AI 에이전트, MCP, 코딩 에이전트 플러그인, agent skills 및 새로운 오픈 소스 도구처럼 빠르게 변화하는 개발 도구 동향을 추적하는 데 유용합니다.

## 실행 요구 사항

- Python 3.10 이상.
- Python 표준 라이브러리만 사용하며 추가 패키지는 필요하지 않습니다.
- GitHub API에 접근할 수 있는 인터넷 연결.

아래 명령은 macOS／Linux 셸 기준입니다. Windows에서는 `python3`를 `py -3`로 바꾸고, 토큰 설정에는 아래 PowerShell 예시를 사용하세요.

## 기능

- 최근에 활동했거나 새로 생성된 저장소 중 스타 수 기준을 충족하는 항목을 검색합니다.
- 여러 시점의 스냅샷을 로컬 JSON 데이터베이스에 저장합니다.
- 최근 시간 구간의 스타 증가량을 계산합니다.
- 증가량, 시간당 증가량, 총 스타 수, 언어, 설명 및 URL을 순위에 표시합니다.
- 한 번 실행하거나 백그라운드에서 지속적으로 모니터링할 수 있습니다.

## 빠른 시작

```bash
python3 github_star_watch.py --once
```

첫 실행은 기준 스냅샷을 만듭니다. 잠시 기다린 후 다시 실행하면 증가량을 계산할 수 있습니다.

```bash
python3 github_star_watch.py --once
```

지속적인 모니터링:

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

## GitHub Token

토큰 없이도 실행할 수 있지만 인증되지 않은 API 요청의 한도는 낮습니다. 지속적인 모니터링에는 본인의 토큰 사용을 권장합니다.

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Windows PowerShell:

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

위 값은 예시용 자리 표시자입니다. 본인의 토큰을 로컬에서 설정하세요. 토큰, 로그 또는 스냅샷 데이터베이스를 Git에 커밋하지 마세요.

## 자주 사용하는 명령

한 번 수집:

```bash
python3 github_star_watch.py --once
```

30분마다 모니터링:

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

프로그래밍 언어로 필터링:

```bash
python3 github_star_watch.py --watch --language Python
```

스타 기준을 낮춰 더 초기 단계의 프로젝트 찾기:

```bash
python3 github_star_watch.py --watch --min-stars 20 --days 7
```

더 많은 항목 표시:

```bash
python3 github_star_watch.py --once --limit 50
```

로컬 데이터베이스 경로 지정:

```bash
python3 github_star_watch.py --watch --db data/star_snapshots.json
```

## 순위 계산

주로 시간당 스타 증가 속도로 정렬합니다.

```text
stars_per_hour = star_delta / elapsed_hours
```

저장소가 처음 발견되면 기준 스냅샷만 저장됩니다. 증가 속도를 계산하려면 이후 스냅샷이 필요합니다.

## 출력 예시

```text
Top 20 fastest-growing GitHub repos
------------------------------------------------------------------------------------------------
 1. owner/repo  +227 stars / 1.0h  (225.8/h, total 41920, JavaScript)
    Short repository description...
    https://github.com/owner/repo
```

일일 보고서 형식은 [`examples/sample_report.md`](examples/sample_report.md)를 참고하세요.

모니터링 프로그램은 터미널 순위를 출력합니다. 날짜가 포함된 전체 일일 보고서는 별도 워크플로에서 생성해야 합니다. 예시는 템플릿이며 자동 보고서 생성기가 아닙니다.

## macOS LaunchAgent

macOS 백그라운드에서 실행하려면 [`launchd/com.example.github-star-watch.plist`](launchd/com.example.github-star-watch.plist) 템플릿을 수정하세요.

불러오기 전에 프로그램, 작업 디렉터리 및 로그 경로를 본인 환경에 맞게 변경하세요.

## 저장소 데이터 관리

저장소에는 소스와 예시만 포함합니다. 다음 실행 데이터와 개인 파일은 기본적으로 Git 관리 대상에서 제외됩니다.

- `star_snapshots.json`
- `*.log`
- `daily_reports/`
- 개인 경로가 포함된 로컬 LaunchAgent 설정
- Python 캐시

## 프로젝트 상태

작고 실용적이며 의도적으로 단순하게 유지합니다. Python 표준 라이브러리만 사용합니다.

검색 결과는 후보 샘플이며 모든 GitHub 저장소를 포함하지 않습니다. 저장소당 최대 1,600개의 스냅샷을 보관합니다. 실제 기록 기간은 수집 빈도에 따라 달라집니다. 관측이 없거나 오래되었다고 해서 증가량이 0인 것은 아닙니다.

다국어 버전은 문서만 번역합니다. 터미널 메시지는 영어와 중국어로 유지됩니다.
