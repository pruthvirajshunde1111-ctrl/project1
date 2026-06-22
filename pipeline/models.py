from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class DocumentType(str, Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    REPORT = "report"
    CORRESPONDENCE = "correspondence"
    UNKNOWN = "unknown"


class Document(BaseModel):
    text: str
    source: str = ""
    metadata: dict[str, Any] = {}


class ExtractedEntity(BaseModel):
    name: str
    value: Any
    confidence: int = Field(ge=1, le=5, default=3)
    source_text: str = ""


class ExtractedEntities(BaseModel):
    entities: list[ExtractedEntity] = []
    raw_text: str = ""
    extraction_confidence: int = Field(ge=1, le=5, default=3)


class Classification(BaseModel):
    document_type: DocumentType
    confidence_score: int = Field(ge=1, le=5, default=3)
    reasoning: str = ""


class Summary(BaseModel):
    document_type: DocumentType
    summary_text: str
    key_points: list[str] = []
    financial_summary: Optional[dict] = None
    confidence: int = Field(ge=1, le=5, default=3)


class SpanStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DEGRADED = "degraded"


class TraceStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DEGRADED = "degraded"


class FailureCategory(str, Enum):
    EXTRACTION_HALLUCINATION = "extraction_hallucination"
    MISCLASSIFICATION = "misclassification"
    PROPAGATION_ERROR = "propagation_error"
    PROMPT_FAILURE = "prompt_failure"
    CONTEXT_LOSS = "context_loss"
    UNKNOWN = "unknown"


@dataclass
class StepOutput:
    result: dict
    prompt: str = ""
    raw_response: str = ""
    confidence: float = 0.0
    token_count: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
