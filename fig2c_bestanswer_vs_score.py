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
    "Basic Information\n(q1–q8)": [f"q{x}" for x in range(1, 9)],
    "Allele Frequency\nand Population Distribution\n(q9–q15)": [f"q{x}" for x in range(9, 16)],
    "Clinical Significance\n(q16–q23)": [f"q{x}" for x in range(16, 24)],
    "Pharmacogenomics\nand Drug Metabolism\n(q24–q28)": [f"q{x}" for x in range(24, 29)],
    "Functional Impact\nand Molecular Mechanism\n(q29–q35)": [f"q{x}" for x in range(29, 36)],
    "Evolutionary Background\n(q36–q40)": [f"q{x}" for x in range(36, 41)],
    "Comparison with Related Variants\n(q41–q46)": [f"q{x}" for x in range(41, 47)],
    "Databases\nand Bioinformatics Analysis\n(q47–q50)": [f"q{x}" for x in range(47, 51)],
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
    out = df.groupby("Category")["BestAnswer"].value_counts().unstack().fillna(0)
    # 欠けているモデル列を補完（存在しない場合0列を追加）
    for m in models:
        if m not in out.columns:
            out[m] = 0
    # ★ カテゴリ順を明示的に揃える
    return out[models].reindex(categories).fillna(0)

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

import matplotlib.patheffects as pe

def plot_combined(best_counts, score_means, title, outfile, best_answer_max=25):
    y_pos = np.arange(len(categories))
    bar_height = 0.18
    gap = 0.25
    offsets = [-gap, 0, gap]
    offsets_right = [-gap, 0, gap]  # ← 左と同じ順で ChatTogoVar, GPT-4o, VarChat

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(24, 12),
        gridspec_kw={'width_ratios': [1, 3]}
    )
    fig.suptitle(title, fontsize=18, y=0.98)

    # --- 左：Number of Best Answers ---
    for i, model in enumerate(models):
        vals = best_counts[model].values  # 順序固定
        bars = ax1.barh(
            y_pos + offsets[i], vals, height=bar_height,
            label=model, color='#e0e0e0', edgecolor='black',
            hatch=model_hatches[model], linewidth=0.8
        )
        for bar, val in zip(bars, vals):
            ax1.text(
                bar.get_x() + bar.get_width() + 0.5,
                bar.get_y() + bar.get_height()/2,
                f"{int(val)}", ha='left', va='center', fontsize=14
            )

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(categories, fontsize=16)
    ax1.invert_yaxis()  # 上から categories の順
    ax1.set_xlim(0, best_answer_max)
    ax1.set_xlabel("Number of Answers", fontsize=16)  # 用語をより自然に
    ax1.set_title("Number of Highest-Scoring Answers", fontsize=20)

    # --- 右：Mean Total Score（合計値を太字＆縁取りで強調） ---
    for i, model in enumerate(models):
        base = np.zeros(len(categories))
        for j, score in enumerate(score_keys):
            values = score_means[model][:, j]  # すでに categories 順
            bars = ax2.barh(
                y_pos + offsets_right[i], values, height=bar_height,
                left=base, color=score_colors[score],
                hatch=model_hatches[model], edgecolor='black', linewidth=0.8
            )
            # セグメント内の数値（必要十分なときのみ）
            for bar, val in zip(bars, values):
                if val > 1.5:
                    ax2.text(
                        bar.get_x() + bar.get_width()/2,
                        bar.get_y() + bar.get_height()/2,
                        f"{val:.1f}", ha='center', va='center',
                        fontsize=12, color='white'
                    )
            base += values

        # 合計値（太字＋白縁取りで視認性UP）
        for yb, total in zip(y_pos + offsets_right[i], base):
            txt = ax2.text(
                total + 0.5, yb, f"{total:.1f}",
                va='center', ha='left', fontsize=14, fontweight='bold', color='black'
            )
            txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='white')])

    ax2.set_yticks([])          # 右はカテゴリラベル非表示
    ax2.set_xlim(0, 50)
    ax2.set_xlabel("Mean Total Score", fontsize=16)
    ax2.set_title("Mean Total Scores across Evaluation Criteria", fontsize=20)
    ax2.invert_yaxis()          # 左と上下を揃える

    # --- 凡例を二段構成に分離（読みやすさ向上） ---
    # モデル用（ハッチング）
    legend_models = [
        mpatches.Patch(facecolor='#e0e0e0', edgecolor='black',
                    hatch=model_hatches[m], label=m) for m in models
    ]
    # 指標用（色）
    legend_scores = [
        mpatches.Patch(facecolor=score_colors[s], edgecolor='black', label=s) for s in score_keys
    ]

    # 下部に2行で配置（左右に分けて衝突回避）
    leg1 = fig.legend(
        handles=legend_models, loc='lower left',
        bbox_to_anchor=(0.08, 0.02), ncol=len(models), fontsize=14,
        frameon=True
    )
    leg2 = fig.legend(
        handles=legend_scores, loc='lower right',
        bbox_to_anchor=(0.92, 0.02), ncol=len(score_keys), fontsize=14,
        frameon=True
    )
    leg1.set_zorder(10); leg2.set_zorder(10)

    # 余白を下に確保（凡例が重ならないように）
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])

    os.makedirs("figures", exist_ok=True)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')


# === データ処理・描画 ===
aqe_best = compute_best_counts(aqe_df)
aqe_means = compute_score_means(aqe_df)
plot_combined(aqe_best, aqe_means, "LLM-based Evaluation", "figures/llm_bestanswer_vs_score.png", best_answer_max=250)

human_best = compute_best_counts(human_df)
human_means = compute_score_means(human_df)
#plot_combined(human_best, human_means, "Manual Evaluation", "figures/fig2c_human_bestanswer_vs_score.png", best_answer_max=25)
plot_combined(human_best, human_means, "", "figures/fig2c_human_bestanswer_vs_score.png", best_answer_max=25)
