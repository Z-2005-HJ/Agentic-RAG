import json
import logging
from pathlib import Path
from typing import Iterator

import gradio as gr
import httpx

logger = logging.getLogger(__name__)

# 配置
API_BASE_URL = "http://localhost:8000/api/v1"
DEFAULT_MODEL = "llama3.2:1b"
AVAILABLE_CATEGORIES = ["cs.AI", "cs.LG"]
UPLOAD_FILE_TYPES = [".pdf", ".txt", ".md", ".docx", ".xlsx", ".xls"]


async def stream_response(
    query: str, top_k: int = 3, use_hybrid: bool = True, model: str = DEFAULT_MODEL, categories: str = ""
) -> Iterator[str]:
    """从 RAG API 流式获取回答"""
    if not query.strip():
        yield "Please enter a question."
        return

    # 解析分类过滤
    category_list = [cat.strip() for cat in categories.split(",") if cat.strip()] if categories else None

    # 组装请求体
    payload = {"query": query, "top_k": top_k, "use_hybrid": use_hybrid, "model": model, "categories": category_list}

    try:
        url = f"{API_BASE_URL}/stream"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers={"Accept": "text/plain"}) as response:
                if response.status_code != 200:
                    yield f"Error: API returned status {response.status_code}"
                    return

                current_answer = ""
                sources = []
                chunks_used = 0
                search_mode = ""

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        try:
                            data = json.loads(data_str)

                            # 处理错误
                            if "error" in data:
                                yield f"Error: {data['error']}"
                                return

                            # 处理元数据（来源、检索模式等）
                            if "sources" in data:
                                sources = data["sources"]
                                chunks_used = data.get("chunks_used", 0)
                                search_mode = data.get("search_mode", "unknown")
                                continue

                            # 处理流式文本块
                            if "chunk" in data:
                                current_answer += data["chunk"]
                                # 若有来源信息则拼接到回答下方
                                formatted_response = current_answer
                                if sources or chunks_used:
                                    formatted_response += f"\n\n**Search Info:**\n"
                                    formatted_response += f"- Mode: {search_mode}\n"
                                    formatted_response += f"- Chunks used: {chunks_used}\n"
                                    if sources:
                                        formatted_response += f"- Sources: {len(sources)} papers\n"
                                        for i, source in enumerate(sources[:3], 1):  # 只展示前 3 个来源
                                            formatted_response += f"  {i}. [{source.split('/')[-1]}]({source})\n"
                                        if len(sources) > 3:
                                            formatted_response += f"  ... and {len(sources) - 3} more\n"

                                yield formatted_response

                            # 处理流结束
                            if data.get("done", False):
                                final_answer = data.get("answer", current_answer)
                                if final_answer != current_answer:
                                    current_answer = final_answer

                                # 最终格式化输出
                                formatted_response = current_answer
                                if sources or chunks_used:
                                    formatted_response += f"\n\n**Search Info:**\n"
                                    formatted_response += f"- Mode: {search_mode}\n"
                                    formatted_response += f"- Chunks used: {chunks_used}\n"
                                    if sources:
                                        formatted_response += f"- Sources: {len(sources)} papers\n"
                                        for i, source in enumerate(sources[:3], 1):
                                            formatted_response += f"  {i}. [{source.split('/')[-1]}]({source})\n"
                                        if len(sources) > 3:
                                            formatted_response += f"  ... and {len(sources) - 3} more\n"

                                yield formatted_response
                                break

                        except json.JSONDecodeError:
                            continue  # 跳过格式错误的 JSON 行

    except httpx.RequestError as e:
        yield f"Connection error: {str(e)}\nMake sure the API server is running at {API_BASE_URL}"
    except Exception as e:
        yield f"Unexpected error: {str(e)}"


async def upload_document(file_path: str | None, title: str = "") -> str:
    """通过 FastAPI 上传接口将本地文件写入知识库。"""
    if not file_path:
        return "请先选择要上传的文件。"

    path = Path(file_path)
    if not path.exists():
        return f"文件不存在: {file_path}"

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            with path.open("rb") as file_handle:
                files = {"file": (path.name, file_handle, "application/octet-stream")}
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
        return (
            f"**上传成功**\n\n"
            f"- 标题: {payload.get('title')}\n"
            f"- 文档 ID: `{payload.get('arxiv_id')}`\n"
            f"- 解析器: {payload.get('parser_used')}\n"
            f"- 分块数: {payload.get('chunks_created')}\n"
            f"- 已索引: {payload.get('chunks_indexed')}\n"
            f"- 状态: {payload.get('status')}\n"
            f"- 说明: {payload.get('message', '无')}\n\n"
            f"现在可以在「问答对话」里提问，系统会检索 arXiv 论文和刚上传的文档。"
        )
    except httpx.RequestError as exc:
        return f"连接 API 失败: {exc}\n请确认 FastAPI 已在 http://localhost:8000 运行。"
    except Exception as exc:
        return f"上传过程中发生错误: {exc}"


def create_gradio_interface():
    """创建并配置 Gradio 界面"""

    with gr.Blocks(
        title="arXiv Paper Curator - RAG Chat",
        theme=gr.themes.Soft(),
    ) as interface:
        gr.Markdown(
            """
            # 🔬 arXiv Paper Curator - RAG Chat
            
            Ask questions about indexed arXiv papers and your uploaded documents.
            """
        )

        with gr.Tabs():
            with gr.Tab("💬 问答对话"):
                with gr.Row():
                    with gr.Column(scale=3):
                        query_input = gr.Textbox(
                            label="Your Question",
                            placeholder="What are transformers in machine learning?",
                            lines=2,
                            max_lines=5,
                        )

                    with gr.Column(scale=1):
                        submit_btn = gr.Button("Ask Question", variant="primary", size="lg")

                with gr.Row():
                    with gr.Column():
                        with gr.Accordion("Advanced Options", open=False):
                            top_k = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=3,
                                step=1,
                                label="Number of chunks to retrieve",
                                info="More chunks = more context but slower generation",
                            )

                            use_hybrid = gr.Checkbox(
                                value=True,
                                label="Use hybrid search (BM25 + vector embeddings)",
                                info="Usually better results than keyword-only search",
                            )

                            model_choice = gr.Dropdown(
                                choices=["llama3.2:1b", "llama3.2:3b", "llama3.1:8b", "qwen2.5:7b"],
                                value=DEFAULT_MODEL,
                                label="LLM Model",
                                info="Larger models may give better answers but are slower",
                            )

                            categories = gr.Textbox(
                                label="arXiv Categories (optional)",
                                placeholder="cs.AI, cs.LG, cs.CL",
                                info="Comma-separated. Leave empty for all categories",
                            )

                response_output = gr.Markdown(
                    label="Answer",
                    value="Ask a question to get started!",
                    height=400,
                    elem_classes=["response-markdown"],
                )

                gr.Examples(
                    examples=[
                        ["What are transformers in machine learning?", 3, True, "llama3.2:1b", "cs.AI, cs.LG"],
                        ["How do convolutional neural networks work?", 5, True, "llama3.2:1b", "cs.CV, cs.LG"],
                        ["What is attention mechanism in deep learning?", 4, False, "llama3.2:1b", "cs.AI"],
                        ["Explain reinforcement learning algorithms", 3, True, "llama3.2:1b", "cs.LG, cs.AI"],
                        ["What are the latest developments in NLP?", 5, True, "llama3.2:1b", "cs.CL"],
                    ],
                    inputs=[query_input, top_k, use_hybrid, model_choice, categories],
                )

                submit_btn.click(
                    fn=stream_response,
                    inputs=[query_input, top_k, use_hybrid, model_choice, categories],
                    outputs=[response_output],
                    show_progress=True,
                )

                query_input.submit(
                    fn=stream_response,
                    inputs=[query_input, top_k, use_hybrid, model_choice, categories],
                    outputs=[response_output],
                    show_progress=True,
                )

            with gr.Tab("📤 上传文档"):
                gr.Markdown(
                    """
                    支持 **PDF / TXT / Markdown / DOCX / Excel (.xlsx/.xls)**。
                    上传后会写入 PostgreSQL，并切块索引到 OpenSearch，可在问答里一起检索。
                    """
                )
                upload_file = gr.File(
                    label="选择文件",
                    file_types=UPLOAD_FILE_TYPES,
                    type="filepath",
                )
                upload_title = gr.Textbox(
                    label="标题（可选）",
                    placeholder="例如：课程笔记 / 实验记录",
                )
                upload_btn = gr.Button("开始处理", variant="primary")
                upload_status = gr.Markdown(value="选择文件后点击「开始处理」。")

                upload_btn.click(
                    fn=upload_document,
                    inputs=[upload_file, upload_title],
                    outputs=[upload_status],
                    show_progress=True,
                )

        gr.Markdown(
            """
            ---
            
            **Note**: Make sure the RAG API server is running at `http://localhost:8000` before using this interface.
            
            **Categories**: cs.AI (Artificial Intelligence), cs.LG (Machine Learning), cs.CL (Computational Linguistics), 
            cs.CV (Computer Vision), cs.NE (Neural Networks), stat.ML (Statistics - Machine Learning)
            """
        )

    return interface


def main():
    """Gradio 应用入口"""
    print("🚀 Starting arXiv Paper Curator Gradio Interface...")
    print(f"📡 API Base URL: {API_BASE_URL}")

    interface = create_gradio_interface()

    # 启动 Web 界面
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,  # 避免与默认 7860 端口冲突
        share=False,
        show_error=True,
        quiet=False,
    )


if __name__ == "__main__":
    main()
