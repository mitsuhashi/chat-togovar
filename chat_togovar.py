#!/usr/bin/env python

import requests
import os
import json5
from dotenv import load_dotenv
from open_ai_azure import OpenAIAzure
from utils import read_rs_numbers_from_file
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
        # TogoVar APIから結果を取得
        togovar_result = self.search_togovar(rs)
        if not togovar_result:
            print("Failed to get TogoVar result.")
            return None

        prompt = (
            "1. Only provide information on the items from 1-1 to 1-6 if they are directly related to the question. "
            "If no information is available, explicitly state that there is no information. Also, include a source URL for each answer.\n"
            "1-1. Display link information such as the rs number, HGVS, gene name, and transcript name.\n"
            "1-2. Discuss the relationship with diseases based on curated information (ClinVar) and predictions (AlphaMissense, SIFT, Polyphen).\n"
            "1-3. Include the content of literature where this variant appears.\n"
            "1-4. Compare allele frequencies between Japanese and non-Japanese populations and explain the differences among populations.\n"
            "1-5. Consider GWAS results and mention phenotypes related to this variant.\n"
            "1-6. Include a link to the TogoVar page for this variant.\n"
            f"2. Please consider the result by searching with TogoVar API:```\n{togovar_result}\n```\n"
            f"2-1. If no information is available from TogoVar API, the answer should be generated based on ChatGPT.\n"
        )
        return prompt

def main():
    QA_SYSTEM = "ChatTogoVar"

    load_dotenv()
    result_dir = os.getenv("CHAT_TOGOVAR_RESULT_DIR")

    with open("questions.json", "r") as f:
        questions = json5.load(f)

    rs_numbers = read_rs_numbers_from_file("pubtator3/rs.txt")

    # 質問ごとに処理を行う
    for question_no, question_statement_template in questions.items():
        for rs in rs_numbers:
            question_statement = question_statement_template.format(rs=rs)
            print(f"Processing: {question_statement}...")
            chat_gpt = ChatTogoVar()
            openai_response_content = chat_gpt.query_azure_openai(question_statement, rs)
            if openai_response_content:
                file_path = f"{result_dir}/{question_no}/{rs}.md"
                save_answer_to_markdown(QA_SYSTEM, file_path, openai_response_content)
                print(f"done.")
            else:
                print("No response from Azure OpenAI")

if __name__ == "__main__":
    main()