from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: UUID = Field(..., description="Internal UUID for the uploaded document")
    arxiv_id: str = Field(..., description="Document identifier used in search index (upload-{uuid})")
    title: str = Field(..., description="Stored document title")
    original_filename: str = Field(..., description="Original uploaded filename")
    chunks_created: int = Field(..., description="Number of text chunks created")
    chunks_indexed: int = Field(..., description="Number of chunks indexed in OpenSearch")
    embeddings_generated: int = Field(..., description="Number of embeddings generated")
    parser_used: str = Field(..., description="Parser used to extract text")
    status: Literal["indexed", "partial", "failed"] = Field(..., description="Ingest outcome")
    message: Optional[str] = Field(None, description="Human-readable status message")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "arxiv_id": "upload-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "title": "My Research Notes",
                "original_filename": "notes.pdf",
                "chunks_created": 8,
                "chunks_indexed": 8,
                "embeddings_generated": 8,
                "parser_used": "docling",
                "status": "indexed",
                "message": "Document indexed successfully using parser 'docling'.",
            }
        }
