"""
Discord Q&A パーサー
エクスポートしたJSONから質問と回答のペアを抽出する
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = "../discord-chat-exporter/output.json"
OUTPUT_FILE = "qa_pairs.json"

GUILD_ID = "1441619538293686387"
CHANNEL_ID = "1444479247669530664"


def make_discord_url(guild_id, channel_id, message_id):
    """Discord message URL"""
    return f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"


def parse_qa(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    msgs = data['messages']

    # Build message index (id -> message)
    msg_index = {m['id']: m for m in msgs}

    # Collect Q&A pairs
    # Strategy: group replies by their reference (parent) message
    # A "question" = top-level Default message (not a reply)
    # An "answer" = Reply message pointing to a question

    qa_pairs = []

    # First pass: find all top-level questions (Default type, no reference)
    questions = []
    for m in msgs:
        if m['type'] == 'Default' and not m.get('reference'):
            questions.append(m)

    # Second pass: group replies by their root question
    # Some replies are to other replies (threaded conversation)
    # We trace back to find the root question
    def find_root(msg_id, depth=0):
        """Trace reply chain back to root question"""
        if depth > 20:
            return msg_id
        msg = msg_index.get(msg_id)
        if not msg:
            return msg_id
        ref = msg.get('reference')
        if ref and ref.get('messageId') and ref['messageId'] in msg_index:
            parent = msg_index[ref['messageId']]
            if parent['type'] == 'Default' and not parent.get('reference'):
                return parent['id']
            return find_root(ref['messageId'], depth + 1)
        return msg_id

    # Build threads: root_question_id -> [reply messages]
    threads = {}
    for m in msgs:
        if m['type'] == 'Reply':
            root_id = find_root(m['id'])
            if root_id not in threads:
                threads[root_id] = []
            threads[root_id].append(m)

    # Build Q&A pairs
    for q in questions:
        # Skip the pinned announcement message
        if q.get('isPinned') and '質問ボックス' in q.get('content', ''):
            continue

        # Skip empty messages
        if not q['content'].strip():
            continue

        replies = threads.get(q['id'], [])
        # Sort replies by timestamp
        replies.sort(key=lambda r: r['timestamp'])

        # Combine all replies into answer text
        answer_parts = []
        answer_authors = set()
        for r in replies:
            author = r['author']['nickname'] or r['author']['name']
            answer_authors.add(author)
            answer_parts.append(f"【{author}】\n{r['content']}")

        qa_pair = {
            "question": q['content'],
            "question_author": q['author']['nickname'] or q['author']['name'],
            "answer": "\n\n---\n\n".join(answer_parts) if answer_parts else "",
            "answer_authors": list(answer_authors),
            "date": q['timestamp'][:10],
            "discord_url": make_discord_url(GUILD_ID, CHANNEL_ID, q['id']),
            "reply_count": len(replies),
            "message_id": q['id']
        }
        qa_pairs.append(qa_pair)

    # Preserve approved status for existing entries.
    # Entries already in qa_pairs.json default to approved=True (already published).
    # Genuinely new entries get no approved field (treated as pending review).
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as ef:
            old_data = json.load(ef)
        existing_approved = {
            qa['message_id']: qa.get('approved', True)
            for qa in old_data
            if 'message_id' in qa
        }
        for qa in qa_pairs:
            mid = qa['message_id']
            if mid in existing_approved:
                qa['approved'] = existing_approved[mid]
            # else: new entry — leave without approved field (pending review)

    return qa_pairs


def main():
    qa_pairs = parse_qa(INPUT_FILE)

    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

    # Summary
    with_answer = sum(1 for q in qa_pairs if q['answer'])
    no_answer = sum(1 for q in qa_pairs if not q['answer'])

    print(f"=== Q&A Parse Result ===")
    print(f"Total Q&A pairs: {len(qa_pairs)}")
    print(f"  With answers:  {with_answer}")
    print(f"  No answer yet: {no_answer}")
    print(f"Output: {OUTPUT_FILE}")

    # Show first 3 samples
    print(f"\n=== Samples ===")
    for i, qa in enumerate(qa_pairs[:3]):
        print(f"\n--- Q{i+1} ({qa['date']}) by {qa['question_author']} ---")
        print(f"Q: {qa['question'][:100]}...")
        if qa['answer']:
            print(f"A: {qa['answer'][:100]}...")
        else:
            print(f"A: (no answer)")


if __name__ == '__main__':
    main()
