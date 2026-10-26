# GitHub Star Watch

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

GitHub リポジトリのスター数を定期的に記録し、直近の増加速度から急成長中のプロジェクトを見つけます。

AI エージェント、MCP、コーディングエージェント用プラグイン、agent skills、新しいオープンソースツールなど、変化の速い開発者向けツールの動向を追うためのシンプルなツールです。

## 動作要件

- Python 3.10 以降。
- Python 標準ライブラリのみを使用し、追加パッケージは不要です。
- GitHub API にアクセスできるインターネット接続。

以下は macOS／Linux シェルの例です。Windows では `python3` を `py -3` に置き換え、トークンは下記の PowerShell の例で設定してください。

## 機能

- 最近活動した、または新しく作成されたリポジトリから、スター数の条件を満たすものを検索。
- スター数のスナップショットをローカルの JSON データベースに保存。
- 直近の時間枠でスター数の増加を計算。
- 増加数、時間あたりの増加数、総スター数、言語、説明、URL をランキングに表示。
- 1 回だけの実行と、バックグラウンドでの継続監視に対応。

## クイックスタート

```bash
python3 github_star_watch.py --once
```

初回は基準となるスナップショットを保存します。しばらく待ってから再実行すると、増加を計算できます。

```bash
python3 github_star_watch.py --once
```

継続監視：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

## GitHub Token

トークンなしでも実行できますが、未認証 API の利用上限は低くなります。継続監視では自分のトークンの使用を推奨します。

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Windows PowerShell の場合：

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

これはプレースホルダーです。自分のトークンをローカルで設定してください。トークン、ログ、スナップショットのデータベースを Git にコミットしないでください。

## よく使うコマンド

収集を 1 回実行：

```bash
python3 github_star_watch.py --once
```

30 分ごとに監視：

```bash
python3 github_star_watch.py --watch --interval-minutes 30
```

プログラミング言語で絞り込み：

```bash
python3 github_star_watch.py --watch --language Python
```

スター数の条件を下げ、より初期段階のプロジェクトを検索：

```bash
python3 github_star_watch.py --watch --min-stars 20 --days 7
```

表示件数を増やす：

```bash
python3 github_star_watch.py --once --limit 50
```

ローカルデータベースのパスを指定：

```bash
python3 github_star_watch.py --watch --db data/star_snapshots.json
```

## ランキングの計算

主に、時間あたりのスター増加速度で並べ替えます。

```text
stars_per_hour = star_delta / elapsed_hours
```

リポジトリを初めて見つけた時点では基準のみを保存します。速度の計算には、その後のスナップショットが必要です。

## 出力例

```text
Top 20 fastest-growing GitHub repos
------------------------------------------------------------------------------------------------
 1. owner/repo  +227 stars / 1.0h  (225.8/h, total 41920, JavaScript)
    Short repository description...
    https://github.com/owner/repo
```

日次レポートの書式は [`examples/sample_report.md`](examples/sample_report.md) を参照してください。

監視プログラムはターミナルにランキングを出力します。日付付きの完全な日次レポートの作成は別のワークフローです。この例はテンプレートであり、自動レポート生成機能ではありません。

## macOS LaunchAgent

macOS のバックグラウンドで実行する場合は、[`launchd/com.example.github-star-watch.plist`](launchd/com.example.github-star-watch.plist) を編集してください。

読み込む前に、プログラム、作業ディレクトリ、ログのパスを自分の環境に合わせて変更します。

## リポジトリのデータ管理

リポジトリにはソースとサンプルのみを含めます。次の実行時データや個人用ファイルは、既定で Git の管理対象外です。

- `star_snapshots.json`
- `*.log`
- `daily_reports/`
- 個人用パスを含むローカルの LaunchAgent 設定
- Python のキャッシュ

## プロジェクトの状態

小さく実用的で、意図的にシンプルな構成です。Python 標準ライブラリのみを使用します。

検索結果は候補のサンプルであり、GitHub 全体を網羅するものではありません。各リポジトリで最大 1,600 件のスナップショットを保持します。履歴の長さは収集頻度によって変わります。観測の欠落や古いデータは、増加がゼロであることを意味しません。

多言語対応はドキュメントのみです。ターミナルのメッセージは英語と中国語のままです。
