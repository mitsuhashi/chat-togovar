#!/usr/bin/env python

import requests
import time
import os
import json
from dotenv import load_dotenv
from utils import read_rs_numbers_from_file
from utils import save_answer_to_markdown

# 環境変数をロード
load_dotenv()

def search_varchat(rs_number):
    """
    TogoVar APIを使用して指定されたバリアントIDを検索し、結果を返します。
    """
    varchat_url=f"https://varchat.engenome.com/varchat/api/request/?gene=&rs={rs_number}&hgvs_c=&hgvs_p=&hgvs_m=&transcript=&genomic_coord=&stream=true&user=mitsuhashi&user_input=rs671&country=Japan&source="
    try:
        response = requests.get(varchat_url)
        response.raise_for_status()
        return format_data(response.text)
    except requests.exceptions.RequestException as e:
        print(f"VarChatエラー: {e}")
        return None

# 整形して出力
def format_data(data):
    text_lines = []
    json_line = None
    
    for line in data.splitlines():
        if line.startswith("data: {") and json_line is None:
            # 最初のJSON部分を抽出
            json_line = line[6:] # "data: "を取り除く
        else:
            # 他の行を収集
            text_lines.append(line[6:])  # "data: "を取り除く

    # 残りの値を連結して1つの文字列に
    combined_text = "".join(text_lines)

    # 結果を出力
    return f"{json_line}\n{combined_text}"

def varchat(rs_number):
    # 環境変数から設定を読み込む
    varchat_result_dir = os.getenv("VARCHAT_RESULT_DIR")

    # VarChat APIから結果を取得
    varchat_result = search_varchat(rs_number)

    # Markdownファイルに保存
    if varchat_result:
        save_answer_to_markdown(f"{varchat_result_dir}/original/{rs_number}.md", varchat_result)
    else:
        print(f"VarChat search failed for {rs_number}")

def main():
    rs_numbers = read_rs_numbers_from_file("pubtator3/rs.txt")
    seconds_between_requests = 5

    for rs in rs_numbers:
        print(f"Processing: {rs}")
        varchat(rs)
        time.sleep(seconds_between_requests)

if __name__ == "__main__":
    main()
