"""PDF parsing module using PyMuPDF (fitz)."""

import os
import re
import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> dict:
    """Parse a PDF file and extract chapters with content.

    Merges pages belonging to the same chapter, producing real chapter-level
    content blocks instead of per-page fragments.

    Returns:
        dict with keys: filename, title, total_pages, total_chars, chapters
    """
    doc = fitz.open(file_path)
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]

    # Extract all page texts first
    page_texts = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        lines = text.split("\n")
        filtered = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^\d+$", stripped):
                continue
            if len(stripped) < 4 and not re.match(r"[一-鿿]", stripped):
                continue
            filtered.append(stripped)
        page_texts.append("\n".join(filtered))

    # Detect true chapter boundaries by finding NEW chapter titles
    # A chapter title is "第X章 ..." that differs from the previous page's chapter
    chapter_breaks = []  # list of (page_num, chapter_title)
    prev_ch_title = None

    for page_num, text in enumerate(page_texts):
        # Look for chapter title in first few lines
        for line in text.split("\n")[:3]:
            m = re.match(r"^(第[一二三四五六七八九十百千\d]+[章节]\s*\S*)", line)
            if m:
                ch_title = m.group(1).strip()
                if ch_title != prev_ch_title:
                    chapter_breaks.append((page_num, line.strip()))
                    prev_ch_title = ch_title
                break

    # If no chapters detected, treat entire doc as one chapter
    if not chapter_breaks:
        all_text = "\n".join(page_texts)
        total_pages = len(doc)
        doc.close()
        return {
            "filename": filename,
            "title": title,
            "total_pages": total_pages,
            "total_chars": len(all_text),
            "chapters": [{
                "chapter_id": "ch_01",
                "title": "全文",
                "page_start": 1,
                "page_end": total_pages,
                "content": all_text,
                "char_count": len(all_text),
            }],
        }

    # Build chapters from breaks
    chapters = []
    total_chars = 0
    for i, (start_page, ch_title) in enumerate(chapter_breaks):
        end_page = chapter_breaks[i + 1][0] - 1 if i + 1 < len(chapter_breaks) else len(page_texts) - 1
        content = "\n".join(page_texts[start_page:end_page + 1]).strip()
        ch = {
            "chapter_id": f"ch_{i + 1:02d}",
            "title": ch_title,
            "page_start": start_page + 1,
            "page_end": end_page + 1,
            "content": content,
            "char_count": len(content),
        }
        total_chars += ch["char_count"]
        chapters.append(ch)

    # Add front matter (pages before first chapter) if exists
    if chapter_breaks[0][0] > 0:
        front_text = "\n".join(page_texts[:chapter_breaks[0][0]]).strip()
        if front_text:
            front_ch = {
                "chapter_id": "ch_00",
                "title": "前言/目录",
                "page_start": 1,
                "page_end": chapter_breaks[0][0],
                "content": front_text,
                "char_count": len(front_text),
            }
            total_chars += front_ch["char_count"]
            chapters.insert(0, front_ch)

    total_pages = len(doc)
    doc.close()

    return {
        "filename": filename,
        "title": title,
        "total_pages": total_pages,
        "total_chars": total_chars,
        "chapters": chapters,
    }


def parse_file(file_path: str) -> dict:
    """Parse a file (PDF/MD/TXT) and return structured content."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in (".md", ".txt"):
        return parse_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def parse_text_file(file_path: str) -> dict:
    """Parse a plain text or markdown file."""
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Split by chapter headings for markdown
    sections = re.split(r"(^#{1,3}\s+.+$|^第[一二三四五六七八九十百千\d]+章\s*.+$)", text, flags=re.MULTILINE)

    chapters = []
    current_text = ""
    ch_idx = 0

    i = 0
    while i < len(sections):
        s = sections[i].strip()
        if not s:
            i += 1
            continue
        # Check if this is a heading
        if re.match(r"^(#{1,3}\s+.+|第[一二三四五六七八九十百千\d]+章\s*.+)", s):
            if current_text.strip():
                ch_idx += 1
                chapters.append({
                    "chapter_id": f"ch_{ch_idx:02d}",
                    "title": "前言" if ch_idx == 1 else f"章节 {ch_idx}",
                    "page_start": 1,
                    "page_end": 1,
                    "content": current_text.strip(),
                    "char_count": len(current_text.strip()),
                })
            ch_idx += 1
            ch_title = re.sub(r"^#{1,3}\s+", "", s).strip()
            # Get content after heading
            content = sections[i + 1].strip() if i + 1 < len(sections) else ""
            chapters.append({
                "chapter_id": f"ch_{ch_idx:02d}",
                "title": ch_title,
                "page_start": 1,
                "page_end": 1,
                "content": content,
                "char_count": len(content),
            })
            current_text = ""
            i += 2
        else:
            current_text += s + "\n"
            i += 1

    if current_text.strip():
        ch_idx += 1
        chapters.append({
            "chapter_id": f"ch_{ch_idx:02d}",
            "title": f"章节 {ch_idx}",
            "page_start": 1,
            "page_end": 1,
            "content": current_text.strip(),
            "char_count": len(current_text.strip()),
        })

    return {
        "filename": filename,
        "title": title,
        "total_pages": 1,
        "total_chars": len(text),
        "chapters": chapters if chapters else [{
            "chapter_id": "ch_01",
            "title": "全文",
            "page_start": 1,
            "page_end": 1,
            "content": text,
            "char_count": len(text),
        }],
    }
