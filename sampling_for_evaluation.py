#!/usr/bin/env python

import json
import random

# データ読み込み
with open("./evaluation/gpt-4o/aggregate_aqes.json") as f:
    data = json.load(f)

with open("./questions_ja.json") as f:
    questions_ja = json.load(f)  # 例: { "q1": "rs796052984に関する基本情報を教えてください。" }

# BestAnswerごとに分類
by_best_answer = {
    "ChatTogoVar": [],
    "GPT-4o": [],
    "VarChat": []
}

for entry in data:
    best = entry.get("BestAnswer")
    if best in by_best_answer:
        by_best_answer[best].append(entry)

# サンプリング（最大30件ずつ）
sampled_entries = []
for key in by_best_answer:
    sampled = random.sample(by_best_answer[key], min(30, len(by_best_answer[key])))
    sampled_entries.extend(sampled)

# 日本語＆英語の質問 + rsid を付けた簡易出力用リストを作成
sampled_entries_simple = []
for entry in sampled_entries:
    qnum = entry.get("QuestionNumber")  # 例: "q1"
    rsid = entry.get("Filename").replace(".md", "")  # 例: "rs796052984"
    question_en = entry.get("Question")  # 英語質問（元データに含まれていると想定）
    question_ja = questions_ja.get(qnum, "")
    sampled_entries_simple.append({
        "QuestionNumber": qnum,
        "Question_en": question_en,
        "Question_ja": question_ja,
        "rsid": rsid
    })

# フル情報付きファイル
with open("./evaluation/human/sampled_30_each_full.json", "w") as f:
    json.dump(sampled_entries, f, indent=2, ensure_ascii=False)

# rsid付き簡易ファイル
with open("./evaluation/human/sampled_30_each.json", "w") as f:
    json.dump(sampled_entries_simple, f, indent=2, ensure_ascii=False)