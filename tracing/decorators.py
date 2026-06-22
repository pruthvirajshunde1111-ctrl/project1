import functools
import time
from datetime import datetime, timezone

from .trace import current_trace, Span, SpanStatus
from pipeline.models import StepOutput


def instrument_step(step_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace = current_trace.get()
            span = Span(step_name=step_name)
            span.start_time = datetime.now(timezone.utc).isoformat()
            start = time.time()

            if args:
                span.input_data = _serialize(args[0])

            try:
                step_output = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000
                span.latency_ms = elapsed
                span.end_time = datetime.now(timezone.utc).isoformat()

                if isinstance(step_output, StepOutput):
                    span.output_data = step_output.result
                    span.prompt = step_output.prompt
                    span.raw_response = step_output.raw_response
                    span.confidence = step_output.confidence
                    span.token_count = step_output.token_count
                    span.status = SpanStatus.SUCCESS if not step_output.error else SpanStatus.DEGRADED
                    span.error = step_output.error
                else:
                    span.output_data = _serialize(step_output)
                    span.status = SpanStatus.SUCCESS

                if trace:
                    trace.add_span(span)

                return step_output

            except Exception as e:
                elapsed = (time.time() - start) * 1000
                span.latency_ms = elapsed
                span.end_time = datetime.now(timezone.utc).isoformat()
                span.status = SpanStatus.FAILURE
                span.error = str(e)
                if trace:
                    trace.add_span(span)
                raise

        return wrapper

    return decorator


def _serialize(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return str(obj)
