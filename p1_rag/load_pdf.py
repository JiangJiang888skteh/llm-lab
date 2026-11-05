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


def load_txt(txt_path):
    """把 txt 文件当成一整页，返回 [{page, text}]"""
    text = txt_path.read_text(encoding="utf-8")
    if text.strip():
        return [{"page": 1, "text": text}]
    return []


if __name__ == "__main__":
    data_dir = Path("data")
    pdf_files = sorted(data_dir.glob("*.pdf"))
    txt_files = sorted(data_dir.glob("*.txt"))
    all_files = pdf_files + txt_files

    if not all_files:
        print("data 文件夹里没有 PDF 或 txt 文件！")
        exit(1)

    all_pages = []
    for f in all_files:
        print(f"正在解析：{f.name}")
        if f.suffix == ".pdf":
            pages = load_pdf(f)
        else:
            pages = load_txt(f)
        for p in pages:
            p["source"] = f.name
        all_pages.extend(pages)
        print(f"  → {len(pages)} 页")

    print(f"\n共 {len(all_pages)} 页，来自 {len(all_files)} 个文件（{len(pdf_files)} PDF + {len(txt_files)} txt）")
    print("---- 第 1 页前 200 字 ----")
    print(all_pages[0]["text"][:200])

    with open("data/pages.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=2)
    print("已保存到 data/pages.json")
