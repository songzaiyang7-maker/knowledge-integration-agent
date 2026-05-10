"""ECharts HTML template for knowledge graph visualization with force-directed layout."""

import json
import os

_GRAPH_HTML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


def render_knowledge_graph(nodes, edges, book_colors, title="知识图谱"):
    """Render an ECharts force-directed graph as HTML string.

    Returns an iframe HTML that loads a generated graph page from static/.
    """
    categories = []
    seen_textbooks = set()
    for node in nodes:
        tb = node.get("textbook", "未知")
        if tb not in seen_textbooks:
            seen_textbooks.add(tb)
            categories.append({"name": tb})

    echarts_nodes = []
    for node in nodes:
        freq = node.get("frequency", 1)
        symbol_size = 20 + freq * 12
        echarts_nodes.append({
            "id": node["id"],
            "name": node["name"],
            "symbolSize": symbol_size,
            "category": list(seen_textbooks).index(node.get("textbook", "未知")),
            "itemStyle": {"color": book_colors.get(node.get("textbook", ""), "#999")},
            "label": {"show": symbol_size > 30, "fontSize": 11},
            "value": freq,
            "_definition": node.get("definition", ""),
            "_chapter": node.get("chapter", ""),
            "_page": node.get("page", ""),
            "_textbook": node.get("textbook", ""),
            "_category_type": node.get("category", ""),
        })

    line_styles = {
        "prerequisite": {"type": "solid", "width": 2, "color": "#555", "curveness": 0.1},
        "parallel": {"type": "dashed", "width": 1.5, "color": "#999", "curveness": 0.2},
        "contains": {"type": "dotted", "width": 1.5, "color": "#666", "curveness": 0.15},
        "applies_to": {"type": "dashed", "width": 2, "color": "#888", "curveness": 0.1},
    }

    echarts_edges = []
    for edge in edges:
        style = line_styles.get(edge.get("relation_type", "prerequisite"), line_styles["prerequisite"])
        echarts_edges.append({
            "source": edge["source"],
            "target": edge["target"],
            "lineStyle": style,
            "label": {
                "show": False,
                "formatter": edge.get("relation_type", ""),
                "fontSize": 9,
            },
            "_relation_type": edge.get("relation_type", ""),
            "_description": edge.get("description", ""),
        })

    nodes_json = json.dumps(echarts_nodes, ensure_ascii=False)
    edges_json = json.dumps(echarts_edges, ensure_ascii=False)
    categories_json = json.dumps(categories, ensure_ascii=False)

    # Read echarts.min.js content
    echarts_js_path = os.path.join(_GRAPH_HTML_DIR, "echarts.min.js")
    echarts_js_tag = '<p style="color:red;padding:20px;">ECharts JS 文件未找到</p>'
    if os.path.exists(echarts_js_path):
        echarts_js_tag = '<script src="http://127.0.0.1:8080/echarts.min.js"></script>'

    graph_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{echarts_js_tag}
<style>
  html, body, #graph-container {{ margin: 0; padding: 0; width: 100%; height: 100%; }}
</style>
</head>
<body>
<div id="graph-container"></div>
<script>
(function() {{
  if (typeof echarts === 'undefined') {{
    document.getElementById('graph-container').innerHTML = '<p style="color:red;padding:20px;">ECharts 加载失败</p>';
    return;
  }}
  var chart = echarts.init(document.getElementById('graph-container'));
  var nodes = {nodes_json};
  var edges = {edges_json};
  var categories = {categories_json};

  var option = {{
    title: {{ text: '{title}', left: 'center', top: 5, textStyle: {{ fontSize: 16 }} }},
    tooltip: {{
      trigger: 'item',
      formatter: function(params) {{
        if (params.dataType === 'node') {{
          var d = params.data;
          return '<b>' + d.name + '</b><br/>' +
            '来源: ' + d._textbook + '<br/>' +
            '类型: ' + d._category_type + '<br/>' +
            (d._chapter ? '章节: ' + d._chapter + '<br/>' : '') +
            '频次: ' + d.value;
        }}
        if (params.dataType === 'edge') {{
          var e = params.data;
          return '<b>' + e._relation_type + '</b><br/>' + e._description;
        }}
        return '';
      }}
    }},
    legend: {{
      data: categories.map(function(c) {{ return c.name; }}),
      bottom: 5,
      textStyle: {{ fontSize: 12 }}
    }},
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: edges,
      categories: categories,
      roam: true,
      draggable: true,
      force: {{
        repulsion: 300,
        edgeLength: [80, 200],
        gravity: 0.1,
      }},
      label: {{
        show: true,
        position: 'right',
        formatter: '{{{{b}}}}',
        fontSize: 11,
      }},
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [4, 8],
      emphasis: {{
        focus: 'adjacency',
        lineStyle: {{ width: 4 }}
      }},
    }}]
  }};

  chart.setOption(option);
  window.addEventListener('resize', function() {{ chart.resize(); }});
}})();
</script>
</body>
</html>"""

    # Write graph HTML to static directory and return iframe
    graph_file_path = os.path.join(_GRAPH_HTML_DIR, "graph.html")
    os.makedirs(_GRAPH_HTML_DIR, exist_ok=True)
    with open(graph_file_path, "w", encoding="utf-8") as f:
        f.write(graph_html)

    import time
    ts = int(time.time() * 1000)
    return f'<iframe src="http://127.0.0.1:8080/graph.html?t={ts}" width="100%" height="650px" frameborder="0" style="border:none;"></iframe>'
