#!/usr/bin/env python

import os
import json5
from dotenv import load_dotenv
from utils import load_rs_gene_data
from utils import save_answer_to_markdown
from open_ai_azure import OpenAIAzure

load_dotenv()

class ChatGPT(OpenAIAzure):
    def __init__(self):
        super().__init__()

    def generate_prompt(self):
        """
        プロンプトを生成する関数
        """
        # promptのテンプレートファイルファイルを読み込む
        with open(os.getenv("CHAT_GPT_RESULT_DIR") + "/prompt.md", "r", encoding="utf-8") as file:
            prompt_template = file.read()

        return prompt_template.format()

    def query_azure_openai(self, question_statement):
        prompt = self.generate_prompt()
        return super().query_azure_openai(prompt, question_statement)

def main():
    load_dotenv()
    result_dir = os.getenv("CHAT_GPT_RESULT_DIR")

    # 質問のリストを読み込む
    with open("questions.json", "r") as f:
        questions = json5.load(f)

    # rs番号が書かれたファイルを読み込む
    rs_gene_list = load_rs_gene_data("pubtator3/rs.txt")

    # 質問ごとに処理を行う
    for question_no, question_statement_template in questions.items():
        for entry in rs_gene_list:
            rs = entry["rs_id"]
            question_statement = question_statement_template.format(rs=rs)
            print(f"Processing: {question_statement}...")
            chat_gpt = ChatGPT()
            openai_response_content = chat_gpt.query_azure_openai(question_statement)
            if openai_response_content:
                file_path = f"{result_dir}/{question_no}/{rs}.md"
                save_answer_to_markdown(file_path, openai_response_content)
                print(f"done.")
            else:
                print("No response from Azure OpenAI")

if __name__ == "__main__":
    main()