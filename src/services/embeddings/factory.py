from typing import Optional

from src.config import Settings, get_settings

from .jina_client import JinaEmbeddingsClient

#从配置里读取 Jina API Key 和地址，
#自动创建并返回一个可用的 JinaEmbeddingsClient 向量客户端。
def make_embeddings_service(settings: Optional[Settings] = None) -> JinaEmbeddingsClient:
    if settings is None:
        settings = get_settings()

    api_key = settings.jina_api_key
    base_url = settings.jina_base_url

    return JinaEmbeddingsClient(api_key=api_key, base_url=base_url)


def make_embeddings_client(settings: Optional[Settings] = None) -> JinaEmbeddingsClient:
    if settings is None:
        settings = get_settings()

    api_key = settings.jina_api_key
    base_url = settings.jina_base_url

    return JinaEmbeddingsClient(api_key=api_key, base_url=base_url)
