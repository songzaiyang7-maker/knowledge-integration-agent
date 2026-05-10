"""学科知识整合智能体 - Gradio 主应用"""

import json
import os
import time
import threading
import http.server
import functools
import gradio as gr
from src.mock_data import (
    MOCK_TEXTBOOKS, MOCK_NODES, MOCK_EDGES, MOCK_DECISIONS,
    MOCK_INTEGRATED_NODES, MOCK_INTEGRATED_EDGES,
    MOCK_COMPRESSION_STATS, MOCK_RAG_STATUS, MOCK_RAG_RESPONSE,
    MOCK_FILE_LIST, MOCK_REPORT, BOOK_COLORS,
)
from src.echarts_templates import render_knowledge_graph

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
# State
# ============================================================
class AppState:
    is_integrated = False
    decisions = [dict(d) for d in MOCK_DECISIONS]

state = AppState()

# ============================================================
# HTML Builders
# ============================================================

def hdr():
    return """<div class="hdr">
  <div class="hdr-left"><div class="hdr-logo">K</div><div class="hdr-title">学科知识整合智能体</div></div>
  <div class="hdr-status"><span class="dot-live"></span>Mock 数据模式 · 2 本教材 · 18 个知识点</div>
</div>"""

def file_list_html():
    rows = ""
    for i, f in enumerate(MOCK_FILE_LIST):
        rows += f'<div class="file-item"><span>📄</span><span class="file-name">{f[0]}</span><span class="file-meta">{f[2]}</span><span class="badge-ok">已完成</span><button class="file-del" onclick="document.querySelector(\'#del-idx textarea\').value=\'{i}\';document.querySelector(\'#del-go\').click()">删除</button></div>'
    if not MOCK_FILE_LIST:
        rows = '<div style="text-align:center;color:#94a3b8;padding:16px;font-size:12px">暂无教材</div>'
    return rows

def stats_html():
    s = MOCK_COMPRESSION_STATS
    return f"""<div class="stats-row">
  <div class="stat"><b>{s['original_textbooks']}</b><span>教材</span></div>
  <div class="stat"><b>{s['original_nodes']}</b><span>知识点</span></div>
  <div class="stat"><b>{s['original_total_chars']//1000}K</b><span>总字数</span></div>
</div>"""

def legend_html():
    items = ""
    for name, color in BOOK_COLORS.items():
        if name in ["生理学", "病理学", "整合后"]:
            items += f'<span><span class="dot-legend" style="background:{color}"></span>{name}</span>'
    return f'<div class="graph-legend">{items}</div>'

def compression_html():
    s = MOCK_COMPRESSION_STATS
    if not state.is_integrated:
        return '<div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">点击上方按钮开始跨教材整合</div>'
    return f"""<div class="pbar-wrap">
  <div class="pbar-labels"><span>{s['original_total_chars']:,} 字</span><span>{s['integrated_total_chars']:,} 字</span></div>
  <div class="pbar-track"><div class="pbar-fill" style="width:{s['compression_ratio']}%"></div></div>
  <div class="pbar-result">压缩比 {s['compression_ratio']}%</div>
</div>
<div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
  <span class="badge-merge">合并 {s['merge_count']} 项</span>
  <span class="badge-keep">保留 {s['keep_count']} 项</span>
  <span class="badge-remove">删除 {s['remove_count']} 项</span>
</div>"""

def decision_html(decisions):
    rows = ""
    for d in decisions:
        a = d["action"].upper()
        cls = {"MERGE":"badge-merge","KEEP":"badge-keep","REMOVE":"badge-remove"}.get(a,"badge-merge")
        reason_short = d["reason"][:35] + "…" if len(d["reason"]) > 35 else d["reason"]
        rows += f'<tr><td><span class="{cls}">{a}</span></td><td style="font-weight:500;color:#1e293b">{d["merged_name"]}</td><td>{d["confidence"]:.2f}</td><td style="color:#a1a1aa;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{d["reason"]}">{reason_short}</td></tr>'
    return f'<table class="dtable"><thead><tr><th>决策</th><th>知识点</th><th>置信度</th><th>理由</th></tr></thead><tbody>{rows}</tbody></table>'

# ============================================================
# Logic
# ============================================================

def get_graph_html():
    nodes = MOCK_INTEGRATED_NODES if state.is_integrated else MOCK_NODES
    edges = MOCK_INTEGRATED_EDGES if state.is_integrated else MOCK_EDGES
    title = "整合后" if state.is_integrated else "整合前"
    return render_knowledge_graph(nodes, edges, BOOK_COLORS, title=title)

def get_node_detail(q):
    if not q or not q.strip():
        return ""
    for n in MOCK_NODES + MOCK_INTEGRATED_NODES:
        if q in n["name"] or q in n["id"]:
            return f"<div class='node-detail'><h3>{n['name']}</h3><b>定义：</b>{n.get('definition','')}<br><b>来源：</b>{n.get('textbook','')} · {n.get('chapter','')} · 第{n.get('page','?')}页<br><b>频次：</b>{n.get('frequency',1)} 本教材 · <b>类别：</b>{n.get('category','')}</div>"
    return f"<div class='node-detail' style='color:#94a3b8'>未找到「{q}」</div>"

def do_integrate():
    state.is_integrated = True
    return "整合后视图", compression_html(), decision_html(state.decisions), get_graph_html()

def do_toggle(view):
    state.is_integrated = (view == "整合后视图")
    return get_graph_html()

def rag_chat(message, history):
    if not message.strip():
        return history, ""
    if "炎症" in message or "白细胞" in message or "免疫" in message:
        resp = MOCK_RAG_RESPONSE
    elif "动作电位" in message or "静息电位" in message or "电位" in message:
        answer = "动作电位是细胞受到刺激后膜电位发生的快速可逆倒转：\n\n1. **去极化相**：Na⁺ 通道开放，Na⁺ 内流\n2. **复极化相**：K⁺ 通道开放，K⁺ 外流\n3. **特征**：\"全或无\"现象"
        resp = {"answer": answer, "citations": [{"textbook":"生理学","chapter":"第二章 细胞的基本功能","page":35,"relevance_score":0.94},{"textbook":"生理学","chapter":"第二章 细胞的基本功能","page":25,"relevance_score":0.88}], "source_chunks":["动作电位是指细胞受到刺激后，膜电位发生的一次快速而可逆的倒转...","静息电位是动作电位产生的基础，正常约为-70mV..."]}
    elif "T细胞" in message or "T淋巴" in message:
        answer = "T细胞是适应性免疫的核心：\n\n1. **Th 辅助性**：分泌细胞因子\n2. **Tc 细胞毒性**：杀伤感染细胞\n3. **Treg 调节性**：维持免疫耐受"
        resp = {"answer": answer, "citations": [{"textbook":"生理学","chapter":"第三章 血液","page":88,"relevance_score":0.91},{"textbook":"病理学","chapter":"第五章 免疫性疾病","page":178,"relevance_score":0.89}], "source_chunks":["T细胞由胸腺发育而来...","T淋巴细胞介导细胞免疫..."]}
    else:
        answer = f"关于「{message}」— Mock 模式，可尝试：白细胞/动作电位/T细胞"
        resp = {"answer": answer, "citations": [], "source_chunks": []}
    content = resp["answer"]
    if resp["citations"]:
        content += "\n\n---\n**📎 引用来源：**\n"
        for i, c in enumerate(resp["citations"], 1):
            chunk = resp["source_chunks"][i-1][:250] if i-1 < len(resp["source_chunks"]) else ""
            content += f'\n<details><summary>[{c["textbook"]}, {c["chapter"]}, 第{c["page"]}页] · {c["relevance_score"]:.2f}</summary>\n\n> {chunk}...\n</details>'
    return history + [{"role":"user","content":message},{"role":"assistant","content":content}], ""

def do_delete(idx_str):
    """按索引删除教材"""
    try:
        idx = int(idx_str.strip())
        if 0 <= idx < len(MOCK_FILE_LIST):
            removed = MOCK_FILE_LIST.pop(idx)
            return f"已删除「{removed[0]}」", file_list_html()
    except (ValueError, IndexError):
        pass
    return "删除失败", file_list_html()

def dialogue_chat(message, history):
    if not message.strip():
        return history, "", get_graph_html()
    if "为什么" in message and "合并" in message:
        r = "合并基于**三级对齐**：\n\n1. L1 精确匹配\n2. L2 Embedding > 0.85\n3. LLM 精判\n\n置信度 > 0.85 视为语义等价。"
    elif "保留" in message:
        r = "未找到可恢复的删除项。"
        for d in state.decisions:
            if d["action"]=="remove":
                d["action"]="keep"; r=f"✅ 「{d['merged_name']}」已恢复保留，图谱已刷新"; state.is_integrated=True; break
    elif "删除" in message or "移除" in message:
        r = "未找到可删除项。"
        for d in state.decisions:
            if d["action"]=="keep":
                d["action"]="remove"; r=f"🗑️ 「{d['merged_name']}」已删除，图谱已刷新"; state.is_integrated=True; break
    elif "分开" in message or "拆分" in message:
        r = "未找到可拆分项。"
        for d in state.decisions:
            if d["action"]=="merge":
                d["action"]="keep"; r=f"🔓 「{d['merged_name']}」已拆分，图谱已刷新"; state.is_integrated=True; break
    else:
        r = f"收到：「{message}」\n\n指令：`保留XX` / `删除XX` / `分开XX` / `为什么合并`"
    return history + [{"role":"user","content":message},{"role":"assistant","content":r}], "", get_graph_html()

# ============================================================
# Gradio UI — native three-column layout
# ============================================================

with gr.Blocks(title="学科知识整合智能体", css=CSS) as app:

    gr.HTML(hdr())

    # ===== THREE-COLUMN ROW =====
    with gr.Row(equal_height=True):

        # ===== LEFT: 教材管理 =====
        with gr.Column(scale=2, min_width=220):
            gr.HTML('<div class="card-hd"><h3>📚 教材管理</h3></div>')
            file_upload = gr.File(label="上传教材 (PDF/MD/TXT)", file_count="multiple", file_types=[".pdf",".md",".txt"], elem_classes=["upload-wrap"])
            parse_btn = gr.Button("解析教材", elem_classes=["btn-primary"])
            parse_status = gr.Markdown("")
            file_list_display = gr.HTML(value=file_list_html())
            del_idx = gr.Textbox(visible=False, elem_id="del-idx")
            del_go = gr.Button(visible=False, elem_id="del-go")
            gr.HTML(stats_html())

        # ===== CENTER: 知识图谱 =====
        with gr.Column(scale=5, min_width=400):
            gr.HTML('<div class="card-hd"><h3>🕸️ 知识图谱</h3></div>')
            graph_display = gr.HTML(value=get_graph_html())
            gr.HTML(legend_html())
            node_detail = gr.HTML("")
            node_search = gr.Textbox(placeholder="搜索知识点名称…", label="节点搜索", lines=1)
            search_btn = gr.Button("搜索", size="sm")

        # ===== RIGHT: 功能面板 =====
        with gr.Column(scale=4, min_width=300):
            with gr.Tabs():
                with gr.Tab("🔧 整合操作"):
                    integrate_btn = gr.Button("✨ 开始跨教材整合", elem_classes=["btn-primary"])
                    graph_view_toggle = gr.Radio(choices=["整合前视图","整合后视图"], value="整合前视图", label="视图切换", interactive=True)
                    compression_display = gr.HTML(value=compression_html())
                    decision_display = gr.HTML(value=decision_html(state.decisions))

                with gr.Tab("💬 RAG 问答"):
                    gr.Markdown(f"已索引 2 本教材，共 {MOCK_RAG_STATUS['total_chunks']} 个知识块")
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
                    report_display = gr.Markdown(value=MOCK_REPORT)

    gr.HTML('<div class="ftr">学科知识整合智能体 · 浙大 AI 黑客松</div>')

    # ===== Events =====
    integrate_btn.click(fn=do_integrate, inputs=[], outputs=[graph_view_toggle, compression_display, decision_display, graph_display])
    del_go.click(fn=do_delete, inputs=[del_idx], outputs=[parse_status, file_list_display])
    graph_view_toggle.change(fn=do_toggle, inputs=[graph_view_toggle], outputs=[graph_display])
    rag_send.click(fn=rag_chat, inputs=[rag_input, rag_chatbot], outputs=[rag_chatbot, rag_input])
    rag_input.submit(fn=rag_chat, inputs=[rag_input, rag_chatbot], outputs=[rag_chatbot, rag_input])
    dialogue_send.click(fn=dialogue_chat, inputs=[dialogue_input, dialogue_chatbot], outputs=[dialogue_chatbot, dialogue_input, graph_display])
    dialogue_input.submit(fn=dialogue_chat, inputs=[dialogue_input, dialogue_chatbot], outputs=[dialogue_chatbot, dialogue_input, graph_display])
    search_btn.click(fn=get_node_detail, inputs=[node_search], outputs=[node_detail])


if __name__ == "__main__":
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    os.environ["no_proxy"] = "localhost,127.0.0.1"
    app.launch(server_name="127.0.0.1", server_port=7860)
