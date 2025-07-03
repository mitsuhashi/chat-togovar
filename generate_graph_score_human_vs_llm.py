#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# === ファイルパス ===
aqe_path = "./evaluation/gpt-4o/aggregate_aqes.json"
human_path = "./evaluation/human/aggregate_human.json"

# === JSON読み込み ===
with open(aqe_path, "r") as f:
    aqe_data = json.load(f)

with open(human_path, "r") as f:
    human_data = json.load(f)

# === DataFrame変換 ===
aqe_df = pd.DataFrame(aqe_data)
human_df = pd.DataFrame(human_data)

# === 質問カテゴリ定義 ===
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

# === 質問番号 → カテゴリ名のマッピング ===
question_category_map = {q: cat for cat, qs in question_groups.items() for q in qs}

# === モデルとスコア軸 ===
models = ["ChatTogoVar", "GPT-4o", "VarChat"]
score_keys = ["Accuracy", "Completeness", "Logical Consistency", "Clarity and Conciseness", "Evidence Support"]

# === 評価カテゴリの色分け、モデルのハッチ模様 ===
score_colors = {
    "Accuracy": "#e41a1c",
    "Completeness": "#377eb8",
    "Logical Consistency": "#4daf4a",
    "Clarity and Conciseness": "#984ea3",
    "Evidence Support": "#ff7f00"
}

model_hatches = {
    "ChatTogoVar": "",
    "GPT-4o": "//",
    "VarChat": ".."
}

# === カテゴリごとの平均スコアを算出 ===
def compute_means(df, question_col, model_names, score_keys):
    df = df.copy()
    df["Category"] = df[question_col].map(question_category_map)
    grouped = df.groupby("Category")
    result = {}
    for model in model_names:
        model_scores = []
        for cat in question_groups.keys():
            if cat in grouped.groups:
                values = grouped.get_group(cat)
                means = [values[f"{model}_{k}"].mean() for k in score_keys]
            else:
                means = [0] * len(score_keys)
            model_scores.append(means)
        result[model] = np.array(model_scores)
    return result

aqe_detailed = compute_means(aqe_df, "QuestionNumber", models, score_keys)
human_detailed = compute_means(human_df, "QuestionNumber", models, score_keys)

# === グラフ描画 ===
categories = list(question_groups.keys())
y_pos = np.arange(len(categories))
bar_width = 0.18
gap = 0.25
offsets = [-gap, 0, gap]

fig, ax = plt.subplots(figsize=(22, 12))

# === LLM評価（左側） ===
for i, model in enumerate(models):
    base = np.zeros(len(categories))
    for j, score in enumerate(score_keys):
        values = aqe_detailed[model][:, j]
        bars = ax.barh(
            y_pos + offsets[i], -values, height=bar_width,
            left=-base,
            color=score_colors[score],
            hatch=model_hatches[model],
            edgecolor='black',
            linewidth=0.8
        )
        for bar, v in zip(bars, values):
            if v > 1.5:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                        f"{v:.1f}", ha='center', va='center', fontsize=8, color='white')
        base += values

# === 人手評価（右側） ===
for i, model in enumerate(models):
    base = np.zeros(len(categories))
    for j, score in enumerate(score_keys):
        values = human_detailed[model][:, j]
        bars = ax.barh(
            y_pos + offsets[i], values, height=bar_width,
            left=base,
            color=score_colors[score],
            hatch=model_hatches[model],
            edgecolor='black',
            linewidth=0.8
        )
        for bar, v in zip(bars, values):
            if v > 1.5:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                        f"{v:.1f}", ha='center', va='center', fontsize=8, color='white')
        base += values

# === 軸とラベル設定 ===
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=11)
ax.invert_yaxis()

max_val = 50
ax.set_xlim(-max_val, max_val)
ax.axvline(0, color='black', linestyle='--', linewidth=1)

xticks = np.arange(0, max_val + 1, 10)
xtick_positions = np.concatenate([-xticks[::-1][:-1], xticks])
ax.set_xticks(xtick_positions)
ax.set_xticklabels([str(abs(x)) for x in xtick_positions], fontsize=10, rotation=45)

for x in xticks[1:]:
    ax.axvline(x, color='gray', linestyle=':', linewidth=0.8)
    ax.axvline(-x, color='gray', linestyle=':', linewidth=0.8)

# === タイトルとラベル ===
fig.text(0.5, 1.02, "Mean Total Score per Question Category", fontsize=16, ha='center')
ax.text(-25, -0.8, "LLM Evaluation (n=1500)", fontsize=13, ha='center', va='bottom')
ax.text(25, -0.8, "Human Evaluation (n=150)", fontsize=13, ha='center', va='bottom')
ax.set_xlabel("Mean Total Score", fontsize=13, labelpad=20)

# === 凡例 ===
legend_handles = []
for score in score_keys:
    patch = mpatches.Patch(facecolor=score_colors[score], label=score)
    legend_handles.append(patch)
for model in models:
    patch = mpatches.Patch(facecolor="white", edgecolor='black', hatch=model_hatches[model], label=model)
    legend_handles.append(patch)

ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, fontsize=10)

# === 保存と表示 ===
os.makedirs("figures", exist_ok=True)
plt.subplots_adjust(top=0.93, bottom=0.30)
plt.tight_layout()
plt.savefig("figures/fig2c_model_comparison_by_category_color_model_hatch.png", dpi=300, bbox_inches='tight')
