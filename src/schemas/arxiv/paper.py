from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ArxivPaper(BaseModel):
#和前的数据库的paper不一样，那个paper主要是存到数据库给数据库用的
#这个paper主要是用来给接口、数据传输用的

    arxiv_id: str = Field(..., description="arXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract")
    categories: List[str] = Field(..., description="Paper categories")
    published_date: str = Field(..., description="Date published on arXiv (ISO format)")
    pdf_url: str = Field(..., description="URL to PDF")


class PaperBase(BaseModel):
#公共基础模板，别的类可以直接继承他
#ArxivPaper是刚从 arXiv 爬下来的原始数据，date是str类型
#PaperBase是处理干净、准备存数据库的标准数据，date是datetime类型

    arxiv_id: str = Field(..., description="arXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract")
    categories: List[str] = Field(..., description="Paper categories")
    published_date: datetime = Field(..., description="Date published on arXiv")
    pdf_url: str = Field(..., description="URL to PDF")


class PaperCreate(PaperBase):
#存进数据库用的格式

    #获取全文其他内容
    raw_text: Optional[str] = Field(None, description="Full raw text extracted from PDF")
    sections: Optional[List[Dict[str, Any]]] = Field(None, description="List of sections with titles and content")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="List of references if extracted")

    #解析器
    parser_used: Optional[str] = Field(None, description="Which parser was used (DOCLING, etc.)")
    parser_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional parser metadata")
    pdf_processed: Optional[bool] = Field(False, description="Whether PDF was successfully processed")
    pdf_processing_date: Optional[datetime] = Field(None, description="When PDF was processed")


class PaperResponse(PaperBase):
#从数据库查出来之后，最终展示给外界的数据
    id: UUID

    raw_text: Optional[str] = Field(None, description="Full raw text extracted from PDF")
    sections: Optional[List[Dict[str, Any]]] = Field(None, description="List of sections with titles and content")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="List of references if extracted")

    parser_used: Optional[str] = Field(None, description="Which parser was used")
    parser_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional parser metadata")
    pdf_processed: bool = Field(False, description="Whether PDF was successfully processed")
    pdf_processing_date: Optional[datetime] = Field(None, description="When PDF was processed")

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    #这个类让模型可以直接读取前面数据库的paper对象，同时可以被response直接解析

class PaperSearchResponse(BaseModel):
    papers: List[PaperResponse]
    total: int
