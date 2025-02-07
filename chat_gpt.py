#!/usr/bin/env python

import requests
import os
from dotenv import load_dotenv
from utils import read_rs_numbers_from_file
from utils import save_answer_to_markdown
from utils import make_azure_openai_client

# 環境変数をロード
load_dotenv()

def search_togovar(api_url, variant_id):
    """
    TogoVar APIを使用して指定されたバリアントIDを検索し、結果を返します。
    """
    try:
        response = requests.post(
            f"{api_url}/search/variant",
            json={"query": {"id": [variant_id]}},
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"TogoVar APIエラー: {e}")
        return None

def query_azure_openai(client, question, deployment_name, max_tokens=8192, temperature=1.0):
    """
    Azure OpenAI APIを使用してプロンプトを送信し、応答を取得します。
    """
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "user", "content": question}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Azure OpenAIエラー: {e}")
        return None

def generate_prompt(variant_id):
    """
    プロンプトを生成する関数

    Args:
        variant_id (str): バリアントID (例: rs123456)
        json_data_str (str): TogoVar APIの検索結果 (JSON文字列)

    Returns:
        str: 生成されたプロンプト
    """
    question = f"Could you show me the allele frequency of {variant_id} in Japanese populations?\n"
    question = f"How does the {variant_id} allele affect the structure and function of genes?\n"
    question = f"How does the location of {variant_id} influence the clinical phenotype?"

    return question


def chat_gpt(variant_id):
    # 環境変数から設定を読み込む
    api_base = os.getenv("api_base")
    api_key = os.getenv("api_key")
    api_version = os.getenv("api_version")
    deployment_name = os.getenv("deployment_name")
    chat_gpt_result_dir = os.getenv("CHAT_GPT_RESULT_DIR")

    # クライアントを作成
    client = make_azure_openai_client(api_base, api_key, api_version)

    # プロンプトを作成
    prompt = generate_prompt(variant_id)

    # Azure OpenAIにプロンプトを送信
    openai_response_content = query_azure_openai(client, prompt, deployment_name)
    if openai_response_content:
        # Markdownファイルに保存
        file_path = f"{chat_gpt_result_dir}/{variant_id}.md"
        save_answer_to_markdown(file_path, openai_response_content)

def main():
    rs_numbers = read_rs_numbers_from_file("pubtator3/rs.txt")

    for rs in rs_numbers:
        print(f"Processing: {rs}")
        chat_gpt(rs)

if __name__ == "__main__":
    main()