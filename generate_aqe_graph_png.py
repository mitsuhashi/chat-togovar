#!/usr/bin/env python3

import os
import json5
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# === 設定 ===
input_json_path = "./evaluation/gpt-4o/aggregate_aqes.json"
output_dir = "./evaluation/gpt-4o/png"
os.makedirs(output_dir, exist_ok=True)

models = ["ChatTogoVar", "GPT-4o", "VarChat"]

json_category_keys = {
    "Accuracy": "Accuracy",
    "Completeness": "Completeness",
    "Logical Consistency": "LogicalConsistency",
    "Clarity and Conciseness": "ClarityandConciseness",
    "Evidence Support": "EvidenceSupport"
}

categories = list(json_category_keys.keys())

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

# === データ読み込み ===
with open(input_json_path, "r", encoding="utf-8") as f:
    data = json5.load(f)

df = pd.DataFrame(data)

# === グループ列追加と列名正規化 ===
group_map = {q: g for g, qs in question_groups.items() for q in qs}
df["QuestionGroup"] = df["QuestionNumber"].map(group_map)

# === 合計スコア算出（存在列のみ使用） ===
for model in models:
    for cat in categories:
        if f"{model}_{cat}" not in df.columns:
            print(f"{model}_{cat} not in df.columns")
    valid_cols = [f"{model}_{cat}" for cat in categories if f"{model}_{cat}" in df.columns]
    df[f"{model}_Total"] = df[valid_cols].sum(axis=1)

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
                col = f"{model}_{cat}"
                if col in group.columns:
                    row[f"{model}_{cat}_Avg"] = group[col].mean()
        rows.append(row)
    return pd.DataFrame(rows)

summary_q = summarize(df, "QuestionNumber")
summary_g = summarize(df, "QuestionGroup")

# === 通常のグラフ ===
def save_horizontal_bar(df, title, columns, index_col, filename):
    fig_height = 0.5 * len(df)
    fig, ax = plt.subplots(figsize=(10, max(fig_height, 3)))
    df.set_index(index_col)[columns].plot(kind="barh", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Score")
    plt.tight_layout()
    outpath = os.path.join(output_dir, filename)
    plt.savefig(outpath)
    plt.close()
    print(f"📊 Saved: {outpath}")

def save_all_graphs(df, prefix, index_col):
    save_horizontal_bar(df, "Num of BestAnswer", [f"BestAnswer_{m}" for m in models], index_col, f"{prefix}_BestAnswer.png")
    save_horizontal_bar(df, "Average Total Score", [f"{m}_TotalAvg" for m in models], index_col, f"{prefix}_TotalScore.png")
    for cat in categories:
        cols = [f"{m}_{cat}_Avg" for m in models if f"{m}_{cat}_Avg" in df.columns]
        if cols:
            filename = f"{prefix}_{cat.replace(' ', '')}.png"
            save_horizontal_bar(df, f"Average Score: {cat}", cols, index_col, filename)

# === 質問50件をカテゴリごとに色分けし1枚に描画 ===
def save_all_questions_grouped_plot(df):
    df = df.sort_values("QuestionNumber", key=lambda col: col.map(lambda x: int(x[1:])))
    x_labels = df["QuestionNumber"].tolist()
    x = range(len(x_labels))

    bar_width = 0.25
    fig, ax = plt.subplots(figsize=(max(15, len(x) * 0.3), 6))

    for i, model in enumerate(models):
        heights = df[f"{model}_Total"]
        ax.bar([p + bar_width * i for p in x], heights, width=bar_width, label=model)

    category_colors = [
        "#f0f0f0", "#e0f7fa", "#fce4ec", "#e8f5e9", "#fff3e0", "#ede7f6", "#f9fbe7", "#f3e5f5"
    ]
    patches = []
    for idx, (group_name, question_ids) in enumerate(question_groups.items()):
        indices = [i for i, q in enumerate(x_labels) if q in question_ids]
        if indices:
            start = min(indices)
            end = max(indices)
            ax.axvspan(start - 0.5, end + 0.5, color=category_colors[idx % len(category_colors)], alpha=0.2)
            patches.append(mpatches.Patch(color=category_colors[idx % len(category_colors)], label=group_name))

    ax.set_xticks([p + bar_width for p in x])
    ax.set_xticklabels(x_labels, rotation=90)
    ax.set_ylabel("Total Score")
    ax.set_ylim(0, 50)
    ax.set_title("Total Score per Question (Grouped by Category)")

    handles_model, labels_model = ax.get_legend_handles_labels()
    handles_all = handles_model + patches
    labels_all = labels_model + [p.get_label() for p in patches]
    ax.legend(handles_all, labels_all, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    plt.tight_layout()

    outpath = os.path.join(output_dir, "all_questions_by_category.png")
    plt.savefig(outpath)
    plt.close()
    print(f"📊 Saved all-in-one grouped graph: {outpath}")

# === カテゴリごとの平均Totalスコアを1枚に描画（ご要望対応）===
def save_category_avg_total_score_plot(summary_g):
    # カテゴリ順を question_groups に従って並べ替え
    desired_order = list(question_groups.keys())
    summary_g["CategoryOrder"] = pd.Categorical(summary_g["QuestionGroup"], categories=desired_order, ordered=True)
    summary_g = summary_g.sort_values("CategoryOrder")

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_height = 0.25
    y_labels = summary_g["QuestionGroup"].tolist()
    y = range(len(y_labels))

    for i, model in enumerate(models):
        heights = summary_g[f"{model}_TotalAvg"]
        ax.barh(
            [p + bar_height * i for p in y],
            heights,
            height=bar_height,
            label=model
        )

    ax.set_yticks([p + bar_height for p in y])
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Average Total Score")
    ax.set_xlim(0, 50)
    ax.set_title("Average Total Score by Category")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    ax.invert_yaxis()

    outpath = os.path.join(output_dir, "average_total_score_by_category.png")
    plt.savefig(outpath)
    plt.close()
    print(f"📊 Saved horizontal category-level average score plot: {outpath}")

# === 実行 ===
#save_all_graphs(summary_q, "by_question", "QuestionNumber")
#save_all_graphs(summary_g, "by_group", "QuestionGroup")
#save_all_questions_grouped_plot(df)
save_category_avg_total_score_plot(summary_g)
