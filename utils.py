import os
from openai import AzureOpenAI

def make_azure_openai_client():
    """
    Azure OpenAI クライアントを作成する。
    """
    api_base = os.getenv("api_base")
    api_key = os.getenv("api_key")
    api_version = os.getenv("api_version")
    
    return AzureOpenAI(
        azure_endpoint=api_base,
        api_key=api_key,
        api_version=api_version
    )

def query_azure_openai(client, prompt, question, max_tokens=8192, temperature=1.0):
    """
    Azure OpenAI APIを使用してプロンプトを送信し、応答を取得します。
    """
    deployment_name = os.getenv("deployment_name")
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

def read_rs_numbers_from_file(file_path):
    """
    rs番号が書かれたファイルを読み込んでリストを返す関数
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            rs_numbers = [line.strip() for line in file if line.strip()]
        return rs_numbers
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_answer_to_markdown(system_name, file_path, content):
    """
    指定された内容をMarkdownファイルとして保存します。
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"# {system_name}\n\n")
            file.write(content)
        print(f"Response saved to {file_path}")
    except Exception as e:
        print(f"ファイル保存エラー: {e}")

def get_file_content(file_path):
    """
    Read a Markdown file and return its content as a string.
    
    Args:
        file_path (str): Path to the Markdown file.
    
    Returns:
        str: Content of the Markdown file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""