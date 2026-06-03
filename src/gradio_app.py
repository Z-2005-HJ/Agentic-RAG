import json
import logging
from pathlib import Path
from typing import Iterator

import gradio as gr
import httpx

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"
DEFAULT_MODEL = "llama3.2:3b"
# Agentic 多轮 LLM（护栏/改写/打分/生成），常超过 5 分钟
AGENTIC_HTTP_TIMEOUT = 900.0
UPLOAD_FILE_TYPES = [".pdf", ".txt", ".md", ".docx", ".xlsx", ".xls"]
MODEL_CHOICES = ["llama3.2:3b", "llama3.2:1b", "deepseek-r1:7b", "qwen2.5:7b"]


async def check_api_health() -> str:
    """检查 FastAPI 是否可用。"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            return f"✅ API 正常（{API_BASE_URL}）"
        return f"⚠️ API 返回 HTTP {response.status_code}"
    except httpx.RequestError as exc:
        return f"❌ 无法连接 API: {exc}\n请先启动后端（docker compose up 或 uvicorn）。"


def _format_sources(sources: list[str], chunks_used: int, search_mode: str) -> str:
    block = f"\n\n**检索信息**\n- 模式: {search_mode or '未知'}\n- 使用 chunk 数: {chunks_used}\n"
    if sources:
        block += f"- 来源数: {len(sources)}\n"
        for index, source in enumerate(sources[:3], 1):
            label = source.split("/")[-1] if "/" in source else source
            block += f"  {index}. [{label}]({source})\n"
        if len(sources) > 3:
            block += f"  … 另有 {len(sources) - 3} 条\n"
    return block


async def stream_standard_response(
    query: str,
    top_k: int,
    use_hybrid: bool,
    model: str,
    categories: str,
) -> Iterator[str]:
    """流式标准 RAG（/stream）。"""
    if not query.strip():
        yield "请输入问题。"
        return

    category_list = [cat.strip() for cat in categories.split(",") if cat.strip()] if categories else None
    payload = {
        "query": query,
        "top_k": top_k,
        "use_hybrid": use_hybrid,
        "model": model,
        "categories": category_list,
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", f"{API_BASE_URL}/stream", json=payload) as response:
                if response.status_code != 200:
                    yield f"请求失败: HTTP {response.status_code}"
                    return

                current_answer = ""
                sources: list[str] = []
                chunks_used = 0
                search_mode = ""

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        data = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

                    if "error" in data:
                        yield f"错误: {data['error']}"
                        return

                    if "sources" in data:
                        sources = data.get("sources", [])
                        chunks_used = data.get("chunks_used", 0)
                        search_mode = data.get("search_mode", "")
                        continue

                    if "chunk" in data:
                        current_answer += data["chunk"]
                        yield current_answer + _format_sources(sources, chunks_used, search_mode)

                    if data.get("done"):
                        final = data.get("answer", current_answer)
                        yield final + _format_sources(sources, chunks_used, search_mode)
                        break
    except httpx.RequestError as exc:
        yield f"连接失败: {exc}"


async def ask_agentic_response(
    query: str,
    top_k: int,
    use_hybrid: bool,
    model: str,
    categories: str,
) -> str:
    """Agentic RAG（/ask-agentic）。"""
    if not query.strip():
        return "请输入问题。"

    category_list = [cat.strip() for cat in categories.split(",") if cat.strip()] if categories else None
    payload = {
        "query": query,
        "top_k": top_k,
        "use_hybrid": use_hybrid,
        "model": model,
        "categories": category_list,
    }

    try:
        async with httpx.AsyncClient(timeout=AGENTIC_HTTP_TIMEOUT) as client:
            response = await client.post(f"{API_BASE_URL}/ask-agentic", json=payload)
        if response.status_code != 200:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            return f"Agentic 请求失败（HTTP {response.status_code}）: {detail}"

        data = response.json()
        answer = data.get("answer", "")
        reasoning = data.get("reasoning_steps", [])
        attempts = data.get("retrieval_attempts", 0)
        sources = data.get("sources", [])
        search_mode = data.get("search_mode", "")

        text = answer + _format_sources(sources, data.get("chunks_used", top_k), search_mode)
        text += f"\n\n**Agentic 信息**\n- 检索轮次: {attempts}\n- 检索模式: {search_mode}\n"
        if reasoning:
            text += "- 推理步骤:\n"
            for step in reasoning:
                text += f"  - {step}\n"
        return text
    except httpx.ReadTimeout:
        return (
            "请求超时：Agentic 流程较慢（护栏→检索→打分→生成），通常需 5～10 分钟。\n"
            "请确认后端仍在运行（docker logs rag-api --tail 20），然后重试或稍后再看 API 日志是否已完成。"
        )
    except httpx.RequestError as exc:
        detail = str(exc).strip() or repr(exc)
        return f"连接失败: {detail}"


async def upload_document(file_path: str | None, title: str = "") -> str:
    """上传文档到知识库。"""
    if not file_path:
        return "请先选择文件。"

    path = Path(file_path)
    if not path.exists():
        return f"文件不存在: {file_path}"

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            with path.open("rb") as handle:
                files = {"file": (path.name, handle, "application/octet-stream")}
                data = {"title": title.strip()} if title.strip() else {}
                response = await client.post(f"{API_BASE_URL}/documents/upload", files=files, data=data)

        if response.status_code != 200:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            return f"上传失败（HTTP {response.status_code}）: {detail}"

        payload = response.json()
        doc_id = payload.get("arxiv_id")
        return (
            f"**上传成功**\n\n"
            f"- 标题: {payload.get('title')}\n"
            f"- 文档 ID: `{doc_id}`\n"
            f"- 解析器: {payload.get('parser_used')}\n"
            f"- 分块: {payload.get('chunks_created')} / 已索引: {payload.get('chunks_indexed')}\n"
            f"- 状态: {payload.get('status')}\n\n"
            f"全文 API: `GET /api/v1/papers/{doc_id}`"
        )
    except httpx.RequestError as exc:
        return f"连接 API 失败: {exc}"


def create_gradio_interface() -> gr.Blocks:
    """构建 Gradio 演示界面。"""

    with gr.Blocks(title="arXiv Paper Curator - RAG 演示", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 🔬 arXiv 论文策展 · RAG 演示

            **Gradio** 是 Python 的 Web UI 框架：本页仅负责展示与发 HTTP 请求，**检索与生成逻辑在 FastAPI**。
            默认后端: `http://localhost:8000`，本页: `http://localhost:7861`。
            """
        )

        with gr.Row():
            health_btn = gr.Button("检查 API 状态", size="sm")
            health_output = gr.Markdown("点击按钮检查后端。")
        health_btn.click(fn=check_api_health, outputs=health_output)

        with gr.Accordion("高级参数（标准 / Agentic 共用）", open=False):
            top_k = gr.Slider(1, 10, value=3, step=1, label="top_k（检索 chunk 数）")
            use_hybrid = gr.Checkbox(value=True, label="混合检索 (BM25 + BGE 512维)")
            model_choice = gr.Dropdown(choices=MODEL_CHOICES, value=DEFAULT_MODEL, label="Ollama 模型")
            categories = gr.Textbox(label="arXiv 分类（可选，逗号分隔）", placeholder="cs.AI, cs.LG")

        rag_params = [top_k, use_hybrid, model_choice, categories]

        with gr.Tabs():
            with gr.Tab("💬 标准 RAG（流式）"):
                gr.Markdown("`POST /api/v1/stream` · 支持 Redis 整答缓存")
                q_std = gr.Textbox(label="问题", placeholder="什么是 Transformer？", lines=2)
                btn_std = gr.Button("流式提问", variant="primary")
                out_std = gr.Markdown("等待提问…", height=400)
                btn_std.click(fn=stream_standard_response, inputs=[q_std, *rag_params], outputs=out_std)
                q_std.submit(fn=stream_standard_response, inputs=[q_std, *rag_params], outputs=out_std)

            with gr.Tab("🤖 Agentic RAG"):
                gr.Markdown(
                    "`POST /api/v1/ask-agentic` · 含护栏、打分、推理步骤\n\n"
                    "**注意：** 比标准 RAG 慢很多，请耐心等待 **5～10 分钟**，不要重复点击。"
                )
                q_ag = gr.Textbox(label="问题", lines=2)
                btn_ag = gr.Button("Agentic 提问", variant="primary")
                out_ag = gr.Markdown("等待提问…", height=400)
                btn_ag.click(fn=ask_agentic_response, inputs=[q_ag, *rag_params], outputs=out_ag)

            with gr.Tab("📤 上传文档"):
                gr.Markdown("`POST /api/v1/documents/upload`")
                up_file = gr.File(label="文件", file_types=UPLOAD_FILE_TYPES, type="filepath")
                up_title = gr.Textbox(label="标题（可选）")
                up_btn = gr.Button("入库", variant="primary")
                up_status = gr.Markdown("选择文件后点击入库。")
                up_btn.click(fn=upload_document, inputs=[up_file, up_title], outputs=up_status)

        gr.Markdown(
            """
            ---
            [API 文档](http://localhost:8000/docs) ·
            [RAG 模式说明](docs/RAG-modes.md) ·
            [缓存策略](docs/cache.md) ·
            [BGE 嵌入](docs/embeddings.md)
            """
        )

    return interface


def main() -> None:
    print("🚀 启动 Gradio 演示界面...")
    print(f"📡 后端 API: {API_BASE_URL}")
    interface = create_gradio_interface()
    interface.launch(server_name="0.0.0.0", server_port=7861, share=False, show_error=True)


if __name__ == "__main__":
    main()
