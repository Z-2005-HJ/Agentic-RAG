'''
这是一个基于 Redis 的问答结果缓存工具，
专门给 RAG 问答系统做精准命中缓存，让一模一样的问题不再重复计算，直接秒回答案。
_generate_cache_key生成唯一身份证，
find_cached_response用 key 去 Redis查有没有缓存答案，有就直接返回，没有就走正常流程
store_response把 AI 生成的答案存进 Redis，并设置过期时间
'''
import hashlib
import json
import logging
from datetime import timedelta
from typing import Optional

import redis
from src.config import RedisSettings
from src.schemas.api.ask import AskRequest, AskResponse

logger = logging.getLogger(__name__)


class CacheClient:

    def __init__(self, redis_client: redis.Redis, settings: RedisSettings):
        self.redis = redis_client
        self.settings = settings
        self.ttl = timedelta(hours=settings.ttl_hours)

    #根据用户的提问参数，生成一个唯一、固定、不可重复的Redis缓存Key，用来标记这一次问答的缓存
    def _generate_cache_key(self, request: AskRequest) -> str:
        key_data = {
            "query": request.query,
            "model": request.model,
            "top_k": request.top_k,
            "use_hybrid": request.use_hybrid,
            "categories": sorted(request.categories) if request.categories else [],
        }
        #这些参数只要有一个不一样，答案就不一样，就必须单独缓存
        key_string = json.dumps(key_data, sort_keys=True)
        #保证上面那些参数的顺序一样，防止因为顺序不同产生了不同的key
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        #用SHA256哈希，把字符串变成唯一16位编码
        return f"exact_cache:{key_hash}"
        #最终返回缓存key

    #根据用户的请求，去Redis里找有没有缓存好的答案
    async def find_cached_response(self, request: AskRequest) -> Optional[AskResponse]:
        try:
            cache_key = self._generate_cache_key(request)
            #调用_generate_cache_key，根据用户请求生成唯一缓存key

            cached_response = self.redis.get(cache_key)
            #去redis查这个key有没有数据
            if cached_response:
                try:
                    response_data = json.loads(cached_response)
                    #把json字符串变成字典
                    logger.info(f"Cache hit for exact query match")
                    return AskResponse(**response_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to deserialize cached response: {e}")
                    return None

            return None

        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return None

    #把AI生成好的答案存到redis缓存里
    async def store_response(self, request: AskRequest, response: AskResponse) -> bool:
        try:
            cache_key = self._generate_cache_key(request)

            success = self.redis.set(cache_key, response.model_dump_json(), ex=self.ttl)
            #把答案存到redis里面，并且设置过期时间

            if success:
                logger.info(f"Stored response in exact cache with key {cache_key[:16]}...")
                return True
            else:
                logger.warning(f"Failed to store response in cache")
                return False

        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
            return False
