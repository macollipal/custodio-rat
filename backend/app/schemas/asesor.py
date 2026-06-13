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


class AsesorStatsResponse(BaseModel):
    total_chunks: int
    total_documents: int
    chunks_por_source: dict
    ultimo_indexado: Optional[datetime] = None
    provider: str
