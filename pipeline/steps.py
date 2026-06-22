from .models import (
    Document, ExtractedEntities, ExtractedEntity,
    Classification, Summary, DocumentType, StepOutput,
)
from .llm_client import LLMClient


def intake_step(raw_text: str, source: str = "") -> StepOutput:
    doc = Document(text=raw_text, source=source)
    return StepOutput(
        result=doc.model_dump(),
        prompt="",
        raw_response="",
        confidence=1.0,
        token_count=0,
    )


def extraction_step(doc: Document, llm: LLMClient) -> StepOutput:
    system_prompt = (
        "You are a precise document entity extractor. "
        "Extract all named entities (names, dates, monetary amounts, key terms, IDs) from the document. "
        "Return a JSON object with:\n"
        "- entities: list of {name, value, confidence (1-5), source_text}\n"
        "- extraction_confidence: your overall confidence (1-5)\n\n"
        "Rules:\n"
        "1. ONLY extract entities that explicitly appear in the text.\n"
        "2. If a date or amount is ambiguous, note the ambiguity in source_text.\n"
        "3. NEVER make up or hallucinate entities.\n"
        "4. If no entities are found, return an empty entities list.\n"
        "5. Return valid JSON only, no markdown formatting."
    )

    user_prompt = f"Extract all entities from this document:\n\n{doc.text}"
    response = llm.call_structured(system_prompt, user_prompt)

    parsed = response.get("parsed", {})
    entities_data = parsed.get("entities", []) if isinstance(parsed, dict) else []
    extraction_confidence = parsed.get("extraction_confidence", 3) if isinstance(parsed, dict) else 3

    entities = []
    for ent in entities_data:
        if isinstance(ent, dict):
            entities.append(ExtractedEntity(
                name=ent.get("name", "unknown"),
                value=ent.get("value", ""),
                confidence=ent.get("confidence", 3),
                source_text=ent.get("source_text", ""),
            ))

    result = ExtractedEntities(
        entities=entities,
        raw_text=doc.text,
        extraction_confidence=extraction_confidence,
    )

    return StepOutput(
        result=result.model_dump(),
        prompt=f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}",
        raw_response=response["content"],
        confidence=extraction_confidence / 5.0,
        token_count=response["usage"]["total_tokens"],
        latency_ms=response["latency_ms"],
    )


def classification_step(entities: ExtractedEntities, llm: LLMClient) -> StepOutput:
    system_prompt = (
        "You are a document classifier. Based on the extracted entities and content, "
        "classify the document into exactly one of these types:\n"
        "- contract: Legal agreements, terms of service, NDAs\n"
        "- invoice: Bills, receipts, payment requests\n"
        "- report: Analysis documents, status reports, research\n"
        "- correspondence: Letters, emails, memos\n"
        "- unknown: Cannot determine\n\n"
        "Return JSON with:\n"
        "- document_type: string (one of the above)\n"
        "- confidence_score: integer 1-5\n"
        "- reasoning: brief explanation\n\n"
        "Return valid JSON only."
    )

    user_prompt = (
        f"Classify this document. Entities found:\n"
        f"{[e.model_dump() for e in entities.entities]}\n\n"
        f"Raw text excerpt:\n{entities.raw_text[:2000]}"
    )

    response = llm.call_structured(system_prompt, user_prompt)
    parsed = response.get("parsed", {})
    if not isinstance(parsed, dict):
        parsed = {}

    doc_type_str = parsed.get("document_type", "unknown")
    try:
        doc_type = DocumentType(doc_type_str)
    except ValueError:
        doc_type = DocumentType.UNKNOWN

    result = Classification(
        document_type=doc_type,
        confidence_score=parsed.get("confidence_score", 3),
        reasoning=parsed.get("reasoning", ""),
    )

    return StepOutput(
        result=result.model_dump(),
        prompt=f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}",
        raw_response=response["content"],
        confidence=result.confidence_score / 5.0,
        token_count=response["usage"]["total_tokens"],
        latency_ms=response["latency_ms"],
    )


def summarization_step(
    doc_type: Classification,
    entities: ExtractedEntities,
    original_doc: Document,
    llm: LLMClient,
) -> StepOutput:
    type_name = doc_type.document_type.value

    if doc_type.document_type == DocumentType.INVOICE:
        summary_instruction = (
            "Generate an invoice summary with:\n"
            "- total_amount (extract or note missing)\n"
            "- invoice_date\n"
            "- vendor_name\n"
            "- line_items\n"
            "- payment_terms\n"
            "- key_points: list of important details\n"
            "- confidence: integer 1-5\n"
            "- summary_text: narrative summary"
        )
    elif doc_type.document_type == DocumentType.CONTRACT:
        summary_instruction = (
            "Generate a contract summary with:\n"
            "- parties: list of involved parties\n"
            "- effective_date\n"
            "- key_obligations: list\n"
            "- termination_clause: summary\n"
            "- key_points: list of important terms\n"
            "- confidence: integer 1-5\n"
            "- summary_text: narrative summary"
        )
    elif doc_type.document_type == DocumentType.REPORT:
        summary_instruction = (
            "Generate a report summary with:\n"
            "- title\n"
            "- author\n"
            "- date\n"
            "- key_findings: list\n"
            "- key_points: list of main takeaways\n"
            "- confidence: integer 1-5\n"
            "- summary_text: narrative summary"
        )
    else:
        summary_instruction = (
            "Generate a correspondence summary with:\n"
            "- sender\n"
            "- recipient\n"
            "- date\n"
            "- subject\n"
            "- key_points: list of main points\n"
            "- confidence: integer 1-5\n"
            "- summary_text: narrative summary"
        )

    system_prompt = (
        f"You are a document summarizer specializing in {type_name}s.\n"
        f"{summary_instruction}\n\n"
        "Return valid JSON only."
    )

    user_prompt = (
        f"Summarize this {type_name}:\n\n"
        f"Full text:\n{original_doc.text}\n\n"
        f"Entities extracted:\n{[e.model_dump() for e in entities.entities]}"
    )

    response = llm.call_structured(system_prompt, user_prompt)
    parsed = response.get("parsed", {})
    if not isinstance(parsed, dict):
        parsed = {}

    summary_text = parsed.get("summary_text", "")
    key_points = parsed.get("key_points", [])
    if isinstance(key_points, list):
        key_points = [str(kp) for kp in key_points]
    else:
        key_points = [str(key_points)]

    financial = parsed.get("financial_summary", parsed.get("total_amount", None))
    if financial is not None and not isinstance(financial, dict):
        financial = {"total_amount": financial}

    confidence = parsed.get("confidence", 3)

    result = Summary(
        document_type=doc_type.document_type,
        summary_text=summary_text,
        key_points=key_points,
        financial_summary=financial,
        confidence=confidence,
    )

    return StepOutput(
        result=result.model_dump(),
        prompt=f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}",
        raw_response=response["content"],
        confidence=confidence / 5.0,
        token_count=response["usage"]["total_tokens"],
        latency_ms=response["latency_ms"],
    )
