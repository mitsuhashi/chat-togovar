#!/usr/bin/env python

import os
from dotenv import load_dotenv
from utils import read_rs_numbers_from_file
from utils import save_answer_to_markdown
from utils import make_azure_openai_client
from utils import get_file_content

def query_azure_openai(client, prompt, deployment_name=os.getenv("deployment_name") , max_tokens=8192, temperature=1.0):
    """
    Azure OpenAI APIを使用してプロンプトを送信し、応答を取得します。
    """
    try:
        response = client.chat.completions.create(
            model = deployment_name,
            messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in genetic variation."},
                {"role": "user", "content": prompt},
            ],
            max_tokens = max_tokens,
            temperature = temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Azure OpenAIエラー: {e}")
        return None

def generate_prompt(question, rs_number):
    chat_togovar = get_file_content(os.getenv("CHAT_TOGOVCAR_RESULT_DIR") + f"/{rs_number}.md")
    chat_gpt = get_file_content(os.getenv("CHAT_GPT_RESULT_DIR") + f"/{rs_number}.md")
    varchat = get_file_content(os.getenv("VARCHAT_RESULT_DIR") + f"/{rs_number}.md")

    # promptのテンプレートファイルファイルを読み込む
    evaluation_dir = os.getenv("EVALUATION_DIR")
    with open(f"{evaluation_dir}/prompt.md", "r", encoding="utf-8") as file:
        prompt_template = file.read()

    return prompt_template.format(chat_togovar=chat_togovar, chat_gpt=chat_gpt, varchat=varchat, question=question)

def run_aqe(rs_number, language="en"):
    api_base = os.getenv("api_base")
    api_key = os.getenv("api_key")
    api_version = os.getenv("api_version")
    deployment_name = os.getenv("deployment_name")
    evaluation_dir = os.getenv("EVALUATION_DIR")

    # クライアントを作成
    client = make_azure_openai_client(api_base, api_key, api_version)

    # プロンプトを作成
    question = (
        f"Could you show me the allele frequency of {rs_number} in Japanese populations?"
    )
    prompt = generate_prompt(question, rs_number)

    # Azure OpenAIにプロンプトを送信
    openai_response_content = query_azure_openai(client, prompt, deployment_name)
    if openai_response_content:
        # Markdownファイルに保存
        file_path = f"{evaluation_dir}/{language}/{rs_number}.md"
        save_answer_to_markdown(file_path, openai_response_content)

def main():
    load_dotenv()

    rs_numbers = read_rs_numbers_from_file("pubtator3/rs.txt")

    for rs in rs_numbers:
        print(f"Processing: {rs}")
        run_aqe(rs, "ja")

if __name__ == "__main__":
    main()