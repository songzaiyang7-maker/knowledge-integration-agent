"""Knowledge point extraction from parsed textbook content via LLM."""

import json
import uuid
from src.llm_client import call_llm_json

EXTRACT_SYSTEM_PROMPT = """你是一位学科知识分析专家。你的任务是从教材文本中提取知识点和知识点之间的关系。

## 知识点粒度定义
- 一个知识点 = 一个可独立考查的概念/定理/方法/现象
- 每个知识点必须有独立的定义，可以单独解释，可以出考题
- 不要提取过于笼统的上位概念（如"生理学"、"细胞"），也不要提取过细的子步骤
- 如果两个概念总是一起出现且无法独立解释，合并为一个知识点

## 关系类型（4种）
1. prerequisite: A是B的前置知识，学B之前必须先学A
2. parallel: A和B是并列关系，属于同一层级
3. contains: A包含B（整体-部分关系）
4. applies_to: A应用于B（方法-对象关系）

## 输出格式
返回严格的JSON，格式如下：
```json
{
  "knowledge_points": [
    {
      "name": "知识点名称",
      "definition": "知识点的完整定义（1-3句话）",
      "category": "核心概念|基本组成|生理过程|方法技术"
    }
  ],
  "relations": [
    {
      "source": "知识点A名称",
      "target": "知识点B名称",
      "relation_type": "prerequisite|parallel|contains|applies_to",
      "description": "关系说明"
    }
  ]
}
```

注意：
- 尽可能多地提取知识点，不要遗漏
- 每个知识点必须有清晰的definition
- 关系只在确实存在时才提取，不要硬编
- 只输出JSON，不要输出其他内容"""


def extract_knowledge_points(chapter_content: str, textbook_title: str, chapter_title: str) -> dict:
    """Extract knowledge points and relations from a chapter's content.

    Returns:
        dict with "knowledge_points" and "relations" lists.
    """
    user_prompt = f"""请从以下教材内容中提取知识点和关系。

教材：《{textbook_title}》
章节：{chapter_title}

内容：
{chapter_content[:6000]}

请严格按照JSON格式输出知识点和关系。"""

    result = call_llm_json(EXTRACT_SYSTEM_PROMPT, user_prompt, max_tokens=4096)

    if not result or not isinstance(result, dict):
        return {"knowledge_points": [], "relations": []}

    return result


def process_textbook(parsed_data: dict) -> dict:
    """Process a full parsed textbook and extract all knowledge points.

    Returns:
        dict with "nodes" and "edges" lists suitable for graph building.
    """
    title = parsed_data["title"]
    all_nodes = []
    all_edges = []

    name_to_id = {}
    book_prefix = title[:3]

    for chapter in parsed_data.get("chapters", []):
        content = chapter.get("content", "")
        if len(content.strip()) < 50:
            continue

        chapter_title = chapter.get("title", "")
        page_start = chapter.get("page_start", 1)

        result = extract_knowledge_points(content, title, chapter_title)

        for kp in result.get("knowledge_points", []):
            name = kp.get("name", "").strip()
            if not name:
                continue

            if name in name_to_id:
                # Update frequency
                existing = next(n for n in all_nodes if n["id"] == name_to_id[name])
                existing["frequency"] += 1
                continue

            node_id = f"{book_prefix}_{uuid.uuid4().hex[:6]}"
            name_to_id[name] = node_id

            all_nodes.append({
                "id": node_id,
                "name": name,
                "definition": kp.get("definition", ""),
                "category": kp.get("category", "核心概念"),
                "chapter": chapter_title,
                "page": page_start,
                "textbook": title,
                "frequency": 1,
            })

        for rel in result.get("relations", []):
            src_name = rel.get("source", "").strip()
            tgt_name = rel.get("target", "").strip()
            rel_type = rel.get("relation_type", "prerequisite")

            src_id = name_to_id.get(src_name)
            tgt_id = name_to_id.get(tgt_name)

            if src_id and tgt_id and src_id != tgt_id:
                # Avoid duplicate edges
                dup = any(
                    e["source"] == src_id and e["target"] == tgt_id and e["relation_type"] == rel_type
                    for e in all_edges
                )
                if not dup:
                    all_edges.append({
                        "source": src_id,
                        "target": tgt_id,
                        "relation_type": rel_type,
                        "description": rel.get("description", ""),
                    })

    return {"nodes": all_nodes, "edges": all_edges}
