import streamlit as st
# ─── ページ設定は最初の Streamlit コマンドとして配置 ─────────────────
st.set_page_config(page_title="📚 読書理解チェックアプリ (MVP)")


from dotenv import load_dotenv
import chardet

from utils.loader import load_text
from utils.chunker import chunk_text
from utils.generator import generate_questions_for_chunk
from utils.scorer import score_answer
from utils.db import init_db, save_questions, save_answer

# ─── 初期設定 ─────────────────────────
load_dotenv()


init_db()
st.title("📚 読書理解チェックアプリ (MVP)")


# ─── サイドバー：チャンクあたりの質問数 ─────────────────
n_q = st.sidebar.slider(
    "チャンクあたりの質問数", min_value=1, max_value=10, value=1, step=1
)

# ─── ファイルアップロード or サンプル読み込み ─────────────────
uploaded = st.file_uploader("テキストファイルをアップロード", type=["txt"])
if uploaded:
    raw = uploaded.read()
    enc = chardet.detect(raw)["encoding"]
    try:
        text = raw.decode(enc)
        st.success(f"ファイルを正常に読み込みました（文字コード:{enc}）。")
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        st.stop()
else:
    st.info("テスト用サンプルテキストを使用します")
    text = load_text("data/sample_text.txt")

# ─── テキスト切り替え検知 & セッションリセット ─────────────────
if st.session_state.get("last_text") != text:
    st.session_state["last_text"] = text
    st.session_state["questions_generated"] = False
    # 旧データをクリア
    for k in list(st.session_state.keys()):
        if k.startswith(("questions", "q_ids", "answer_", "score_", "fb_")):
            del st.session_state[k]

# ─── テキストをチャンク分割 ─────────────────────────
chunks = chunk_text(text)

# ─── 質問生成トリガー ─────────────────────────
if st.button("🔎 質問を生成する"):
    # 生成フラグを立てて、セッションにリストを初期化
    st.session_state["questions_generated"] = True
    st.session_state["questions"] = []
    st.session_state["q_ids"] = []
    st.success("チャンクごとに質問を生成します。各チャンクを展開してください。")

# ─── 質問生成後の各チャンク表示 & 回答・採点 ─────────────────
if st.session_state.get("questions_generated"):
    for idx, chunk in enumerate(chunks):
        with st.expander(f"チャンク {idx+1} の質問と回答"):
            # このチャンクが未生成ならここで生成
            if len(st.session_state.questions) <= idx:
                with st.spinner(f"チャンク {idx+1} の質問を生成中…"):
                    qs = generate_questions_for_chunk(chunk, n_questions=n_q)
                    ids = save_questions(idx, qs)
                    st.session_state.questions.append(qs)
                    st.session_state.q_ids.append(ids)
            # 既に生成済みならセッションから読み出し
            qs = st.session_state.questions[idx]
            ids = st.session_state.q_ids[idx]

            # 質問リスト ➡ 回答入力 ➡ 採点 ➡ フィードバック
            for qid, q_text in zip(ids, qs):
                st.write(f"**Q:** {q_text}")
                # 回答入力
                akey = f"answer_{qid}"
                if akey not in st.session_state:
                    st.session_state[akey] = ""
                answer = st.text_input("回答を入力", value=st.session_state[akey], key=akey)

                # 採点ボタン
                skey = f"score_{qid}"
                fkey = f"fb_{qid}"
                if st.button("採点する", key=f"btn_{qid}"):
                    sc, fb = score_answer(
                        question=q_text,
                        user_answer=answer,
                        reference=chunk
                    )
                    save_answer(qid, answer, sc, fb)
                    st.session_state[skey] = sc
                    st.session_state[fkey] = fb

                # 採点結果とフィードバック表示
                if skey in st.session_state:
                    st.write(f"**点数：** {st.session_state[skey]}")
                if fkey in st.session_state:
                    st.write(f"**正解例：** {st.session_state[fkey]}")
else:
    st.info("まずは「🔎 質問を生成する」ボタンを押してください。")
