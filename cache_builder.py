"""
缓存构建脚本 - 预先加载教材并序列化结果到磁盘
运行方式: python cache_builder.py
"""

import json
import os
import sys
import traceback
import pickle

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.pdf_parser import parse_file
from src.knowledge_extractor import process_textbook
from src.graph_builder import build_graph, get_book_color
from src.rag_pipeline import RAGPipeline
from src.config import UPLOAD_DIR

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
FAISS_DIR = os.path.join(CACHE_DIR, "faiss_index")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)


def build_cache():
    """预先加载所有教材并缓存结果."""
    textbooks_dir = r"c:\Users\user\Desktop\textbooks"
    if not os.path.isdir(textbooks_dir):
        print(f"[WARN] Textbooks dir not found: {textbooks_dir}")
        return

    pdf_files = [
        os.path.join(textbooks_dir, f)
        for f in os.listdir(textbooks_dir)
        if f.lower().endswith(".pdf") and "赛题" not in f
    ]

    if not pdf_files:
        print("[WARN] No PDF files found")
        return

    print(f"Building cache for {len(pdf_files)} textbooks...")

    parsed_textbooks = []
    extraction_results = []
    file_list = []
    book_colors = {}

    for pdf_path in pdf_files:
        fname = os.path.basename(pdf_path)
        print(f"  Parsing: {fname}")

        try:
            parsed = parse_file(pdf_path)
            parsed_textbooks.append(parsed)

            extraction = process_textbook(parsed)
            extraction_results.append(extraction)

            size_mb = f"{os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB"
            file_list.append([fname, "PDF", size_mb, "已完成"])

            print(f"    OK: {len(extraction.get('nodes', []))} nodes")

        except Exception as e:
            size_mb = f"{os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB"
            file_list.append([fname, "PDF", size_mb, "失败"])
            print(f"    FAILED: {e}")
            traceback.print_exc()

    # Build unified graph
    all_nodes, all_edges, colors = build_graph(extraction_results)
    book_colors.update(colors)

    # Build RAG index
    rag = RAGPipeline()
    for parsed in parsed_textbooks:
        rag.add_textbook(parsed)
    rag.build_index()

    # Save FAISS index
    faiss_index_path = os.path.join(FAISS_DIR, "index.pkl")
    with open(faiss_index_path, "wb") as f:
        pickle.dump(rag, f)
    print(f"  FAISS index saved: {faiss_index_path}")

    # Save cache data
    cache_data = {
        "parsed_textbooks": parsed_textbooks,
        "extraction_results": extraction_results,
        "all_nodes": all_nodes,
        "all_edges": all_edges,
        "book_colors": book_colors,
        "file_list": file_list,
        "compression_stats": _compute_compression_stats(all_nodes),
    }

    cache_path = os.path.join(CACHE_DIR, "cache_data.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    print(f"  Cache saved: {cache_path}")
    print(f"\nCache built: {len(parsed_textbooks)} textbooks, {len(all_nodes)} nodes")


def _compute_compression_stats(nodes):
    """计算压缩统计."""
    original_nodes = len(nodes)
    integrated_nodes = original_nodes  # 整合后暂未计算
    original_total_chars = sum(len(n.get("definition", "")) for n in nodes)
    integrated_total_chars = original_total_chars  # 暂用相同值
    compression_ratio = int((1 - integrated_nodes / original_nodes) * 100) if original_nodes > 0 else 0

    return {
        "original_textbooks": len(set(n.get("textbook", "") for n in nodes)),
        "original_nodes": original_nodes,
        "integrated_nodes": integrated_nodes,
        "original_total_chars": original_total_chars,
        "integrated_total_chars": integrated_total_chars,
        "compression_ratio": max(0, compression_ratio),
        "merge_count": 0,
        "keep_count": original_nodes,
        "remove_count": 0,
    }


if __name__ == "__main__":
    print("=" * 50)
    print("缓存构建脚本 - 预先加载教材")
    print("=" * 50)
    build_cache()
    print("\n缓存构建完成！")