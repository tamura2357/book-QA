def load_text(file_path: str) -> str:
    """テキストファイルを読み込んで文字列で返す"""
    with open(file_path, encoding="utf-8") as f:
        return f.read()
