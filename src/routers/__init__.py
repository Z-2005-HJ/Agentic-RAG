# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；本文件若含中文，均为补充释义而非替换原文。
"""Router modules for the RAG API."""

# Import all available routers
from . import ask, hybrid_search, ping

__all__ = ["ask", "ping", "hybrid_search"]
