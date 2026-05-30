'''
整个 RAG 系统的大模型调用核心客户端,提供健康检查、模型管理、普通生成、
流式生成、RAG 问答、RAG 流式问答全套能力，自带错误处理、日志、性能监控、结构化解析，
是上层业务直接使用的统一入口。

1.基础接口
    health_check健康检查，list_models获取模型列表
    generate一次性文本生成，generate_stream流式文本生成
2.业务接口
    generate_rag_answer，内部调用generate
    generate_rag_answer_stream，内部调用generate_stream
'''
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from langchain_ollama import ChatOllama
from src.config import Settings
from src.exceptions import OllamaConnectionError, OllamaException, OllamaTimeoutError
from src.schemas.ollama import RAGResponse
from src.services.ollama.prompts import RAGPromptBuilder, ResponseParser

logger = logging.getLogger(__name__)

#与本地 Ollama LLM 服务交互的客户端
class OllamaClient:
    def __init__(self, settings: Settings):
        """使用配置初始化 Ollama 客户端"""
        self.base_url = settings.ollama_host
        self.timeout = httpx.Timeout(float(settings.ollama_timeout))
        self.prompt_builder = RAGPromptBuilder()
        self.response_parser = ResponseParser()

    def get_langchain_model(self, model: str, temperature: float = 0.0) -> ChatOllama:
        """返回供 Agent 图节点使用的 LangChain ChatOllama 实例。"""
        return ChatOllama(
            model=model,
            temperature=temperature,
            base_url=self.base_url,
        )

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 通过版本接口检查服务健康状态
                response = await client.get(f"{self.base_url}/api/version")

                if response.status_code == 200:
                    version_data = response.json()
                    return {
                        "status": "healthy",
                        "message": "Ollama 服务运行正常",
                        "version": version_data.get("version", "unknown"),
                    }
                else:
                    raise OllamaException(f"Ollama 返回状态码 {response.status_code}")

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"无法连接到 Ollama 服务: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama 服务请求超时: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"Ollama 健康检查失败: {str(e)}")

    async def list_models(self) -> List[Dict[str, Any]]:
    #获取本地可用的模型列表
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")

                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
                else:
                    raise OllamaException(f"获取模型列表失败: {response.status_code}")

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"无法连接到 Ollama 服务: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama 服务请求超时: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"获取模型列表出错: {e}")

    #Ollama 客户端的核心文本生成方法，负责调用本地大模型生成回答，
    # 并自动解析 Token、耗时、性能数据，供监控（Langfuse）使用。
    async def generate(self, model: str, prompt: str, stream: bool = False, **kwargs) -> Optional[Dict[str, Any]]:
        """
        使用指定模型生成文本

        参数：
            model: 使用的模型名称
            prompt: 输入提示词
            stream: 是否流式返回
            **kwargs: 其他生成参数

        返回：
            包含 usage_metadata 的响应字典，包含：
                - prompt_tokens: 提示词 token 数量
                - completion_tokens: 生成内容 token 数量
                - total_tokens: 总 token 数量
                - latency_ms: 生成耗时（毫秒）
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {"model": model, "prompt": prompt, "stream": stream, **kwargs}

                logger.info(f"发送请求至 Ollama: model={model}, stream={stream}, 额外参数={kwargs}")
                response = await client.post(f"{self.base_url}/api/generate", json=data)

                if response.status_code == 200:
                    result = response.json()

                    # 解析 Ollama 返回的用量信息，转为通用格式
                    usage_metadata = {}

                    if "prompt_eval_count" in result:
                        usage_metadata["prompt_tokens"] = result.get("prompt_eval_count", 0)
                    if "eval_count" in result:
                        usage_metadata["completion_tokens"] = result.get("eval_count", 0)

                    # 计算总 token
                    if usage_metadata:
                        usage_metadata["total_tokens"] = (
                                usage_metadata.get("prompt_tokens", 0) +
                                usage_metadata.get("completion_tokens", 0)
                        )

                    # 解析时间信息（纳秒转毫秒）
                    if "total_duration" in result:
                        usage_metadata["latency_ms"] = round(result["total_duration"] / 1_000_000, 2)

                    # 附加详细耗时
                    if "prompt_eval_duration" in result:
                        usage_metadata["prompt_eval_duration_ms"] = round(result["prompt_eval_duration"] / 1_000_000, 2)
                    if "eval_duration" in result:
                        usage_metadata["eval_duration_ms"] = round(result["eval_duration"] / 1_000_000, 2)

                    # 将用量信息附加到结果中
                    result["usage_metadata"] = usage_metadata

                    logger.debug(f"用量信息: {usage_metadata}")

                    return result
                else:
                    raise OllamaException(f"文本生成失败: {response.status_code}")

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"无法连接到 Ollama 服务: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama 服务请求超时: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"调用 Ollama 生成文本出错: {e}")

    #流式输出
    async def generate_stream(self, model: str, prompt: str, **kwargs):
        """
        流式生成文本

        参数：
            model: 使用的模型名称
            prompt: 输入提示词
            **kwargs: 其他生成参数

        生成：
            流式响应的 JSON 块
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {"model": model, "prompt": prompt, "stream": True, **kwargs}

                logger.info(f"开始流式生成: model={model}")

                async with client.stream("POST", f"{self.base_url}/api/generate", json=data) as response:
                    if response.status_code != 200:
                        raise OllamaException(f"流式生成失败: {response.status_code}")

                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                yield chunk
                            except json.JSONDecodeError:
                                logger.warning(f"解析流式片段失败: {line}")
                                continue

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"无法连接到 Ollama 服务: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama 服务请求超时: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"流式生成出错: {e}")

    #接收用户问题 + 检索到的文档块 → 自动拼提示词 → 调用大模型
    # → 解析返回结果 → 输出带引用的标准 RAG 回答。
    async def generate_rag_answer(
            self,
            query: str,
            chunks: List[Dict[str, Any]],
            model: str = "llama3.2",
            use_structured_output: bool = False,
    ) -> Dict[str, Any]:
        """
        使用检索到的文本块生成 RAG 回答

        参数：
            query: 用户问题
            chunks: 检索到的文本块（含元数据）
            model: 使用的模型
            use_structured_output: 是否使用结构化输出

        返回：
            包含答案、来源、置信度、引用的字典
        """
        try:
            if use_structured_output:
                # 使用带格式约束的结构化输出
                prompt_data = self.prompt_builder.create_structured_prompt(query, chunks)

                response = await self.generate(
                    model=model,
                    prompt=prompt_data["prompt"],
                    temperature=0.7,
                    top_p=0.9,
                    format=prompt_data["format"],
                )
            else:
                # 普通文本模式
                prompt = self.prompt_builder.create_rag_prompt(query, chunks)

                response = await self.generate(
                    model=model,
                    prompt=prompt,
                    temperature=0.7,
                    top_p=0.9,
                )

            if response and "response" in response:
                answer_text = response["response"]
                logger.debug(f"原始模型响应: {answer_text[:500]}")

                if use_structured_output:
                    # 解析结构化响应
                    parsed_response = self.response_parser.parse_structured_response(answer_text)
                    logger.debug(f"解析后响应: {parsed_response}")
                    return parsed_response
                else:
                    # 普通文本 → 构建简单结构
                    sources = []
                    seen_urls = set()
                    for chunk in chunks:
                        arxiv_id = chunk.get("arxiv_id")
                        if arxiv_id:
                            arxiv_id_clean = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
                            pdf_url = f"https://arxiv.org/pdf/{arxiv_id_clean}.pdf"
                            if pdf_url not in seen_urls:
                                sources.append(pdf_url)
                                seen_urls.add(pdf_url)

                    citations = list(set(chunk.get("arxiv_id") for chunk in chunks if chunk.get("arxiv_id")))

                    return {
                        "answer": answer_text,
                        "sources": sources,
                        "confidence": "medium",
                        "citations": citations[:5],
                    }
            else:
                raise OllamaException("Ollama 未返回有效结果")

        except Exception as e:
            logger.error(f"生成 RAG 回答出错: {e}")
            raise OllamaException(f"生成 RAG 回答失败: {e}")

    #流式输出
    async def generate_rag_answer_stream(
            self,
            query: str,
            chunks: List[Dict[str, Any]],
            model: str = "llama3.2",
    ):
        """
        流式生成 RAG 回答

        参数：
            query: 用户问题
            chunks: 检索到的文本块
            model: 使用的模型

        生成：
            流式响应片段
        """
        try:
            prompt = self.prompt_builder.create_rag_prompt(query, chunks)

            async for chunk in self.generate_stream(
                    model=model,
                    prompt=prompt,
                    temperature=0.7,
                    top_p=0.9,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"流式生成 RAG 回答出错: {e}")
            raise OllamaException(f"流式生成 RAG 回答失败: {e}")