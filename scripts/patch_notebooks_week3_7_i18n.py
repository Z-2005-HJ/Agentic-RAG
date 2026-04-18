# -*- coding: utf-8 -*-
"""Enrich Week 3-7 notebooks: intro cell, section-specific 中文 blockquotes, code first-line hints."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOTEBOOKS = REPO / "notebooks"

GENERIC_RE = re.compile(
    r"> \*\*中文（单元格对照）：\*\* 上文/上表 \*\*英文为原文\*\*；本段补充中文提示：请结合 \*\*第 \d+ 周\*\* 仓库 `README\.md` 与 `notebooks/week\d+/README\.md` 理解术语与步骤。\n"
)


def last_h2_before_chinese(text: str) -> str:
    pre, _, _ = text.partition("> **中文（单元格对照）")
    for line in reversed(pre.split("\n")):
        s = line.strip()
        if s.startswith("## ") and not s.startswith("###"):
            return s[3:].strip()
    return ""


def first_h2_in_cell(text: str) -> str:
    pre, _, _ = text.partition("> **中文（单元格对照）")
    for line in pre.split("\n"):
        s = line.strip()
        if s.startswith("## ") and not s.startswith("###"):
            return s[3:].strip()
    return ""


def pick_heading_for_cn(text: str) -> str:
    return last_h2_before_chinese(text) or first_h2_in_cell(text)


def text_to_cell_source(text: str) -> list[str]:
    """Ipynb markdown lines: interior lines end with \\n; final line may omit \\n."""
    if not text:
        return []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        return [ln + "\n" for ln in lines[:-1]]
    if len(lines) == 1:
        return [lines[0]]
    return [ln + "\n" for ln in lines[:-1]] + [lines[-1]]


def cn_blockquote(week: int, heading: str, cell_lower: str) -> str:
    h = (heading or "").lower()
    cl = cell_lower

    if week == 3:
        if "essential setup" in h:
            return "> **中文 · 环境与配置：** 先复制 `.env.example` → `.env`，确认 **OpenSearch** 变量（如 `OPENSEARCH__HOST`、`OPENSEARCH__INDEX_NAME`）；关键词检索是后续向量/混合检索的基础。\n"
        if "week 3 focus areas" in h or "week 3 component status" in h:
            return "> **中文 · 本周路线图：** 在 OpenSearch 上建立 **arxiv-papers** 索引与 **BM25** 查询，并把 Postgres 论文同步进索引；组件表对应 `src/services/opensearch/` 等实现。\n"
        if "important" in cl and "docker compose" in cl:
            return "> **中文 · 容器与前置：** Week 3 依赖 OpenSearch 就绪；索引/映射冲突时可 **`docker compose down -v`** 后重建。需完成 Week 1–2，Postgres 中建议已有论文便于灌库。\n"
        if "prerequisites check" in h:
            return "> **中文 · 前置检查：** 逐项确认 Week 1 基础设施、Week 2 数据、UV 与 Docker；服务 URL 用于手动排查。\n"
        if h.strip() == "environment setup":
            return "> **中文 · Notebook 环境：** 下一格配置 `sys.path` 与 Python 版本；请在含 `compose.yml` 的仓库根或 `notebooks/week3` 下运行内核。\n"
        if "infrastructure verification" in h:
            return "> **中文 · 服务健康：** 用 HTTP 探测 FastAPI、OpenSearch、Airflow 等；OpenSearch 也可用 `9200/_cluster/health`。\n"
        if "opensearch client" in h:
            return "> **中文 · 客户端：** 工厂函数创建客户端，封装连接与健康检查；与 FastAPI **lifespan** 注入一致。\n"
        if "index configuration" in h:
            return "> **中文 · 索引与映射：** JSON 定义字段、**analyzer** 与 **BM25** 设置；英文学术内容常用英文分析链。\n"
        if "data pipeline" in h:
            return "> **中文 · 数据管道：** Airflow DAG 将论文写入 OpenSearch；关注任务顺序与失败重试。\n"
        if "simple bm25" in h:
            return "> **中文 · BM25 基础：** 多字段 `match` 与 **boost**；理解 `_score` 与查询 DSL。\n"
        if "advanced opensearch" in h:
            return "> **中文 · 进阶查询：** 高亮、分页、模糊与过滤；对照 `QueryBuilder` 实现。\n"
        if "summary" in h:
            return "> **中文 · 小结：** 完成 **索引 → 灌库 → BM25 → API** 验证；Week 4 引入分块与向量。\n"

    if week == 4:
        if "week 4 focus" in h or "key architecture" in h:
            return "> **中文 · 本周目标：** **分块**、**Jina 嵌入**、统一索引上的 **BM25 / 向量 / RRF 混合**。\n"
        if "important" in h:
            return "> **中文 · 重建提示：** 新索引（如 `arxiv-papers-chunks`）可能与旧卷不兼容；按英文说明清理或重建后再跑。\n"
        if "sample papers" in h:
            return "> **中文 · 样例数据：** 从库/API 取论文驱动分块演示；依赖前几周入库数据。\n"
        if "chunking" in h and "overlap" not in h:
            return "> **中文 · 分块：** 利用章节结构切分并配置 overlap；见 `CHUNKING__*` 环境变量。\n"
        if "overlap strategy" in h:
            return "> **中文 · 重叠分析：** overlap 缓解切块边界信息丢失；可对比不同 overlap 下的块统计。\n"
        if "embedding" in h:
            return "> **中文 · 嵌入：** `make_embeddings_service()` 生成向量；需 **`JINA_API_KEY`**，失败时常回退 BM25。\n"
        if "unified search" in h:
            return "> **中文 · 统一检索：** 同一客户端上切换 **BM25 / 向量 / 混合** 模式，观察 `search_unified` 行为。\n"
        if "bm25 keyword" in h:
            return "> **中文 · BM25：** 关键词路径最快，适合精确术语与高频查询。\n"
        if "vector similarity" in h:
            return "> **中文 · 向量：** kNN 语义相似；依赖索引 mapping 中的 **dense_vector** 字段。\n"
        if "hybrid search" in h:
            return "> **中文 · 混合：** RRF 融合两套排序；延迟通常高于纯 BM25。\n"
        if "performance comparison" in h or "enhanced performance" in h:
            return "> **中文 · 性能：** 表中数字为示例环境；混合模式含嵌入调用，慢于纯关键词属正常。\n"
        if "production api" in h:
            return "> **中文 · API：** `POST /api/v1/hybrid-search/` 带校验与可选自动嵌入。\n"
        if "summary" in h:
            return "> **中文 · 小结：** 掌握分块 + 双路检索 + 融合；衔接 Week 5 生成式 RAG。\n"

    if week == 5:
        if "week 5 focus" in h or ("prerequisites" in h and "week 6" not in cl):
            return "> **中文 · 前置：** Ollama、OpenSearch、Jina 与索引就绪；`/ask` 与 `/stream` 共享检索与提示逻辑。\n"
        if "api endpoints" in h or "system architecture" in h or "performance metrics" in h or "key features" in h:
            return "> **中文 · 架构：** **`/ask`** 返回完整 JSON；**`/stream`** 为 SSE；**Gradio** 默认 **7861**。\n"
        if "testing guide" in h or "troubleshooting" in h or "next steps" in h or "additional resources" in h:
            return "> **中文 · 排错：** 404/慢响应见英文表；重建 `api` 镜像、减小 `top_k`、换小模型。\n"
        if "environment setup" in h:
            return "> **中文 · 路径：** 注入 `sys.path` 以便 `import src`。\n"
        if "service health" in h:
            return "> **中文 · 健康：** 先确认 8000/11434/9200 等再跑 RAG 单元。\n"
        if "api structure" in h:
            return "> **中文 · OpenAPI：** 用 `/openapi.json` 核对 ask/stream/hybrid-search。\n"
        if "ollama" in h:
            return "> **中文 · LLM：** 直连探测模型列表；RAG 内由客户端封装。\n"
        if "search functionality" in h:
            return "> **中文 · 检索：** 先验证混合检索与索引文档量再调用生成接口。\n"
        if "complete rag pipeline" in h and "streaming" not in h:
            return "> **中文 · 完整 RAG：** 检索 → 上下文 → Ollama 生成；关注 **sources**。\n"
        if "streaming" in h:
            return "> **中文 · 流式：** 按 SSE 解析增量 token。\n"
        if "gradio" in h:
            return "> **中文 · Gradio：** 本地启动 Web UI 做交互演示。\n"
        if "summary" in h:
            return "> **中文 · 小结：** 端到端 RAG + 流式 + UI；Week 6 加缓存与追踪。\n"

    if week == 6:
        if "week 6 focus" in h or ("prerequisites" in h and "week 6" in cl):
            return "> **中文 · 本周栈：** **Redis** 精确缓存与 **Langfuse** 追踪；倍数类指标为理想环境示例。\n"
        if "api endpoints" in h or "system architecture" in h or "performance metrics" in h or "key features" in h:
            return "> **中文 · 可观测性：** 命中缓存时显著降延迟；Langfuse 分解检索/生成耗时。\n"
        if "environment setup" in h:
            return "> **中文 · 环境：** 检查 `.env` 中 **Langfuse**、**Redis** 与端口说明。\n"
        if "api structure" in h:
            return "> **中文 · API：** Week 5 路由 + 健康字段扩展；以 OpenAPI 为准。\n"
        if "system status" in h or "using the gradio" in h:
            return "> **中文 · 实验：** 重复相同 **/ask** 请求对比延迟；观察是否命中缓存。\n"
        if "summary" in h:
            return "> **中文 · 小结：** 理解缓存键与追踪视图；Week 7 引入 Agent 与 Bot。\n"

    if week == 7:
        if "agentic rag features" in h or ("prerequisites" in h and "week 7" in cl):
            return "> **中文 · Agentic：** LangGraph 控制 **是否检索、文档评分、查询改写**；简单问题可直答。\n"
        if "service health" in h:
            return "> **中文 · 依赖：** Agent/Bot 共用 Week 5–6 栈；先跑健康检查。\n"
        if "traditional rag" in h or "baseline" in h:
            return "> **中文 · 基线：** 对比 **`/ask`** 与 **`/ask-agentic`** 的延迟与 **reasoning_steps**。\n"
        if "out-of-scope" in h or "scenario 1" in h:
            return "> **中文 · 场景 1：** 期望拒绝无关问题、避免空检索。\n"
        if "scenario 2" in h or "successful retrieval" in h:
            return "> **中文 · 场景 2：** 检索—评分—生成闭环成功路径。\n"
        if "scenario 3" in h or "rewriting" in h:
            return "> **中文 · 场景 3：** 不相关时改写查询再检索。\n"
        if "interactive" in h:
            return "> **中文 · 交互：** 可改查询做探索；Telegram 需 **Bot token** 与 `TELEGRAM__ENABLED`。\n"
        if "summary" in h:
            return "> **中文 · 小结：** 图式 Agentic RAG + 可选即时通讯入口；生产注意 webhook 与密钥。\n"

    return f"> **中文 · 本节提要（Week {week}）：** 英文为步骤原文；更多说明见 `notebooks/week{week}/README.md`。\n"


def refresh_intro_cell(week: int) -> list[str]:
    bullets = {
        3: "- **本周重点**：**OpenSearch + BM25**；索引/映射、灌库、查询 DSL、Search API。\n",
        4: "- **本周重点**：**分块**、**Jina 嵌入**、**BM25 / 向量 / RRF**、统一 chunk 索引。\n",
        5: "- **本周重点**：**Ollama** 生成、`/ask` 与 **`/stream`**、**Gradio** 完整 RAG。\n",
        6: "- **本周重点**：**Redis** 缓存、**Langfuse** 追踪与性能对比。\n",
        7: "- **本周重点**：**LangGraph Agentic RAG** 与可选 **Telegram Bot**。\n",
    }
    return [
        f"# Week {week} Notebook — 中文导读\n",
        "\n",
        "> **中文说明：** 本 notebook 为 **英中对照**：**保留全部英文单元格原文**；中文以 **段末 `> **中文**` 摘要** 与 **代码首行「# …  # 中文：…」** 补充，体例与 `notebooks/week1/week1_setup.ipynb`、`notebooks/week2/week2_arxiv_integration.ipynb` 一致。\n",
        "\n",
        "**说明 / Note：** 下方 Markdown 与代码中的 **英文说明保留不动**。  \n",
        "Cells below **keep English**; Chinese notes are additive.\n",
        "\n",
        bullets[week],
        "- **建议**：自上而下依次运行；环境变量与同周 `README.md` 对齐。\n",
        "\n",
        "---\n",
    ]


def zh_suffix_for_code_line(line: str) -> str | None:
    if "  # 中文" in line:
        return None
    if not line.lstrip().startswith("#"):
        return None
    low = line.lower()
    if "path" in low or "environment setup" in low:
        return "  # 中文：配置 Python 路径与项目根"
    if ("health" in low or "prerequisite" in low or "service" in low) and "cache" not in low:
        return "  # 中文：HTTP 探测依赖服务是否就绪"
    if "opensearch" in low and "client" in low:
        return "  # 中文：OpenSearch 客户端与健康检查"
    if "index" in low and "creat" in low:
        return "  # 中文：创建/更新索引与 mapping"
    if "bulk" in low or "reindex" in low:
        return "  # 中文：批量写入 OpenSearch"
    if "bm25" in low or ("search" in low and "advanced" not in low):
        return "  # 中文：执行检索并查看得分/结果"
    if "chunk" in low:
        return "  # 中文：分块（章节 + overlap）"
    if "embed" in low:
        return "  # 中文：嵌入向量生成"
    if "hybrid" in low or "vector" in low:
        return "  # 中文：向量或混合检索实验"
    if "openapi" in low or "api structure" in low:
        return "  # 中文：OpenAPI 路由探测"
    if "ollama" in low:
        return "  # 中文：LLM 连通性或调用"
    if "rag" in low or "/ask" in low or "stream" in low:
        return "  # 中文：RAG HTTP 调用"
    if "cache" in low:
        return "  # 中文：缓存配置或命中对比"
    if "langfuse" in low:
        return "  # 中文：Langfuse 相关"
    if "gradio" in low:
        return "  # 中文：Gradio 演示"
    if "agentic" in low or "traditional" in low:
        return "  # 中文：Agentic / 基线 RAG"
    if "telegram" in low:
        return "  # 中文：Telegram Bot"
    if "first query" in low or "second query" in low:
        return "  # 中文：缓存命中/未命中对比请求"
    return "  # 中文：按英文步骤执行"


def patch_code_cell_source(lines: list[str]) -> tuple[list[str], bool]:
    if not lines:
        return lines, False
    first = lines[0]
    if not first.strip().startswith("#"):
        return lines, False
    suf = zh_suffix_for_code_line(first)
    if not suf or suf in first:
        return lines, False
    lines = [first.rstrip("\n") + suf + "\n"] + lines[1:]
    return lines, True


def patch_notebook(path: Path) -> tuple[int, int, int]:
    week = int(path.parent.name.replace("week", ""))
    nb = json.loads(path.read_text(encoding="utf-8"))
    md_repl = 0
    intro_done = 0
    code_hits = 0
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown":
            src = cell.get("source", [])
            if not src:
                continue
            text = "".join(src)
            if i == 0 and (
                "中文导读" in text or "Chinese Guide" in text or f"Week {week} Notebook — 中文导读" in text
            ):
                cell["source"] = refresh_intro_cell(week)
                intro_done = 1
                text = "".join(cell["source"])
            if "中文（单元格对照）" in text:
                heading = pick_heading_for_cn(text)
                new_cn = cn_blockquote(week, heading, text.lower())
                new_text, n = GENERIC_RE.subn(new_cn, text, count=1)
                if n:
                    cell["source"] = text_to_cell_source(new_text)
                    md_repl += n
        elif cell["cell_type"] == "code":
            new_src, ch = patch_code_cell_source(list(cell.get("source", [])))
            if ch:
                cell["source"] = new_src
                code_hits += 1
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return md_repl, intro_done, code_hits


def main() -> None:
    t_md = t_intro = t_code = 0
    for w in range(3, 8):
        for p in sorted((NOTEBOOKS / f"week{w}").glob("*.ipynb")):
            md, intro, cd = patch_notebook(p)
            t_md += md
            t_intro += intro
            t_code += cd
            print(p.name, "md:", md, "intro:", intro, "code:", cd)
    print("TOTAL md replacements", t_md, "code cells", t_code)


if __name__ == "__main__":
    main()
