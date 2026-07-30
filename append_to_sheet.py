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

    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        sheet.append_rows(data_rows, value_input_option="USER_ENTERED")
    except Exception as e:
        print(f"エラー: スプレッドシートへの書き込みに失敗しました。 {e}")
        sys.exit(1)

    print(f"スプレッドシートに {len(data_rows)} 件を追加しました。")


if __name__ == "__main__":
    main()
