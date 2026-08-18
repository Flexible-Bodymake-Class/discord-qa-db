"""
Q&A JSON → CSV変換

使い方:
  python export_csv.py          # 全件出力
  python export_csv.py --since  # 未送信の差分のみ出力（exported_ids.json を参照）
"""
import json
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "qa_pairs.json"
OUTPUT_FILE = "qa.csv"
EXPORTED_IDS_FILE = "exported_ids.json"


def load_exported_ids():
    try:
        with open(EXPORTED_IDS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_exported_ids(ids):
    with open(EXPORTED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(ids), f, ensure_ascii=False, indent=2)


def main():
    since_mode = '--since' in sys.argv

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)

    # 回答ありのみに絞る
    answered = [qa for qa in qa_pairs if qa.get('answer', '').strip()]

    # --since モード: まだスプレッドシートに送っていないものだけ（message_id基準）
    exported_ids = load_exported_ids()
    if since_mode:
        before = len(answered)
        answered = [qa for qa in answered if qa['message_id'] not in exported_ids]
        print(f"差分モード: 未送信の Q&A を抽出（回答あり {before} 件中 {len(answered)} 件が未送信）")

    if not answered:
        print("新しい Q&A はありません。")
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        return

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "非公開",
            "質問",
            "回答",
            "質問者",
            "回答者",
            "日付",
            "Discord元リンク",
            "回答数"
        ])
        for qa in answered:
            answer_authors = ", ".join(qa['answer_authors']) if qa['answer_authors'] else ""
            writer.writerow([
                "",
                qa['question'].replace('\n', ' '),
                qa['answer'],
                qa['question_author'],
                answer_authors,
                qa['date'],
                qa['discord_url'],
                qa['reply_count']
            ])

    # 送信済みIDを更新（--since モードのみ）
    if since_mode:
        exported_ids.update(qa['message_id'] for qa in answered)
        save_exported_ids(exported_ids)

    total_answered = sum(1 for qa in qa_pairs if qa.get('answer', '').strip())
    label = "差分（未送信分）" if since_mode else "全件"
    print(f"CSV exported: {OUTPUT_FILE}")
    print(f"出力件数: {len(answered)} 件（{label} / 回答あり {total_answered} 件中）")


if __name__ == '__main__':
    main()
