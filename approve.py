"""
Q&A レビューツール
未承認の Q&A をブラウザで確認し、承認/保留を管理する

使い方:
  python approve.py
  → ブラウザが自動で開きます
  → チェックして「承認して保存」を押すとサーバーが終了します
  → その後 build_search.py を実行してサイトを更新してください
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8")

QA_FILE = "qa_pairs.json"
PORT = 8765

_server_instance = None


def load_qa():
    with open(QA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_qa(data):
    with open(QA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


REVIEW_HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Q&A レビュー — FBC</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif;
  background: #faf9f7;
  color: #333;
  line-height: 1.6;
}
.container { max-width: 800px; margin: 0 auto; padding: 16px; }

.header {
  text-align: center;
  padding: 24px 0 20px;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}
.header h1 { font-size: 1.4rem; color: #e67e22; margin-bottom: 6px; }
.header p { font-size: 0.9rem; color: #888; }

.actions {
  position: sticky;
  top: 0;
  background: #faf9f7;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
  z-index: 100;
  display: flex;
  gap: 8px;
  align-items: center;
}
.btn-save {
  padding: 10px 24px;
  background: #27ae60;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:hover { background: #229954; }
.btn-select-all {
  padding: 8px 14px;
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
}
.btn-select-all:hover { border-color: #aaa; }
.selected-count { font-size: 0.85rem; color: #27ae60; font-weight: 600; margin-left: 4px; }

.qa-item {
  background: #fff;
  border: 1.5px solid #eee;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.qa-item:hover { border-color: #ccc; }
.qa-item.checked { border-color: #27ae60; background: #f0faf4; }

.qa-item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid #ddd;
  border-radius: 5px;
  flex-shrink: 0;
  margin-top: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.15s;
  color: transparent;
}
.qa-item.checked .checkbox {
  background: #27ae60;
  border-color: #27ae60;
  color: #fff;
}

.qa-content { flex: 1; min-width: 0; }
.qa-meta { font-size: 0.78rem; color: #aaa; margin-bottom: 5px; }
.qa-question {
  font-weight: 600;
  font-size: 0.93rem;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}
.qa-no-answer { font-size: 0.78rem; color: #bbb; margin-top: 6px; }
.toggle-answer-btn {
  font-size: 0.75rem;
  color: #e67e22;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  margin-top: 6px;
  display: block;
}
.qa-answer {
  display: none;
  margin-top: 8px;
  padding: 12px;
  background: #faf9f7;
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  border-left: 3px solid #e67e22;
}
.qa-answer.show { display: block; }

.empty-state { text-align: center; padding: 60px 16px; color: #bbb; }
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }

.done-state { text-align: center; padding: 48px 16px; }
.done-state h2 { font-size: 1.3rem; color: #27ae60; margin-bottom: 8px; }
.done-state p { color: #888; font-size: 0.9rem; }

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: #27ae60;
  color: #fff;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  display: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Q&A レビュー</h1>
    <p id="headerSub">読み込み中...</p>
  </div>

  <div class="actions" id="actions" style="display:none">
    <button class="btn-save" onclick="saveApprovals()">✅ 承認して保存</button>
    <button class="btn-select-all" onclick="selectAll()">すべて選択</button>
    <span class="selected-count" id="selectedCount">0件選択中</span>
  </div>

  <div id="list"></div>
</div>
<div class="toast" id="toast"></div>

<script>
let qaData = [];
let selected = new Set();

async function init() {
  const res = await fetch('/api/qa');
  qaData = await res.json();

  if (qaData.length === 0) {
    document.getElementById('headerSub').textContent = '承認待ちのQ&Aはありません';
    document.getElementById('list').innerHTML =
      '<div class="empty-state"><div class="icon">✅</div><p>すべてのQ&Aが確認済みです</p></div>';
    return;
  }

  document.getElementById('headerSub').textContent =
    `承認待ち ${qaData.length} 件 — 公開するものにチェックして「承認して保存」`;
  document.getElementById('actions').style.display = 'flex';
  renderList();
}

function renderList() {
  document.getElementById('list').innerHTML = qaData.map((qa, i) => {
    const hasAnswer = qa.answer && qa.answer.trim();
    return `
      <div class="qa-item" id="item-${i}" onclick="toggleItem(${i})">
        <div class="qa-item-row">
          <div class="checkbox" id="cb-${i}">✓</div>
          <div class="qa-content">
            <div class="qa-meta">👤 ${esc(qa.question_author)} · 📅 ${qa.date}</div>
            <div class="qa-question">${esc(qa.question)}</div>
            ${hasAnswer
              ? `<button class="toggle-answer-btn" onclick="event.stopPropagation(); toggleAnswer(${i})">回答を見る ▼</button>
                 <div class="qa-answer" id="ans-${i}">${esc(qa.answer)}</div>`
              : `<div class="qa-no-answer">💡 テキスト回答なし（LIVEで回答済みの可能性あり）</div>`}
          </div>
        </div>
      </div>`;
  }).join('');
  updateCount();
}

function toggleItem(i) {
  const id = qaData[i].message_id;
  const item = document.getElementById('item-' + i);
  if (selected.has(id)) {
    selected.delete(id);
    item.classList.remove('checked');
  } else {
    selected.add(id);
    item.classList.add('checked');
  }
  updateCount();
}

function selectAll() {
  qaData.forEach((qa, i) => {
    selected.add(qa.message_id);
    document.getElementById('item-' + i).classList.add('checked');
  });
  updateCount();
}

function updateCount() {
  document.getElementById('selectedCount').textContent = `${selected.size}件選択中`;
}

function toggleAnswer(i) {
  const el = document.getElementById('ans-' + i);
  const btn = el.previousElementSibling;
  const open = el.classList.toggle('show');
  btn.textContent = open ? '回答を閉じる ▲' : '回答を見る ▼';
}

async function saveApprovals() {
  const res = await fetch('/api/approve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved: [...selected] })
  });
  if (!res.ok) { alert('保存に失敗しました'); return; }

  showToast(`✅ ${selected.size}件を承認しました`);
  document.getElementById('actions').style.display = 'none';
  document.getElementById('list').innerHTML = `
    <div class="done-state">
      <h2>✅ 完了！</h2>
      <p>${selected.size} 件を承認しました。</p>
      <p style="margin-top:8px">このウィンドウを閉じて、build_search.py を実行してサイトを更新してください。</p>
    </div>`;

  setTimeout(async () => {
    await fetch('/api/shutdown', { method: 'POST' }).catch(() => {});
  }, 1500);
}

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s || '';
  return d.innerHTML;
}

init();
</script>
</body>
</html>"""


class ReviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            data = REVIEW_HTML.encode("utf-8")
            self._respond(200, "text/html; charset=utf-8", data)
        elif path == "/api/qa":
            pending = [qa for qa in load_qa() if qa.get("approved") is None]
            data = json.dumps(pending, ensure_ascii=False).encode("utf-8")
            self._respond(200, "application/json; charset=utf-8", data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if path == "/api/approve":
            qa_data = load_qa()
            approved_ids = set(body.get("approved", []))
            for qa in qa_data:
                if qa["message_id"] in approved_ids:
                    qa["approved"] = True
            save_qa(qa_data)
            self._respond(200, "application/json", json.dumps({"ok": True}).encode())

        elif path == "/api/shutdown":
            self.send_response(200)
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        else:
            self.send_response(404)
            self.end_headers()

    def _respond(self, status, content_type, data):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)


def main():
    if not os.path.exists(QA_FILE):
        print(f"エラー: {QA_FILE} が見つかりません。parse_qa.py を先に実行してください。")
        sys.exit(1)

    qa_data = load_qa()
    pending = [qa for qa in qa_data if qa.get("approved") is None]

    print(f"=== Q&A レビュー ===")
    print(f"全件数:      {len(qa_data)} 件")
    print(f"承認済み:    {sum(1 for q in qa_data if q.get('approved') is True)} 件")
    print(f"承認待ち:    {len(pending)} 件")

    if not pending:
        print("\n承認待ちの Q&A はありません。終了します。")
        return

    server = HTTPServer(("localhost", PORT), ReviewHandler)

    def open_browser():
        import time
        time.sleep(0.5)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()
    print(f"\nブラウザを開いています → http://localhost:{PORT}")
    print("「承認して保存」ボタンを押すとサーバーが自動終了します")
    print("手動終了: Ctrl+C\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    print("\n完了！build_search.py を実行してサイトを更新してください。")


if __name__ == "__main__":
    main()
