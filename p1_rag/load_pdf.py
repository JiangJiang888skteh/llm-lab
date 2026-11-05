import pdfplumber
import json
from pathlib import Path

def load_pdf(pdf_path):
    """把 PDF 转成 [{page, text}] 列表"""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({
                    "page": i + 1,
                    "text": text
                })
    return pages


if __name__ == "__main__":
    data_dir = Path("data")
    pdf_files = sorted(data_dir.glob("*.pdf"))

    if not pdf_files:
        print("data 文件夹里没有 PDF 文件！")
        exit(1)

    all_pages = []
    for pdf_file in pdf_files:
        print(f"正在解析：{pdf_file.name}")
        pages = load_pdf(pdf_file)
        for p in pages:
            p["source"] = pdf_file.name
        all_pages.extend(pages)
        print(f"  → {len(pages)} 页")

    print(f"\n共 {len(all_pages)} 页，来自 {len(pdf_files)} 个 PDF")
    print("---- 第 1 页前 200 字 ----")
    print(all_pages[0]["text"][:200])

    with open("data/pages.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=2)
    print("已保存到 data/pages.json")
