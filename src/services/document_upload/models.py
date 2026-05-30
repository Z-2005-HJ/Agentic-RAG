from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadParserType(str, Enum):
    DOCLING = "docling"
    TXT = "txt"
    MARKDOWN = "markdown"
    DOCX = "docx"
    EXCEL = "excel"


class ParsedUploadDocument(BaseModel):
    """Structured output from parsing a user-uploaded file (stage 1 — no DB/OpenSearch yet)."""

    raw_text: str = Field(..., description="Full extracted plain text")
    sections: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional section list with title/content keys",
    )
    parser_used: UploadParserType = Field(..., description="Parser that produced the content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Parser-specific metadata")
    original_filename: str = Field(..., description="Original uploaded filename")
    file_extension: str = Field(..., description="Normalized lowercase extension, e.g. .pdf")
    title_hint: str = Field(..., description="Suggested title derived from filename or document properties")


class UploadIngestStatus(str, Enum):
    INDEXED = "indexed"
    PARTIAL = "partial"
    FAILED = "failed"


class UploadIngestResult(BaseModel):
    document_id: UUID
    arxiv_id: str
    title: str
    chunks_created: int = 0
    chunks_indexed: int = 0
    embeddings_generated: int = 0
    parser_used: str
    status: UploadIngestStatus
    message: Optional[str] = None
    original_filename: str
