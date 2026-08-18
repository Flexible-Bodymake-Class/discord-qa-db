# FBC Q&A サイト更新スクリプト
# 使い方:
#   1. DiscordChatExporter で最新をエクスポート（output.json を更新）
#   2. この discord-qa-db フォルダで .\update.ps1 を実行
#
# 処理: parse_qa.py（構造化）-> export_csv.py --since（差分抽出）-> append_to_sheet.py（スプレッドシートに自動追記）
# 成果物: 差分のQ&Aがスプレッドシートに追記される（サイトはCSVを直接読むため自動反映）

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "=== FBC Q&A サイト更新 ===" -ForegroundColor Cyan

# 入力チェック
if (-not (Test-Path "C:\Users\tomo4\tools\discord-chat-exporter\output.json")) {
    Write-Host "エラー: output.json が見つかりません。先にDiscordChatExporterでエクスポートしてください。" -ForegroundColor Red
    exit 1
}

# ① 構造化
Write-Host "`n[1/3] parse_qa.py 実行中..." -ForegroundColor Yellow
python -u parse_qa.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "parse_qa.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

# ② 差分CSV抽出
Write-Host "`n[2/3] export_csv.py --since 実行中..." -ForegroundColor Yellow
python -u export_csv.py --since
if ($LASTEXITCODE -ne 0) {
    Write-Host "export_csv.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

# ③ スプレッドシートに自動追記
Write-Host "`n[3/3] append_to_sheet.py 実行中..." -ForegroundColor Yellow
python -u append_to_sheet.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "append_to_sheet.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 更新完了 ===" -ForegroundColor Green
Write-Host "非公開にしたい行があれば、スプレッドシートの「非公開」列にチェックしてください。"
