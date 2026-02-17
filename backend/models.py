from pydantic import BaseModel
from typing import List, Optional

class Citation(BaseModel):
    act: str
    section: str
    summary: str
    url: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    language: str = "en"

class QueryResponse(BaseModel):
    domain: str
    relevant_laws: List[str]
    explanation: str
    general_guidance: str
    confidence: str
    disclaimer: str
    citations: List[Citation]
