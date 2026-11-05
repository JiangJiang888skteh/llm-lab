import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

from load_pdf import load_pdf
from splitter import split_fixed
from store import embed

load_dotenv()

llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

PROMPT_TEMPLATE = """你是成都锦城学院电子信息学院的智能顾问，用友好、简洁的语气回答学生的问题。

规则：
1. 基于下面提供的资料回答，不要编造资料里没有的信息
2. 用口语化的方式表达，像学长学姐在聊天一样
3. 不要在回答中标注 [1] [2] 这类引用编号，直接说就好
4. 如果资料里没有相关信息，就说"这个我暂时不太清楚，建议去学院官网看看"
5. 回答控制在 3-5 句话

资料：
{context}

问题：{question}
"""

def format_context(hits):
    """把检索结果拼成带编号的资料块"""
    blocks = []
    for i, (doc, meta) in enumerate(hits, 1):
        blocks.append(f"[{i}] (第{meta['page']}页)\n{doc}")
    return "\n\n".join(blocks)

def answer(question, col, k=5):
    q_vec = embed([question])[0]
    res = col.query(query_embeddings=[q_vec], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]

    context = format_context(list(zip(docs, metas)))
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    text = resp.choices[0].message.content

    sources = [
        {"page": m["page"], "text": d[:120]}
        for d, m in zip(docs, metas)
    ]
    return text, sources


if __name__ == "__main__":
    client = chromadb.PersistentClient(path="data/chroma_db")
    col = client.get_collection("rag_docs")

    print(f"向量库共 {col.count()} 个片段\n")
    while True:
        q = input("问：")
        if q.lower() == "q":
            break
        ans, srcs = answer(q, col)
        print("\n答：", ans)
        print()
