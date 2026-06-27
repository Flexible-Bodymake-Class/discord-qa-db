"""
FBC Q&A 検索ページビルダー
qa_pairs.json → タグ自動付与 → search.html 生成
"""
import json
import sys
import html as html_mod

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "qa_pairs.json"
OUTPUT_FILE = "search.html"
# Published copy served to users. Kept in sync with OUTPUT_FILE automatically
# so we never forget to copy search.html -> index.html after a rebuild.
PUBLISH_FILE = "index.html"

# Tag definitions: keyword -> tag name
TAG_RULES = {
    # Body parts
    "股関節": "股関節",
    "膝": "膝",
    "足首": "足首",
    "アーカイブ": "アーカイブ",
    "お尻": "お尻",
    "臀筋": "お尻",
    "腰": "腰",
    "肩": "肩",
    "肩甲骨": "肩",
    "背中": "背中",
    "肋骨": "肋骨",
    "前もも": "前もも",
    "前腿": "前もも",
    "内もも": "内もも",
    "内転筋": "内もも",
    "腸腰筋": "腸腰筋",
    "骨盤": "骨盤",
    "胸椎": "背中",
    "脛": "脛",
    "ふくらはぎ": "ふくらはぎ",
    "首": "首",
    # Exercise types
    "ストレッチ": "ストレッチ",
    "開脚": "開脚",
    "ヨガ": "ヨガ",
    "ダウンドッグ": "ヨガ",
    "スワン": "スワン",
    "ピジョン": "ピジョン",
    "トレーニング": "トレーニング",
    "筋トレ": "トレーニング",
    "リリース": "リリース",
    "筋膜": "リリース",
    # Symptoms
    "痛み": "痛み",
    "痛い": "痛み",
    "痛く": "痛み",
    "硬い": "柔軟性",
    "硬さ": "柔軟性",
    "柔軟": "柔軟性",
    "可動域": "柔軟性",
    "姿勢": "姿勢",
    "猫背": "姿勢",
    "反り腰": "姿勢",
    "X脚": "脚の形",
    "O脚": "脚の形",
}

# Tag colors (CSS classes)
TAG_COLORS = {
    # Body parts - warm tones
    "股関節": "#e74c3c",
    "膝": "#e67e22",
    "足首": "#f39c12",
    "アーカイブ": "#8e44ad",
    "お尻": "#d35400",
    "腰": "#c0392b",
    "肩": "#2980b9",
    "背中": "#3498db",
    "肋骨": "#1abc9c",
    "前もも": "#e74c3c",
    "内もも": "#e74c3c",
    "腸腰筋": "#9b59b6",
    "骨盤": "#8e44ad",
    "脛": "#f39c12",
    "ふくらはぎ": "#e67e22",
    "首": "#2980b9",
    # Exercise types - cool tones
    "ストレッチ": "#27ae60",
    "開脚": "#2ecc71",
    "ヨガ": "#16a085",
    "トレーニング": "#2c3e50",
    "リリース": "#1abc9c",
    "スワン": "#16a085",
    "ピジョン": "#1abc9c",
    # Symptoms - neutral
    "痛み": "#e74c3c",
    "柔軟性": "#3498db",
    "姿勢": "#9b59b6",
    "脚の形": "#e67e22",
}


def auto_tag(qa):
    """Auto-generate tags from question + answer text"""
    text = (qa["question"] + " " + qa.get("answer", "")).lower()
    # Japanese doesn't need lowering but keep for safety
    text_orig = qa["question"] + " " + qa.get("answer", "")

    tags = set()
    for keyword, tag in TAG_RULES.items():
        if keyword in text_orig:
            tags.add(tag)

    # Status tag
    if qa.get("answer") and qa["answer"].strip():
        tags.add("回答済み")
    else:
        tags.add("LIVE回答")

    return sorted(tags)


def escape_js_string(s):
    """Escape string for embedding in JS"""
    return (s
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("$", "\\$")
            .replace("</", "<\\/"))


def build_html(qa_pairs):
    """Generate the search.html file"""

    # Add tags to each QA pair
    for qa in qa_pairs:
        qa["tags"] = auto_tag(qa)

    # Collect all unique tags and their counts
    tag_counts = {}
    for qa in qa_pairs:
        for tag in qa["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort tags: status first, then by count
    status_tags = ["回答済み", "LIVE回答"]
    other_tags = sorted(
        [t for t in tag_counts if t not in status_tags],
        key=lambda t: -tag_counts[t]
    )

    # Place アーカイブ just before お尻 regardless of count
    if "アーカイブ" in other_tags and "お尻" in other_tags:
        other_tags.remove("アーカイブ")
        other_tags.insert(other_tags.index("お尻"), "アーカイブ")

    # Answered count
    answered = sum(1 for qa in qa_pairs if "回答済み" in qa["tags"])
    total = len(qa_pairs)

    # JSON data for embedding
    qa_json = json.dumps(qa_pairs, ensure_ascii=False)

    # Tag colors JSON
    colors_json = json.dumps(TAG_COLORS, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FBCサロン Q&A 検索</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans",
    "Noto Sans JP", sans-serif;
  background: #faf9f7;
  color: #333;
  line-height: 1.6;
}}

.container {{
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
}}

/* Header */
.header {{
  text-align: center;
  padding: 32px 0 24px;
}}
.header h1 {{
  font-size: 1.5rem;
  color: #e67e22;
  margin-bottom: 8px;
}}
.header p {{
  color: #888;
  font-size: 0.9rem;
}}
.stats {{
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
  font-size: 0.85rem;
}}
.stats span {{
  background: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #eee;
}}

/* Search */
.search-box {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: #faf9f7;
  padding: 12px 0;
}}
.search-input {{
  width: 100%;
  padding: 14px 20px;
  font-size: 1rem;
  border: 2px solid #e0ddd8;
  border-radius: 12px;
  outline: none;
  background: #fff;
  transition: border-color 0.2s;
}}
.search-input:focus {{
  border-color: #e67e22;
}}
.search-input::placeholder {{
  color: #bbb;
}}

/* Tags */
.tag-section {{
  padding: 8px 0 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}}
.tag-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}}
.tag-btn {{
  padding: 4px 12px;
  border-radius: 20px;
  border: 1.5px solid #ddd;
  background: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  color: #666;
}}
.tag-btn:hover {{
  border-color: #e67e22;
  color: #e67e22;
}}
.tag-btn.active {{
  background: #e67e22;
  border-color: #e67e22;
  color: #fff;
}}
.tag-btn .count {{
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 2px;
}}

/* Results */
.results-info {{
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 12px;
}}

.qa-card {{
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #eee;
  transition: box-shadow 0.2s;
}}
.qa-card:hover {{
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}}

.qa-question {{
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 8px;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}}
.qa-question-body {{
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}}
.qa-question-text {{
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.qa-question-text.expanded {{
  display: block;
  overflow: visible;
}}
.expand-btn {{
  align-self: flex-start;
  font-size: 0.75rem;
  color: #e67e22;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-weight: 500;
}}
.qa-question::before {{
  content: "Q";
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #e67e22;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}}

.qa-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.8rem;
  color: #999;
}}
.qa-meta .author {{
  color: #666;
}}

.qa-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}}
.qa-tag {{
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  color: #fff;
  font-weight: 500;
}}

.qa-answer-toggle {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid #e0ddd8;
  background: #faf9f7;
  font-size: 0.8rem;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}}
.qa-answer-toggle:hover {{
  background: #f0eeea;
}}
.qa-answer-toggle .arrow {{
  transition: transform 0.2s;
  font-size: 0.7rem;
}}
.qa-answer-toggle.open .arrow {{
  transform: rotate(90deg);
}}

.qa-answer {{
  display: none;
  margin-top: 12px;
  padding: 14px;
  background: #faf9f7;
  border-radius: 8px;
  font-size: 0.9rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  border-left: 3px solid #e67e22;
}}
.qa-answer.show {{
  display: block;
}}

.qa-answer-label {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #e67e22;
  margin-bottom: 8px;
}}
.qa-answer-label::before {{
  content: "A";
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 5px;
  background: #27ae60;
  color: #fff;
  font-size: 0.7rem;
}}

.no-answer {{
  color: #ccc;
  font-style: italic;
  font-size: 0.85rem;
  margin-top: 8px;
}}

.discord-link {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: #7289da;
  text-decoration: none;
  margin-top: 8px;
}}
.discord-link:hover {{
  text-decoration: underline;
}}

/* Highlight */
mark {{
  background: #ffeaa7;
  color: inherit;
  padding: 0 2px;
  border-radius: 2px;
}}

/* Empty state */
.empty-state {{
  text-align: center;
  padding: 48px 16px;
  color: #ccc;
}}
.empty-state .icon {{
  font-size: 3rem;
  margin-bottom: 12px;
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 32px 16px;
  margin-top: 24px;
  border-top: 1px solid #eee;
}}
.footer a {{
  display: inline-block;
  padding: 12px 24px;
  background: #7289da;
  color: #fff;
  text-decoration: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: opacity 0.2s;
}}
.footer a:hover {{
  opacity: 0.9;
}}
.footer p {{
  margin-top: 8px;
  font-size: 0.8rem;
  color: #999;
}}

/* Responsive */
@media (max-width: 480px) {{
  .header h1 {{ font-size: 1.3rem; }}
  .qa-card {{ padding: 14px; }}
}}
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>FBCサロン Q&A 検索</h1>
    <p>過去のQ&amp;Aから、あなたの悩みのヒントが見つかるかも！</p>
    <div class="stats">
      <span>📝 全 {total} 件</span>
      <span>✅ 回答済み {answered} 件</span>
    </div>
  </div>

  <div class="search-box">
    <input type="text" class="search-input" id="searchInput"
      placeholder="🔍 キーワードで検索（例：股関節 痛み）" autocomplete="off">
  </div>

  <div class="tag-section">
    <div class="tag-row" id="statusTags"></div>
    <div class="tag-row" id="categoryTags"></div>
  </div>

  <div class="results-info" id="resultsInfo"></div>
  <div id="results"></div>

  <div class="footer">
    <a href="https://discord.com/channels/1441619538293686387/1444479247669530664"
       target="_blank" rel="noopener">
      💬 質問部屋で新しい質問をする
    </a>
    <p>見つからない場合はDiscordで直接質問してください</p>
  </div>
</div>

<script>
// === Data ===
const QA_DATA = {qa_json};
const TAG_COLORS = {colors_json};
TAG_COLORS["回答済み"] = "#27ae60";
TAG_COLORS["LIVE回答"] = "#7289da";

const STATUS_TAGS = ["回答済み", "LIVE回答"];
const CATEGORY_TAGS = {json.dumps(other_tags, ensure_ascii=False)};

// === State ===
let activeTags = new Set(["回答済み"]);
let searchQuery = "";

// === Init ===
function init() {{
  renderTags();
  renderResults();
  document.getElementById("searchInput").addEventListener("input", (e) => {{
    searchQuery = e.target.value.trim();
    renderResults();
  }});
}}

function renderTags() {{
  const statusEl = document.getElementById("statusTags");
  const catEl = document.getElementById("categoryTags");

  statusEl.innerHTML = STATUS_TAGS.map(tag => {{
    const count = QA_DATA.filter(qa => qa.tags.includes(tag)).length;
    return `<button class="tag-btn ${{activeTags.has(tag) ? 'active' : ''}}" data-tag="${{tag}}" onclick="toggleTag('${{tag}}')">
      ${{tag}} <span class="count">${{count}}</span>
    </button>`;
  }}).join("");

  catEl.innerHTML = CATEGORY_TAGS.map(tag => {{
    const count = QA_DATA.filter(qa => qa.tags.includes(tag)).length;
    return `<button class="tag-btn ${{activeTags.has(tag) ? 'active' : ''}}" data-tag="${{tag}}" onclick="toggleTag('${{tag}}')">
      ${{tag}} <span class="count">${{count}}</span>
    </button>`;
  }}).join("");
}}

function toggleTag(tag) {{
  if (activeTags.has(tag)) {{
    activeTags.delete(tag);
  }} else {{
    activeTags.add(tag);
  }}
  document.querySelectorAll(".tag-btn").forEach(btn => {{
    btn.classList.toggle("active", activeTags.has(btn.dataset.tag));
  }});
  renderResults();
}}

function filterQA() {{
  let results = [...QA_DATA].sort((a, b) => b.date.localeCompare(a.date));

  // Filter by tags
  if (activeTags.size > 0) {{
    results = results.filter(qa =>
      [...activeTags].every(tag => qa.tags.includes(tag))
    );
  }}

  // Filter by search query
  if (searchQuery) {{
    const keywords = searchQuery.split(/\\s+/).filter(k => k.length > 0);
    results = results.filter(qa => {{
      const text = (qa.question + " " + qa.answer).toLowerCase();
      return keywords.every(kw => text.includes(kw.toLowerCase()));
    }});
  }}

  return results;
}}

function highlightText(text, maxLen) {{
  if (!text) return "";
  let display = text;
  if (maxLen && display.length > maxLen) {{
    display = display.substring(0, maxLen) + "...";
  }}
  if (!searchQuery) return escapeHtml(display);

  const keywords = searchQuery.split(/\\s+/).filter(k => k.length > 0);
  let result = escapeHtml(display);
  keywords.forEach(kw => {{
    const re = new RegExp("(" + escapeRegex(escapeHtml(kw)) + ")", "gi");
    result = result.replace(re, "<mark>$1</mark>");
  }});
  return result;
}}

function escapeHtml(s) {{
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}}

function escapeRegex(s) {{
  return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, "\\\\$&");
}}

function renderResults() {{
  const filtered = filterQA();
  const el = document.getElementById("results");
  const infoEl = document.getElementById("resultsInfo");

  if (searchQuery || activeTags.size > 0) {{
    infoEl.textContent = `${{filtered.length}} 件見つかりました`;
  }} else {{
    infoEl.textContent = `全 ${{QA_DATA.length}} 件のQ&A`;
  }}

  if (filtered.length === 0) {{
    el.innerHTML = `
      <div class="empty-state">
        <div class="icon">🔍</div>
        <p>該当するQ&Aが見つかりませんでした</p>
        <p style="margin-top:8px;font-size:0.85rem">
          キーワードを変えるか、質問部屋で直接質問してください
        </p>
      </div>`;
    return;
  }}

  el.innerHTML = filtered.map((qa, i) => {{
    const tagHtml = qa.tags.map(tag => {{
      const color = TAG_COLORS[tag] || "#999";
      return `<span class="qa-tag" style="background:${{color}}">${{tag}}</span>`;
    }}).join("");

    const hasAnswer = qa.answer && qa.answer.trim();
    const answerHtml = hasAnswer
      ? `<button class="qa-answer-toggle" onclick="toggleAnswer(this)">
           <span class="arrow">▶</span> 回答を見る
         </button>
         <div class="qa-answer" id="answer-${{i}}">
           <div class="qa-answer-label">回答</div>
           ${{escapeHtml(qa.answer).replace(/\\n/g, "<br>")}}
         </div>`
      : `<div class="no-answer">💡 質疑応答LIVEで回答済み（テキスト回答なし）</div>`;

    return `
      <div class="qa-card">
        <div class="qa-question" onclick="toggleAnswer(this.parentElement.querySelector('.qa-answer-toggle'))">
          <div class="qa-question-body" onclick="event.stopPropagation()">
            <span class="qa-question-text" id="q-text-${{i}}">${{highlightText(qa.question)}}</span>
            <button class="expand-btn" onclick="toggleExpand(this, 'q-text-${{i}}')">もっと見る ▼</button>
          </div>
        </div>
        <div class="qa-tags">${{tagHtml}}</div>
        <div class="qa-meta">
          <span class="author">👤 ${{escapeHtml(qa.question_author)}}</span>
          <span>📅 ${{qa.date}}</span>
          ${{qa.reply_count > 0 ? `<span>💬 ${{qa.reply_count}}件の返信</span>` : ""}}
        </div>
        ${{answerHtml}}
        <a class="discord-link" href="${{qa.discord_url}}" target="_blank" rel="noopener">
          🔗 Discordで見る
        </a>
      </div>`;
  }}).join("");

  // Hide expand buttons for questions that fit within 3 lines
  setTimeout(checkExpandButtons, 0);
}}

function toggleExpand(btn, textId) {{
  const el = document.getElementById(textId);
  const isExpanded = el.classList.contains('expanded');
  el.classList.toggle('expanded');
  btn.textContent = isExpanded ? 'もっと見る ▼' : '閉じる ▲';
}}

function checkExpandButtons() {{
  document.querySelectorAll('.qa-question-text').forEach(el => {{
    if (el.scrollHeight <= el.clientHeight + 2) {{
      const btn = el.nextElementSibling;
      if (btn) btn.style.display = 'none';
    }}
  }});
}}

function toggleAnswer(btn) {{
  if (!btn) return;
  const answer = btn.nextElementSibling;
  if (!answer) return;
  const isOpen = answer.classList.contains("show");
  answer.classList.toggle("show");
  btn.classList.toggle("open");
  btn.innerHTML = isOpen
    ? '<span class="arrow">▶</span> 回答を見る'
    : '<span class="arrow">▶</span> 回答を閉じる';
}}

// Start
init();
</script>
</body>
</html>'''

    return html


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    total_loaded = len(qa_pairs)
    qa_pairs = [qa for qa in qa_pairs if qa.get("approved") is True]
    print(f"Loaded {total_loaded} Q&A pairs ({len(qa_pairs)} approved, {total_loaded - len(qa_pairs)} pending review)")

    html = build_html(qa_pairs)

    # Write both the working file and the published copy in one pass
    for path in (OUTPUT_FILE, PUBLISH_FILE):
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {path}")

    print(f"File size: {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
