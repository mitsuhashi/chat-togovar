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
categories = list(question_groups.keys())
models = ["ChatTogoVar", "GPT-4o", "VarChat"]
score_keys = ["Accuracy", "Completeness", "Logical Consistency", "Clarity and Conciseness", "Evidence Support"]

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

def compute_best_counts(df):
    df = df.copy()
    df["Category"] = df["QuestionNumber"].map(question_category_map)
    df["BestAnswer"] = df["BestAnswer"].replace({"GPT4o": "GPT-4o"})
    return df.groupby("Category")["BestAnswer"].value_counts().unstack().fillna(0)[models]

def compute_score_means(df):
    df = df.copy()
    df["Category"] = df["QuestionNumber"].map(question_category_map)
    grouped = df.groupby("Category")
    result = {}
    for model in models:
        model_scores = []
        for cat in categories:
            values = grouped.get_group(cat) if cat in grouped.groups else pd.DataFrame()
            means = [values[f"{model}_{k}"].mean() if f"{model}_{k}" in values else 0 for k in score_keys]
            model_scores.append(means)
        result[model] = np.array(model_scores)
    return result

def plot_combined(best_counts, score_means, title, outfile, best_answer_max=25):
    y_pos = np.arange(len(categories))
    bar_height = 0.18
    gap = 0.25
    offsets = [-gap, 0, gap]
    offsets_right = [gap, 0, -gap]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12), gridspec_kw={'width_ratios': [1, 3]})
    fig.suptitle(title, fontsize=18, y=0.98)

    # --- 左：Best Answer Count ---
    for i, model in enumerate(models):
        bars = ax1.barh(
            y_pos + offsets[i], best_counts[model], height=bar_height,
            label=model, color='#e0e0e0', edgecolor='black', hatch=model_hatches[model]
        )
        for bar, val in zip(bars, best_counts[model]):
            ax1.text(bar.get_x() + bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                     f"{int(val)}", ha='left', va='center', fontsize=9)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(categories, fontsize=11)
    ax1.invert_yaxis()
    ax1.set_xlim(0, best_answer_max)
    ax1.set_xlabel("Best Answer Count", fontsize=12)
    ax1.set_title("Best Answer Count", fontsize=14)

    # --- 右：Mean Total Score ---
    for i, model in enumerate(models):
        base = np.zeros(len(categories))
        for j, score in enumerate(score_keys):
            values = score_means[model][:, j]
            bars = ax2.barh(
                y_pos + offsets_right[i], values, height=bar_height,
                left=base, color=score_colors[score],
                hatch=model_hatches[model], edgecolor='black', linewidth=0.8
            )
            for bar, val in zip(bars, values):
                if val > 1.5:
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                            f"{val:.1f}", ha='center', va='center', fontsize=8, color='white')
            base += values
        for b, total in zip(y_pos + offsets_right[i], base):
            ax2.text(total + 0.5, b, f"{total:.1f}", va='center', ha='left', fontsize=9)

    ax2.set_yticks([])
    ax2.set_xlim(0, 50)
    ax2.set_xlabel("Mean Total Score", fontsize=12)
    ax2.set_title("Mean Total Score", fontsize=14)

    # --- 凡例 ---
    legend1 = [mpatches.Patch(facecolor='#e0e0e0', edgecolor='black', hatch=model_hatches[m], label=m) for m in models]
    legend2 = [mpatches.Patch(facecolor=score_colors[s], label=s) for s in score_keys]
    fig.legend(handles=legend1 + legend2, loc='lower center', bbox_to_anchor=(0.5, 0.02), ncol=4, fontsize=10)

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    os.makedirs("figures", exist_ok=True)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')

# === データ処理・描画 ===
aqe_best = compute_best_counts(aqe_df)
aqe_means = compute_score_means(aqe_df)
plot_combined(aqe_best, aqe_means, "LLM Evaluation", "figures/llm_eval_combined_fixed.png", best_answer_max=250)

human_best = compute_best_counts(human_df)
human_means = compute_score_means(human_df)
plot_combined(human_best, human_means, "Human Evaluation", "figures/human_eval_combined_fixed.png", best_answer_max=25)
