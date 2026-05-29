# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；中文为补充释义。
"""Shared fixtures for agentic RAG unit tests."""

from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.services.agents.config import GraphConfig


@pytest.fixture
def mock_opensearch_client():
    client = Mock()
    client.search_unified = Mock(return_value={"hits": [], "total": 0})
    return client


@pytest.fixture
def mock_jina_embeddings_client():
    client = Mock()
    client.embed_query = AsyncMock(return_value=[0.1] * 1024)
    client.embed_passages = AsyncMock(return_value=[[0.1] * 1024])
    return client


@pytest.fixture
def mock_ollama_client():
    client = Mock()
    client.get_langchain_model = Mock(return_value=Mock())
    client.generate = AsyncMock(return_value={"response": "test"})
    return client


@pytest.fixture
def test_context(mock_opensearch_client, mock_ollama_client, mock_jina_embeddings_client):
    from src.services.agents.context import Context

    return Context(
        ollama_client=mock_ollama_client,
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
        langfuse_tracer=None,
        langfuse_enabled=False,
        model_name="llama3.2:1b",
        temperature=0.0,
        top_k=3,
        max_retrieval_attempts=2,
        guardrail_threshold=60,
    )


@pytest.fixture
def sample_human_message():
    return HumanMessage(content="What is machine learning?")


@pytest.fixture
def sample_ai_message():
    return AIMessage(content="Machine learning is a subset of AI.")


@pytest.fixture
def sample_tool_message():
    return ToolMessage(
        content="Transformers are neural network architectures for sequence modeling.",
        tool_call_id="call_1",
    )
