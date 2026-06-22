"""
Failure Forensics Tool for AI Pipelines

Usage:
  # Start the server (serves both API + React frontend)
  python -m uvicorn feedback.api:app --host 0.0.0.0 --port 8000

  # Run a single document through the pipeline
  python main.py run "path/to/document.txt"

  # Batch-process all 10 sample documents
  python main.py batch
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')  # type: ignore

load_dotenv()


def cmd_api():
    """Launch the FastAPI server."""
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    print(f"Starting API server on port {port}...")
    print(f"API docs at http://localhost:{port}/docs")
    uvicorn.run("feedback.api:app", host="0.0.0.0", port=port, reload=False)


def cmd_run(filepath: str):
    """Run a single document through the pipeline."""
    from pipeline.pipeline import Pipeline
    from pipeline.llm_client import LLMClient
    from tracing.storage import TraceStorage

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    source = os.path.basename(filepath)
    llm = LLMClient()
    pipeline = Pipeline(llm)
    storage = TraceStorage()

    print(f"Running pipeline on {source}...")
    trace = pipeline.run(text, source=source)
    path = storage.save(trace)

    print(f"\n{'='*60}")
    print(f"Trace ID: {trace.trace_id}")
    print(f"Status: {trace.status.value}")
    print(f"Score: {trace.final_score:.0%}")
    print(f"Saved to: {path}")
    print(f"{'='*60}")

    for span in trace.spans:
        print(f"\n  [{span.status.value}] {span.step_name}")
        print(f"    Confidence: {span.confidence:.0%}")
        print(f"    Tokens: {span.token_count} | Latency: {span.latency_ms:.0f}ms")
        if span.error:
            print(f"    Error: {span.error}")


def cmd_batch():
    """Process all sample documents through the pipeline."""
    from data.sample_documents import SAMPLE_DOCUMENTS
    from pipeline.pipeline import Pipeline
    from pipeline.llm_client import LLMClient
    from tracing.storage import TraceStorage

    llm = LLMClient()
    pipeline = Pipeline(llm)
    storage = TraceStorage()

    print(f"Processing {len(SAMPLE_DOCUMENTS)} documents...\n")

    results = []
    for i, doc in enumerate(SAMPLE_DOCUMENTS, 1):
        print(f"[{i}/{len(SAMPLE_DOCUMENTS)}] {doc['source']}...", end=" ")
        try:
            trace = pipeline.run(doc["text"], source=doc["source"])
            storage.save(trace)
            print(f"[OK] ({trace.status.value}, score: {trace.final_score:.0%})")
            results.append({
                "id": doc["id"],
                "source": doc["source"],
                "status": trace.status.value,
                "score": trace.final_score,
            })
        except Exception as e:
            print(f"[ERR] Error: {e}")
            results.append({
                "id": doc["id"],
                "source": doc["source"],
                "status": "error",
                "score": 0,
            })

    print(f"\n{'='*60}")
    print("Summary:")
    success = sum(1 for r in results if r["status"] == "success")
    degraded = sum(1 for r in results if r["status"] == "degraded")
    failed = sum(1 for r in results if r["status"] == "failure")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"  Success: {success} | Degraded: {degraded} | Failure: {failed} | Error: {errors}")

    json.dump(results, open("batch_results.json", "w"), indent=2)
    print(f"  Results saved to batch_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Failure Forensics Tool for AI Pipelines"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("api", help="Launch the FastAPI server")

    run_parser = subparsers.add_parser("run", help="Run pipeline on a document file")
    run_parser.add_argument("filepath", help="Path to the document file")

    subparsers.add_parser("batch", help="Run pipeline on all sample documents")

    args = parser.parse_args()

    if args.command == "api":
        cmd_api()
    elif args.command == "run":
        cmd_run(args.filepath)
    elif args.command == "batch":
        cmd_batch()
    else:
        parser.print_help()
