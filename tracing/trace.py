import uuid
import time
from datetime import datetime, timezone
from typing import Optional
import contextvars

from pipeline.models import SpanStatus, TraceStatus


current_trace: contextvars.ContextVar[Optional["Trace"]] = contextvars.ContextVar("current_trace", default=None)


class Span:
    def __init__(
        self,
        step_name: str,
        span_id: str | None = None,
    ):
        self.span_id = span_id or str(uuid.uuid4())
        self.step_name = step_name
        self.input_data: dict = {}
        self.output_data: dict = {}
        self.prompt: str = ""
        self.raw_response: str = ""
        self.token_count: int = 0
        self.latency_ms: float = 0.0
        self.confidence: float = 0.0
        self.error: str | None = None
        self.status: SpanStatus = SpanStatus.SUCCESS
        self.start_time: str = datetime.now(timezone.utc).isoformat()
        self.end_time: str = ""

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "step_name": self.step_name,
            "input_data": self._serialize(self.input_data),
            "output_data": self._serialize(self.output_data),
            "prompt": self.prompt,
            "raw_response": self.raw_response,
            "token_count": self.token_count,
            "latency_ms": round(self.latency_ms, 2),
            "confidence": round(self.confidence, 2),
            "error": self.error,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @staticmethod
    def _serialize(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (list, tuple)):
            return [Span._serialize(item) for item in obj]
        if isinstance(obj, dict):
            return {k: Span._serialize(v) for k, v in obj.items()}
        return str(obj)


class Trace:
    def __init__(
        self,
        trace_id: str | None = None,
        source: str = "",
    ):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.timestamp: str = datetime.now(timezone.utc).isoformat()
        self.source: str = source
        self.status: TraceStatus = TraceStatus.SUCCESS
        self.final_score: float = 1.0
        self.spans: list[Span] = []
        self.flagged: bool = False
        self.flag_notes: str = ""
        self.diagnosis: dict | None = None

    def add_span(self, span: Span):
        span.end_time = datetime.now(timezone.utc).isoformat()
        self.spans.append(span)

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "status": self.status.value,
            "final_score": self.final_score,
            "flagged": self.flagged,
            "flag_notes": self.flag_notes,
            "diagnosis": self.diagnosis,
            "spans": [s.to_dict() for s in self.spans],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Trace":
        trace = cls(trace_id=data["trace_id"], source=data.get("source", ""))
        trace.timestamp = data["timestamp"]
        trace.status = TraceStatus(data["status"])
        trace.final_score = data["final_score"]
        trace.flagged = data.get("flagged", False)
        trace.flag_notes = data.get("flag_notes", "")
        trace.diagnosis = data.get("diagnosis")
        for sd in data.get("spans", []):
            span = Span(step_name=sd["step_name"], span_id=sd["span_id"])
            span.input_data = sd.get("input_data", {})
            span.output_data = sd.get("output_data", {})
            span.prompt = sd.get("prompt", "")
            span.raw_response = sd.get("raw_response", "")
            span.token_count = sd.get("token_count", 0)
            span.latency_ms = sd.get("latency_ms", 0.0)
            span.confidence = sd.get("confidence", 0.0)
            span.error = sd.get("error")
            span.status = SpanStatus(sd.get("status", "success"))
            span.start_time = sd.get("start_time", "")
            span.end_time = sd.get("end_time", "")
            trace.add_span(span)
        return trace
