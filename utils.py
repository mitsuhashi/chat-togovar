import os

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

def load_rs_gene_data(file_path):
    """
    rsID と gene_symbol を辞書のリストに格納する関数
    """
    rs_gene_list = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("\t")  # タブ区切りで分割
            print(parts[0])
            if len(parts) >= 2:
                rs_id = parts[0]
                gene_symbols = parts[1].split(",")  # 複数のGene Symbolがある場合に対応
                rs_gene_list.append({"rs_id": rs_id, "gene_symbol": gene_symbols})

    return rs_gene_list

def save_answer_to_markdown(file_path, content):
    """
    指定された内容をMarkdownファイルとして保存します。
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
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