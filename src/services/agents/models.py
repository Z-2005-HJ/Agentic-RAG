from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

#用户提问的安全校验评分结果，判断问题是否合规、违规等
class GuardrailScoring(BaseModel):
    score: int = Field(ge=0, le=100, description="Relevance score between 0 and 100")
    reason: str = Field(description="Brief reason for the score")

#判断检索回来的论文是否有用，告诉系统要不要用这篇论文来生成答案
class GradeDocuments(BaseModel):
    binary_score: Literal["yes", "no"] = Field(description="Document relevance: 'yes' or 'no'")
    reasoning: str = Field(default="", description="Explanation for the decision")

#一条论文来源信息，把论文的信息返回给前端
class SourceItem(BaseModel):
    arxiv_id: str = Field(description="arXiv paper ID")
    title: str = Field(description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    url: str = Field(description="Link to paper")
    relevance_score: float = Field(default=0.0, description="Relevance score from search")

    def to_dict(self) -> Dict[str, Any]:
        #把对象转为字典
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "url": self.url,
            "relevance_score": self.relevance_score,
        }

#工具调用返回的结果包，智能体调用工具之后把工具、结果元数据打包，让系统知道谁在干活
class ToolArtefact(BaseModel):
    tool_name: str = Field(description="Name of the tool")
    tool_call_id: str = Field(description="Unique tool call ID")
    content: Any = Field(description="Tool result content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

#智能体路线决策，决定智能体下一步做什么，是智能体的大脑决策
class RoutingDecision(BaseModel):
    route: Literal["retrieve", "out_of_scope", "generate_answer", "rewrite_query"] = Field(
        description="Next node to route to"
    )
    reason: str = Field(default="", description="Reason for routing decision")

#文档评分详细结果
class GradingResult(BaseModel):
    document_id: str = Field(description="Document identifier")
    is_relevant: bool = Field(description="Relevance flag")
    score: float = Field(default=0.0, description="Relevance score")
    reasoning: str = Field(default="", description="Grading reasoning")

#记录智能体的思考步骤
class ReasoningStep(BaseModel):
    step_name: str = Field(description="Name of the reasoning step")
    description: str = Field(description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Step metadata")
