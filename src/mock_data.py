"""Mock data for Phase 2 UI development. Covers 2 textbooks with knowledge graph nodes, edges, integration decisions, and RAG Q&A results."""

# ============================================================
# 1. 教材解析结果（2 本教材）
# ============================================================
MOCK_TEXTBOOKS = [
    {
        "textbook_id": "book_01",
        "filename": "生理学.pdf",
        "title": "生理学",
        "total_pages": 520,
        "total_chars": 385000,
        "chapters": [
            {
                "chapter_id": "ch_01",
                "title": "第一章 绪论",
                "page_start": 1,
                "page_end": 15,
                "content": "生理学是研究生物体正常生命活动规律的科学...",
                "char_count": 8500,
            },
            {
                "chapter_id": "ch_02",
                "title": "第二章 细胞的基本功能",
                "page_start": 16,
                "page_end": 65,
                "content": "细胞是生物体结构和功能的基本单位...",
                "char_count": 32000,
            },
            {
                "chapter_id": "ch_03",
                "title": "第三章 血液",
                "page_start": 66,
                "page_end": 120,
                "content": "血液是由血浆和血细胞组成的流体组织...",
                "char_count": 35000,
            },
            {
                "chapter_id": "ch_04",
                "title": "第四章 血液循环",
                "page_start": 121,
                "page_end": 200,
                "content": "心脏是血液循环的动力器官...",
                "char_count": 52000,
            },
            {
                "chapter_id": "ch_09",
                "title": "第九章 神经系统的功能",
                "page_start": 350,
                "page_end": 430,
                "content": "神经系统是人体最复杂的系统...",
                "char_count": 48000,
            },
        ],
    },
    {
        "textbook_id": "book_02",
        "filename": "病理学.pdf",
        "title": "病理学",
        "total_pages": 480,
        "total_chars": 360000,
        "chapters": [
            {
                "chapter_id": "ch_01",
                "title": "第一章 细胞和组织的适应与损伤",
                "page_start": 1,
                "page_end": 40,
                "content": "细胞和组织对有害刺激的反应...",
                "char_count": 28000,
            },
            {
                "chapter_id": "ch_02",
                "title": "第二章 损伤的修复",
                "page_start": 41,
                "page_end": 75,
                "content": "组织损伤后的修复过程包括再生和纤维性修复...",
                "char_count": 22000,
            },
            {
                "chapter_id": "ch_04",
                "title": "第四章 炎症",
                "page_start": 110,
                "page_end": 165,
                "content": "炎症是具有血管系统的活体组织对各种损伤因子的刺激所发生的防御性反应...",
                "char_count": 38000,
            },
            {
                "chapter_id": "ch_05",
                "title": "第五章 免疫性疾病",
                "page_start": 166,
                "page_end": 210,
                "content": "免疫系统在维持机体稳态中发挥重要作用...",
                "char_count": 30000,
            },
        ],
    },
]

# ============================================================
# 2. 知识图谱节点（18 个节点，跨 2 本教材）
# ============================================================
BOOK_COLORS = {
    "生理学": "#5470C6",
    "病理学": "#91CC75",
    "组织学与胚胎学": "#FAC858",
    "医学微生物学": "#EE6666",
    "局部解剖学": "#73C0DE",
    "传染病学": "#3BA272",
    "病理生理学": "#FC8452",
    "整合后": "#9A60B4",
}

MOCK_NODES = [
    # -- 生理学 (book_01) --
    {"id": "b01_n01", "name": "静息电位", "definition": "细胞在未受刺激时，细胞膜内外两侧存在的电位差，表现为膜内为负、膜外为正的状态。", "category": "核心概念", "chapter": "第二章 细胞的基本功能", "page": 25, "textbook": "生理学", "frequency": 2},
    {"id": "b01_n02", "name": "动作电位", "definition": "细胞受到刺激后，膜电位发生的一次快速而可逆的倒转，以及随后恢复到原来静息电位水平的过程。", "category": "核心概念", "chapter": "第二章 细胞的基本功能", "page": 35, "textbook": "生理学", "frequency": 3},
    {"id": "b01_n03", "name": "血细胞", "definition": "血液中的细胞成分，包括红细胞、白细胞和血小板三类。", "category": "核心概念", "chapter": "第三章 血液", "page": 70, "textbook": "生理学", "frequency": 3},
    {"id": "b01_n04", "name": "红细胞", "definition": "血液中数量最多的血细胞，主要功能是运输氧气和二氧化碳。", "category": "基本组成", "chapter": "第三章 血液", "page": 72, "textbook": "生理学", "frequency": 2},
    {"id": "b01_n05", "name": "白细胞", "definition": "一类有核的血细胞，包括中性粒细胞、嗜酸性粒细胞、嗜碱性粒细胞、单核细胞和淋巴细胞，主要参与免疫防御。", "category": "核心概念", "chapter": "第三章 血液", "page": 78, "textbook": "生理学", "frequency": 4},
    {"id": "b01_n06", "name": "心脏泵血", "definition": "心脏通过节律性的收缩和舒张活动，将血液从静脉系统吸入，经动脉系统泵出，维持血液循环的过程。", "category": "生理过程", "chapter": "第四章 血液循环", "page": 130, "textbook": "生理学", "frequency": 1},
    {"id": "b01_n07", "name": "突触传递", "definition": "神经冲动从一个神经元传递到另一个神经元或效应器细胞的过程，包括化学突触传递和电突触传递。", "category": "生理过程", "chapter": "第九章 神经系统的功能", "page": 370, "textbook": "生理学", "frequency": 1},
    {"id": "b01_n08", "name": "神经递质", "definition": "由突触前膜释放，在突触间隙中扩散，与突触后膜受体结合，引起突触后膜电位变化的化学物质。", "category": "核心概念", "chapter": "第九章 神经系统的功能", "page": 375, "textbook": "生理学", "frequency": 2},
    {"id": "b01_n09", "name": "免疫应答", "definition": "机体免疫系统识别和排除抗原性异物，以维持自身稳定的生理过程，包括固有免疫和适应性免疫。", "category": "生理过程", "chapter": "第三章 血液", "page": 95, "textbook": "生理学", "frequency": 3},
    {"id": "b01_n10", "name": "T细胞", "definition": "由胸腺发育而来的淋巴细胞，主要参与细胞免疫，包括辅助性T细胞和细胞毒性T细胞。", "category": "基本组成", "chapter": "第三章 血液", "page": 88, "textbook": "生理学", "frequency": 2},

    # -- 病理学 (book_02) --
    {"id": "b02_n01", "name": "细胞适应", "definition": "细胞和组织对内外环境变化作出的非损伤性应答反应，包括萎缩、肥大、增生和化生。", "category": "核心概念", "chapter": "第一章 细胞和组织的适应与损伤", "page": 5, "textbook": "病理学", "frequency": 1},
    {"id": "b02_n02", "name": "细胞损伤", "definition": "细胞和组织受到超过适应能力的有害因子刺激后，出现的形态学和功能上的可逆或不可逆改变。", "category": "核心概念", "chapter": "第一章 细胞和组织的适应与损伤", "page": 18, "textbook": "病理学", "frequency": 2},
    {"id": "b02_n03", "name": "炎症", "definition": "具有血管系统的活体组织对各种损伤因子的刺激所发生的以防御为主的局部组织反应，包括红、肿、热、痛和功能障碍。", "category": "核心概念", "chapter": "第四章 炎症", "page": 112, "textbook": "病理学", "frequency": 4},
    {"id": "b02_n04", "name": "白细胞", "definition": "炎症反应中的主要效应细胞，包括中性粒细胞、巨噬细胞、淋巴细胞等，参与炎症的各个阶段。", "category": "核心概念", "chapter": "第四章 炎症", "page": 120, "textbook": "病理学", "frequency": 4},
    {"id": "b02_n05", "name": "免疫应答", "definition": "机体对抗原刺激产生的特异性免疫反应，包括体液免疫和细胞免疫，在防御感染和肿瘤监视中起关键作用。", "category": "生理过程", "chapter": "第五章 免疫性疾病", "page": 170, "textbook": "病理学", "frequency": 3},
    {"id": "b02_n06", "name": "T淋巴细胞", "definition": "来源于骨髓并在胸腺中成熟的淋巴细胞，介导细胞免疫应答，是适应性免疫的核心组成部分。", "category": "基本组成", "chapter": "第五章 免疫性疾病", "page": 178, "textbook": "病理学", "frequency": 2},
    {"id": "b02_n07", "name": "修复", "definition": "组织损伤后通过细胞再生和纤维结缔组织增生来修补缺损的过程，包括完全再生和不完全再生。", "category": "生理过程", "chapter": "第二章 损伤的修复", "page": 42, "textbook": "病理学", "frequency": 1},
    {"id": "b02_n08", "name": "肉芽组织", "definition": "由新生薄壁毛细血管和成纤维细胞构成的幼稚结缔组织，伴有炎性细胞浸润，是创伤修复的重要成分。", "category": "核心概念", "chapter": "第二章 损伤的修复", "page": 50, "textbook": "病理学", "frequency": 1},
]

# ============================================================
# 3. 知识图谱边（关系，20 条，4 种类型）
# ============================================================
MOCK_EDGES = [
    # prerequisite (前置依赖)
    {"source": "b01_n01", "target": "b01_n02", "relation_type": "prerequisite", "description": "理解动作电位需要先掌握静息电位的概念"},
    {"source": "b01_n05", "target": "b01_n09", "relation_type": "prerequisite", "description": "理解免疫应答需要先了解白细胞的功能"},
    {"source": "b02_n02", "target": "b02_n03", "relation_type": "prerequisite", "description": "炎症是机体对细胞损伤的防御反应"},
    {"source": "b01_n03", "target": "b01_n04", "relation_type": "contains", "description": "血细胞包含红细胞"},
    {"source": "b02_n02", "target": "b02_n07", "relation_type": "prerequisite", "description": "修复过程发生在细胞损伤之后"},

    # parallel (并列关系)
    {"source": "b01_n04", "target": "b01_n05", "relation_type": "parallel", "description": "红细胞和白细胞同为血细胞的并列组成"},
    {"source": "b02_n01", "target": "b02_n02", "relation_type": "parallel", "description": "细胞适应与细胞损伤是细胞对刺激的两种不同反应"},

    # contains (包含关系)
    {"source": "b01_n03", "target": "b01_n05", "relation_type": "contains", "description": "血细胞包含白细胞"},
    {"source": "b01_n09", "target": "b01_n10", "relation_type": "contains", "description": "免疫应答包含T细胞的参与"},
    {"source": "b02_n05", "target": "b02_n06", "relation_type": "contains", "description": "免疫应答包含T淋巴细胞介导的细胞免疫"},
    {"source": "b02_n07", "target": "b02_n08", "relation_type": "contains", "description": "修复过程包含肉芽组织的形成"},
    {"source": "b01_n09", "target": "b01_n05", "relation_type": "applies_to", "description": "免疫应答主要由白细胞执行"},

    # applies_to (应用关系)
    {"source": "b01_n08", "target": "b01_n07", "relation_type": "applies_to", "description": "神经递质是突触传递的物质基础"},
    {"source": "b02_n04", "target": "b02_n03", "relation_type": "applies_to", "description": "白细胞是炎症反应的主要效应细胞"},
    {"source": "b02_n06", "target": "b02_n05", "relation_type": "applies_to", "description": "T淋巴细胞是免疫应答的执行者"},

    # 跨教材关系
    {"source": "b01_n02", "target": "b02_n02", "relation_type": "prerequisite", "description": "理解细胞损伤需要了解正常的细胞电生理活动"},
    {"source": "b01_n05", "target": "b02_n04", "relation_type": "parallel", "description": "两本教材中的白细胞概念高度相关"},
    {"source": "b01_n09", "target": "b02_n05", "relation_type": "parallel", "description": "两本教材中的免疫应答概念高度相关"},
    {"source": "b01_n10", "target": "b02_n06", "relation_type": "parallel", "description": "T细胞与T淋巴细胞指同一类细胞"},
]

# ============================================================
# 4. 整合决策（merge/keep/remove）
# ============================================================
MOCK_DECISIONS = [
    {
        "decision_id": "merge_001",
        "action": "merge",
        "affected_nodes": ["b01_n05", "b02_n04"],
        "result_node": "merged_001",
        "merged_name": "白细胞",
        "reason": "两本教材中'白细胞'的概念高度一致，均描述为参与免疫防御的有核血细胞。保留《病理学》版本因其描述更详细地涵盖了炎症相关功能。",
        "confidence": 0.95,
    },
    {
        "decision_id": "merge_002",
        "action": "merge",
        "affected_nodes": ["b01_n09", "b02_n05"],
        "result_node": "merged_002",
        "merged_name": "免疫应答",
        "reason": "两本教材的'免疫应答'概念在核心定义上一致，均涵盖固有免疫和适应性免疫。《病理学》版本额外涵盖了免疫病理内容，更全面。",
        "confidence": 0.92,
    },
    {
        "decision_id": "merge_003",
        "action": "merge",
        "affected_nodes": ["b01_n10", "b02_n06"],
        "result_node": "merged_003",
        "merged_name": "T细胞",
        "reason": "'T细胞'与'T淋巴细胞'指同一类细胞，均来源于胸腺，介导细胞免疫。合并后保留更完整的描述。",
        "confidence": 0.97,
    },
    {
        "decision_id": "keep_001",
        "action": "keep",
        "affected_nodes": ["b01_n01"],
        "result_node": "b01_n01",
        "merged_name": "静息电位",
        "reason": "静息电位是生理学特有的核心概念，病理学中未涉及，必须保留。",
        "confidence": 0.99,
    },
    {
        "decision_id": "keep_002",
        "action": "keep",
        "affected_nodes": ["b01_n06"],
        "result_node": "b01_n06",
        "merged_name": "心脏泵血",
        "reason": "心脏泵血是生理学独有概念，无重复，保留。",
        "confidence": 0.99,
    },
    {
        "decision_id": "keep_003",
        "action": "keep",
        "affected_nodes": ["b02_n03"],
        "result_node": "b02_n03",
        "merged_name": "炎症",
        "reason": "炎症是病理学的核心概念，虽然与免疫应答相关，但作为独立疾病过程必须保留。",
        "confidence": 0.95,
    },
    {
        "decision_id": "remove_001",
        "action": "remove",
        "affected_nodes": ["b01_n03"],
        "result_node": None,
        "merged_name": "血细胞（笼统概念）",
        "reason": "'血细胞'是红细胞和白细胞的笼统上位概念，整合后已被更具体的子概念（红细胞、白细胞）覆盖，删除不影响教学完整性。",
        "confidence": 0.88,
    },
]

# ============================================================
# 5. 整合后的节点（用于展示整合后图谱）
# ============================================================
MOCK_INTEGRATED_NODES = [
    {"id": "merged_001", "name": "白细胞", "definition": "一类有核的血细胞，包括中性粒细胞、嗜酸性粒细胞、嗜碱性粒细胞、单核细胞和淋巴细胞。在免疫防御和炎症反应中发挥核心作用，是炎症反应的主要效应细胞。", "category": "核心概念", "textbook": "整合后", "frequency": 4},
    {"id": "merged_002", "name": "免疫应答", "definition": "机体免疫系统识别和排除抗原性异物的生理过程，包括固有免疫和适应性免疫（体液免疫和细胞免疫），在防御感染、肿瘤监视和免疫病理中起关键作用。", "category": "生理过程", "textbook": "整合后", "frequency": 3},
    {"id": "merged_003", "name": "T细胞", "definition": "来源于骨髓并在胸腺中成熟的淋巴细胞，介导细胞免疫应答，包括辅助性T细胞和细胞毒性T细胞，是适应性免疫的核心组成部分。", "category": "基本组成", "textbook": "整合后", "frequency": 2},
    {"id": "b01_n01", "name": "静息电位", "definition": "细胞在未受刺激时，细胞膜内外两侧存在的电位差，表现为膜内为负、膜外为正的状态。", "category": "核心概念", "textbook": "生理学", "frequency": 2},
    {"id": "b01_n02", "name": "动作电位", "definition": "细胞受到刺激后，膜电位发生的一次快速而可逆的倒转。", "category": "核心概念", "textbook": "生理学", "frequency": 3},
    {"id": "b01_n04", "name": "红细胞", "definition": "血液中数量最多的血细胞，主要功能是运输氧气和二氧化碳。", "category": "基本组成", "textbook": "生理学", "frequency": 2},
    {"id": "b01_n06", "name": "心脏泵血", "definition": "心脏通过节律性的收缩和舒张活动维持血液循环。", "category": "生理过程", "textbook": "生理学", "frequency": 1},
    {"id": "b01_n07", "name": "突触传递", "definition": "神经冲动从一个神经元传递到另一个神经元的过程。", "category": "生理过程", "textbook": "生理学", "frequency": 1},
    {"id": "b01_n08", "name": "神经递质", "definition": "突触前膜释放的化学物质，引起突触后膜电位变化。", "category": "核心概念", "textbook": "生理学", "frequency": 2},
    {"id": "b02_n01", "name": "细胞适应", "definition": "细胞和组织对内外环境变化作出的非损伤性应答反应。", "category": "核心概念", "textbook": "病理学", "frequency": 1},
    {"id": "b02_n02", "name": "细胞损伤", "definition": "细胞受到超过适应能力的有害刺激后的可逆或不可逆改变。", "category": "核心概念", "textbook": "病理学", "frequency": 2},
    {"id": "b02_n03", "name": "炎症", "definition": "具有血管系统的活体组织对各种损伤因子的防御性反应。", "category": "核心概念", "textbook": "病理学", "frequency": 4},
    {"id": "b02_n07", "name": "修复", "definition": "组织损伤后通过再生和纤维结缔组织增生修补缺损。", "category": "生理过程", "textbook": "病理学", "frequency": 1},
    {"id": "b02_n08", "name": "肉芽组织", "definition": "由新生毛细血管和成纤维细胞构成的幼稚结缔组织。", "category": "核心概念", "textbook": "病理学", "frequency": 1},
]

MOCK_INTEGRATED_EDGES = [
    {"source": "b01_n01", "target": "b01_n02", "relation_type": "prerequisite", "description": "理解动作电位需要先掌握静息电位"},
    {"source": "merged_001", "target": "merged_002", "relation_type": "prerequisite", "description": "理解免疫应答需要了解白细胞功能"},
    {"source": "b02_n02", "target": "b02_n03", "relation_type": "prerequisite", "description": "炎症是对细胞损伤的防御反应"},
    {"source": "b01_n04", "target": "merged_001", "relation_type": "parallel", "description": "红细胞和白细胞并列"},
    {"source": "merged_002", "target": "merged_003", "relation_type": "contains", "description": "免疫应答包含T细胞"},
    {"source": "b02_n02", "target": "b02_n07", "relation_type": "prerequisite", "description": "修复发生在损伤之后"},
    {"source": "merged_001", "target": "b02_n03", "relation_type": "applies_to", "description": "白细胞是炎症的主要效应细胞"},
    {"source": "b01_n08", "target": "b01_n07", "relation_type": "applies_to", "description": "神经递质是突触传递的基础"},
    {"source": "b02_n07", "target": "b02_n08", "relation_type": "contains", "description": "修复过程包含肉芽组织形成"},
]

# ============================================================
# 6. 压缩比统计
# ============================================================
MOCK_COMPRESSION_STATS = {
    "original_textbooks": 2,
    "original_nodes": 18,
    "original_total_chars": 745000,
    "integrated_nodes": 14,
    "integrated_total_chars": 195000,
    "compression_ratio": 26.2,
    "merge_count": 3,
    "keep_count": 3,
    "remove_count": 1,
}

# ============================================================
# 7. RAG 问答 Mock 结果
# ============================================================
MOCK_RAG_STATUS = {
    "indexed_textbooks": 2,
    "total_chunks": 486,
    "total_chars": 745000,
}

MOCK_RAG_RESPONSE = {
    "question": "白细胞在炎症反应中发挥什么作用？",
    "answer": "白细胞是炎症反应中最主要的效应细胞。在炎症过程中，白细胞（特别是中性粒细胞和巨噬细胞）通过以下机制发挥作用：\n\n1. **趋化迁移**：白细胞受趋化因子吸引，从血管内游走到炎症部位。\n2. **吞噬作用**：中性粒细胞和巨噬细胞吞噬并消化病原体和组织碎片。\n3. **释放炎症介质**：白细胞释放多种炎症介质（如细胞因子、前列腺素等），放大炎症反应。\n4. **免疫调节**：淋巴细胞参与特异性免疫应答，调控炎症的强度和持续时间。",
    "citations": [
        {"textbook": "生理学", "chapter": "第三章 血液", "page": 78, "relevance_score": 0.95},
        {"textbook": "病理学", "chapter": "第四章 炎症", "page": 120, "relevance_score": 0.92},
        {"textbook": "病理学", "chapter": "第五章 免疫性疾病", "page": 170, "relevance_score": 0.78},
    ],
    "source_chunks": [
        "白细胞（leukocyte）是一类有核的血细胞，包括中性粒细胞、嗜酸性粒细胞、嗜碱性粒细胞、单核细胞和淋巴细胞，主要参与免疫防御。在炎症反应中，中性粒细胞首先到达炎症部位，发挥吞噬和杀菌作用...",
        "炎症反应中的主要效应细胞是白细胞，其中中性粒细胞和巨噬细胞在急性炎症中发挥吞噬作用，淋巴细胞则在慢性炎症和免疫应答中起关键作用。白细胞通过释放炎症介质如IL-1、TNF-α等调控炎症过程...",
        "免疫应答中T淋巴细胞和B淋巴细胞分别介导细胞免疫和体液免疫，在感染防御和免疫调节中发挥重要作用。T细胞可通过分泌细胞因子调节炎症反应的强度和方向...",
    ],
}

# ============================================================
# 8. 文件列表 Mock
# ============================================================
MOCK_FILE_LIST = [
    ["生理学.pdf", "PDF", "38.5 MB", "已完成"],
    ["病理学.pdf", "PDF", "36.0 MB", "已完成"],
]

# ============================================================
# 9. 整合报告 Mock
# ============================================================
MOCK_REPORT = """# 学科知识整合报告

## 一、整合概览

| 指标 | 数值 |
|------|------|
| 原始教材数量 | 2 本 |
| 原始总字数 | 745,000 字 |
| 整合后字数 | 195,000 字 |
| **压缩比** | **26.2%** |

## 二、整合决策摘要

| 决策类型 | 数量 |
|---------|------|
| 合并（merge） | 3 项 |
| 保留（keep） | 3 项 |
| 删除（remove） | 1 项 |
| **总计** | **7 项** |

## 三、知识图谱统计

- 整合前总节点数：18 个
- 整合后总节点数：14 个
- 节点减少：4 个（22.2%）
- 关系数量：整合前 20 条 → 整合后 9 条

## 四、重点整合案例

### 案例 1：白细胞（merge, 置信度 0.95）
- **受影响节点**：生理学·白细胞 + 病理学·白细胞
- **决策**：合并保留病理学版本
- **理由**：两本教材中白细胞概念高度一致，病理学版本更详细地涵盖了炎症相关功能

### 案例 2：T细胞 / T淋巴细胞（merge, 置信度 0.97）
- **受影响节点**：生理学·T细胞 + 病理学·T淋巴细胞
- **决策**：合并为"T细胞"
- **理由**：同一类细胞的不同命名，合并后保留更完整的描述

### 案例 3：血细胞（remove, 置信度 0.88）
- **受影响节点**：生理学·血细胞
- **决策**：删除
- **理由**：上位笼统概念，已被更具体的子概念（红细胞、白细胞）覆盖

## 五、教学完整性说明

经 prerequisite 链路审计，整合后教学链路完整，无断裂节点。所有保留知识点的前置依赖均满足，教学连贯性得到保证。
"""
