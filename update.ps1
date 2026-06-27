# FBC Q&A サイト更新スクリプト
# 使い方:
#   1. DiscordChatExporter で最新をエクスポート（output.json を更新）
#   2. この discord-qa-db フォルダで .\update.ps1 を実行
#
# 処理: parse_qa.py（構造化）-> approve.py（レビュー）-> build_search.py（HTML生成）
# 成果物: search.html / index.html を最新Q&Aで再生成する

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Get-QaCount {
    if (Test-Path "qa_pairs.json") {
        return (Get-Content "qa_pairs.json" -Raw -Encoding UTF8 | ConvertFrom-Json).Count
    }
    return 0
}

Write-Host "=== FBC Q&A サイト更新 ===" -ForegroundColor Cyan

# 入力チェック
if (-not (Test-Path "..\discord-chat-exporter\output.json")) {
    Write-Host "エラー: output.json が見つかりません。先にDiscordChatExporterでエクスポートしてください。" -ForegroundColor Red
    exit 1
}

$before = Get-QaCount
Write-Host "更新前のQ&A件数: $before 件"

# ① 構造化
Write-Host "`n[1/3] parse_qa.py 実行中..." -ForegroundColor Yellow
python parse_qa.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "parse_qa.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

# ② レビュー（承認待ちがあればブラウザが開く）
Write-Host "`n[2/3] approve.py 実行中（ブラウザでレビュー）..." -ForegroundColor Yellow
python approve.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "approve.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

# ③ HTML生成（承認済みのみ）
Write-Host "`n[3/3] build_search.py 実行中..." -ForegroundColor Yellow
python build_search.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "build_search.py が失敗しました。中断します。" -ForegroundColor Red
    exit 1
}

$after = Get-QaCount
$diff = $after - $before

Write-Host "`n=== 更新完了 ===" -ForegroundColor Green
Write-Host "Q&A件数: $before -> $after 件 (+$diff)"
Write-Host "更新ファイル: search.html / index.html"
