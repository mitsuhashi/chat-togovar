#!/usr/bin/env python

import os
from dotenv import load_dotenv
from open_ai_azure import OpenAIAzure

load_dotenv()

class Translator(OpenAIAzure):
    def __init__(self):
        super().__init__()

    def generate_prompt(self, text):
        return f"Translate the following sentences into Japanese: {text}"

    def query_azure_openai(self, prompt, max_tokens=8192, temperature=0.0):
        """
        Azure OpenAI APIを使用してプロンプトと質問を送信し、回答を取得します。
        """
        print(f"*****prompt={prompt}")
        deployment_name = os.getenv("deployment_name")
        try:
            response = self.client.chat.completions.create(
                model = deployment_name,
                messages = [
                    {"role": "system", "content": prompt}
                ],
                max_tokens = max_tokens,
                temperature = temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Azure OpenAIエラー: {e}")
            return None

def main():
    load_dotenv()

    input_text = "The genomic variant c.191-26563G>A, also known as rs704341, is located within an intronic region of the PTPRG gene. PTPRG encodes for the protein tyrosine phosphatase receptor type G (RPTPγ), which is a member of the receptor-type PTPs. This protein plays a role in various biological processes including cell growth, differentiation, mitotic cycle, and oncogenic transformation. PTPRG is widely expressed and has been implicated in the regulation of microvascular perfusion and blood pressure, as well as being associated with several diseases including cancer, ischemic vascular diseases, and neurological disorders [1].The variant rs704341 has been nominally associated with ischemic stroke incidence in African-Americans, suggesting a potential role in vascular pathophysiology. This association may provide a mechanistic insight into the strong link between PTPRG variants and Fuchs' endothelial corneal dystrophy, a disorder characterized by the loss of corneal endothelial cells [1]. Additionally, the variant rs704341 has been associated with reduced stroke susceptibility in the Chinese population, particularly in individuals over the age of 64, women, non-smokers, and non-drinkers [2]. This suggests that the variant may confer a protective effect against stroke in these subgroups, although the exact mechanism by which it exerts this influence remains to be elucidated.Given the intronic location of rs704341, it is possible that this variant may affect gene expression or splicing, although the specific functional consequences have not been detailed in the provided literature. The role of PTPRG in a wide range of cellular functions and its association with disease phenotypes underscores the importance of further research to understand the impact of intronic variants like rs704341 on gene function and disease risk [1][2]."

    translator = Translator()
    prompt = translator.generate_prompt(input_text)
    response = translator.query_azure_openai(prompt)
    print(response)


if __name__ == "__main__":
    main()