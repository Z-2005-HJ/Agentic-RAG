import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.config import get_settings
from src.db.factory import make_database
from src.routers import agentic_ask, hybrid_search, ping
from src.routers.ask import ask_router, stream_router
from src.services.arxiv.factory import make_arxiv_client
from src.services.cache.factory import make_cache_client
from src.services.embeddings.factory import make_embeddings_service
from src.services.langfuse.factory import make_langfuse_tracer
from src.services.ollama.factory import make_ollama_client
from src.services.opensearch.factory import make_opensearch_client
from src.services.pdf_parser.factory import make_pdf_parser_service
from src.services.telegram.factory import make_telegram_service

logging.basicConfig(
    level=logging.INFO,
    #设置日志为最低输出级别为info，低于info的日志不会输出
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #发生的时间+所属模块的名字+日志级别+具体内容
)
logger = logging.getLogger(__name__)
#会创建一个模块级别的日志器，命名由系统自动命名


@asynccontextmanager
#异步上下文管理器，启动时执行yield之前的代码，关闭时执行yield之后的代码
async def lifespan(app: FastAPI):
#lifespan用来管理应用启动和关闭生命周期的函数
    logger.info("Starting RAG API...")

    settings = get_settings()
    app.state.settings = settings

    database = make_database()
    app.state.database = database
    logger.info("Database connected")

    #初始化 OpenSearch 检索客户端
    opensearch_client = make_opensearch_client()
    app.state.opensearch_client = opensearch_client

    # Verify OpenSearch connectivity and create index if needed  # 检查连通性并按需创建索引
    if opensearch_client.health_check():
        logger.info("OpenSearch connected successfully")

        # Setup hybrid index (supports all search types)  # 创建/准备混合检索索引（覆盖多种检索模式）
        setup_results = opensearch_client.setup_indices(force=False)
        if setup_results.get("hybrid_index"):
            logger.info("Hybrid index created")
        else:
            logger.info("Hybrid index already exists")

        # Get simple statistics  # 获取索引文档数量等简单统计
        try:
            stats = opensearch_client.client.count(index=opensearch_client.index_name)
            logger.info(f"OpenSearch ready: {stats['count']} documents indexed")
        except Exception:
            logger.info("OpenSearch index ready (stats unavailable)")
    else:
        logger.warning("OpenSearch connection failed - search features will be limited")

    # Initialize other services (kept for future endpoints and notebook demos)  # 初始化其余服务（供接口与 notebook 演示）
    app.state.arxiv_client = make_arxiv_client()
    app.state.pdf_parser = make_pdf_parser_service()
    app.state.embeddings_service = make_embeddings_service()
    app.state.ollama_client = make_ollama_client()
    app.state.langfuse_tracer = make_langfuse_tracer()
    app.state.cache_client = make_cache_client(settings)
    logger.info("Services initialized: arXiv API client, PDF parser, OpenSearch, Embeddings, Ollama, Langfuse, Cache")

    # Initialize Telegram bot (Week 7)  # 初始化 Telegram 机器人（第 7 周；未配置则跳过）
    telegram_service = make_telegram_service(
        opensearch_client=app.state.opensearch_client,
        embeddings_client=app.state.embeddings_service,
        ollama_client=app.state.ollama_client,
        cache_client=app.state.cache_client,
        langfuse_tracer=app.state.langfuse_tracer,
    )

    if telegram_service:
        app.state.telegram_service = telegram_service
        try:
            await telegram_service.start()
            logger.info("Telegram bot started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
    else:
        logger.info("Telegram bot not configured - skipping initialization")

    logger.info("API ready")
    yield

    # Cleanup  # 关闭阶段：停止 Telegram、释放数据库等
    if hasattr(app.state, "telegram_service") and app.state.telegram_service:
        await app.state.telegram_service.stop()
        logger.info("Telegram bot stopped")

    database.teardown()
    logger.info("API shutdown complete")


app = FastAPI(
    title="arXiv Paper Curator API",
    description="Personal arXiv CS.AI paper curator with RAG capabilities",
    version=os.getenv("APP_VERSION", "0.1.0"),
    lifespan=lifespan,
)

# Include routers  # 注册路由：健康检查、混合检索、问答/流式、智能体问答
app.include_router(ping.router, prefix="/api/v1")  # Health check endpoint  # 健康检查
app.include_router(hybrid_search.router, prefix="/api/v1")  # Search chunks with BM25/hybrid  # BM25/混合检索分块
app.include_router(ask_router, prefix="/api/v1")  # RAG question answering with LLM  # 标准 RAG 问答
app.include_router(stream_router, prefix="/api/v1")  # Streaming RAG responses  # 流式 RAG
app.include_router(agentic_ask.router)  # Agentic RAG with intelligent retrieval  # LangGraph 智能体 RAG


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
