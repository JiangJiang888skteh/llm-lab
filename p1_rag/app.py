import os
import base64
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import chromadb

from store import embed
from openai import OpenAI

load_dotenv()

MORANDI = {
    "bg": "#D5DEE6",
    "primary": "#4A6B7F",
    "accent": "#7A9BAD",
    "text": "#2C3E50",
    "light_text": "#5A7A8F",
    "bubble_ai": "#C4D2DC",
    "bubble_user": "#8FB3C9",
    "border": "#A3B8C8",
}

st.set_page_config(page_title="华为产业学院顾问", page_icon="🎓", layout="wide")

# 读取头像为 base64
mascot_file = Path(__file__).parent / "mascot.png"
with open(mascot_file, "rb") as f:
    mascot_b64 = base64.b64encode(f.read()).decode()
mascot_img = f"data:image/png;base64,{mascot_b64}"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    * {{ font-family: 'Noto Sans SC', sans-serif; }}
    .stApp {{ background-color: {MORANDI["bg"]}; }}

    .main-header {{ text-align: center; padding: 1.5rem 0 0.5rem; }}
    .main-header h1 {{ color: {MORANDI["primary"]}; font-weight: 700; font-size: 2rem; margin-bottom: 0.3rem; }}
    .main-header p {{ color: {MORANDI["light_text"]}; font-size: 0.95rem; }}

    .chat-container {{ max-height: 520px; overflow-y: auto; padding: 1rem; }}

    .msg {{ display: flex; margin-bottom: 1rem; align-items: flex-start; }}
    .msg.user {{ flex-direction: row-reverse; }}
    .msg-avatar {{
        width: 42px; height: 42px; border-radius: 50%;
        flex-shrink: 0; overflow: hidden;
        border: 2px solid {MORANDI["border"]};
    }}
    .msg-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
    .msg-bubble {{
        max-width: 70%; padding: 0.8rem 1.1rem;
        border-radius: 18px; font-size: 0.95rem;
        line-height: 1.6; color: {MORANDI["text"]};
    }}
    .msg.ai .msg-bubble {{
        background-color: {MORANDI["bubble_ai"]};
        border-bottom-left-radius: 6px; margin-left: 0.6rem;
    }}
    .msg.user .msg-bubble {{
        background-color: {MORANDI["bubble_user"]};
        border-bottom-right-radius: 6px; margin-right: 0.6rem;
    }}

    .source-card {{
        background: #FFF; border: 1px solid {MORANDI["border"]};
        border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.6rem;
    }}
    .source-card .src-title {{
        font-weight: 600; color: {MORANDI["primary"]};
        font-size: 0.85rem; margin-bottom: 0.3rem;
    }}
    .source-card .src-text {{
        color: {MORANDI["light_text"]}; font-size: 0.82rem; line-height: 1.5;
    }}

    .doc-tag {{
        display: inline-block; background: {MORANDI["bubble_ai"]};
        color: {MORANDI["text"]}; padding: 0.25rem 0.7rem;
        border-radius: 20px; font-size: 0.78rem; margin: 0.2rem;
    }}
    hr {{ border-color: {MORANDI["border"]}; }}
</style>
""", unsafe_allow_html=True)

# ── 会话状态 ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "col" not in st.session_state:
    db = chromadb.PersistentClient(path="data/chroma_db")
    st.session_state.col = db.get_collection("rag_docs")
if "pending" not in st.session_state:
    st.session_state.pending = None

PROMPT = """你是成都锦城学院电子信息学院的智能顾问"小锦"，戴着眼镜，性格呆萌但很靠谱。
用友好、简洁的语气回答学生的问题。

规则：
1. 基于下面提供的资料回答，不要编造资料里没有的信息
2. 用口语化的方式表达，像学长学姐在聊天一样
3. 不要在回答中标注引用编号，直接说就好
4. 如果资料里没有相关信息，就说"这个我暂时不太清楚，建议去学院官网看看哦～"
5. 回答控制在 3-5 句话
6. 开头可以偶尔用"嗯～""这个嘛""好问题！"等语气词，显得自然

资料：
{context}

问题：{question}
"""

llm = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def get_answer(question, col, k=8):
    q_vec = embed([question])[0]
    res = col.query(query_embeddings=[q_vec], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]

    blocks = []
    for i, (doc, meta) in enumerate(zip(docs, metas), 1):
        blocks.append(f"[{i}] (第{meta.get('page', 0)}页 | {meta.get('source', '')})\n{doc}")
    context = "\n\n".join(blocks)

    prompt = PROMPT.format(context=context, question=question)
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = resp.choices[0].message.content

    sources = [
        {"idx": i, "page": m.get("page", 0), "source": m.get("source", ""), "text": d[:200]}
        for i, (d, m) in enumerate(zip(docs, metas), 1)
    ]
    return text, sources


def render_messages():
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="msg ai">
            <div class="msg-avatar"><img src="{mascot_img}"></div>
            <div class="msg-bubble">
                嗨～我是小锦！🎓 关于电子信息学院和华为产业学院的问题都可以问我哦，比如专业设置、实训平台、师资力量什么的～
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg user">
                <div class="msg-avatar" style="background: {MORANDI['accent']}; display:flex; align-items:center; justify-content:center; color:white; font-size:1.2rem;">我</div>
                <div class="msg-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg ai">
                <div class="msg-avatar"><img src="{mascot_img}"></div>
                <div class="msg-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)


# ── 侧边栏 ──
with st.sidebar:
    st.markdown("### 🎓 关于小锦")
    st.image(str(mascot_file), width=160)
    st.markdown("""
    <div style="color: #5A7A8F; font-size: 0.85rem; line-height: 1.6;">
    我是<strong>小锦</strong>，电子信息学院的智能顾问～<br>
    戴着眼镜，有点呆萌，但关于学院的问题我都很认真回答哦！<br><br>
    📚 知识库来源：<br>
    华为产业学院概况、多功能中心等学院文档
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 试试问这些")
    questions = [
        "华为产业学院有几个专业？",
        "学院有哪些实训平台？",
        "华为创新班是什么？",
        "学院有多少老师？",
    ]
    for q in questions:
        if st.button(q, use_container_width=True, type="secondary"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.pending = q
            st.rerun()


# ── 主区域 ──
st.markdown("""
<div class="main-header">
    <h1>🎓 电子信息学院华为产业学院顾问</h1>
    <p>你好！我是小锦，关于华为产业学院的问题随便问～</p>
</div>
""", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    render_messages()
    st.markdown('</div>', unsafe_allow_html=True)

# 处理待回答的问题
if st.session_state.pending:
    question = st.session_state.pending
    st.session_state.pending = None

    # 判断是否在问依据
    source_keywords = ["依据", "来源", "出处", "哪里看到的", "文档中", "原文"]
    is_source_query = any(kw in question for kw in source_keywords)

    if is_source_query:
        # 找最近一条 AI 回答的来源
        last_sources = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant" and msg.get("sources"):
                last_sources = msg["sources"]
                break

        if last_sources:
            src_text = "\n".join([
                f"📄 {s['source']}（第{s['page']}页）：{s['text'][:150]}..."
                for s in last_sources
            ])
            reply = f"这个问题的依据来自以下文档片段：\n\n{src_text}"
        else:
            reply = "嗯～前面没有找到相关的文档依据，要不你换个问题问问看？"

        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        with st.spinner("小锦正在思考..."):
            answer, sources = get_answer(question, st.session_state.col)
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

    st.rerun()

# 输入框
user_input = st.chat_input("问小锦一个问题...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.pending = user_input
    st.rerun()
