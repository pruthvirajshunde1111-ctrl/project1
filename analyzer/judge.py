from pipeline.models import FailureCategory, TraceStatus
from tracing.trace import Trace, Span, SpanStatus
from pipeline.llm_client import LLMClient


class TraceJudge:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def diagnose(self, trace: Trace) -> dict:
        spans = trace.spans
        if len(spans) < 2:
            return {
                "root_cause_step": None,
                "failure_category": FailureCategory.UNKNOWN.value,
                "explanation": "Trace has insufficient spans for diagnosis.",
                "confidence": 0.0,
                "evidence_chain": [],
            }

        scores = []
        for span in spans[1:]:
            if not span.input_data or not span.output_data:
                scores.append({"step": span.step_name, "score": 5, "reasoning": "Skipped (no data)", "issues": []})
                continue

            result = self._judge_span(span)
            scores.append(result)

        failing = [s for s in scores if s.get("score", 5) < 3]
        if not failing:
            return {
                "root_cause_step": None,
                "failure_category": FailureCategory.UNKNOWN.value,
                "explanation": "All steps appear reasonable. Output may be acceptable.",
                "confidence": trace.final_score,
                "evidence_chain": scores,
            }

        root = failing[0]
        root_index = next(i for i, s in enumerate(scores) if s["step"] == root["step"])

        evidence_chain = []
        for i in range(max(0, root_index - 1), min(len(spans), root_index + 3)):
            span = spans[i]
            evidence_chain.append({
                "step": span.step_name,
                "input": span.input_data,
                "output": span.output_data,
                "score": scores[i]["score"] if i < len(scores) else None,
                "issues": scores[i].get("issues", []) if i < len(scores) else [],
            })

        category = self._categorize_failure(root, trace)

        return {
            "root_cause_step": root["step"],
            "failure_category": category,
            "explanation": root.get("reasoning", "Quality drop detected."),
            "confidence": round(1.0 - (root["score"] / 5.0), 2),
            "evidence_chain": evidence_chain,
        }

    def _judge_span(self, span: Span) -> dict:
        if span.status == SpanStatus.FAILURE:
            return {
                "step": span.step_name,
                "score": 1,
                "reasoning": f"Step failed with error: {span.error}",
                "issues": [f"Exception: {span.error}"],
            }

        system_prompt = (
            "You are a quality judge for AI pipeline steps. "
            "Given the step name, input, and output, evaluate whether the output is a "
            "reasonable transformation of the input.\n\n"
            "Return JSON with:\n"
            "- score: integer 1-5 (5=perfect, 3=acceptable, 1=completely wrong)\n"
            "- reasoning: brief explanation\n"
            "- issues: list of specific problems (empty if none)\n\n"
            "Return valid JSON only."
        )

        user_prompt = (
            f"Step name: {span.step_name}\n\n"
            f"Input:\n{span.input_data}\n\n"
            f"Output:\n{span.output_data}\n\n"
            f"Confidence reported by step: {span.confidence}\n\n"
            "Evaluate the quality of this step's output."
        )

        try:
            response = self.llm.call_structured(system_prompt, user_prompt)
            parsed = response.get("parsed", {})
            if not isinstance(parsed, dict):
                parsed = {}

            score = parsed.get("score", 3)
            issues = parsed.get("issues", [])
            if not isinstance(issues, list):
                issues = [str(issues)]

            return {
                "step": span.step_name,
                "score": score,
                "reasoning": parsed.get("reasoning", ""),
                "issues": issues,
            }
        except Exception as e:
            return {
                "step": span.step_name,
                "score": 3,
                "reasoning": f"Judge evaluation failed: {e}",
                "issues": ["Judge LLM call failed"],
            }

    def _categorize_failure(self, failing_span: dict, trace: Trace) -> str:
        issues = " ".join(failing_span.get("issues", []))
        step = failing_span.get("step", "")

        if step == "extraction" and ("hallucinat" in issues.lower() or "not exist" in issues.lower() or "not present" in issues.lower()):
            return FailureCategory.EXTRACTION_HALLUCINATION.value
        if step == "classification":
            return FailureCategory.MISCLASSIFICATION.value
        if "propagat" in issues.lower() or "previous" in issues.lower():
            return FailureCategory.PROPAGATION_ERROR.value
        if "instruct" in issues.lower() or "ignored" in issues.lower() or "format" in issues.lower():
            return FailureCategory.PROMPT_FAILURE.value
        if "context" in issues.lower() or "inform" in issues.lower() or "detail" in issues.lower():
            return FailureCategory.CONTEXT_LOSS.value

        return FailureCategory.UNKNOWN.value
