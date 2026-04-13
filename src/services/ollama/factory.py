# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；本文件若含中文，均为补充释义而非替换原文。
from functools import lru_cache

from src.config import get_settings
from src.services.ollama.client import OllamaClient


@lru_cache(maxsize=1)
def make_ollama_client() -> OllamaClient:
    """
    Create and return a singleton Ollama client instance.

    Returns:
        OllamaClient: Configured Ollama client
    """
    settings = get_settings()
    return OllamaClient(settings)
