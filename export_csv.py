"""
Q&A JSON → Notion用CSV変換
"""
import json
import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "qa_pairs.json"
OUTPUT_FILE = "qa.csv"


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Header row matching our Notion DB design
        writer.writerow([
            "非公開",           # Checkbox — check to HIDE from site
            "質問",             # Title
            "回答",             # Text
            "質問者",           # Select
            "回答者",           # Select
            "日付",             # Date
            "Discord元リンク",  # URL
            "回答数"            # Number
        ])

        for qa in qa_pairs:
            # Only export Q&As that have a text answer
            if not qa.get('answer', '').strip():
                continue

            answer_authors = ", ".join(qa['answer_authors']) if qa['answer_authors'] else ""

            writer.writerow([
                "",                                        # 非公開（デフォルト空欄）
                qa['question'].replace('\n', ' '),        # 質問
                qa['answer'],                             # 回答
                qa['question_author'],                    # 質問者
                answer_authors,                           # 回答者
                qa['date'],                               # 日付
                qa['discord_url'],                        # Discord元リンク
                qa['reply_count']                         # 回答数
            ])

    answered = sum(1 for qa in qa_pairs if qa.get('answer', '').strip())
    print(f"CSV exported: {OUTPUT_FILE}")
    print(f"Total rows: {answered} (回答あり / {len(qa_pairs)} 件中)")


if __name__ == '__main__':
    main()
