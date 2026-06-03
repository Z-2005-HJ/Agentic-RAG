#!/usr/bin/env python3
"""
批量评估标准 RAG（/ask）与 Agentic RAG（/ask-agentic），对比固定问题集表现。

用法：
  uv run python scripts/eval_rag.py
  uv run python scripts/eval_rag.py --base-url http://localhost:8000 --top-k 3
  uv run python scripts/eval_rag.py --questions scripts/eval_questions.jsonl --output results.csv

输出 CSV 可在表格中人工打分（1-5），列包括：
  query, mode, status_code, latency_ms, answer, sources, chunks_used, search_mode,
  retrieval_attempts, reasoning_steps, error
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DEFAULT_QUESTIONS = Path(__file__).parent / "eval_questions.jsonl"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "eval_results"


def load_questions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Question file not found: {path}")

    questions: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            item = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_no} of {path}: {exc}") from exc
        if "query" not in item:
            raise ValueError(f"Missing 'query' on line {line_no} of {path}")
        questions.append(item)
    return questions


async def call_endpoint(
    client: httpx.AsyncClient,
    path: str,
    payload: dict[str, Any],
) -> tuple[int, dict[str, Any] | None, float, str | None]:
    started = time.perf_counter()
    try:
        response = await client.post(path, json=payload)
        latency_ms = (time.perf_counter() - started) * 1000
        if response.status_code == 200:
            return response.status_code, response.json(), latency_ms, None
        return response.status_code, None, latency_ms, response.text
    except httpx.HTTPError as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        return 0, None, latency_ms, str(exc)


def row_from_response(
    query: str,
    mode: str,
    status_code: int,
    latency_ms: float,
    data: dict[str, Any] | None,
    error: str | None,
    notes: str = "",
) -> dict[str, Any]:
    answer = ""
    sources = ""
    chunks_used = ""
    search_mode = ""
    retrieval_attempts = ""
    reasoning_steps = ""

    if data:
        answer = data.get("answer", "")
        sources_list = data.get("sources", [])
        sources = " | ".join(sources_list) if isinstance(sources_list, list) else str(sources_list)
        chunks_used = data.get("chunks_used", "")
        search_mode = data.get("search_mode", "")
        retrieval_attempts = data.get("retrieval_attempts", "")
        steps = data.get("reasoning_steps", [])
        if isinstance(steps, list):
            reasoning_steps = " | ".join(steps)

    return {
        "query": query,
        "notes": notes,
        "mode": mode,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 1),
        "answer": answer,
        "sources": sources,
        "chunks_used": chunks_used,
        "search_mode": search_mode,
        "retrieval_attempts": retrieval_attempts,
        "reasoning_steps": reasoning_steps,
        "error": error or "",
        "manual_score_1_to_5": "",
        "manual_comment": "",
    }


async def run_eval(args: argparse.Namespace) -> Path:
    questions = load_questions(args.questions)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = args.output or (DEFAULT_OUTPUT_DIR / f"eval_{timestamp}.csv")

    base_payload = {
        "top_k": args.top_k,
        "use_hybrid": args.use_hybrid,
        "model": args.model,
    }
    if args.categories:
        base_payload["categories"] = args.categories

    rows: list[dict[str, Any]] = []

    async with httpx.AsyncClient(base_url=args.base_url, timeout=args.timeout) as client:
        for item in questions:
            query = item["query"]
            notes = item.get("notes", "")
            payload = {"query": query, **base_payload}

            if not args.agentic_only:
                status, data, latency, error = await call_endpoint(client, "/api/v1/ask", payload)
                rows.append(row_from_response(query, "standard", status, latency, data, error, notes))

            if not args.standard_only:
                status, data, latency, error = await call_endpoint(client, "/api/v1/ask-agentic", payload)
                rows.append(row_from_response(query, "agentic", status, latency, data, error, notes))

    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="评估 RAG 接口并导出 CSV 供人工打分。")
    parser.add_argument("--base-url", default="http://localhost:8000", help="FastAPI base URL")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS, help="JSONL question file")
    parser.add_argument("--output", type=Path, default=None, help="Output CSV path")
    parser.add_argument("--model", default="deepseek-r1:7b", help="Ollama 模型名称")
    parser.add_argument("--top-k", type=int, default=3, help="Retrieval top_k")
    parser.add_argument("--use-hybrid", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--categories", nargs="*", default=None, help="Optional arXiv category filter")
    parser.add_argument("--timeout", type=float, default=300.0, help="HTTP timeout seconds")
    parser.add_argument("--standard-only", action="store_true", help="Only call /ask")
    parser.add_argument("--agentic-only", action="store_true", help="Only call /ask-agentic")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_path = asyncio.run(run_eval(args))
    except (FileNotFoundError, ValueError, httpx.HTTPError) as exc:
        print(f"Eval failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    print("Open the CSV and fill manual_score_1_to_5 / manual_comment for each row.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
