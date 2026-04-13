# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；本文件若含中文，均为补充释义而非替换原文。
from functools import lru_cache

from src.config import get_settings
from src.services.langfuse.client import LangfuseTracer


@lru_cache(maxsize=1)
def make_langfuse_tracer() -> LangfuseTracer:
    """
    Create and return a singleton Langfuse tracer instance.

    Returns:
        LangfuseTracer: Configured Langfuse tracer
    """
    settings = get_settings()
    return LangfuseTracer(settings)
