"""PDF parsing module using PyMuPDF (fitz)."""

import os
import re
import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> dict:
    """Parse a PDF file and extract chapters with content.

    Returns:
        dict with keys: filename, title, total_pages, total_chars, chapters
    """
    doc = fitz.open(file_path)
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]

    chapters = []
    current_chapter = None
    total_chars = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        # Filter headers/footers (short repeated lines)
        lines = text.split("\n")
        filtered = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Skip page numbers
            if re.match(r"^\d+$", stripped):
                continue
            # Skip very short lines that look like headers/footers
            if len(stripped) < 4 and not re.match(r"[一-鿿]", stripped):
                continue
            filtered.append(stripped)

        page_text = "\n".join(filtered)

        # Detect chapter boundaries
        chapter_match = re.match(r"^(第[一二三四五六七八九十百千\d]+章\s*.+)", page_text)

        if chapter_match:
            # Save previous chapter
            if current_chapter:
                current_chapter["content"] = current_chapter["content"].strip()
                current_chapter["char_count"] = len(current_chapter["content"])
                total_chars += current_chapter["char_count"]
                chapters.append(current_chapter)

            ch_title = chapter_match.group(1).strip()
            current_chapter = {
                "chapter_id": f"ch_{len(chapters) + 1:02d}",
                "title": ch_title,
                "page_start": page_num + 1,
                "page_end": page_num + 1,
                "content": page_text,
                "char_count": 0,
            }
        else:
            if current_chapter is None:
                # Content before first chapter heading
                current_chapter = {
                    "chapter_id": "ch_00",
                    "title": "前言/目录",
                    "page_start": page_num + 1,
                    "page_end": page_num + 1,
                    "content": page_text,
                    "char_count": 0,
                }
            else:
                current_chapter["content"] += "\n" + page_text
                current_chapter["page_end"] = page_num + 1

    # Save last chapter
    if current_chapter:
        current_chapter["content"] = current_chapter["content"].strip()
        current_chapter["char_count"] = len(current_chapter["content"])
        total_chars += current_chapter["char_count"]
        chapters.append(current_chapter)

    doc.close()

    return {
        "filename": filename,
        "title": title,
        "total_pages": len(doc) if hasattr(doc, '__len__') else 0,
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
