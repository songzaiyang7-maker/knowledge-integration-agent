# 学科知识整合智能体

> AI 全栈黑客松参赛作品 — 基于知识图谱的多教材知识整合与 RAG 问答系统

## 一、环境依赖

- **Python 3.10+**
- **依赖包**：见 `requirements.txt`

| 核心依赖 | 版本要求 | 用途 |
|---------|---------|------|
| gradio | >= 4.0 | Web 界面框架 |
| pymupdf | >= 1.24 | PDF 解析 |
| sentence-transformers | >= 3.0 | 文本向量化（BGE-small-zh） |
| faiss-cpu | >= 1.7 | 向量检索引擎 |
| openai | >= 1.0 | LLM API 调用 |
| numpy | >= 1.24 | 数值计算 |

## 二、安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/songzaiyang7-maker/knowledge-integration-agent.git
cd knowledge-integration-agent

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 三、配置说明

复制 `.env.example` 为 `.env` 并填写 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 LLM API 配置：

```env
APP_LLM_BASE_URL=https://api.minimaxi.com/anthropic
APP_LLM_API_KEY=你的API密钥
APP_LLM_MODEL=MiniMax-M2.7
```

> 支持任何 OpenAI 兼容格式的 API（如智谱 GLM、DeepSeek 等），修改 `BASE_URL` 和 `MODEL` 即可切换。

## 四、运行命令

```bash
# 启动应用（Windows 需设置 NO_PROXY 避免 Gradio 502 错误）
NO_PROXY=localhost,127.0.0.1 python -u app.py
```

启动后访问 **http://127.0.0.1:7860** 即可使用。

## 五、项目结构

```
├── app.py                      # Gradio 主应用（含真实逻辑 + Mock fallback）
├── requirements.txt            # Python 依赖
├── .env                        # API 配置（勿上传）
├── static/                     # 静态资源（ECharts）
├── src/                        # 核心模块
│   ├── config.py               # 配置常量
│   ├── llm_client.py           # LLM API 封装
│   ├── pdf_parser.py           # PDF/TXT/MD 解析
│   ├── knowledge_extractor.py  # LLM 知识点提取
│   ├── embedding.py            # BGE 向量嵌入
│   ├── graph_builder.py        # 知识图谱构建
│   ├── integrator.py           # 三级对齐整合算法
│   ├── echarts_templates.py    # 图谱可视化模板
│   └── rag_pipeline.py         # RAG 问答管道
├── docs/                       # 项目文档
│   ├── 需求分析.md
│   └── 系统设计.md
└── report/                     # 整合报告
    ├── 整合报告.md
    └── technical_report.pdf    # 技术报告（LaTeX）
```

## 六、核心功能

| 功能 | 说明 |
|------|------|
| 多教材解析 | 支持 PDF/TXT/MD，按章节拆分 |
| 知识图谱构建 | LLM 提取知识点 + 4 种关系，ECharts 力导向图可视化 |
| 跨教材整合 | 三级对齐算法（精确匹配 → 语义相似 → LLM 精判），压缩比 < 30% |
| RAG 问答 | FAISS 向量检索 + LLM 生成，回答带引用来源（教材、章节、页码） |
| 教师反馈 | 多轮对话修改整合决策 |
