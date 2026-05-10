"""Incremental cache builder v3 — one book per run, auto-restart for next."""

import json
import os
import sys
import gc
import traceback

sys.path.insert(0, os.path.dirname(__file__))
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,open.bigmodel.cn,huggingface.co'

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "cache_data.json")
os.makedirs(CACHE_DIR, exist_ok=True)

TEXTBOOKS_DIR = r"c:\Users\user\Desktop\textbooks"


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"extraction_results": [], "book_colors": {}, "file_list": [],
            "all_nodes": [], "all_edges": []}


def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


def get_pending():
    """Return list of PDFs not yet in cache."""
    cache = load_cache()
    done = {f[0] for f in cache["file_list"]}
    pdfs = sorted([f for f in os.listdir(TEXTBOOKS_DIR)
                   if f.endswith(".pdf") and "赛题" not in f and f not in done])
    return pdfs


def process_next():
    """Process the next pending textbook. Returns True if one was processed."""
    pending = get_pending()
    if not pending:
        print("All textbooks processed!")
        return False

    pdf_name = pending[0]
    pdf_path = os.path.join(TEXTBOOKS_DIR, pdf_name)
    print(f"Processing [{pdf_name}]...")

    try:
        from src.pdf_parser import parse_file
        from src.knowledge_extractor import process_textbook

        # Parse & extract
        parsed = parse_file(pdf_path)
        extraction = process_textbook(parsed)
        n_nodes = len(extraction.get("nodes", []))
        n_edges = len(extraction.get("edges", []))
        print(f"  Extracted: {n_nodes} nodes, {n_edges} edges")

        # Free parse memory
        del parsed
        gc.collect()

        # Load cache & append extraction result only (skip build_graph to save memory)
        cache = load_cache()
        cache["extraction_results"].append(extraction)
        size_mb = f"{os.path.getsize(pdf_path)/1024/1024:.1f} MB"
        cache["file_list"].append([pdf_name, "PDF", size_mb, "已完成"])

        # Simple node merge (no build_graph to avoid OOM)
        for n in extraction.get("nodes", []):
            cache["all_nodes"].append(n)
        for e in extraction.get("edges", []):
            cache["all_edges"].append(e)

        # Stats
        cache["compression_stats"] = {
            "original_textbooks": len(set(n.get("textbook", "") for n in all_nodes)),
            "original_nodes": len(all_nodes),
            "integrated_nodes": len(all_nodes),
            "original_total_chars": sum(len(n.get("definition", "")) for n in all_nodes),
            "integrated_total_chars": sum(len(n.get("definition", "")) for n in all_nodes),
            "compression_ratio": 0, "merge_count": 0,
            "keep_count": len(all_nodes), "remove_count": 0,
        }

        save_cache(cache)
        done = len(cache["file_list"])
        print(f"  Saved! ({done}/7 done, {len(all_nodes)} total nodes)")

        # Free memory
        del cache, extraction, all_nodes, all_edges, colors
        gc.collect()
        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(f"Cache builder v3 (one-at-a-time)")
    remaining = get_pending()
    print(f"Pending: {len(remaining)} textbooks")

    if not remaining:
        cache = load_cache()
        print(f"Cache complete: {len(cache['file_list'])} books, {len(cache['all_nodes'])} nodes")
    else:
        # Process ONE book, then exit. Runner script will restart us.
        process_next()
