#!/usr/bin/env python

import os
import json
import pandas as pd
import re
from collections import defaultdict

# 入力ディレクトリ
human_eval_dir = "./evaluation/human"

# 評価項目
criteria_keys = [
    "Accuracy",
    "Completeness",
    "Logical Consistency",
    "Clarity and Conciseness",
    "Evidence Support"
]

# モデル名
models = ["ChatTogoVar", "GPT-4o", "VarChat"]

# 質問ごと＋モデルごとのスコア＆理由格納
question_data = {}

# .jsonl 読み込み
for filename in os.listdir(human_eval_dir):
    if not filename.endswith(".jsonl"):
        continue

    match = re.match(r"evaluation_(\d+)_q(\d+)_rs(.+)\.jsonl", filename)
    if not match:
        continue

    eval_id_raw, question_num, rs_id = match.groups()
    eval_id = int(eval_id_raw) + 1  # +1する
    question_no = f"q{question_num}"
    rs_id = f"rs{rs_id}"
    filepath = os.path.join(human_eval_dir, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())

    label_mapping = data.get("label_mapping", {})
    evaluation = data.get("evaluation", {})

    model_info = {}

    for answer_label, model_name in label_mapping.items():
        if model_name not in models:
            continue

        model_eval = evaluation.get(answer_label, {})
        total_score = 0
        score_items = {}

        for criterion in criteria_keys:
            score_str = model_eval.get(criterion, {}).get("score")
            try:
                score = int(score_str)
                score_items[criterion] = score
                total_score += score
            except (TypeError, ValueError):
                score_items[criterion] = None

        reason = None
        for val in model_eval.values():
            if isinstance(val, dict) and "reason_ja" in val:
                reason = val["reason_ja"]
                break

        model_info[model_name] = {
            "Total": total_score,
            "Scores": score_items,
            "Reason": reason
        }

    question_data[eval_id] = {
        "EvaluationID": eval_id,
        "QuestionNumber": question_no,
        "RSID": rs_id,
        "ModelInfo": model_info
    }

# DataFrame用データ作成
records = []
for eval_id in sorted(question_data.keys()):
    q = question_data[eval_id]
    record = {
        "EvaluationID": q["EvaluationID"],
        "QuestionNumber": q["QuestionNumber"],
        "RSID": q["RSID"]
    }

    model_info = q["ModelInfo"]

    # 各モデルの合計スコアを記録 & TopModel 判定用
    totals = {}
    for model in models:
        total = model_info.get(model, {}).get("Total", 0)
        record[f"{model}_Total"] = total
        totals[model] = total

    # トップスコアモデルを記録
    top_model = max(totals.items(), key=lambda x: x[1])[0]
    record["TopModel"] = top_model

    # 各モデルのスコア詳細
    for model in models:
        scores = model_info.get(model, {}).get("Scores", {})
        for criterion in criteria_keys:
            record[f"{model}_{criterion}"] = scores.get(criterion)

    # 各モデルの理由
    for model in models:
        record[f"{model}_Reason"] = model_info.get(model, {}).get("Reason", "")

    records.append(record)

# DataFrame化
df = pd.DataFrame(records)

# 列順の定義
cols = ["EvaluationID", "QuestionNumber", "RSID", "TopModel"]
cols += [f"{model}_Total" for model in models]
for model in models:
    for criterion in criteria_keys:
        cols.append(f"{model}_{criterion}")
for model in models:
    cols.append(f"{model}_Reason")

df = df[cols]

# 出力
output_excel = "./evaluation/human/questionwise_detailed_scores.xlsx"
output_json = "./evaluation/human/questionwise_detailed_scores.json"

df.to_excel(output_excel, index=False)
df.to_json(output_json, orient="records", force_ascii=False, indent=4)

print("出力完了:")
print(f"- Excel: {output_excel}")
print(f"- JSON : {output_json}")