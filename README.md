# FBCサロン Q&A 検索アプリ

DiscordのQ&Aチャンネルの質問と回答を検索できるWebサイト。
GitHub Pages で公開中。

サイトはGoogleスプレッドシート(`qa_master`シート)を「ウェブに公開」したCSVを直接読み込んで表示する仕組み。スプレッドシートを更新すれば、サイトは自動的に最新データを表示する(pushは不要)。

スプレッドシート: https://docs.google.com/spreadsheets/d/1S9QY_faN0O4_He7f2DbGO60bEvz_PfTk-K78EHsIRD0/edit?gid=0#gid=0

---

## 定期更新手順

### ① Discordからエクスポート（手動）

`discord-chat-exporter` フォルダで以下を実行。
`TOKEN` は Discord の認証トークンに差し替える。

```powershell
cd "C:\Users\tomo4\tools\discord-chat-exporter"
.\DiscordChatExporter.Cli.exe export -t "TOKEN" -c 1444479247669530664 -f Json -o output.json
```

> トークンの取得方法：ブラウザでDiscordを開く → F12 → Network タブ → 任意のチャンネルをクリック → messages リクエストの Authorization ヘッダーの値

### ② スプレッドシートに自動反映（ワンコマンド）

```powershell
cd "C:\Users\tomo4\workspace\01_work\03_clients\01_LYNO\04_DEV\質問検索サイト開発_FBC\discord-qa-db"
.\update.ps1
```

Discordの差分Q&Aが自動でスプレッドシート(`qa_master`シート)に追記される。手動でのCSVインポート作業は不要。

### ③ 非公開にしたい質問があれば手動チェック

スプレッドシートを開いて、非公開にしたい行の「非公開」列に `TRUE` と入力して保存する。サイトはCSVを直接読むので、保存するだけで即座に反映される。

---

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `index.html` | 公開サイト本体（GitHub Pages がここを配信、スプレッドシートのCSVをfetchして表示） |
| `parse_qa.py` | output.json → qa_pairs.json に変換（質問と回答をペアリング） |
| `export_csv.py --since` | qa_pairs.json → 前回以降の差分を qa.csv に出力 |
| `append_to_sheet.py` | qa.csv をスプレッドシート(qa_master)に自動追記 |
| `update.ps1` | parse → export_csv --since → append_to_sheet を一発実行 |
| `credentials/service-account-key.json` | Google Sheets APIの認証情報（Gitには含まれない・各自のPCに個別配置） |
| `last_exported.txt` | 前回エクスポート済みの最新日付（差分抽出の基準・自動更新される） |

### 現在使用していないファイル（過去の設計の名残）

CSV fetch型に移行する前、qa_pairs.jsonをHTMLに直接埋め込んでいた頃の名残。**実行するとindex.htmlが古い形式で上書きされ、サイトが壊れる**ので使わないこと。

| ファイル | 備考 |
|---------|------|
| `build_search.py` | qa_pairs.json埋め込み型のHTML生成（今のCSV fetch型サイトとは別方式） |
| `approve.py` | ローカルレビューUI（非公開判定は今スプレッドシート側で行っているため未使用） |
| `search.html` | build_search.pyの出力先（同上） |

---

## 処理フロー

```
Discord質問部屋
  ↓ ①DiscordChatExporter（手動）
output.json（生データ）
  ↓ update.ps1 → parse_qa.py
qa_pairs.json（マスターデータ）
  ↓ update.ps1 → export_csv.py --since
qa.csv（差分のみ）
  ↓ update.ps1 → append_to_sheet.py
Googleスプレッドシート（qa_master シート）
  ↓ 「ウェブに公開」CSV を index.html が fetch
GitHub Pages（公開サイト）
```

---

## GitHubアカウント切替が必要な場合

index.htmlのデザインや機能自体を変更してpushする場合のみ必要。通常の定期更新ではpush不要。

```powershell
gh auth switch -u Flexible-Bodymake-Class
gh auth status
```
