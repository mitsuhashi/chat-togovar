#!/usr/bin/env python3

import os
import re
import json5
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage

# === 設定 ===
root_dir = "./evaluation/gpt-4o"
questions_json_path = "./questions.json"
output_excel_path = os.path.join(root_dir, "aggregate_aqes_with_summary.xlsx")

models = ["ChatTogoVar", "GPT-4o", "VarChat"]
categories = [
    "Accuracy",
    "Completeness",
    "Logical Consistency",
    "Clarity and Conciseness",
    "Evidence Support"
]

question_groups = {
    "Basic Information (q1–q8)": [f"q{x}" for x in range(1, 9)],
    "Allele Frequency and Population Distribution (q9–q15)": [f"q{x}" for x in range(9, 16)],
    "Clinical Significance (q16–q23)": [f"q{x}" for x in range(16, 24)],
    "Pharmacogenomics and Drug Metabolism (q24–q28)": [f"q{x}" for x in range(24, 29)],
    "Functional Impact and Molecular Mechanism (q29–q35)": [f"q{x}" for x in range(29, 36)],
    "Evolutionary Background (q36–q40)": [f"q{x}" for x in range(36, 41)],
    "Comparison with Related Variants (q41–q46)": [f"q{x}" for x in range(41, 47)],
    "Databases and Bioinformatics Analysis (q47–q50)": [f"q{x}" for x in range(47, 51)],
}

basic_patterns = {
    "BestAnswer": r"Best Answer: (.+)",
    "ChatTogoVar": r"Total Score for ChatTogoVar: (\d+)/\d+",
    "GPT-4o": r"Total Score for GPT-4o: (\d+)/\d+",
    "VarChat": r"Total Score for VarChat: (\d+)/\d+",
}

# === Markdown評価ファイル読み込み ===
with open(questions_json_path, "r", encoding="utf-8") as f:
    question_templates = json5.load(f)

def parse_md_file(path, question_no, filename):
    rsid = filename.replace(".md", "")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    record = {
        "QuestionNumber": question_no,
        "Filename_Text": filename,
        "BestAnswer": None,
        "Question": question_templates.get(question_no, "").format(rs=rsid)
    }

    for key, pattern in basic_patterns.items():
        match = re.search(pattern, content)
        if match:
            record[key] = int(match.group(1)) if key in models else match.group(1)

    for model in models:
        for cat in categories:
            pattern = rf"- {cat} Score: (\d+)/10"
            block_pattern = rf"## Answer {re.escape(model)}\n(.*?)(?:\n## Answer |\Z)"
            block_match = re.search(block_pattern, content, re.DOTALL)
            if block_match:
                block = block_match.group(1)
                match = re.search(pattern, block)
                record[f"{model}_{cat}"] = int(match.group(1)) if match else None
            else:
                record[f"{model}_{cat}"] = None

    return record

# === データ読み込みと整形 ===
records = []
for qdir in sorted(os.listdir(root_dir)):
    qpath = os.path.join(root_dir, qdir)
    if not os.path.isdir(qpath):
        continue
    for fname in sorted(os.listdir(qpath)):
        if fname.endswith(".md"):
            record = parse_md_file(os.path.join(qpath, fname), qdir, fname)
            records.append(record)

df = pd.DataFrame(records)
for model in models:
    df[f"{model}_Total"] = df[[f"{model}_{cat}" for cat in categories]].sum(axis=1)

# === 集計関数 ===
def summarize(df, by):
    rows = []
    grouped = df.groupby(by)
    for key, group in grouped:
        row = {by: key}
        for model in models:
            row[f"BestAnswer_{model}"] = (group["BestAnswer"] == model).sum()
            row[f"{model}_TotalAvg"] = group[f"{model}_Total"].mean()
        for cat in categories:
            for model in models:
                row[f"{model}_{cat}_Avg"] = group[f"{model}_{cat}"].mean()
        rows.append(row)
    return pd.DataFrame(rows)

summary_q = summarize(df, "QuestionNumber")

group_map = {q: g for g, qs in question_groups.items() for q in qs}
df["QuestionGroup"] = df["QuestionNumber"].map(group_map)
summary_g = summarize(df, "QuestionGroup")

# === 横棒グラフ関数 ===
def add_horizontal_bar_plot(ws, df, title, columns, index_col, start_row):
    fig_height = 0.5 * len(df)
    fig, ax = plt.subplots(figsize=(8, max(fig_height, 3)))
    df.set_index(index_col)[columns].plot(kind="barh", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Score")
    plt.tight_layout()
    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    ws.add_image(XLImage(img), f"K{start_row}")

def add_all_graphs(ws, df, index_col):
    # ベストアンサー数とトータル平均
    add_horizontal_bar_plot(ws, df, "Num of BestAnswer", [f"BestAnswer_{m}" for m in models], index_col, start_row=2)
    add_horizontal_bar_plot(ws, df, "Average Total Score", [f"{m}_TotalAvg" for m in models], index_col, start_row=22)

    # 各評価項目の平均スコア
    for i, cat in enumerate(categories):
        add_horizontal_bar_plot(ws, df, f"Average Score: {cat}", [f"{m}_{cat}_Avg" for m in models], index_col, start_row=42 + i * 20)

# === Excel 出力 ===
with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="RawData", index=False)
    summary_q.to_excel(writer, sheet_name="Summary_by_Question", index=False)
    summary_g.to_excel(writer, sheet_name="Summary_by_Group", index=False)

    wb = writer.book
    ws_q = wb["Summary_by_Question"]
    ws_g = wb["Summary_by_Group"]

    add_all_graphs(ws_q, summary_q, "QuestionNumber")
    add_all_graphs(ws_g, summary_g, "QuestionGroup")

print(f"\n✅ 集計結果を出力しました: {output_excel_path}")