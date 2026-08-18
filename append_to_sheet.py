"""
qa.csv をスプレッドシートに自動追記する
使い方:
  python append_to_sheet.py
"""
import csv
import os
import sys

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import ValidationConditionType

sys.stdout.reconfigure(encoding='utf-8')

CSV_FILE = "qa.csv"
CREDENTIALS_FILE = "credentials/service-account-key.json"
SPREADSHEET_ID = "1S9QY_faN0O4_He7f2DbGO60bEvz_PfTk-K78EHsIRD0"
SHEET_NAME = "qa_master"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main():
    if not os.path.exists(CSV_FILE):
        print("qa.csv が見つかりません。追加するQ&Aはありません。")
        return

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    data_rows = rows[1:]  # ヘッダー行を除く
    if not data_rows:
        print("qa.csv にデータ行がありません。")
        return

    # 非公開列(A列)は常に未チェック状態(False)で追加する
    for row in data_rows:
        row[0] = False

    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        existing_row_count = len(sheet.col_values(2))  # B列(質問列)基準の既存データ行数
        sheet.append_rows(data_rows, value_input_option="USER_ENTERED")

        # 追加した行のA列に明示的にチェックボックス検証を設定（書式の自動継承に頼らない）
        start_row = existing_row_count + 1
        end_row = existing_row_count + len(data_rows)
        sheet.add_validation(f"A{start_row}:A{end_row}", ValidationConditionType.boolean, [])
    except Exception as e:
        print(f"エラー: スプレッドシートへの書き込みに失敗しました。 {e}")
        sys.exit(1)

    print(f"スプレッドシートに {len(data_rows)} 件を追加しました。")


if __name__ == "__main__":
    main()
