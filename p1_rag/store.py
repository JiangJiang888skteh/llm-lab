import os
import json
import chromadb
from dotenv import load_dotenv
from pathlib import Path
from zhipuai import ZhipuAI

load_dotenv()

client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))


def embed(texts):
    """用智谱 embedding-3 把文本列表转向量"""
    resp = client.embeddings.create(model="embedding-3", input=texts)
    return [item.embedding for item in resp.data]


def store(chunks, db_path="data/chroma_db"):
    """把切片存入 ChromaDB"""
    db = chromadb.PersistentClient(path=db_path)
    col = db.get_or_create_collection("rag_docs")

    texts = [c["text"] for c in chunks]
    vectors = embed(texts)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metas = [{"page": c.get("page", 0), "source": c.get("source", "")} for c in chunks]

    col.upsert(ids=ids, embeddings=vectors, metadatas=metas, documents=texts)
    print(f"已存入 {len(chunks)} 条向量")
    return col


def search(query, top_k=3, db_path="data/chroma_db"):
    """用一句话查相关片段"""
    db = chromadb.PersistentClient(path=db_path)
    col = db.get_collection("rag_docs")

    q_vec = embed([query])
    results = col.query(query_embeddings=q_vec, n_results=top_k)

    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i]
        print(f"\n--- 第 {i+1} 条 (距离={dist:.3f}) ---")
        print(f"来源：{meta.get('source','')} 第{meta.get('page',0)}页")
        print(doc[:200])


if __name__ == "__main__":
    with open("data/pages.json", "r", encoding="utf-8") as f:
        pages = json.load(f)

    from splitter import split_fixed
    chunks = split_fixed(pages, size=800, overlap=100)

    store(chunks)

    print("\n==== 测试搜索 ====")
    search("华为产业学院有几个专业")
