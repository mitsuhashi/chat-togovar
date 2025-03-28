#!/usr/bin/env python

import os
import re
import json5
import pandas as pd
import openpyxl

# ディレクトリのパス
directory_path = "./evaluation/gpt-4o"  # 実際のファイルが保存されているパスに置き換えてください

# 抽出したデータを格納するリスト
extracted_data = {}

# 抽出する情報の正規表現パターン
patterns = {
    "BestAnswer" : r"Best Answer: (.+)",
    "ChatTogoVar" : r"Total Score for ChatTogoVar: (\d+)/\d+",
    "GPT-4o" : r"Total Score for GPT-4o: (\d+)/\d+",
    "VarChat" : r"Total Score for VarChat: (\d+)/\d+",
    "Reason_en" : r"- Reason:\n  - English: (.+)",
    "Reason_ja" : r"- Reason:\n  - English: .+\n  - 日本語:? (.+)"
}

# ディレクトリ内のファイルを処理
with open("questions.json", "r") as f:
    questions = json5.load(f)

# 抽出データをDataFrameに変換
df = pd.DataFrame(columns = ["QuestionNumber", "Question", "Filename",
                            "BestAnswer", "ChatTogoVar", "GPT-4o", "VarChat"])

for question_no, question_statement_template in questions.items():
    for filename in os.listdir(directory_path + "/" + question_no):
        if filename.endswith(".md"):
            rs = filename.replace(".md", "")
            file_path = os.path.join(directory_path + "/" + question_no, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                file_data = {"QuestionNumber": question_no,
                            "Question": question_statement_template.format(rs=rs),
                            "Filename": filename}
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        file_data[key] = match.group(1)
                    else:
                        file_data[key] = None  # 該当情報が見つからない場合はNone
                print([file_data])
                new_data = pd.DataFrame([file_data])
                df = pd.concat([df, new_data], ignore_index=True)

# Excelに保存
output_path = "./evaluation/aggregate_aqes.xlsx" 

with pd.ExcelWriter(output_path) as writer:
    for question_no, group in df.groupby("QuestionNumber"):  # "QuestionNumber" の値ごとにグループ化
        group.to_excel(writer, sheet_name=question_no, index=False)  # Questionごとにシート作成

print(f"{output_path} にデータを保存しました！")