#!/usr/bin/env python3

import os
import json5
import pandas as pd
import matplotlib.pyplot as plt

# === 設定 ===
input_json_path = "./evaluation/human/aggregate_human.json"
output_dir = "./evaluation/human/png"
os.makedirs(output_dir, exist_ok=True)

models = ["ChatTogoVar", "GPT-4o", "VarChat"]

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

# === グループ列追加 ===
group_map = {q: g for g, qs in question_groups.items() for q in qs}
df["QuestionGroup"] = df["QuestionNumber"].map(group_map)

# === Total スコアの平均をカテゴリ単位で算出 ===
df_grouped = df.groupby("QuestionGroup")[["ChatTogoVar_Total", "GPT-4o_Total", "VarChat_Total"]].mean().reset_index()

# === カテゴリ順を維持した並び替え ===
df_grouped["CategoryOrder"] = pd.Categorical(df_grouped["QuestionGroup"], categories=list(question_groups.keys()), ordered=True)
df_grouped = df_grouped.sort_values("CategoryOrder")

# === 横棒グラフの描画 ===
fig, ax = plt.subplots(figsize=(10, 6))
bar_height = 0.25
y = range(len(df_grouped))

for i, model in enumerate(models):
    ax.barh(
        [p + bar_height * i for p in y],
        df_grouped[f"{model}_Total"],
        height=bar_height,
        label=model
    )

ax.set_yticks([p + bar_height for p in y])
ax.set_yticklabels(df_grouped["QuestionGroup"])
ax.set_xlabel("Mean Total Score")
ax.set_xlim(0, 50)
ax.set_title("Mean Total Scores per Question Category (Human Evaluation)")
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
ax.invert_yaxis()

plt.tight_layout()
outpath = os.path.join(output_dir, "mean_total_score_per_question_category_for_human_evaluation.png")
plt.savefig(outpath)
plt.close()
print(f"📊 Saved: {outpath}")
