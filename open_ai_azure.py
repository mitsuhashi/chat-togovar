import os
from openai import AzureOpenAI
from dotenv import load_dotenv

class OpenAIAzure:
    def __init__(self):
        load_dotenv()
        
        # Azure OpenAI クライアントを作成する。
        api_base = os.getenv("api_base")
        api_key = os.getenv("api_key")
        api_version = os.getenv("api_version")
        
        self.client = AzureOpenAI(
            azure_endpoint = api_base,
            api_key = api_key,
            api_version = api_version)
        
    def get_client(self):
        """
        Azure OpenAI クライアントを取得する。
        """
        return self.client

    def query_azure_openai(self, prompt, question, max_tokens=8192, temperature=0.0):
        """
        Azure OpenAI APIを使用してプロンプトと質問を送信し、回答を取得します。
        """
        deployment_name = os.getenv("deployment_name")
        try:
            response = self.client.chat.completions.create(
                model = deployment_name,
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens = max_tokens,
                temperature = temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Azure OpenAIエラー: {e}")
            return None