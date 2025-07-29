#!/usr/bin/env python

import os
import json
import pandas as pd
import re
import xlsxwriter

# 設定
human_eval_dir = "./evaluation/human"
output_file = "./evaluation/human/aggregate_evaluation_human.xlsx"

criteria_keys = [
    "Accuracy", "Completeness", "Logical Consistency", "Clarity and Conciseness", "Evidence Support"
]
models = ["ChatTogoVar", "GPT4o", "VarChat"]
base_url = "https://github.com/mitsuhashi/chat-togovar/blob/main/answers"

def parse_evaluations():
    rows = []
    for filename in sorted(os.listdir(human_eval_dir)):
        if not filename.endswith(".json"):
            continue

        match = re.match(r"evaluation_(\d+)_q(\d+)_rs(.+)\.json", filename)
        if not match:
            continue

        eval_id_raw, question_num, rs_id = match.groups()
        eval_id = int(eval_id_raw) + 1
        question_no = f"q{question_num}"
        rs_id_full = f"rs{rs_id}"

        filepath = os.path.join(human_eval_dir, filename)
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        row = {
            "ID": eval_id,
            "Question": question_no,
            "rsID": rs_id_full,
        }

        total_scores = {}

        for model in models:
            model_data = data["evaluation"].get(model, {})
            total = 0
            for criterion in criteria_keys:
                crit_data = model_data.get(criterion, {})
                score = int(crit_data.get("score", 0))
                total += score
                row[f"{model}_{criterion}"] = score
                row[f"{model}_{criterion}_reason_ja"] = crit_data.get("reason_ja", "")
                row[f"{model}_{criterion}_reason_en"] = crit_data.get("reason_en", "")
            
            # 正しい GitHub ディレクトリ構造に従ってハイパーリンクを生成
            if model == "ChatTogoVar":
                url = f"{base_url}/chat_togovar/{question_no}/{rs_id_full}.md"
            elif model == "GPT4o":
                url = f"{base_url}/gpt-4o/{question_no}/{rs_id_full}.md"
            elif model == "VarChat":
                url = f"{base_url}/varchat/{rs_id_full}.md"
            else:
                url = ""

            row[f"{model}_Total"] = f'=HYPERLINK("{url}", "{total}")'
            total_scores[model] = total

        best_model = max(total_scores, key=total_scores.get)
        row["BestAnswer"] = best_model

        rows.append(row)

    df = pd.DataFrame(rows)

    # 列順を指定
    prefix = ["ID", "Question", "rsID", "BestAnswer",
            "ChatTogoVar_Total", "GPT4o_Total", "VarChat_Total"]
    other_cols = [col for col in df.columns if col not in prefix]
    df = df[prefix + sorted(other_cols)]
    return df

def calculate_category_averages(df):
    records = []
    for model in models:
        for criterion in criteria_keys:
            col = f"{model}_{criterion}"
            if col in df.columns:
                records.append({
                    "Model": model,
                    "Criterion": criterion,
                    "Average Score": df[col].mean()
                })
    return pd.DataFrame(records)

def calculate_win_rates(df):
    counts = df["BestAnswer"].value_counts().reindex(models, fill_value=0)
    return pd.DataFrame({
        "Model": counts.index,
        "Wins": counts.values,
        "Win Rate (%)": (counts.values / len(df) * 100).round(2)
    })

def save_to_excel(df, category_df, winrate_df, path):
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        # メイン評価シート
        df.to_excel(writer, sheet_name="Evaluation", index=False)

        # カテゴリ平均シート: Criterionを行、Modelを列にピボット
        pivot_df = category_df.pivot(index="Criterion", columns="Model", values="Average Score")
        pivot_df.to_excel(writer, sheet_name="Category Averages")

        workbook = writer.book
        worksheet = writer.sheets["Category Averages"]

        # グラフの作成
        chart = workbook.add_chart({'type': 'column'})

        # モデルごとに series を追加
        for i, model in enumerate(models):
            chart.add_series({
                'name':       model,
                'categories': ['Category Averages', 1, 0, len(pivot_df), 0],
                'values':     ['Category Averages', 1, i + 1, len(pivot_df), i + 1],
            })

        chart.set_title({'name': 'Average Scores per Category'})
        chart.set_x_axis({'name': 'Criterion'})
        chart.set_y_axis({'name': 'Average Score'})
        chart.set_style(11)
        worksheet.insert_chart('E2', chart)

        # 勝率シート
        winrate_df.to_excel(writer, sheet_name="Win Rates", index=False)

    print(f"✅ Excelファイルを出力しました: {path}")

# --- JSON出力 ---
def clean_and_save_to_json(df, output_dir="./evaluation/human", filename="aggregate_human.json"):
    os.makedirs(output_dir, exist_ok=True)
    output_path_json = os.path.join(output_dir, filename)

    # *_Total 列の HYPERLINK(...) → 数値 へ変換
    for col in df.columns:
        if col.endswith("_Total"):
            df[col] = df[col].apply(lambda x: int(re.search(r'"(\d+)"', x).group(1)) if isinstance(x, str) and "HYPERLINK" in x else x)

    # "GPT4o" → "GPT-4o" に列名変更
    for col in df.columns:
        if col.startswith("GPT4o"):
            df = df.rename(columns={col: col.replace("GPT4o", "GPT-4o")})

    # *_reason_ja と *_reason_en の列を削除
    reason_cols = [col for col in df.columns if col.endswith("_reason_ja") or col.endswith("_reason_en")]
    df_cleaned = df.drop(columns=reason_cols)

    # "Question" → "QuestionNumber" に列名変更
    if "Question" in df_cleaned.columns:
        df_cleaned = df_cleaned.rename(columns={"Question": "QuestionNumber"})

    # 保存
    try:
        df_cleaned.to_json(output_path_json, orient="records", force_ascii=False, indent=4)
        print(f"✅ {output_path_json} に保存しました。")
    except Exception as e:
        print(f"❌ JSON保存中にエラーが発生しました: {e}")

def main():
    df = parse_evaluations()
    df = df.sort_values(by="ID")  # ← ID列で昇順ソート
    category_df = calculate_category_averages(df)
    winrate_df = calculate_win_rates(df)
    save_to_excel(df, category_df, winrate_df, output_file)
    clean_and_save_to_json(df)

if __name__ == "__main__":
    main()