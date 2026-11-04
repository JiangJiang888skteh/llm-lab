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

PROMPT_TEMPLATE = """你是一个严谨的文档助手。请只根据下面提供的资料回答问题。

规则：
1. 答案必须基于资料，不要使用资料以外的知识
2. 每条结论后面用 [1] [2] 标注依据的编号
3. 如果资料里没有相关信息，直接回答"文档中未提及"，不要猜测

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
    client = chromadb.PersistentClient(path=".chroma")
    col = client.get_collection("docs")

    print(f"向量库共 {col.count()} 个片段\n")
    while True:
        q = input("问：")
        if q.lower() == "q":
            break
        ans, srcs = answer(q, col)
        print("\n答：", ans)
        print("\n依据：")
        for i, s in enumerate(srcs, 1):
            print(f"  [{i}] 第{s['page']}页 — {s['text']}...")
        print()
