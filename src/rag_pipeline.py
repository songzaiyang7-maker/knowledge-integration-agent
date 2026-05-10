"""RAG pipeline — chunking, indexing, retrieval, and generation."""

import numpy as np
import faiss
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, RAG_TOP_K
from src.embedding import encode_texts
from src.llm_client import call_llm

RAG_SYSTEM_PROMPT = """你是一位学科知识问答专家。请根据提供的参考资料回答用户问题。

## 严格要求
1. 只根据提供的参考资料回答，不要编造信息
2. 如果参考资料中没有相关信息，回答"当前知识库中未找到相关信息"
3. 回答时必须标注引用来源（教材名、章节、页码）
4. 使用Markdown格式，清晰结构化回答
"""


class RAGPipeline:
    def __init__(self):
        self.chunks = []       # list of chunk dicts
        self.embeddings = None  # numpy array
        self.index = None       # FAISS index
        self.indexed = False

    def add_textbook(self, parsed_data: dict):
        """Add a parsed textbook to the RAG index."""
        textbook_title = parsed_data["title"]

        for chapter in parsed_data.get("chapters", []):
            content = chapter.get("content", "")
            if not content.strip():
                continue

            chapter_title = chapter.get("title", "")
            page_start = chapter.get("page_start", 1)

            # Chunk the content
            chapter_chunks = self._chunk_text(content)

            for i, chunk_text in enumerate(chapter_chunks):
                self.chunks.append({
                    "text": chunk_text,
                    "textbook": textbook_title,
                    "chapter": chapter_title,
                    "page": page_start + (i * CHUNK_SIZE // CHUNK_SIZE),
                    "chunk_id": len(self.chunks),
                })

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def build_index(self):
        """Build FAISS index from accumulated chunks."""
        if not self.chunks:
            return

        texts = [c["text"] for c in self.chunks]
        self.embeddings = encode_texts(texts)

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product for cosine similarity (embeddings are normalized)
        self.index.add(self.embeddings.astype(np.float32))
        self.indexed = True

    def search(self, query: str, top_k: int = RAG_TOP_K) -> list[dict]:
        """Search for relevant chunks given a query."""
        if not self.indexed:
            return []

        query_emb = encode_texts([query])

        scores, indices = self.index.search(query_emb.astype(np.float32), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "textbook": chunk["textbook"],
                "chapter": chunk["chapter"],
                "page": chunk["page"],
                "relevance_score": float(score),
            })

        return results

    def answer(self, question: str) -> dict:
        """Answer a question using RAG."""
        results = self.search(question)

        if not results:
            return {
                "answer": "当前知识库中未找到相关信息。请先上传并解析教材。",
                "citations": [],
                "source_chunks": [],
            }

        # Build context from retrieved chunks
        context_parts = []
        for i, r in enumerate(results):
            context_parts.append(
                f"[来源{i+1}] 《{r['textbook']}》{r['chapter']}，第{r['page']}页（相关度: {r['relevance_score']:.2f}）\n{r['text'][:300]}"
            )

        context = "\n\n".join(context_parts)

        user_prompt = f"""参考资料：
{context}

用户问题：{question}

请根据以上参考资料回答问题，并标注引用来源。"""

        answer = call_llm(RAG_SYSTEM_PROMPT, user_prompt, max_tokens=2048)

        citations = [
            {
                "textbook": r["textbook"],
                "chapter": r["chapter"],
                "page": r["page"],
                "relevance_score": r["relevance_score"],
            }
            for r in results
        ]

        source_chunks = [r["text"][:300] for r in results]

        return {
            "answer": answer,
            "citations": citations,
            "source_chunks": source_chunks,
        }

    def get_status(self) -> dict:
        """Return current indexing status."""
        return {
            "indexed_textbooks": len(set(c["textbook"] for c in self.chunks)),
            "total_chunks": len(self.chunks),
            "total_chars": sum(len(c["text"]) for c in self.chunks),
        }
