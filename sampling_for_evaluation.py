#!/usr/bin/env python

import json
import random

# データ読み込み
with open("./evaluation/gpt-4o/aggregate_aqes.json") as f:
    data = json.load(f)

with open("./questions_ja.json") as f:
    questions_ja = json.load(f)

# 全体からランダムに100問抽出（100件以上あることが前提）
sampled_entries = random.sample(data, min(100, len(data)))

# ランダム順を維持しつつ、Index・rsidを追加し、簡易形式も作成
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
with open("./evaluation/human/sampled_100_full.json", "w") as f:
    json.dump(sampled_entries, f, indent=2, ensure_ascii=False)

# 簡易ファイル（Index + rsid 付き）
with open("./evaluation/human/sampled_100.json", "w") as f:
    json.dump(sampled_entries_simple, f, indent=2, ensure_ascii=False)