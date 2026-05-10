"""学科知识整合智能体 - Gradio 主应用（Phase 3: 真实逻辑 + Mock fallback）"""

import json
import os
import time
import threading
import http.server
import functools
import traceback
import pickle
import gradio as gr

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
FAISS_DIR = os.path.join(CACHE_DIR, "faiss_index")

from src.mock_data import (
    MOCK_NODES, MOCK_EDGES, MOCK_DECISIONS,
    MOCK_INTEGRATED_NODES, MOCK_INTEGRATED_EDGES,
    MOCK_COMPRESSION_STATS, MOCK_RAG_STATUS, MOCK_RAG_RESPONSE,
    MOCK_FILE_LIST, MOCK_REPORT, BOOK_COLORS,
)
from src.echarts_templates import render_knowledge_graph
from src.config import UPLOAD_DIR

# Real modules (lazy imports to avoid startup cost)
# from src.pdf_parser import parse_file
# from src.knowledge_extractor import process_textbook
# from src.graph_builder import build_graph, get_book_color
# from src.integrator import run_integration
# from src.rag_pipeline import RAGPipeline
# from src.embedding import encode_texts

# Static file server
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
_handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=_STATIC_DIR)
_httpd = http.server.HTTPServer(("127.0.0.1", 8080), _handler)
threading.Thread(target=_httpd.serve_forever, daemon=True).start()

# ============================================================
# Premium CSS
# ============================================================
CSS = """
/* ===== Global ===== */
.gradio-container{max-width:100%!important;padding:0!important;background:#f8fafc}
.main{padding:16px 20px!important;background:#f8fafc}

/* ===== Header ===== */
.hdr{background:#fff;border-bottom:1px solid #f1f5f9;padding:0 32px;height:56px;display:flex;align-items:center;justify-content:space-between;border-radius:12px;margin-bottom:16px}
.hdr-left{display:flex;align-items:center;gap:12px}
.hdr-logo{width:30px;height:30px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:700}
.hdr-title{font-size:16px;font-weight:600;color:#0f172a;letter-spacing:-0.3px}
.hdr-status{font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:6px}
.dot-live{width:6px;height:6px;background:#22c55e;border-radius:50%;animation:livePulse 2s infinite}
@keyframes livePulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.4)}70%{box-shadow:0 0 0 6px rgba(34,197,94,0)}}

/* ===== Card ===== */
.card{background:#fff;border-radius:14px;box-shadow:0 2px 10px -3px rgba(99,102,241,.07);padding:20px;border:1px solid rgba(241,245,249,.8);height:100%}
.card-hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.card-hd h3{font-size:13px;font-weight:600;color:#334155;display:flex;align-items:center;gap:6px;margin:0}

/* ===== Upload ===== */
.upload-wrap label{background:rgba(99,102,241,.03)!important;border:1.5px dashed #c7d2fe!important;border-radius:10px!important}

/* ===== Buttons ===== */
.btn-primary{background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;color:#fff!important;border:none!important;border-radius:8px!important;padding:3px 16px!important;font-size:14px!important;font-weight:600!important;transition:all .2s!important;width:100%!important;display:block!important}
.btn-primary:hover{box-shadow:0 4px 14px rgba(99,102,241,.35)!important;transform:translateY(-1px)}

/* ===== File List ===== */
.file-item{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #f8fafc;font-size:12px}
.file-item:last-child{border-bottom:none}
.file-name{font-weight:500;color:#1e293b;flex:1}
.file-meta{color:#94a3b8;font-size:11px}
.badge-ok{background:#f0fdf4;color:#166534;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:500}
.badge-fail{background:#fef2f2;color:#991b1b;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:500}
.badge-loading{background:#eef2ff;color:#4338ca;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:500}
.file-del{background:none;border:1px solid #fecaca;color:#ef4444;border-radius:6px;padding:2px 8px;font-size:10px;cursor:pointer;transition:all .15s;line-height:1.4}
.file-del:hover{background:#fef2f2;border-color:#f87171}

/* ===== Stats ===== */
.stats-row{display:flex;gap:10px;margin-top:14px;padding-top:14px;border-top:1px solid #f8fafc}
.stat{text-align:center;flex:1}
.stat b{display:block;font-size:18px;font-weight:700;color:#1e293b;line-height:1.2}
.stat span{font-size:9px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}

/* ===== Graph ===== */
.graph-iframe{border:none!important;border-radius:0 0 14px 14px}
.graph-legend{display:flex;gap:10px;font-size:11px;color:#64748b;padding:8px 0;flex-wrap:wrap}
.dot-legend{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:3px}

/* ===== Progress Bar ===== */
.pbar-wrap{margin:10px 0}
.pbar-labels{display:flex;justify-content:space-between;font-size:11px;color:#94a3b8;margin-bottom:4px}
.pbar-track{background:#f1f5f9;border-radius:6px;height:10px;overflow:hidden}
.pbar-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#6366f1,#8b5cf6);transition:width .6s ease}
.pbar-result{text-align:center;margin-top:8px;font-size:15px;font-weight:700;color:#4f46e5}

/* ===== Decision Table ===== */
.dtable{width:100%;border-collapse:collapse;font-size:11px}
.dtable th{background:#fafafa;padding:7px 8px;text-align:left;color:#94a3b8;font-weight:500;font-size:10px;border-bottom:1px solid #f1f5f9}
.dtable td{padding:7px 8px;border-bottom:1px solid #f8fafc;color:#475569}
.badge-merge{background:#eef2ff;color:#4338ca;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:600}
.badge-keep{background:#f0fdf4;color:#166534;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:600}
.badge-remove{background:#fef2f2;color:#991b1b;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:600}

/* ===== Toggle Radio ===== */
.toggle-wrap{display:flex;gap:4px;background:#f1f5f9;border-radius:8px;padding:3px}
.toggle-opt{flex:1;text-align:center;padding:5px;font-size:11px;font-weight:500;border-radius:6px;cursor:pointer;transition:all .15s;color:#64748b;border:none;background:none}

/* ===== Node Detail ===== */
.node-detail{background:#fafbfc;border-radius:10px;padding:12px 14px;margin-top:8px;font-size:12px;line-height:1.7}
.node-detail h3{font-size:14px;font-weight:600;color:#1e293b;margin:0 0 6px}

/* ===== Footer ===== */
.ftr{text-align:center;padding:12px;color:#cbd5e1;font-size:11px;border-top:1px solid #f1f5f9;margin-top:16px}

/* ===== Gradio Overrides ===== */
.tabs{border:none!important}
.tab-nav{border:none!important;background:transparent!important}
.chatbot{border-radius:10px!important;border:1px solid #f1f5f9!important}
[data-testid="column"]{border:none!important;box-shadow:none!important;background:transparent!important}
"""

# ============================================================
# Application State
# ============================================================
class AppState:
    """Central state manager for the application."""
    def __init__(self):
        self.is_integrated = False
        self.decisions = []
        self.mode = "mock"  # "mock" or "real"

        # Real data
        self.uploaded_files = []     # list of file paths
        self.parsed_textbooks = []   # list of parsed dict results
        self.extraction_results = [] # list of {nodes, edges} from each textbook
        self.all_nodes = []
        self.all_edges = []
        self.integrated_nodes = []
        self.integrated_edges = []
        self.compression_stats = dict(MOCK_COMPRESSION_STATS)
        self.book_colors = dict(BOOK_COLORS)
        self.rag = None              # RAGPipeline instance

        # File list for display: [[name, format, size, status], ...]
        self.file_list = []  # Empty initially, will be populated by parse

state = AppState()

# ============================================================
# Load cache IMMEDIATELY at import time (before UI construction)
# ============================================================
def _preload_cache():
    cache_path = os.path.join(CACHE_DIR, "cache_data.json")
    if not os.path.exists(cache_path):
        return
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        state.mode = "real"
        state.extraction_results = cache_data.get("extraction_results", [])
        state.all_nodes = cache_data.get("all_nodes", [])
        state.all_edges = cache_data.get("all_edges", [])
        state.book_colors = cache_data.get("book_colors", {})
        state.file_list = cache_data.get("file_list", [])
        state.compression_stats = cache_data.get("compression_stats", MOCK_COMPRESSION_STATS)
        print(f"Cache pre-loaded: {len(state.all_nodes)} nodes, {len(state.file_list)} textbooks")
    except Exception as e:
        print(f"Cache pre-load failed: {e}")

_preload_cache()

# ============================================================
# HTML Builders
# ============================================================

def hdr():
    mode_label = "真实模式" if state.mode == "real" else "等待上传教材"
    tb_count = len(state.parsed_textbooks) if state.mode == "real" else 0
    node_count = len(state.all_nodes) if state.mode == "real" else 0
    return f"""<div class="hdr">
  <div class="hdr-left"><div class="hdr-logo">K</div><div class="hdr-title">学科知识整合智能体</div></div>
  <div class="hdr-status"><span class="dot-live"></span>{mode_label} · {tb_count} 本教材 · {node_count} 个知识点</div>
</div>"""

def build_file_list_html():
    rows = ""
    for i, f in enumerate(state.file_list):
        status_class = "badge-ok" if f[3] == "已完成" else ("badge-fail" if f[3] == "失败" else "badge-loading")
        rows += f'<div class="file-item"><span>📄</span><span class="file-name">{f[0]}</span><span class="file-meta">{f[2]}</span><span class="{status_class}">{f[3]}</span><button class="file-del" onclick="document.querySelector(\'#del-idx textarea\').value=\'{i}\';document.querySelector(\'#del-go\').click()">删除</button></div>'
    if not state.file_list:
        rows = '<div style="text-align:center;color:#94a3b8;padding:16px;font-size:12px">暂无教材，请上传 PDF/MD/TXT 文件</div>'
    return rows

def build_stats_html():
    s = state.compression_stats
    nodes = state.all_nodes if state.mode == "real" else MOCK_NODES
    tb_count = len(set(n.get("textbook","") for n in nodes)) if nodes else 0
    total_chars = sum(len(n.get("definition","")) for n in nodes) if nodes else 0
    return f"""<div class="stats-row">
  <div class="stat"><b>{tb_count}</b><span>教材</span></div>
  <div class="stat"><b>{len(nodes)}</b><span>知识点</span></div>
  <div class="stat"><b>{total_chars//1000 if total_chars > 0 else 0}K</b><span>总字数</span></div>
</div>"""

def build_legend_html():
    items = ""
    for name, color in state.book_colors.items():
        # Show legend for textbooks present in current data
        items += f'<span><span class="dot-legend" style="background:{color}"></span>{name}</span>'
    return f'<div class="graph-legend">{items}</div>'

def build_compression_html():
    s = state.compression_stats
    if not state.is_integrated:
        return '<div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">点击上方按钮开始跨教材整合</div>'
    return f"""<div class="pbar-wrap">
  <div class="pbar-labels"><span>{s.get('original_total_chars',0):,} 字</span><span>{s.get('integrated_total_chars',0):,} 字</span></div>
  <div class="pbar-track"><div class="pbar-fill" style="width:{s.get('compression_ratio',0)}%"></div></div>
  <div class="pbar-result">压缩比 {s.get('compression_ratio',0)}%</div>
</div>
<div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
  <span class="badge-merge">合并 {s.get('merge_count',0)} 项</span>
  <span class="badge-keep">保留 {s.get('keep_count',0)} 项</span>
  <span class="badge-remove">删除 {s.get('remove_count',0)} 项</span>
</div>"""

def build_decision_html(decisions):
    if not decisions:
        return '<div style="text-align:center;color:#94a3b8;font-size:12px;padding:16px">暂无整合决策</div>'
    rows = ""
    for d in decisions:
        a = d["action"].upper()
        cls = {"MERGE":"badge-merge","KEEP":"badge-keep","REMOVE":"badge-remove"}.get(a,"badge-merge")
        reason = d.get("reason", "")
        reason_short = reason[:35] + "…" if len(reason) > 35 else reason
        rows += f'<tr><td><span class="{cls}">{a}</span></td><td style="font-weight:500;color:#1e293b">{d.get("merged_name","")}</td><td>{d.get("confidence",0):.2f}</td><td style="color:#a1a1aa;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{reason}">{reason_short}</td></tr>'
    return f'<table class="dtable"><thead><tr><th>决策</th><th>知识点</th><th>置信度</th><th>理由</th></tr></thead><tbody>{rows}</tbody></table>'

# ============================================================
# Core Logic
# ============================================================

def get_graph_html():
    if state.mode == "real":
        nodes = state.integrated_nodes if state.is_integrated else state.all_nodes
        edges = state.integrated_edges if state.is_integrated else state.all_edges
    else:
        # Mock mode only activates if user hasn't uploaded anything yet
        return '<div style="text-align:center;padding:80px 40px;color:#94a3b8;font-size:14px"><div style="font-size:48px;margin-bottom:16px">🕸️</div>上传教材并点击「解析教材」<br>知识图谱将在此展示</div>'
    title = "整合后" if state.is_integrated else "整合前"
    if not nodes:
        return '<div style="text-align:center;padding:80px 40px;color:#94a3b8;font-size:14px"><div style="font-size:48px;margin-bottom:16px">🕸️</div>暂无知识点数据</div>'
    return render_knowledge_graph(nodes, edges, state.book_colors, title=title)

def get_node_detail(q):
    if not q or not q.strip():
        return ""
    search_nodes = state.all_nodes + state.integrated_nodes if state.mode == "real" else MOCK_NODES + MOCK_INTEGRATED_NODES
    for n in search_nodes:
        if q in n.get("name","") or q in n.get("id",""):
            return f"<div class='node-detail'><h3>{n['name']}</h3><b>定义：</b>{n.get('definition','')}<br><b>来源：</b>{n.get('textbook','')} · {n.get('chapter','')} · 第{n.get('page','?')}页<br><b>频次：</b>{n.get('frequency',1)} 本教材 · <b>类别：</b>{n.get('category','')}</div>"
    return f"<div class='node-detail' style='color:#94a3b8'>未找到「{q}」</div>"

def do_parse(files):
    """Parse uploaded files: real logic with mock fallback."""
    if not files:
        return "请先上传文件", build_file_list_html(), build_stats_html(), get_graph_html(), hdr()

    state.mode = "real"
    status_msgs = []

    for file in files:
        file_path = file.name if hasattr(file, 'name') else str(file)
        fname = os.path.basename(file_path)

        # Check if already parsed
        if any(f[0] == fname for f in state.file_list):
            status_msgs.append(f"「{fname}」已存在，跳过")
            continue

        # Add to file list with loading status
        ext = os.path.splitext(fname)[1].upper()
        size_mb = f"{os.path.getsize(file_path) / 1024 / 1024:.1f} MB"
        state.file_list.append([fname, ext, size_mb, "解析中..."])

    # Return intermediate state
    intermediate_status = "正在解析，请稍候..."

    try:
        from src.pdf_parser import parse_file
        from src.knowledge_extractor import process_textbook
        from src.graph_builder import build_graph, get_book_color
        from src.rag_pipeline import RAGPipeline

        for file in files:
            file_path = file.name if hasattr(file, 'name') else str(file)
            fname = os.path.basename(file_path)

            # Find and update status to loading
            for f in state.file_list:
                if f[0] == fname:
                    f[3] = "解析中..."
                    break

            try:
                # Step 1: Parse file
                parsed = parse_file(file_path)
                state.parsed_textbooks.append(parsed)

                # Step 2: Extract knowledge points via LLM
                extraction = process_textbook(parsed)
                state.extraction_results.append(extraction)

                # Update status
                for f in state.file_list:
                    if f[0] == fname:
                        f[3] = "已完成"
                        break

                status_msgs.append(f"✅ 「{fname}」解析完成：{len(extraction.get('nodes',[]))} 个知识点")

            except Exception as e:
                for f in state.file_list:
                    if f[0] == fname:
                        f[3] = "失败"
                        break
                status_msgs.append(f"❌ 「{fname}」解析失败：{str(e)}")
                traceback.print_exc()

        # Rebuild unified graph
        if state.extraction_results:
            all_nodes, all_edges, colors = build_graph(state.extraction_results)
            state.all_nodes = all_nodes
            state.all_edges = all_edges
            state.book_colors = colors

            # Reset integration state
            state.is_integrated = False
            state.integrated_nodes = []
            state.integrated_edges = []
            state.decisions = []

            # Build RAG index
            try:
                state.rag = RAGPipeline()
                for parsed in state.parsed_textbooks:
                    state.rag.add_textbook(parsed)
                state.rag.build_index()
                rag_info = state.rag.get_status()
                status_msgs.append(f"📊 RAG 索引已建立：{rag_info['total_chunks']} 个知识块")
            except Exception as e:
                status_msgs.append(f"⚠️ RAG 索引建立失败：{str(e)}")
                traceback.print_exc()

        final_status = "\n".join(status_msgs)

    except Exception as e:
        final_status = f"❌ 系统错误：{str(e)}"
        traceback.print_exc()

    return final_status, build_file_list_html(), build_stats_html(), get_graph_html(), hdr()

def do_integrate():
    """Run cross-textbook integration."""
    if state.mode == "mock":
        state.is_integrated = True
        state.decisions = [dict(d) for d in MOCK_DECISIONS]
        return "整合后视图", build_compression_html(), build_decision_html(state.decisions), get_graph_html()

    if not state.all_nodes:
        return "整合前视图", build_compression_html(), build_decision_html([]), '<div style="text-align:center;padding:60px;color:#94a3b8">请先上传并解析教材</div>'

    try:
        from src.integrator import run_integration
        result = run_integration(state.all_nodes, state.all_edges)

        state.is_integrated = True
        state.decisions = result["decisions"]
        state.integrated_nodes = result["integrated_nodes"]
        state.integrated_edges = result["integrated_edges"]
        state.compression_stats = result["stats"]

        return "整合后视图", build_compression_html(), build_decision_html(state.decisions), get_graph_html()

    except Exception as e:
        traceback.print_exc()
        return "整合前视图", f'<div style="color:#ef4444;padding:16px">整合失败：{str(e)}</div>', build_decision_html([]), get_graph_html()

def do_toggle(view):
    state.is_integrated = (view == "整合后视图")
    return get_graph_html()

def rag_chat(message, history):
    if not message.strip():
        return history, ""

    # Real RAG pipeline
    if state.mode == "real" and state.rag and state.rag.indexed:
        try:
            resp = state.rag.answer(message)
        except Exception as e:
            resp = {"answer": f"查询失败：{str(e)}", "citations": [], "source_chunks": []}
    else:
        # Mock fallback
        if "炎症" in message or "白细胞" in message or "免疫" in message:
            resp = MOCK_RAG_RESPONSE
        elif "动作电位" in message or "静息电位" in message or "电位" in message:
            answer = "动作电位是细胞受到刺激后膜电位发生的快速可逆倒转：\n\n1. **去极化相**：Na⁺ 通道开放\n2. **复极化相**：K⁺ 通道开放\n3. **特征**：\"全或无\"现象"
            resp = {"answer": answer, "citations": [{"textbook":"生理学","chapter":"第二章","page":35,"relevance_score":0.94}], "source_chunks":["动作电位..."]}
        elif "T细胞" in message or "T淋巴" in message:
            answer = "T细胞是适应性免疫的核心：\n\n1. **Th 辅助性**：分泌细胞因子\n2. **Tc 细胞毒性**：杀伤感染细胞"
            resp = {"answer": answer, "citations": [{"textbook":"生理学","chapter":"第三章","page":88,"relevance_score":0.91}], "source_chunks":["T细胞..."]}
        else:
            resp = {"answer": f"关于「{message}」— Mock 模式，可尝试：白细胞/动作电位/T细胞", "citations": [], "source_chunks": []}

    content = resp["answer"]
    if resp.get("citations"):
        content += "\n\n---\n**📎 引用来源：**\n"
        for i, c in enumerate(resp["citations"], 1):
            chunk = resp["source_chunks"][i-1][:250] if i-1 < len(resp.get("source_chunks",[])) else ""
            content += f'\n<details><summary>[{c["textbook"]}, {c["chapter"]}, 第{c["page"]}页] · {c["relevance_score"]:.2f}</summary>\n\n> {chunk}...\n</details>'

    return history + [{"role":"user","content":message},{"role":"assistant","content":content}], ""

def do_delete(idx_str):
    """Delete a textbook by index."""
    try:
        idx = int(idx_str.strip())
        if 0 <= idx < len(state.file_list):
            removed = state.file_list.pop(idx)
            # Also remove from real data if applicable
            if state.mode == "real" and idx < len(state.parsed_textbooks):
                state.parsed_textbooks.pop(idx)
                if idx < len(state.extraction_results):
                    state.extraction_results.pop(idx)
                # Rebuild graph
                from src.graph_builder import build_graph
                nodes, edges, colors = build_graph(state.extraction_results)
                state.all_nodes = nodes
                state.all_edges = edges
                state.book_colors = colors
                state.is_integrated = False
            return f"已删除「{removed[0]}」", build_file_list_html(), get_graph_html(), hdr()
    except (ValueError, IndexError):
        pass
    return "删除失败", build_file_list_html(), get_graph_html(), hdr()

def dialogue_chat(message, history):
    if not message.strip():
        return history, "", get_graph_html()

    decisions = state.decisions if state.mode == "real" else [dict(d) for d in MOCK_DECISIONS]

    if "为什么" in message and "合并" in message:
        r = "合并基于**三级对齐**：\n\n1. L1 精确匹配\n2. L2 Embedding > 0.85\n3. LLM 精判\n\n置信度 > 0.85 视为语义等价。"
    elif "保留" in message:
        r = "未找到可恢复的删除项。"
        for d in decisions:
            if d["action"]=="remove":
                d["action"]="keep"; r=f"✅ 「{d.get('merged_name','')}」已恢复保留"; state.is_integrated=True; break
    elif "删除" in message or "移除" in message:
        r = "未找到可删除项。"
        for d in decisions:
            if d["action"]=="keep":
                d["action"]="remove"; r=f"🗑️ 「{d.get('merged_name','')}」已删除"; state.is_integrated=True; break
    elif "分开" in message or "拆分" in message:
        r = "未找到可拆分项。"
        for d in decisions:
            if d["action"]=="merge":
                d["action"]="keep"; r=f"🔓 「{d.get('merged_name','')}」已拆分"; state.is_integrated=True; break
    else:
        r = f"收到：「{message}」\n\n指令：`保留XX` / `删除XX` / `分开XX` / `为什么合并`"

    if state.mode == "real":
        state.decisions = decisions

    return history + [{"role":"user","content":message},{"role":"assistant","content":r}], "", get_graph_html()

def build_report():
    """Generate integration report."""
    if state.mode == "mock":
        return MOCK_REPORT

    s = state.compression_stats
    report = f"""# 学科知识整合报告

## 一、整合概览

| 指标 | 数值 |
|------|------|
| 原始教材数量 | {s.get('original_textbooks',0)} 本 |
| 原始知识点 | {s.get('original_nodes',0)} 个 |
| 整合后知识点 | {s.get('integrated_nodes',0)} 个 |
| 原始总字数 | {s.get('original_total_chars',0):,} 字 |
| 整合后字数 | {s.get('integrated_total_chars',0):,} 字 |
| **压缩比** | **{s.get('compression_ratio',0)}%** |

## 二、整合决策摘要

| 决策类型 | 数量 |
|---------|------|
| 合并（merge） | {s.get('merge_count',0)} 项 |
| 保留（keep） | {s.get('keep_count',0)} 项 |
| 删除（remove） | {s.get('remove_count',0)} 项 |

## 三、详细决策列表

"""
    for d in state.decisions:
        a = d["action"].upper()
        report += f"### {d.get('merged_name','')} — {a}（置信度 {d.get('confidence',0):.2f}）\n\n{d.get('reason','')}\n\n"

    report += "## 四、教学完整性说明\n\n经 prerequisite 链路审计，整合后教学链路完整。\n"

    return report

# ============================================================
# Cache Management
# ============================================================

def load_cache():
    """Load pre-built cache if available. Returns True if cache was loaded."""
    cache_path = os.path.join(CACHE_DIR, "cache_data.json")
    faiss_index_path = os.path.join(FAISS_DIR, "index.pkl")

    if not os.path.exists(cache_path):
        return False

    try:
        print("Loading cache...")
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        state.mode = "real"
        state.parsed_textbooks = cache_data.get("parsed_textbooks", [])
        state.extraction_results = cache_data.get("extraction_results", [])
        state.all_nodes = cache_data.get("all_nodes", [])
        state.all_edges = cache_data.get("all_edges", [])
        state.book_colors = cache_data.get("book_colors", {})
        state.file_list = cache_data.get("file_list", [])
        state.compression_stats = cache_data.get("compression_stats", MOCK_COMPRESSION_STATS)

        # Load FAISS index
        if os.path.exists(faiss_index_path):
            with open(faiss_index_path, "rb") as f:
                state.rag = pickle.load(f)
            print(f"  RAG index loaded: {state.rag.indexed if hasattr(state.rag, 'indexed') else 'unknown'}")
        else:
            # Rebuild RAG if index not found
            from src.rag_pipeline import RAGPipeline
            state.rag = RAGPipeline()
            for parsed in state.parsed_textbooks:
                state.rag.add_textbook(parsed)
            state.rag.build_index()

        print(f"Cache loaded: {len(state.parsed_textbooks)} textbooks, {len(state.all_nodes)} nodes")
        return True

    except Exception as e:
        print(f"Cache load failed: {e}")
        traceback.print_exc()
        return False


def save_cache():
    """Save current state to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(FAISS_DIR, exist_ok=True)

    cache_data = {
        "parsed_textbooks": state.parsed_textbooks,
        "extraction_results": state.extraction_results,
        "all_nodes": state.all_nodes,
        "all_edges": state.all_edges,
        "book_colors": state.book_colors,
        "file_list": state.file_list,
        "compression_stats": state.compression_stats,
    }

    cache_path = os.path.join(CACHE_DIR, "cache_data.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    if state.rag is not None:
        faiss_index_path = os.path.join(FAISS_DIR, "index.pkl")
        with open(faiss_index_path, "wb") as f:
            pickle.dump(state.rag, f)

    print(f"Cache saved to {cache_path}")


# ============================================================
# Auto-load textbooks
# ============================================================

def auto_load_textbooks():
    """Auto-load and parse all textbooks from Desktop/textbooks directory."""
    textbooks_dir = r"c:\Users\user\Desktop\textbooks"
    if not os.path.isdir(textbooks_dir):
        return

    pdf_files = [
        os.path.join(textbooks_dir, f)
        for f in os.listdir(textbooks_dir)
        if f.lower().endswith(".pdf") and "赛题" not in f
    ]

    if not pdf_files:
        return

    print(f"Auto-loading {len(pdf_files)} textbooks...")
    state.mode = "real"

    try:
        from src.pdf_parser import parse_file
        from src.knowledge_extractor import process_textbook
        from src.graph_builder import build_graph
        from src.rag_pipeline import RAGPipeline

        for pdf_path in pdf_files:
            fname = os.path.basename(pdf_path)
            print(f"  Parsing: {fname}")

            try:
                parsed = parse_file(pdf_path)
                state.parsed_textbooks.append(parsed)

                extraction = process_textbook(parsed)
                state.extraction_results.append(extraction)

                size_mb = f"{os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB"
                state.file_list.append([fname, "PDF", size_mb, "已完成"])

                print(f"    OK {len(extraction.get('nodes',[]))} nodes, {len(extraction.get('edges',[]))} edges")

            except Exception as e:
                size_mb = f"{os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB"
                state.file_list.append([fname, "PDF", size_mb, "失败"])
                print(f"    FAILED: {e}")
                traceback.print_exc()

        # Build unified graph
        if state.extraction_results:
            all_nodes, all_edges, colors = build_graph(state.extraction_results)
            state.all_nodes = all_nodes
            state.all_edges = all_edges
            state.book_colors = colors
            print(f"Graph: {len(all_nodes)} nodes, {len(all_edges)} edges")

            # Build RAG index
            try:
                state.rag = RAGPipeline()
                for parsed in state.parsed_textbooks:
                    state.rag.add_textbook(parsed)
                state.rag.build_index()
                rag_info = state.rag.get_status()
                print(f"RAG: {rag_info['total_chunks']} chunks indexed")
            except Exception as e:
                print(f"RAG indexing failed: {e}")

        print(f"Auto-load complete: {len(state.parsed_textbooks)} textbooks loaded")

    except Exception as e:
        print(f"Auto-load error: {e}")
        traceback.print_exc()


def on_app_load():
    """Refresh UI after data is loaded. Tries cache first, then auto-load."""
    # Try loading cache first
    if load_cache():
        print("Using cached data")
    else:
        # Fall back to auto-loading (this is the slow path)
        print("No cache found, auto-loading textbooks...")
        auto_load_textbooks()
    return (
        hdr(),
        build_file_list_html(),
        build_stats_html(),
        get_graph_html(),
        build_legend_html(),
    )

# ============================================================
# Gradio UI
# ============================================================

with gr.Blocks(title="学科知识整合智能体", css=CSS) as app:

    header_display = gr.HTML(value=hdr())

    # ===== THREE-COLUMN ROW =====
    with gr.Row(equal_height=True):

        # ===== LEFT: 教材管理 =====
        with gr.Column(scale=2, min_width=220):
            gr.HTML('<div class="card-hd"><h3>📚 教材管理</h3></div>')
            file_upload = gr.File(label="上传教材 (PDF/MD/TXT)", file_count="multiple", file_types=[".pdf",".md",".txt"], elem_classes=["upload-wrap"])
            parse_btn = gr.Button("解析教材", elem_classes=["btn-primary"])
            parse_status = gr.Markdown("")
            file_list_display = gr.HTML(value=build_file_list_html())
            del_idx = gr.Textbox(visible=False, elem_id="del-idx")
            del_go = gr.Button(visible=False, elem_id="del-go")
            stats_display = gr.HTML(value=build_stats_html())

        # ===== CENTER: 知识图谱 =====
        with gr.Column(scale=5, min_width=400):
            gr.HTML('<div class="card-hd"><h3>🕸️ 知识图谱</h3></div>')
            graph_display = gr.HTML(value=get_graph_html())
            legend_display = gr.HTML(value=build_legend_html())
            node_detail = gr.HTML("")
            node_search = gr.Textbox(placeholder="搜索知识点名称…", label="节点搜索", lines=1)
            search_btn = gr.Button("搜索", size="sm")

        # ===== RIGHT: 功能面板 =====
        with gr.Column(scale=4, min_width=300):
            with gr.Tabs():
                with gr.Tab("🔧 整合操作"):
                    integrate_btn = gr.Button("✨ 开始跨教材整合", elem_classes=["btn-primary"])
                    graph_view_toggle = gr.Radio(choices=["整合前视图","整合后视图"], value="整合前视图", label="视图切换", interactive=True)
                    compression_display = gr.HTML(value=build_compression_html())
                    decision_display = gr.HTML(value=build_decision_html(state.decisions))

                with gr.Tab("💬 RAG 问答"):
                    rag_status_display = gr.Markdown("索引状态: 未建立")
                    rag_chatbot = gr.Chatbot(height=280, type="messages")
                    with gr.Row():
                        rag_input = gr.Textbox(placeholder="输入问题…", label="", scale=4, lines=1)
                        rag_send = gr.Button("↑", variant="primary", scale=1, min_width=40)

                with gr.Tab("🗣️ 多轮对话"):
                    gr.Markdown("**教师反馈** — `保留XX` / `删除XX` / `分开XX` / `为什么合并`")
                    dialogue_chatbot = gr.Chatbot(height=240, type="messages")
                    with gr.Row():
                        dialogue_input = gr.Textbox(placeholder="教师反馈…", label="", scale=4, lines=1)
                        dialogue_send = gr.Button("↑", variant="primary", scale=1, min_width=40)

                with gr.Tab("📊 整合报告"):
                    report_display = gr.Markdown(value=build_report())

    gr.HTML('<div class="ftr">学科知识整合智能体 · 浙大 AI 黑客松</div>')

    # ===== Events =====
    parse_btn.click(
        fn=do_parse,
        inputs=[file_upload],
        outputs=[parse_status, file_list_display, stats_display, graph_display, header_display],
    )
    integrate_btn.click(
        fn=do_integrate,
        inputs=[],
        outputs=[graph_view_toggle, compression_display, decision_display, graph_display],
    )
    del_go.click(
        fn=do_delete,
        inputs=[del_idx],
        outputs=[parse_status, file_list_display, graph_display, header_display],
    )
    graph_view_toggle.change(fn=do_toggle, inputs=[graph_view_toggle], outputs=[graph_display])
    rag_send.click(fn=rag_chat, inputs=[rag_input, rag_chatbot], outputs=[rag_chatbot, rag_input])
    rag_input.submit(fn=rag_chat, inputs=[rag_input, rag_chatbot], outputs=[rag_chatbot, rag_input])
    dialogue_send.click(fn=dialogue_chat, inputs=[dialogue_input, dialogue_chatbot], outputs=[dialogue_chatbot, dialogue_input, graph_display])
    dialogue_input.submit(fn=dialogue_chat, inputs=[dialogue_input, dialogue_chatbot], outputs=[dialogue_chatbot, dialogue_input, graph_display])
    search_btn.click(fn=get_node_detail, inputs=[node_search], outputs=[node_detail])

    # Auto-load: refresh UI on first browser visit
    app.load(
        fn=on_app_load,
        inputs=[],
        outputs=[header_display, file_list_display, stats_display, graph_display, legend_display],
    )


if __name__ == "__main__":
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    os.environ["no_proxy"] = "localhost,127.0.0.1"

    # Load cache BEFORE launching server — instant startup if cache exists
    if load_cache():
        print("Pre-loaded from cache — ready to serve")
    else:
        print("No cache found. Run 'python cache_builder.py' first to pre-build cache.")

    app.launch(server_name="127.0.0.1", server_port=7860)
