from fastapi import APIRouter, HTTPException
from src.dependencies import AgenticRAGDep, LangfuseDep
from src.schemas.api.ask import AgenticAskResponse, AskRequest, FeedbackRequest, FeedbackResponse

# 注册路由统一前缀 /api/v1，分类标签 agentic-rag
router = APIRouter(prefix="/api/v1", tags=["agentic-rag"])

#用户提问接口
@router.post("/ask-agentic", response_model=AgenticAskResponse)
async def ask_agentic(
    request: AskRequest,
    agentic_rag: AgenticRAGDep,
) -> AgenticAskResponse:
    """
    智能体RAG问答接口，具备智能检索与查询优化能力。

    核心能力:
    - 自动判断是否需要执行文献检索
    - 对检索文档做相关性打分
    - 文档无关时自动重写用户问题
    - 输出完整推理步骤，可追溯来源

    智能体自动执行流程:
    1. 校验问题领域，判断是否需要论文检索
    2. 按需检索相关学术文献
    3. 筛选、评估文档匹配度
    4. 内容不匹配则改写查询并重试检索
    5. 结合引用文献生成规范回答

    :param request: 用户提问与请求参数
    :param agentic_rag: 依赖注入的Agentic RAG核心服务
    :returns: 包含答案、文献来源、推理流程的标准化响应
    :raises HTTPException: 业务异常、服务异常统一抛出Http错误
    """
    try:
        result = await agentic_rag.ask(
            query=request.query,
        )

        return AgenticAskResponse(
            query=result["query"],
            answer=result["answer"],
            sources=result.get("sources", []),
            chunks_used=request.top_k,
            search_mode="hybrid" if request.use_hybrid else "bm25",
            reasoning_steps=result.get("reasoning_steps", []),
            retrieval_attempts=result.get("retrieval_attempts", 0),
            trace_id=result.get("trace_id"),
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

#用户反馈打分接口
@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    langfuse_tracer: LangfuseDep,
) -> FeedbackResponse:
    """
    提交用户评价反馈，用于优化RAG回答质量。

    支持对单次问答链路打分、填写备注，
    所有反馈数据持久化至Langfuse监控平台。

    :param request: 反馈参数：追踪ID、评分、备注信息
    :param langfuse_tracer: 依赖注入的Langfuse追踪客户端
    :returns: 反馈提交结果状态
    :raises HTTPException: 追踪服务异常、提交失败时抛出错误
    """
    try:
        if not langfuse_tracer:
            raise HTTPException(
                status_code=503,
                detail="Langfuse tracing is disabled. Cannot submit feedback."
            )

        success = langfuse_tracer.submit_feedback(
            trace_id=request.trace_id,
            score=request.score,
            comment=request.comment,
        )

        if success:
            # 强制刷新缓冲区，确保反馈即时上报
            langfuse_tracer.flush()

            return FeedbackResponse(
                success=True,
                message="Feedback recorded successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to submit feedback to Langfuse"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )