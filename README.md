# FBCサロン Q&A 検索アプリ

DiscordのQ&Aチャンネルの質問と回答を検索できるWebサイト。
GitHub Pages で公開中。

---

## 定期更新手順

### ① Discordからエクスポート（手動）

`discord-chat-exporter` フォルダで以下を実行。  
`TOKEN` は Discord の認証トークンに差し替える。

```powershell
cd "C:\Users\tomo4\workspace\01_work\03_clients\01_LYNO\04_DEV\検索サイト開発_FBC\discord-chat-exporter"
.\DiscordChatExporter.Cli.exe export -t "TOKEN" -c 1444479247669530664 -f Json -o output.json
```

> トークンの取得方法：ブラウザでDiscordを開く → F12 → Network タブ → 任意のチャンネルをクリック → messages リクエストの Authorization ヘッダーの値

### ② サイトデータを更新（ワンコマンド）

```powershell
cd "C:\Users\tomo4\workspace\01_work\03_clients\01_LYNO\04_DEV\検索サイト開発_FBC\discord-qa-db"
.\update.ps1
```

search.html と index.html が最新Q&Aで自動再生成される。

### ③ GitHubにpushしてサイト反映

```powershell
git add index.html search.html qa_pairs.json
git commit -m "Q&Aを最新データに更新"
git push origin master
```

pushするだけで GitHub Pages に自動反映される（数分待つ）。

---

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `index.html` | 公開サイト本体（GitHub Pages がここを配信） |
| `search.html` | index.html と同一内容（ローカル確認用） |
| `qa_pairs.json` | Q&Aマスターデータ（156→295件） |
| `parse_qa.py` | output.json → qa_pairs.json に変換 |
| `build_search.py` | qa_pairs.json → HTML生成（index.html / search.html 同時出力） |
| `export_csv.py` | qa_pairs.json → Notion取り込み用CSV変換 |
| `update.ps1` | ②と③の間：parse → build を一発実行するスクリプト |

---

## 処理フロー

```
Discord質問部屋
  ↓ ①DiscordChatExporter
output.json（生データ）
  ↓ ②update.ps1 → parse_qa.py
qa_pairs.json（マスターデータ）
  ↓ update.ps1 → build_search.py
index.html / search.html（サイト本体）
  ↓ ③git push
GitHub Pages（公開サイト）
```

---

## GitHubアカウント切替が必要な場合

pushが403エラーになったら `tomoyo493` に切り替える。

```powershell
gh auth switch --user tomoyo493
gh auth setup-git
```
