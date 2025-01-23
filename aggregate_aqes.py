#!/usr/bin/env python

import os
import re
import pandas as pd

# ディレクトリのパス
directory_path = "./evaluation/en/"  # 実際のファイルが保存されているパスに置き換えてください

# 抽出したデータを格納するリスト
extracted_data = []

# 抽出する情報の正規表現パターン
patterns = {
    "Best Answer": r"Best Answer: (.+)",
    "Answer 1 Score": r"Total Score for Answer 1 ChatTogoVar: (\d+)/\d+",
    "Answer 2 Score": r"Total Score for Answer 2 GPT-4o: (\d+)/\d+",
    "Answer 3 Score": r"Total Score for Answer 3 VarChat: (\d+)/\d+"
}

# ディレクトリ内のファイルを処理
for filename in os.listdir(directory_path):
    if filename.endswith(".md"):  # テキストファイルのみ処理
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            file_data = {"Filename": filename}  # ファイル名を記録
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    file_data[key] = match.group(1)
                else:
                    file_data[key] = None  # 該当情報が見つからない場合はNone
            extracted_data.append(file_data)

# 抽出データをDataFrameに変換
df = pd.DataFrame(extracted_data)

# 結果をTSVファイルに保存
output_path = "./evaluation/aggregate_aqes.tsv"  # 保存先を指定
df.to_csv(output_path, sep="\t", index=False)

print(f"抽出結果が以下のTSVファイルに保存されました: {output_path}")