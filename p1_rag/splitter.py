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
