#!/usr/bin/env python

import json
import random

# データ読み込み
with open("./evaluation/gpt-4o/aggregate_aqes.json") as f:
    data = json.load(f)

with open("./questions_ja.json") as f:
    questions_ja = json.load(f)

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

# ランダムに並び替え
random.shuffle(sampled_entries)

# Index・rsidを追加しつつ、日本語＆英語の質問を含む簡易出力用リストも作成
sampled_entries_simple = []
for idx, entry in enumerate(sampled_entries, start=1):
    qnum = entry.get("QuestionNumber")
    rsid = entry.get("Filename").replace(".md", "")
    entry["Index"] = idx
    entry["rsid"] = rsid

    question_en = entry.get("Question")
    question_ja = questions_ja.get(qnum, "")
    sampled_entries_simple.append({
        "Index": idx,
        "QuestionNumber": qnum,
        "Question_en": question_en,
        "Question_ja": question_ja,
        "rsid": rsid
    })

# フル情報付きファイル（Index + rsid 付き）
with open("./evaluation/human/sampled_30_each_full.json", "w") as f:
    json.dump(sampled_entries, f, indent=2, ensure_ascii=False)

# 簡易ファイル（Index + rsid 付き）
with open("./evaluation/human/sampled_30_each.json", "w") as f:
    json.dump(sampled_entries_simple, f, indent=2, ensure_ascii=False)