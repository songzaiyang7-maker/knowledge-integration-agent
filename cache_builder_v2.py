"""Incremental cache builder — processes one textbook at a time to avoid OOM."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "cache_data.json")
os.makedirs(CACHE_DIR, exist_ok=True)

from src.pdf_parser import parse_file
from src.knowledge_extractor import process_textbook
from src.graph_builder import build_graph


def load_existing_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "parsed_textbooks": [],
        "extraction_results": [],
        "all_nodes": [],
        "all_edges": [],
        "book_colors": {},
        "file_list": [],
        "compression_stats": {},
    }


def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    print(f"  Cache saved ({len(cache['all_nodes'])} total nodes)")


def process_one(pdf_path):
    fname = os.path.basename(pdf_path)
    cache = load_existing_cache()

    # Skip if already processed
    if any(f[0] == fname for f in cache["file_list"]):
        print(f"  SKIP (already cached): {fname}")
        return

    print(f"  Processing: {fname}")
    parsed = parse_file(pdf_path)
    extraction = process_textbook(parsed)
    n_nodes = len(extraction.get("nodes", []))
    n_edges = len(extraction.get("edges", []))
    print(f"  -> {n_nodes} nodes, {n_edges} edges")

    # Append to cache
    cache["parsed_textbooks"].append(parsed)
    cache["extraction_results"].append(extraction)

    size_mb = f"{os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB"
    cache["file_list"].append([fname, "PDF", size_mb, "已完成"])

    # Rebuild graph from all results
    all_nodes, all_edges, colors = build_graph(cache["extraction_results"])
    cache["all_nodes"] = all_nodes
    cache["all_edges"] = all_edges
    cache["book_colors"].update(colors)

    # Update stats
    cache["compression_stats"] = {
        "original_textbooks": len(set(n.get("textbook", "") for n in all_nodes)),
        "original_nodes": len(all_nodes),
        "integrated_nodes": len(all_nodes),
        "original_total_chars": sum(len(n.get("definition", "")) for n in all_nodes),
        "integrated_total_chars": sum(len(n.get("definition", "")) for n in all_nodes),
        "compression_ratio": 0,
        "merge_count": 0,
        "keep_count": len(all_nodes),
        "remove_count": 0,
    }

    save_cache(cache)


if __name__ == "__main__":
    textbooks_dir = r"c:\Users\user\Desktop\textbooks"
    pdfs = sorted([f for f in os.listdir(textbooks_dir)
                   if f.lower().endswith(".pdf") and "赛题" not in f])

    print(f"Found {len(pdfs)} textbooks")
    for pdf in pdfs:
        process_one(os.path.join(textbooks_dir, pdf))

    cache = load_existing_cache()
    print(f"\nDONE! {len(cache['file_list'])} textbooks, {len(cache['all_nodes'])} nodes cached.")
