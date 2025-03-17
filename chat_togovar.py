#!/usr/bin/env python

import requests
import os
import json5
from dotenv import load_dotenv
from open_ai_azure import OpenAIAzure
from utils import load_rs_gene_data
from utils import save_answer_to_markdown

class ChatTogoVar(OpenAIAzure):
    def __init__(self):
        super().__init__()
    
    def query_azure_openai(self, question_statement, rs):
        prompt = self.generate_prompt(rs)
        return super().query_azure_openai(prompt, question_statement)

    def search_togovar(self, rs):
        """
        TogoVar APIを使用して指定されたバリアントIDを検索し、結果を返します。
        """
        try:
            response = requests.post(
                "https://grch38.togovar.org/api/search/variant",
                json={"query": {"id": [rs]}},
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in TogoVar API: {e}")
            return None

    def generate_prompt(self, rs):
        """
        プロンプトを生成する関数
        """
        # promptのテンプレートファイルファイルを読み込む
        with open(os.getenv("CHAT_TOGOVAR_RESULT_DIR") + "/prompt.md", "r", encoding="utf-8") as file:
            prompt_template = file.read()

        # TogoVar APIを使用して、指定されたバリアントIDを検索する
        togovar_response = self.search_togovar(rs)

        return prompt_template.format(togovar_response=togovar_response)

def main():
    load_dotenv()
    result_dir = os.getenv("CHAT_TOGOVAR_RESULT_DIR")

    with open("questions.json", "r") as f:
        questions = json5.load(f)

    rs_gene_list = load_rs_gene_data("pubtator3/rs.txt")

    print(f"Processing {rs_gene_list}")

    # 質問ごとに処理を行う
    for question_no, question_statement_template in questions.items():
        print(f"Processing question {question_no}...{question_statement_template}")
        for entry in rs_gene_list:
            rs = entry["rs_id"]
            question_statement = question_statement_template.format(rs=rs)
            print(f"Processing: {question_statement}...")
            chat_gpt = ChatTogoVar()
            openai_response_content = chat_gpt.query_azure_openai(question_statement, rs)
            if openai_response_content:
                file_path = f"{result_dir}/{question_no}/{rs}.md"
                save_answer_to_markdown(file_path, openai_response_content)
                print(f"done.")
            else:
                print("No response from Azure OpenAI")

if __name__ == "__main__":
    main()