def split_fixed(pages, size=500, overlap=0):
    """v1：最笨的切法。故意先做笨的，让你亲眼看到问题。"""
    chunks = []
    for p in pages:
        text = p["text"]
        for i in range(0, len(text), size - overlap):
            piece = text[i:i + size]
            if len(piece) < 50:
                continue
            chunks.append({
                "text": piece,
                "page": p["page"]
            })
    return chunks


if __name__ == "__main__":
    import json
    from pathlib import Path

    with open("data/pages.json", "r", encoding="utf-8") as f:
        pages = json.load(f)

    chunks = split_fixed(pages, size=500, overlap=0)

    print(f"共 {len(pages)} 页 → 切成 {len(chunks)} 块")
    print("---- 第 1 块 ----")
    print(chunks[0]["text"])
    print(f"\n---- 第 2 块 ----")
    print(chunks[1]["text"])
