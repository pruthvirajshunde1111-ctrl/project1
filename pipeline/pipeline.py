from .models import (
    Document, ExtractedEntities, Classification, Summary,
    StepOutput, DocumentType, TraceStatus, FailureCategory,
)
from .llm_client import LLMClient
from .steps import intake_step, extraction_step, classification_step, summarization_step
from tracing.trace import Trace, Span, current_trace, SpanStatus


class Pipeline:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, raw_text: str, source: str = "") -> Trace:
        trace = Trace(source=source)
        token = current_trace.set(trace)

        span_intake = Span(step_name="intake")
        span_extraction = Span(step_name="extraction")
        span_classification = Span(step_name="classification")
        span_summarization = Span(step_name="summarization")

        avg_conf = 0.0
        all_ok = True

        # Step 1: Intake
        try:
            step_out = intake_step(raw_text, source)
            doc = Document(**step_out.result)
            span_intake.input_data = {"raw_text": raw_text[:500], "source": source}
            span_intake.output_data = step_out.result
            span_intake.status = SpanStatus.SUCCESS
        except Exception as e:
            span_intake.status = SpanStatus.FAILURE
            span_intake.error = f"[{type(e).__name__}] {e}"
            span_intake.input_data = {"raw_text": raw_text[:500], "source": source}
            all_ok = False

        # Step 2: Extraction
        try:
            if all_ok:
                step_out = extraction_step(doc, self.llm)
                entities = ExtractedEntities(**step_out.result)
                _fill_span(span_extraction, step_out, doc.model_dump())
            else:
                span_extraction.status = SpanStatus.FAILURE
                span_extraction.error = "Skipped due to previous step failure"
        except Exception as e:
            span_extraction.status = SpanStatus.FAILURE
            span_extraction.error = f"[{type(e).__name__}] {e}"
            span_extraction.input_data = doc.model_dump() if 'doc' in dir() else {}
            all_ok = False

        # Step 3: Classification
        try:
            if all_ok:
                step_out = classification_step(entities, self.llm)
                classification = Classification(**step_out.result)
                _fill_span(span_classification, step_out, entities.model_dump())
            else:
                span_classification.status = SpanStatus.FAILURE
                span_classification.error = "Skipped due to previous step failure"
        except Exception as e:
            span_classification.status = SpanStatus.FAILURE
            span_classification.error = f"[{type(e).__name__}] {e}"
            if 'entities' in dir():
                span_classification.input_data = entities.model_dump()
            all_ok = False

        # Step 4: Summarization
        try:
            if all_ok:
                step_out = summarization_step(classification, entities, doc, self.llm)
                summary = Summary(**step_out.result)
                _fill_span(span_summarization, step_out, classification.model_dump())
            else:
                span_summarization.status = SpanStatus.FAILURE
                span_summarization.error = "Skipped due to previous step failure"
        except Exception as e:
            span_summarization.status = SpanStatus.FAILURE
            span_summarization.error = f"[{type(e).__name__}] {e}"
            if 'classification' in dir():
                span_summarization.input_data = classification.model_dump()
            all_ok = False

        # Determine overall status
        if all_ok:
            confidences = [
                span_extraction.confidence,
                span_classification.confidence,
                span_summarization.confidence,
            ]
            avg_conf = sum(confidences) / len(confidences) if confidences else 1.0

            if avg_conf < 0.5:
                trace.status = TraceStatus.DEGRADED
            elif span_extraction.error or span_classification.error or span_summarization.error:
                trace.status = TraceStatus.DEGRADED
            else:
                trace.status = TraceStatus.SUCCESS

            trace.final_score = round(avg_conf, 2)
        else:
            trace.status = TraceStatus.FAILURE
            trace.final_score = 0.0

        trace.add_span(span_intake)
        trace.add_span(span_extraction)
        trace.add_span(span_classification)
        trace.add_span(span_summarization)
        current_trace.reset(token)

        return trace


def _fill_span(span: Span, step_out: StepOutput, input_data: dict):
    span.input_data = input_data
    span.output_data = step_out.result
    span.prompt = step_out.prompt
    span.raw_response = step_out.raw_response
    span.confidence = step_out.confidence
    span.token_count = step_out.token_count
    span.latency_ms = step_out.latency_ms
    span.status = SpanStatus.SUCCESS if not step_out.error else SpanStatus.DEGRADED
    span.error = step_out.error
