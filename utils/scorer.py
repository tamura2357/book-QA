import os
from typing import Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import re

# .env から API キーを読み込む
load_dotenv()

_scorer_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def score_answer(
    question: str,
    user_answer: str,
    reference: str
) -> Tuple[int, str]:
    """
    ユーザーの回答を LLM にプロンプト採点させ、
    (score, feedback) のタプルで返す。
    """
    prompt = (
        f"文章：\n{reference}\n\n"
        f"設問：{question}\n"
        f"受験者の回答：{user_answer}\n\n"
        "あなたはこの文章に関する専門家です。\n"
        "合計100点満点で採点した上で、以下のフォーマットで出力してください：\n"

        "フォーマット：\n"
        "点数：XX/100\n"
        "正解例：（簡潔な模範回答）"
    )



    content = _scorer_llm.predict(prompt).strip()
    # 実際のモデル出力を取得
    content = _scorer_llm.predict(prompt).strip()
    # 点数を抽出（「点数：XX」）
    m = re.search(r"点数[：:]\s*(\d+)", content)
    score = int(m.group(1)) if m else 0
    # フィードバック部分を「フィードバック：」以降すべて取得
    parts = re.split(r"正解例[：:]", content, maxsplit=1)
    feedback = parts[1].strip() if len(parts) > 1 else ""
    return score, feedback
