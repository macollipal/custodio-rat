"""
Schemas Pydantic del módulo Asesor.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AsesorAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="Pregunta del usuario")
    context: Optional[str] = Field(None, max_length=2000, description="Contexto adicional del sistema")


class AsesorSource(BaseModel):
    source: str
    source_type: str
    title: Optional[str] = None
    chunk_index: int
    score: float
    snippet: str


class AsesorAskResponse(BaseModel):
    answer: str
    sources: List[AsesorSource] = []
    provider: str
    embedding_provider: str
    latency_ms: int


class AsesorIndexRequest(BaseModel):
    paths: Optional[List[str]] = Field(None, description="Paths a indexar. Si vacío, procesa todo el corpus.")
    force: bool = Field(False, description="Si true, elimina chunks previos antes de reindexar")


class AsesorIndexResponse(BaseModel):
    indexed: int
    skipped: int
    errors: List[str] = []
    duration_ms: int
    status: Optional[str] = None


class AsesorIndexJobResponse(BaseModel):
    message: str
    job: str = "index_corpus"


class AsesorStatsResponse(BaseModel):
    total_chunks: int
    total_documents: int
    chunks_por_source: dict
    ultimo_indexado: Optional[datetime] = None
    provider: str


class AsesorCorpusDocumentSchema(BaseModel):
    id: int
    object_name: str
    original_filename: str
    content_type: str
    size_bytes: int
    content_hash: str
    title: Optional[str] = None
    source_type: str
    chunks_indexed: int
    status: str
    uploaded_by_id: Optional[int] = None
    uploaded_by_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AsesorUploadResponse(BaseModel):
    doc_id: int
    original_filename: str
    title: str
    source_type: str
    size_bytes: int
    chunks_indexed: int
    indexed: int
    skipped: int


class AsesorDeleteResponse(BaseModel):
    ok: bool
    doc_id: int
    original_filename: str
    chunks_removed: int


class AsesorDocumentsListResponse(BaseModel):
    documents: List[AsesorCorpusDocumentSchema]
    total: int
