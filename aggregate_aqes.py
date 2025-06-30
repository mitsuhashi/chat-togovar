#!/usr/bin/env python

import os
import re
import json5
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter

# ディレクトリのパス
directory_path = "./evaluation/gpt-4o"
github_base_url_evaluation = "https://github.com/mitsuhashi/chat-togovar/blob/main/evaluation/gpt-4o"

# モデルごとの回答リンクベース
model_link_bases = {
    "ChatTogoVar": "https://github.com/mitsuhashi/chat-togovar/blob/main/answers/chat_togovar",
    "GPT-4o": "https://github.com/mitsuhashi/chat-togovar/blob/main/answers/gpt-4o",
    "VarChat": "https://github.com/mitsuhashi/chat-togovar/blob/main/answers/varchat"
}

# モデルとカテゴリリスト
models = ["ChatTogoVar", "GPT-4o", "VarChat"]
categories = [
    "Accuracy",
    "Completeness",
    "Logical Consistency",
    "Clarity and Conciseness",
    "Evidence Support"
]

# カテゴリごとの色設定
category_colors = {
    "Accuracy": "B7DEE8",              # 水色
    "Completeness": "D9EAD3",          # 緑色
    "Logical Consistency": "F9CB9C",   # オレンジ
    "Clarity and Conciseness": "EAD1DC", # ピンク
    "Evidence Support": "FFF2CC"       # 黄色
}

# 抽出パターン
basic_patterns = {
    "BestAnswer": r"Best Answer: (.+)",
    "ChatTogoVar": r"Total Score for ChatTogoVar: (\d+)/\d+",
    "GPT-4o": r"Total Score for GPT-4o: (\d+)/\d+",
    "VarChat": r"Total Score for VarChat: (\d+)/\d+",
}

# 質問一覧を読み込み
with open("questions.json", "r") as f:
    questions = json5.load(f)

# データフレーム
df = pd.DataFrame()

# ファイル処理
for question_no, question_statement_template in questions.items():
    question_dir = os.path.join(directory_path, question_no)
    if not os.path.exists(question_dir):
        continue
    for filename in os.listdir(question_dir):
        if filename.endswith(".md"):
            rs = filename.replace(".md", "")
            file_path = os.path.join(question_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                file_data = {
                    "QuestionNumber": question_no,
                    "Question": question_statement_template.format(rs=rs),
                    "Filename_Text": filename,
                    "Filename_Link": f"{github_base_url_evaluation}/q{question_no}/{filename}"
                }

                # 基本情報抽出
                for key, pattern in basic_patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        file_data[key] = match.group(1)
                    else:
                        file_data[key] = None

                # モデルごとにカテゴリスコア抽出
                for model in models:
                    model_block_pattern = rf"## Answer {re.escape(model)}\n(.*?)(?:\n## Answer |\Z)"
                    model_block_match = re.search(model_block_pattern, content, re.DOTALL)
                    if model_block_match:
                        model_block = model_block_match.group(1)
                        for category in categories:
                            score_pattern = rf"- {re.escape(category)} Score: (\d+)/10"
                            score_match = re.search(score_pattern, model_block)
                            file_data[f"{model}_{category}"] = int(score_match.group(1)) if score_match else None
                    else:
                        for category in categories:
                            file_data[f"{model}_{category}"] = None

                new_data = pd.DataFrame([file_data])
                df = pd.concat([df, new_data], ignore_index=True)

# Filename_Link列は不要なので削除
if "Filename_Link" in df.columns:
    df.drop(columns=["Filename_Link"], inplace=True)

# スコア列を数値型に変換
score_cols = ["ChatTogoVar", "GPT-4o", "VarChat"]
for model in models:
    for category in categories:
        score_cols.append(f"{model}_{category}")

for col in score_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# --- Excel出力（リンク付き、色付き、幅調整、数値セル） ---
output_path = os.path.join(directory_path, "aggregate_aqes.xlsx")
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="Sheet1", index=False)

    workbook = writer.book
    worksheet = workbook["Sheet1"]

    # フィルタをつける
    worksheet.auto_filter.ref = worksheet.dimensions

    # ファイル名に evaluationリンク設定
    for row_idx in range(2, worksheet.max_row + 1):
        filename_text = worksheet.cell(row=row_idx, column=df.columns.get_loc("Filename_Text") + 1).value
        question_no = worksheet.cell(row=row_idx, column=df.columns.get_loc("QuestionNumber") + 1).value

        # ファイル名セルにevaluationリンク
        evaluation_url = f"{github_base_url_evaluation}/{question_no}/{filename_text}"
        filename_cell = worksheet.cell(row=row_idx, column=df.columns.get_loc("Filename_Text") + 1)
        filename_cell.value = filename_text
        filename_cell.hyperlink = evaluation_url
        filename_cell.style = "Hyperlink"

        # 各モデル合計スコアセルにそれぞれのモデル回答リンク
        for model in models:
            model_url_base = model_link_bases[model]
            model_url = f"{model_url_base}/{question_no}/{filename_text}"
            model_col_idx = df.columns.get_loc(model) + 1
            model_cell = worksheet.cell(row=row_idx, column=model_col_idx)

            if model == "VarChat":
                model_url = f"{model_url_base}/{filename_text}"  # VarChatだけ question_no を入れない
            else:
                model_url = f"{model_url_base}/{question_no}/{filename_text}"
            
            model_cell.hyperlink = model_url
            model_cell.style = "Hyperlink"

    # カテゴリスコア列に色付け＋列幅狭め
    for model in models:
        for category in categories:
            col_name = f"{model}_{category}"
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name) + 1
                color = category_colors[category]
                fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

                for row_idx in range(2, worksheet.max_row + 1):
                    worksheet.cell(row=row_idx, column=col_idx).fill = fill

                worksheet.column_dimensions[get_column_letter(col_idx)].width = 5

# --- JSON出力 ---
output_path_json = os.path.join(directory_path, "aggregate_aqes.json")
try:
    df.to_json(output_path_json, orient="records", force_ascii=False, indent=4)
    print(f"{output_path_json} にデータを保存しました！")
except Exception as e:
    print(f"JSON保存中にエラーが発生しました: {e}")

print(f"{output_path} にデータを保存しました！")