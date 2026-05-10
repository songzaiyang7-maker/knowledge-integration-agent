"""Cross-textbook knowledge integration — three-level alignment algorithm."""

import uuid
from src.config import EMBEDDING_SIMILARITY_THRESHOLD, LLM_CONFIDENCE_THRESHOLD
from src.embedding import find_similar_pairs, encode_texts
from src.llm_client import call_llm_json

INTEGRATE_SYSTEM_PROMPT = """你是一位学科知识整合专家。你需要判断两个来自不同教材的知识点是否应该合并、保留或删除。

## 判定标准
1. **merge（合并）**：两个知识点描述的是同一个概念，只是表述不同或详略不同。合并后保留更完整准确的定义。
2. **keep（保留）**：两个知识点虽然相关但是不同的概念，都应保留。
3. **remove（删除）**：其中一个知识点是另一个的上位笼统概念，被更具体的子概念完全覆盖。

## 注意
- 跨语言等价概念（如"白细胞"="leukocyte"）应合并
- 概念包含关系（"免疫应答"⊃"体液免疫"）不算重复，应保留
- 合并时将最完整准确的定义保留，可融合两者优点

## 输出格式
```json
{
  "action": "merge|keep|remove",
  "confidence": 0.0-1.0,
  "merged_name": "合并后的名称",
  "merged_definition": "合并后的定义（merge时必须提供）",
  "reason": "决策理由"
}
```"""


def level1_exact_match(all_nodes: list[dict]) -> list[dict]:
    """L1: Find exact name matches across textbooks."""
    decisions = []
    name_groups = {}

    for node in all_nodes:
        name = node["name"].strip()
        if name not in name_groups:
            name_groups[name] = []
        name_groups[name].append(node)

    for name, nodes in name_groups.items():
        if len(nodes) < 2:
            continue

        textbooks = set(n["textbook"] for n in nodes)
        if len(textbooks) < 2:
            continue

        # Pick the best definition (longest)
        best = max(nodes, key=lambda n: len(n.get("definition", "")))
        merged_id = f"merged_{uuid.uuid4().hex[:6]}"

        decisions.append({
            "action": "merge",
            "affected_nodes": [n["id"] for n in nodes],
            "result_node": merged_id,
            "merged_name": name,
            "merged_definition": best.get("definition", ""),
            "confidence": 0.99,
            "reason": f"精确名称匹配：'{name}' 在 {len(textbooks)} 本教材中完全一致，保留最完整定义。",
        })

    return decisions


def level2_embedding_match(all_nodes: list[dict], used_ids: set[str]) -> list[dict]:
    """L2: Find semantically similar nodes using embedding cosine similarity."""
    decisions = []

    # Group by textbook
    by_textbook = {}
    for node in all_nodes:
        if node["id"] in used_ids:
            continue
        tb = node["textbook"]
        if tb not in by_textbook:
            by_textbook[tb] = []
        by_textbook[tb].append(node)

    textbooks = list(by_textbook.keys())

    for i in range(len(textbooks)):
        for j in range(i + 1, len(textbooks)):
            nodes_a = by_textbook[textbooks[i]]
            nodes_b = by_textbook[textbooks[j]]

            if not nodes_a or not nodes_b:
                continue

            try:
                pairs = find_similar_pairs(nodes_a, nodes_b, threshold=EMBEDDING_SIMILARITY_THRESHOLD)
            except Exception:
                print("  [L2] Embedding model unavailable, skipping")
                return decisions
    by_textbook = {}
    for node in all_nodes:
        if node["id"] in used_ids:
            continue
        tb = node["textbook"]
        if tb not in by_textbook:
            by_textbook[tb] = []
        by_textbook[tb].append(node)

    textbooks = list(by_textbook.keys())

    for i in range(len(textbooks)):
        for j in range(i + 1, len(textbooks)):
            nodes_a = by_textbook[textbooks[i]]
            nodes_b = by_textbook[textbooks[j]]

            if not nodes_a or not nodes_b:
                continue

            pairs = find_similar_pairs(nodes_a, nodes_b, threshold=EMBEDDING_SIMILARITY_THRESHOLD)

            for idx_a, idx_b, sim in pairs:
                na = nodes_a[idx_a]
                nb = nodes_b[idx_b]
                if na["id"] in used_ids or nb["id"] in used_ids:
                    continue

                merged_id = f"merged_{uuid.uuid4().hex[:6]}"
                best = na if len(na.get("definition", "")) >= len(nb.get("definition", "")) else nb

                decisions.append({
                    "action": "merge",
                    "affected_nodes": [na["id"], nb["id"]],
                    "result_node": merged_id,
                    "merged_name": best["name"],
                    "merged_definition": best.get("definition", ""),
                    "confidence": round(sim, 3),
                    "reason": f"语义相似度 {sim:.3f}：'{na['name']}'（{na['textbook']}）≈ '{nb['name']}'（{nb['textbook']}），待 LLM 精判。",
                    "needs_llm_review": True,
                })

                used_ids.add(na["id"])
                used_ids.add(nb["id"])

    return decisions


def level3_llm_judgment(decisions: list[dict]) -> list[dict]:
    """L3: Use LLM to verify uncertain merge decisions."""
    refined = []

    for decision in decisions:
        if not decision.get("needs_llm_review"):
            refined.append(decision)
            continue

        affected = decision["affected_nodes"]
        names = decision["merged_name"]
        defn = decision.get("merged_definition", "")

        user_prompt = f"""请判断以下两个知识点是否应该合并：

知识点A：{affected[0]} — {names}
定义：{defn[:200]}

知识点B：{affected[1] if len(affected) > 1 else 'N/A'}
相似度：{decision['confidence']}

请输出JSON格式的判断结果。"""

        result = call_llm_json(INTEGRATE_SYSTEM_PROMPT, user_prompt)

        if result and isinstance(result, dict):
            action = result.get("action", "keep")
            decision["action"] = action
            decision["confidence"] = result.get("confidence", decision["confidence"])
            decision["reason"] = result.get("reason", decision["reason"])
            if action == "merge":
                decision["merged_name"] = result.get("merged_name", names)
                decision["merged_definition"] = result.get("merged_definition", defn)

        decision.pop("needs_llm_review", None)
        refined.append(decision)

    return refined


def run_integration(all_nodes: list[dict], all_edges: list[dict]) -> dict:
    """Run the full three-level integration pipeline.

    Returns:
        dict with keys: decisions, integrated_nodes, integrated_edges, stats
    """
    used_ids = set()

    # L1: Exact match
    l1_decisions = level1_exact_match(all_nodes)
    for d in l1_decisions:
        for nid in d["affected_nodes"]:
            used_ids.add(nid)

    # L2: Embedding similarity
    l2_decisions = level2_embedding_match(all_nodes, set(used_ids))
    for d in l2_decisions:
        for nid in d["affected_nodes"]:
            used_ids.add(nid)

    # L3: LLM judgment on uncertain decisions
    all_decisions = l1_decisions + l2_decisions
    all_decisions = level3_llm_judgment(all_decisions)

    # Build integrated nodes
    integrated_nodes = []
    id_mapping = {}  # old_id -> new_id

    # Add merged nodes
    merge_actions = [d for d in all_decisions if d["action"] == "merge"]
    for d in merge_actions:
        # Find original nodes to get metadata
        original_nodes = [n for n in all_nodes if n["id"] in d["affected_nodes"]]
        textbooks = list(set(n["textbook"] for n in original_nodes))

        integrated_nodes.append({
            "id": d["result_node"],
            "name": d["merged_name"],
            "definition": d.get("merged_definition", ""),
            "category": original_nodes[0].get("category", "核心概念") if original_nodes else "核心概念",
            "textbook": "整合后",
            "frequency": sum(n.get("frequency", 1) for n in original_nodes),
            "source_textbooks": textbooks,
        })

        for nid in d["affected_nodes"]:
            id_mapping[nid] = d["result_node"]

    # Keep unaffected nodes
    remove_ids = set()
    for d in all_decisions:
        if d["action"] == "remove":
            for nid in d["affected_nodes"]:
                remove_ids.add(nid)

    for node in all_nodes:
        if node["id"] not in used_ids and node["id"] not in remove_ids:
            integrated_nodes.append(dict(node))
            id_mapping[node["id"]] = node["id"]

    # Rebuild edges with new IDs
    integrated_edges = []
    seen_edges = set()
    for edge in all_edges:
        src = id_mapping.get(edge["source"])
        tgt = id_mapping.get(edge["target"])
        if not src or not tgt or src == tgt:
            continue
        edge_key = (src, tgt, edge["relation_type"])
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        integrated_edges.append({
            "source": src,
            "target": tgt,
            "relation_type": edge["relation_type"],
            "description": edge["description"],
        })

    # Stats
    from src.graph_builder import compute_compression_stats
    stats = compute_compression_stats(all_nodes, integrated_nodes)
    stats["merge_count"] = sum(1 for d in all_decisions if d["action"] == "merge")
    stats["keep_count"] = sum(1 for d in all_decisions if d["action"] == "keep")
    stats["remove_count"] = sum(1 for d in all_decisions if d["action"] == "remove")
    stats["original_textbooks"] = len(set(n["textbook"] for n in all_nodes))

    return {
        "decisions": all_decisions,
        "integrated_nodes": integrated_nodes,
        "integrated_edges": integrated_edges,
        "stats": stats,
    }
