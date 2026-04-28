from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParserType(str, Enum):
#选择解析器，用docling这个库来解析PDF
    DOCLING = "docling"

class PaperSection(BaseModel):
#章节模型，把PDF解析出来的文本，按章节结构化存储
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    level: int = Field(default=1, description="Section hierarchy level")

class PaperFigure(BaseModel):
#图片模型，用来描述论文里的图片、图表
    caption: str = Field(..., description="Figure caption")
    id: str = Field(..., description="Figure identifier")


class PaperTable(BaseModel):
#表格模型
    caption: str = Field(..., description="Table caption")
    id: str = Field(..., description="Table identifier")


class PdfContent(BaseModel):
#前面的内容会被存储在这里

    sections: List[PaperSection] = Field(default_factory=list, description="Paper sections")
    figures: List[PaperFigure] = Field(default_factory=list, description="Figures")
    tables: List[PaperTable] = Field(default_factory=list, description="Tables")
    raw_text: str = Field(..., description="Full extracted text")
    references: List[str] = Field(default_factory=list, description="References")
    parser_used: ParserType = Field(..., description="Parser used for extraction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Parser metadata")


class ArxivMetadata(BaseModel):
#arxiv元数据

    title: str = Field(..., description="Paper title from arXiv")
    authors: List[str] = Field(..., description="Authors from arXiv")
    abstract: str = Field(..., description="Abstract from arXiv")
    arxiv_id: str = Field(..., description="arXiv identifier")
    categories: List[str] = Field(default_factory=list, description="arXiv categories")
    published_date: str = Field(..., description="Publication date")
    pdf_url: str = Field(..., description="PDF download URL")


class ParsedPaper(BaseModel):
#完整的论文数据模型

    arxiv_metadata: ArxivMetadata = Field(..., description="Metadata from arXiv API")
    pdf_content: Optional[PdfContent] = Field(None, description="Content extracted from PDF")
