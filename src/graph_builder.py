"""Knowledge graph builder — assembles nodes and edges from extraction results."""

from src.mock_data import BOOK_COLORS

# Extra colors for additional textbooks beyond the predefined ones
_EXTRA_COLORS = ["#FC8452", "#9A60B4", "#EA7CCC", "#48b8a0", "#ff9f7f"]


def get_book_color(textbook_name: str, existing_colors: dict | None = None) -> str:
    """Get color for a textbook, assigning new colors as needed."""
    colors = existing_colors or BOOK_COLORS
    if textbook_name in colors:
        return colors[textbook_name]

    # Assign a new color
    used = set(colors.values())
    for c in _EXTRA_COLORS:
        if c not in used:
            colors[textbook_name] = c
            return c

    # Fallback: generate a color
    import hashlib
    hue = int(hashlib.md5(textbook_name.encode()).hexdigest()[:8], 16) % 360
    color = f"hsl({hue}, 60%, 55%)"
    colors[textbook_name] = color
    return color


def build_graph(extraction_results: list[dict]) -> tuple[list, list, dict]:
    """Build a unified knowledge graph from multiple textbook extraction results.

    Args:
        extraction_results: list of dicts, each with "nodes" and "edges" from process_textbook()

    Returns:
        (nodes, edges, book_colors) tuple
    """
    all_nodes = []
    all_edges = []
    colors = dict(BOOK_COLORS)

    for result in extraction_results:
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])

        for node in nodes:
            tb = node.get("textbook", "未知")
            get_book_color(tb, colors)
            all_nodes.append(node)

        all_edges.extend(edges)

    return all_nodes, all_edges, colors


def compute_compression_stats(original_nodes: list, integrated_nodes: list) -> dict:
    """Compute compression statistics for display."""
    original_chars = sum(len(n.get("definition", "")) for n in original_nodes)
    integrated_chars = sum(len(n.get("definition", "")) for n in integrated_nodes)

    ratio = (integrated_chars / original_chars * 100) if original_chars > 0 else 0

    return {
        "original_nodes": len(original_nodes),
        "integrated_nodes": len(integrated_nodes),
        "original_total_chars": original_chars,
        "integrated_total_chars": integrated_chars,
        "compression_ratio": round(ratio, 1),
    }
