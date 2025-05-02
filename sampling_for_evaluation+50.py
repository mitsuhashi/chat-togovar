#!/usr/bin/env python

import json
import random
import re

# データ読み込み
with open("./evaluation/gpt-4o/aggregate_aqes.json") as f:
    data = json.load(f)

with open("./questions_ja.json") as f:
    questions_ja = json.load(f)

# q1〜q50まで1問ずつサンプリング
sampled_entries = []
for i in range(1, 51):
    qnum = f"q{i}"
    candidates = [entry for entry in data if entry.get("QuestionNumber") == qnum]
    if not candidates:
        raise ValueError(f"No entry found for {qnum}")
    sampled_entry = random.choice(candidates)
    sampled_entries.append(sampled_entry)

# QuestionNumberの数値順にソート（念のため）
def extract_q_number(entry):
    match = re.match(r"q(\d+)", entry.get("QuestionNumber", "q0"))
    return int(match.group(1)) if match else 0

sampled_entries.sort(key=extract_q_number)

# Indexとrsidを付加し、簡易形式も作成
sampled_entries_simple = []
for idx, entry in enumerate(sampled_entries, start=1):
    qnum = entry.get("QuestionNumber")
    rsid = entry.get("Filename_Text").replace(".md", "")
    entry["Index"] = idx + 100
    entry["rsid"] = rsid

    question_en = entry.get("Question")
    question_ja = questions_ja.get(qnum, "")
    sampled_entries_simple.append({
        "Index": idx + 100,
        "QuestionNumber": qnum,
        "Question_en": question_en,
        "Question_ja": question_ja,
        "rsid": rsid
    })

    print(f"Index: {idx + 100}, QuestionNumber: {qnum}, rsid: {rsid}")

# フル情報付きファイルの保存
with open("./evaluation/human/sampled_plus_50_full.json", "w") as f:
    json.dump(sampled_entries, f, indent=2, ensure_ascii=False)

# 簡易ファイルの保存
with open("./evaluation/human/sampled_plus_50.json", "w") as f:
    json.dump(sampled_entries_simple, f, indent=2, ensure_ascii=False)
