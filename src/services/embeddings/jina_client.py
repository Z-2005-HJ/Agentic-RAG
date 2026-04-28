'''
异步Jina向量模型客户端，专门负责把文本转换成向量（Embedding）
embed_passages把论文 / 文本片段转成向量
embed_query把用户问题转成向量
'''
import logging
from typing import List

import httpx
from src.schemas.embeddings.jina import JinaEmbeddingRequest, JinaEmbeddingResponse

logger = logging.getLogger(__name__)


class JinaEmbeddingsClient:
    #把连接远程API所需的全部信息准备好，创建可用的异步HTTP客户端。
    def __init__(self, api_key: str, base_url: str = "https://api.jina.ai/v1"):
        #必须传入jina API key，base_url默认为jina的官方接口地址
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        #请求头，发送HTTP请求
        self.client = httpx.AsyncClient(timeout=30.0)
        #创建异步HTTP客户端
        logger.info("Jina embeddings client initialized")

    #把一批文本批量转换成向量，存入Opensearch用于检索
    async def embed_passages(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        embeddings = []
        #创建空列表，用来存放所有最终向量

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            #批量处理
            request_data = JinaEmbeddingRequest(
                model="jina-embeddings-v3", task="retrieval.passage", dimensions=1024, input=batch
            )
            #构造请求体
            try:
                response = await self.client.post(
                    f"{self.base_url}/embeddings", headers=self.headers, json=request_data.model_dump()
                )
                #发送异步 POST 请求，地址：/embeddings，然后带上请求头API key
                response.raise_for_status()
                #判断HTTP状态码

                result = JinaEmbeddingResponse(**response.json())
                batch_embeddings = [item["embedding"] for item in result.data]
                embeddings.extend(batch_embeddings)
                #把最终的向量都加入总列表

                logger.debug(f"Embedded batch of {len(batch)} passages")

            except httpx.HTTPError as e:
                logger.error(f"Error embedding passages: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in embed_passages: {e}")
                raise

        logger.info(f"Successfully embedded {len(texts)} passages")
        return embeddings

    #异步将用户问题转成向量
    async def embed_query(self, query: str) -> List[float]:
        request_data = JinaEmbeddingRequest(model="jina-embeddings-v3", task="retrieval.query", dimensions=1024, input=[query])

        try:
            response = await self.client.post(f"{self.base_url}/embeddings", headers=self.headers, json=request_data.model_dump())
            response.raise_for_status()

            result = JinaEmbeddingResponse(**response.json())
            embedding = result.data[0]["embedding"]

            logger.debug(f"Embedded query: '{query[:50]}...'")
            return embedding

        except httpx.HTTPError as e:
            logger.error(f"Error embedding query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in embed_query: {e}")
            raise

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
