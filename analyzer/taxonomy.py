from pipeline.models import FailureCategory


FAILURE_DESCRIPTIONS = {
    FailureCategory.EXTRACTION_HALLUCINATION: {
        "label": "Extraction Hallucination",
        "description": "The LLM extracted entities that do not exist in the source document.",
        "severity": "high",
        "suggestion": "Add strict no-hallucination constraints and Grounding checks.",
    },
    FailureCategory.MISCLASSIFICATION: {
        "label": "Misclassification",
        "description": "Document was classified into the wrong type (e.g. invoice classified as contract).",
        "severity": "high",
        "suggestion": "Provide more diverse classification examples in few-shot prompts.",
    },
    FailureCategory.PROPAGATION_ERROR: {
        "label": "Propagation Error",
        "description": "A previous step produced correct output, but this step misinterpreted it.",
        "severity": "medium",
        "suggestion": "Improve step interface contracts and add validation between steps.",
    },
    FailureCategory.PROMPT_FAILURE: {
        "label": "Prompt Failure",
        "description": "The LLM ignored or partially followed the system instructions.",
        "severity": "medium",
        "suggestion": "Simplify prompts, add output format examples, reduce ambiguity.",
    },
    FailureCategory.CONTEXT_LOSS: {
        "label": "Context Loss",
        "description": "Important information from earlier steps was dropped or forgotten.",
        "severity": "high",
        "suggestion": "Explicitly pass key context between steps; truncate less aggressively.",
    },
    FailureCategory.UNKNOWN: {
        "label": "Unknown",
        "description": "Failure type could not be automatically categorized.",
        "severity": "low",
        "suggestion": "Review manually and add to training data.",
    },
}


def get_failure_info(category: str) -> dict:
    try:
        cat = FailureCategory(category)
        return FAILURE_DESCRIPTIONS.get(cat, FAILURE_DESCRIPTIONS[FailureCategory.UNKNOWN])
    except ValueError:
        return FAILURE_DESCRIPTIONS[FailureCategory.UNKNOWN]


def format_evidence_chain(evidence: list[dict]) -> str:
    lines = []
    for i, entry in enumerate(evidence):
        lines.append(f"--- Step {i + 1}: {entry.get('step', 'unknown')} ---")
        lines.append(f"  Score: {entry.get('score', 'N/A')}")
        issues = entry.get("issues", [])
        if issues:
            lines.append(f"  Issues: {'; '.join(issues)}")
        lines.append("")
    return "\n".join(lines)
