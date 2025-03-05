#!/usr/bin/env python

import os
import json5
import requests
from open_ai_azure import OpenAIAzure
from dotenv import load_dotenv
from utils import load_rs_gene_data
from utils import save_answer_to_markdown
from utils import get_file_content

class AnswerQualityEvaluator(OpenAIAzure):
    def __init__(self):
        super().__init__()

    def query_azure_openai(self, question_no, question_statement, rs, gene_symbols):
        prompt = self.generate_prompt(question_no, question_statement, rs, gene_symbols)
        question_statement = ""
        return super().query_azure_openai(prompt, question_statement)

    def generate_prompt(self, question_no, question, rs, gene_symbols):
        """
        プロンプトを生成する関数
        """
        chat_togovar = get_file_content(os.getenv("CHAT_TOGOVAR_RESULT_DIR") + f"/{question_no}/{rs}.md")
        chat_gpt = get_file_content(os.getenv("CHAT_GPT_RESULT_DIR") + f"/{question_no}/{rs}.md")
        varchat = get_file_content(os.getenv("VARCHAT_RESULT_DIR") + f"/{rs}.md")

        # promptのテンプレートファイルファイルを読み込む
        evaluation_dir = os.getenv("EVALUATION_DIR")
        with open(f"{evaluation_dir}/prompt.md", "r", encoding="utf-8") as file:
            prompt_template = file.read()

        prompt = prompt_template.format(chat_togovar=chat_togovar, chat_gpt=chat_gpt, varchat=varchat, question=question, gene_symbols=gene_symbols)

        return prompt

def main():
    SYSTEM_NAME = "AnswerQualityEvaluator"

    load_dotenv()
    evaluation_dir = os.getenv("EVALUATION_DIR")

    # 質問のリストを読み込む
    with open("questions.json", "r") as f:
        questions = json5.load(f)

    # rs番号とgene symbolが書かれたファイルを読み込む
    rs_gene_list = load_rs_gene_data("pubtator3/rs.txt")

    # 質問ごとに処理を行う
    for question_no, question_statement_template in questions.items():
        for rs_gene in rs_gene_list:
            rs = rs_gene["rs_id"]
            gene_symbols = ", ".join(rs_gene["gene_symbol"])
            question_statement = question_statement_template.format(rs=rs)
            print(f"Evaluating answers for '{question_statement}'...")
            aqe = AnswerQualityEvaluator()
            openai_response_content = aqe.query_azure_openai(question_no, question_statement, rs, gene_symbols)
            if openai_response_content:
                file_path = f"{evaluation_dir}/{question_no}/{rs}.md"
                save_answer_to_markdown(SYSTEM_NAME, file_path, openai_response_content)
                print("done.")
            else:
                print("No response from Azure OpenAI")

if __name__ == "__main__":
    main()