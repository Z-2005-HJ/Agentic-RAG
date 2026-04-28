from typing import Dict, List

from pydantic import BaseModel

#向量化请求体，调用jinaAPI时要传给它的参数格式
class JinaEmbeddingRequest(BaseModel):
    model: str = "jina-embeddings-v3"
    task: str = "retrieval.passage"
    dimensions: int = 1024
    late_chunking: bool = False
    embedding_type: str = "float"
    input: List[str]

#向量返回体，也就是jinaAPI返回的格式
class JinaEmbeddingResponse(BaseModel):
    model: str
    object: str = "list"
    usage: Dict[str, int]
    data: List[Dict]
