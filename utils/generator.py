import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env から API キーを読み込む
load_dotenv()

_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def generate_questions_for_chunk(chunk: str, n_questions: int = 3) -> List[str]:
    """
    与えられたテキストチャンクについて、
    重要な内容に限った質問を n_questions 個生成してリストで返す
    """
    prompt = (
        f"以下の文章を読んで、核心的な概念や因果関係、応用例を深く理解できているかを確認する"
        f"教育的な質問を、番号なしのリスト形式で{n_questions}つ作成してください。\n\n"
        f"{chunk}\n\n"
        "各質問は具体的かつ文章の要点を掘り下げる内容にしてください。"
    )

    text = _llm.predict(prompt)
    # 改行で切り、空行を除去
    raw_qs = [q.strip() for q in text.split("\n") if q.strip()]
    # 必ず n_questions 件までに制限
    return raw_qs[:n_questions]
