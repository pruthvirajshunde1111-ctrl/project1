import json
import os
from typing import Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

from tracing.storage import TraceStorage
from analyzer.judge import TraceJudge
from analyzer.taxonomy import get_failure_info
from .eval_dataset import EvalDataset
from .analytics import AnalyticsEngine
from pipeline.llm_client import LLMClient


_storage: Optional[TraceStorage] = None
_judge: Optional[TraceJudge] = None
_eval_dataset: Optional[EvalDataset] = None
_analytics: Optional[AnalyticsEngine] = None


class FlagRequest(BaseModel):
    trace_id: str
    notes: str = ""


class DiagnosisOverride(BaseModel):
    trace_id: str
    root_cause_step: str
    failure_category: str
    explanation: str
    corrected_output: Optional[dict] = None


class RunPipelineRequest(BaseModel):
    text: str
    source: str = ""


class BatchRunRequest(BaseModel):
    documents: list[dict]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _storage, _judge, _eval_dataset, _analytics
    db_path = os.getenv("DB_PATH", "data/trace_index.db")
    traces_dir = os.getenv("TRACES_DIR", "data/traces")
    eval_dir = os.getenv("EVAL_DIR", "data/eval")

    _storage = TraceStorage(db_path=db_path, traces_dir=traces_dir)
    _eval_dataset = EvalDataset(eval_dir=eval_dir)
    _analytics = AnalyticsEngine(_storage, _eval_dataset)

    try:
        llm = LLMClient()
        _judge = TraceJudge(llm)
    except ValueError:
        _judge = None

    yield


app = FastAPI(title="Failure Forensics API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "ui", "frontend", "dist")

api = APIRouter(prefix="/api")


@api.get("/traces")
def list_traces(limit: int = 100, offset: int = 0):
    if not _storage:
        raise HTTPException(500, "Storage not initialized")
    return {"traces": _storage.list_traces(limit, offset)}


@api.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    if not _storage:
        raise HTTPException(500, "Storage not initialized")
    trace = _storage.load(trace_id)
    if not trace:
        raise HTTPException(404, "Trace not found")
    return trace.to_dict()


@api.post("/traces/{trace_id}/flag")
def flag_trace(trace_id: str, req: FlagRequest):
    if not _storage:
        raise HTTPException(500, "Storage not initialized")

    trace = _storage.load(trace_id)
    if not trace:
        raise HTTPException(404, "Trace not found")

    trace.flagged = True
    trace.flag_notes = req.notes
    _storage.save(trace)

    if _judge:
        diagnosis = _judge.diagnose(trace)
        trace.diagnosis = diagnosis
        _storage.save(trace)

        if _eval_dataset and diagnosis.get("root_cause_step"):
            _eval_dataset.add_case(
                trace_id=trace_id,
                input_text=trace.spans[0].input_data if trace.spans else {},
                failing_step=diagnosis["root_cause_step"],
                bad_output=trace.to_dict(),
                corrected_output={},
                failure_category=diagnosis["failure_category"],
                diagnosis_explanation=diagnosis["explanation"],
            )
    else:
        diagnosis = None

    return {
        "trace_id": trace_id,
        "flagged": True,
        "diagnosis": diagnosis,
    }


@api.post("/traces/{trace_id}/override-diagnosis")
def override_diagnosis(trace_id: str, override: DiagnosisOverride):
    if not _storage:
        raise HTTPException(500, "Storage not initialized")

    trace = _storage.load(trace_id)
    if not trace:
        raise HTTPException(404, "Trace not found")

    trace.diagnosis = {
        "root_cause_step": override.root_cause_step,
        "failure_category": override.failure_category,
        "explanation": override.explanation,
        "confidence": 1.0,
        "evidence_chain": [],
    }
    _storage.save(trace)

    if _eval_dataset and override.corrected_output:
        _eval_dataset.add_case(
            trace_id=trace_id,
            input_text=trace.spans[0].input_data if trace.spans else {},
            failing_step=override.root_cause_step,
            bad_output=trace.to_dict(),
            corrected_output=override.corrected_output,
            failure_category=override.failure_category,
            diagnosis_explanation=override.explanation,
        )

    return {"trace_id": trace_id, "diagnosis": trace.diagnosis}


@api.get("/analytics")
def get_analytics():
    if not _analytics:
        raise HTTPException(500, "Analytics not initialized")
    return _analytics.compute()


@api.get("/eval-cases")
def list_eval_cases(limit: int = 100):
    if not _eval_dataset:
        raise HTTPException(500, "Eval dataset not initialized")
    return {"cases": _eval_dataset.list_cases(limit)}


@api.get("/sample-documents")
def list_sample_documents():
    from data.sample_documents import SAMPLE_DOCUMENTS
    return {"documents": SAMPLE_DOCUMENTS}


@api.post("/pipeline/run")
def run_pipeline(req: RunPipelineRequest):
    global _storage, _judge
    if not _storage:
        raise HTTPException(500, "Storage not initialized")
    try:
        llm = LLMClient()
    except ValueError:
        raise HTTPException(500, "LLM client not configured. Set GEMINI_API_KEY.")
    from pipeline.pipeline import Pipeline
    pipeline = Pipeline(llm)
    trace = pipeline.run(req.text, source=req.source)
    _storage.save(trace)
    return trace.to_dict()


@api.post("/pipeline/batch-run")
def batch_run_pipeline(req: BatchRunRequest):
    global _storage
    if not _storage:
        raise HTTPException(500, "Storage not initialized")
    try:
        llm = LLMClient()
    except ValueError:
        raise HTTPException(500, "LLM client not configured.")
    from pipeline.pipeline import Pipeline
    pipeline = Pipeline(llm)
    results = []
    for doc in req.documents:
        try:
            trace = pipeline.run(doc.get("text", ""), source=doc.get("source", ""))
            _storage.save(trace)
            results.append({
                "id": doc.get("id", ""),
                "source": doc.get("source", ""),
                "trace_id": trace.trace_id,
                "status": trace.status.value,
                "final_score": trace.final_score,
            })
        except Exception as e:
            results.append({
                "id": doc.get("id", ""),
                "source": doc.get("source", ""),
                "status": "error",
                "error": str(e),
            })
    return {"results": results}


@api.get("/failure-types")
def list_failure_types():
    from analyzer.taxonomy import FAILURE_DESCRIPTIONS
    return {
        "types": {
            k.value: {
                "label": v["label"],
                "description": v["description"],
                "severity": v["severity"],
            }
            for k, v in FAILURE_DESCRIPTIONS.items()
        }
    }


@api.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api)


# Serve built frontend for any unmatched route (SPA)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    file_path = os.path.normpath(os.path.join(FRONTEND_DIST, full_path))
    if os.path.isfile(file_path) and file_path.startswith(os.path.normpath(FRONTEND_DIST)):
        return FileResponse(file_path)
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    raise HTTPException(404)
