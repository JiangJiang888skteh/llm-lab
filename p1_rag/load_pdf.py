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
    pdf_file = Path("data/学生手册.pdf")
    pages = load_pdf(pdf_file)

    print(f"共 {len(pages)} 页")
    print("---- 第 1 页前 200 字 ----")
    print(pages[0]["text"][:200])

    with open("data/pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print("已保存到 data/pages.json")
