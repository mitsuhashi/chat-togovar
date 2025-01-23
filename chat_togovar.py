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

def query_azure_openai(client, prompt, question, deployment_name, max_tokens=8192, temperature=1.0):
    """
    Azure OpenAI APIを使用してプロンプトを送信し、応答を取得します。
    """
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in genomics."},
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Azure OpenAIエラー: {e}")
        return None

def generate_prompt(json_data_str):
    """
    プロンプトを生成する関数

    Args:
        variant_id (str): バリアントID (例: rs123456)
        json_data_str (str): TogoVar APIの検索結果 (JSON文字列)

    Returns:
        str: 生成されたプロンプト
    """

    instructions = (
        "1. Only provide information on the items from 1-1 to 1-6 if they are directly related to the question. "
        "If no information is available, explicitly state that there is no information. Also, include a source URL for each answer.\n"
        "1-1. Display link information such as the rs number, HGVS, gene name, and transcript name.\n"
        "1-2. Discuss the relationship with diseases based on curated information (ClinVar) and predictions (AlphaMissense, SIFT, Polyphen).\n"
        "1-3. Include the content of literature where this variant appears.\n"
        "1-4. Compare allele frequencies between Japanese and non-Japanese populations and explain the differences among populations.\n"
        "1-5. Consider GWAS results and mention phenotypes related to this variant.\n"
        "1-6. Include a link to the TogoVar page for this variant.\n"
        f"2. Please consider the result by searching with TogoVar API:```\n{json_data_str}\n```\n"
    )
    return instructions


def chat_togovar(variant_id):
    # 環境変数から設定を読み込む
    api_base = os.getenv("api_base")
    api_key = os.getenv("api_key")
    api_version = os.getenv("api_version")
    deployment_name = os.getenv("deployment_name")
    chat_togovar_result_dir = os.getenv("CHAT_TOGOVCAR_RESULT_DIR")

    togovar_api_url = "https://grch38.togovar.org/api"

    # クライアントを作成
    client = make_azure_openai_client(api_base, api_key, api_version)

    # TogoVar APIから結果を取得
    togovar_result = search_togovar(togovar_api_url, variant_id)
    if not togovar_result:
        print("TogoVar検索に失敗しました。")
        return None

    # プロンプトを作成
    prompt = generate_prompt(togovar_result)
    question = f"Could you show me the allele frequency of {variant_id} in Japanese populations?\n"

    # Azure OpenAIにプロンプトを送信
    openai_response_content = query_azure_openai(client, prompt, question, deployment_name)
    if openai_response_content:
        # Markdownファイルに保存
        file_path = f"{chat_togovar_result_dir}/{variant_id}.md"
        save_answer_to_markdown(file_path, openai_response_content)

def main():
    rs_numbers = read_rs_numbers_from_file("pubtator3/rs.txt")

    for rs in rs_numbers:
        print(f"Processing: {rs}")
        chat_togovar(rs)

if __name__ == "__main__":
    main()