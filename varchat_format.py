#!/usr/bin/env python
import json
import re
import os
from translator import Translator

# 入力Markdownテキストの読み込み
def load_markdown_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()

# JSON部分を抽出（{} で囲まれた部分）
def extract_json(text):
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return None

# 本文の要約部分を抽出
def extract_summary(text):
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
#        print(match.group(1))
        summary = text.replace(match.group(1), "")
        translator = Translator()
        prompt = translator.generate_prompt(summary)
        summary_ja = translator.query_azure_openai(prompt)
#        print(f"summary={summary}")
        summary = summary + "\n\n" + (summary_ja or "")
    return summary if summary else text  # 空なら全体を返す

IN_DIR = os.getenv("VARCHAT_RESULT_DIR") + "/original"

files = [f for f in os.listdir(IN_DIR) if os.path.isfile(os.path.join(IN_DIR, f))]

for input_file in files:
    print(input_file)

    input_text = load_markdown_text(IN_DIR + "/" + input_file)

    summary_text = extract_summary(input_text)

    json_data = extract_json(input_text)
    if not json_data:
        raise ValueError("JSON data not found in the input file.")

    # citsのリファレンス情報を取得
    references = "\n## References\n"
    for cit in json_data["cits"]:
        ref_num = re.search(r"\[(\d+)\]", cit["cit"]).group(1)
        references += f"- {cit['cit']} [PubMed]({cit['pmid']})\n"

    # ClinVar 情報を取得
    clinvar_info = "\n## ClinVar Submissions\n"
    for rcv in json_data["rcv_cits"]:
        clinvar_info += f"- **[{rcv['rcv']}]({rcv['link']})**: {rcv['condition']}\n"

    # Markdownフォーマットで出力
    markdown_output = f"""
    {summary_text}
    {references}
    {clinvar_info}
    """

    # Markdownファイルに出力
    output_file = os.getenv("VARCHAT_RESULT_DIR") + "/" + input_file
    with open(output_file, "w") as file:
        file.write(markdown_output)

    print(f"Markdown output saved to {output_file}")
    exit
