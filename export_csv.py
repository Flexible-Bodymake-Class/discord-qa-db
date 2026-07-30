"""
Q&A JSON → CSV変換

使い方:
  python export_csv.py          # 全件出力
  python export_csv.py --since  # 前回以降の差分のみ出力（last_exported.txt を参照）
"""
import json
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "qa_pairs.json"
OUTPUT_FILE = "qa.csv"
LAST_EXPORTED_FILE = "last_exported.txt"


def load_last_date():
    try:
        with open(LAST_EXPORTED_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_date(date):
    with open(LAST_EXPORTED_FILE, 'w', encoding='utf-8') as f:
        f.write(date)


def main():
    since_mode = '--since' in sys.argv

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)

    # 回答ありのみに絞る
    answered = [qa for qa in qa_pairs if qa.get('answer', '').strip()]

    # --since モード: 前回の最終日付より新しいものだけ
    since_date = None
    if since_mode:
        since_date = load_last_date()
        if since_date:
            print(f"差分モード: {since_date} より新しい Q&A を抽出")
            answered = [qa for qa in answered if qa['date'] > since_date]
        else:
            print("last_exported.txt が見つかりません。全件出力します。")

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

    # 最終日付を保存（全件中の最新日付）
    latest_date = max(qa['date'] for qa in answered)
    save_last_date(latest_date)

    total_answered = sum(1 for qa in qa_pairs if qa.get('answer', '').strip())
    label = f"差分（{since_date} 以降）" if since_date else "全件"
    print(f"CSV exported: {OUTPUT_FILE}")
    print(f"出力件数: {len(answered)} 件（{label} / 回答あり {total_answered} 件中）")
    print(f"次回 --since 用の日付を保存: {latest_date}")


if __name__ == '__main__':
    main()
