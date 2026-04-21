# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；本文件若含中文，均为补充释义而非替换原文。
"""Simple, efficient Langfuse tracing utility for RAG pipeline."""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from .client import LangfuseTracer


class RAGTracer:
    """Clean, purpose-built tracer for RAG operations."""

    def __init__(self, tracer: LangfuseTracer):
        self.tracer = tracer

    @contextmanager
    def _safe_span(self, trace, name: str, input_data: Dict[str, Any]):
        """Create a span if tracing API exists; otherwise no-op."""
        span = None
        try:
            if hasattr(self.tracer, "create_span"):
                span = self.tracer.create_span(trace=trace, name=name, input_data=input_data)
        except Exception:
            span = None

        try:
            yield span
        finally:
            if span and hasattr(span, "end"):
                try:
                    span.end()
                except Exception:
                    pass

    @contextmanager
    def trace_request(self, user_id: str, query: str):
        """Main request trace context manager."""
        trace = None
        try:
            if hasattr(self.tracer, "trace_rag_request"):
                with self.tracer.trace_rag_request(
                    query=query, user_id=user_id, session_id=f"session_{user_id}", metadata={"simplified_tracing": True}
                ) as trace:
                    yield trace
            else:
                # Langfuse v3 client wrapper in this repo has no trace_rag_request.
                # Degrade gracefully so tracing cannot break /ask or /stream.
                yield None
        finally:
            if trace and hasattr(self.tracer, "flush"):
                self.tracer.flush()

    @contextmanager
    def trace_embedding(self, trace, query: str):
        """Query embedding operation with timing."""
        start_time = time.time()
        with self._safe_span(trace, "query_embedding", {"query": query, "query_length": len(query)}) as span:
            try:
                yield span
            finally:
                duration = time.time() - start_time
                if span:
                    self.tracer.update_span(
                        span=span, output={"embedding_duration_ms": round(duration * 1000, 2), "success": True}
                    )

    @contextmanager
    def trace_search(self, trace, query: str, top_k: int):
        """Search operation with timing."""
        with self._safe_span(trace, "search_retrieval", {"query": query, "top_k": top_k}) as span:
            yield span

    def end_search(self, span, chunks: List[Dict], arxiv_ids: List[str], total_hits: int):
        """End search span with essential results."""
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "chunks_returned": len(chunks),
                "unique_papers": len(set(arxiv_ids)),
                "total_hits": total_hits,
                "arxiv_ids": list(set(arxiv_ids)),
            },
        )

    @contextmanager
    def trace_prompt_construction(self, trace, chunks: List[Dict]):
        """Prompt building with timing."""
        with self._safe_span(trace, "prompt_construction", {"chunk_count": len(chunks)}) as span:
            yield span

    def end_prompt(self, span, prompt: str):
        """End prompt span with final prompt."""
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "prompt_length": len(prompt),
                # Don't duplicate the full prompt here since it's in llm_generation input
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            },
        )

    @contextmanager
    def trace_generation(self, trace, model: str, prompt: str):
        """LLM generation with timing."""
        with self._safe_span(trace, "llm_generation", {"model": model, "prompt_length": len(prompt), "prompt": prompt}) as span:
            yield span

    def end_generation(self, span, response: str, model: str):
        """End generation span with response."""
        if not span:
            return

        self.tracer.update_span(span=span, output={"response": response, "response_length": len(response), "model_used": model})

    def end_request(self, trace, response: str, total_duration: float):
        """End main request trace."""
        if not trace:
            return

        try:
            trace.update(
                output={"answer": response, "total_duration_seconds": round(total_duration, 3), "response_length": len(response)}
            )
        except Exception:
            # Silently fail - don't break the request for tracing issues
            pass
