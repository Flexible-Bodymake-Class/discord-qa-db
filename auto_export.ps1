# FBC Q&A 自動更新スクリプト（タスクスケジューラから毎週火曜19時に実行）
# 処理: Discordエクスポート -> update.ps1（parse -> 差分抽出 -> スプシ追記）
# 非公開判断（スプシの「非公開」列チェック）だけは人間が引き続き手動で行う

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot
$exporterRoot = "C:\Users\tomo4\tools\discord-chat-exporter"
$channelId = "1444479247669530664"
$tokenPath = Join-Path $repoRoot "token.txt"

$logDir = Join-Path $repoRoot "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir ("auto_export_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

Start-Transcript -Path $logFile -Append

try {
    Write-Host "=== FBC Q&A 自動更新開始: $(Get-Date) ===" -ForegroundColor Cyan

    if (-not (Test-Path $tokenPath)) {
        throw "token.txt が見つかりません: $tokenPath"
    }
    $token = (Get-Content $tokenPath -Raw).Trim()

    Write-Host "`n[1/2] Discordエクスポート実行中..." -ForegroundColor Yellow
    Set-Location -Path $exporterRoot
    & .\DiscordChatExporter.Cli.exe export -t $token -c $channelId -f Json -o output.json
    if ($LASTEXITCODE -ne 0) {
        throw "DiscordChatExporter が失敗しました（終了コード: $LASTEXITCODE）"
    }

    Write-Host "`n[2/2] update.ps1 実行中..." -ForegroundColor Yellow
    Set-Location -Path $repoRoot
    & .\update.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "update.ps1 が失敗しました（終了コード: $LASTEXITCODE）"
    }

    Write-Host "`n=== 自動更新完了: $(Get-Date) ===" -ForegroundColor Green
}
catch {
    Write-Host "`n=== エラー発生: $($_.Exception.Message) ===" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

Stop-Transcript
