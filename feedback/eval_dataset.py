import json
import os
import csv
from datetime import datetime, timezone
from typing import Optional


class EvalDataset:
    def __init__(self, eval_dir: str = "data/eval"):
        self.eval_dir = eval_dir
        os.makedirs(eval_dir, exist_ok=True)
        self.cases_path = os.path.join(eval_dir, "eval_cases.jsonl")
        self.regression_path = os.path.join(eval_dir, "regression_results.csv")

    def add_case(
        self,
        trace_id: str,
        input_text: dict,
        failing_step: str,
        bad_output: dict,
        corrected_output: dict,
        failure_category: str,
        diagnosis_explanation: str = "",
    ):
        case = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_text,
            "failing_step": failing_step,
            "bad_output": bad_output,
            "corrected_output": corrected_output,
            "failure_category": failure_category,
            "diagnosis_explanation": diagnosis_explanation,
            "still_failing": True,
        }

        with open(self.cases_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(case) + "\n")

    def list_cases(self, limit: int = 100) -> list[dict]:
        if not os.path.exists(self.cases_path):
            return []

        cases = []
        with open(self.cases_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cases.append(json.loads(line))

        return cases[-limit:]

    def mark_resolved(self, trace_id: str):
        cases = self.list_cases(limit=10000)
        for case in cases:
            if case["trace_id"] == trace_id:
                case["still_failing"] = False

        with open(self.cases_path, "w", encoding="utf-8") as f:
            for case in cases:
                f.write(json.dumps(case) + "\n")

    def get_regression_summary(self) -> dict:
        cases = self.list_cases(limit=10000)
        total = len(cases)
        still_failing = sum(1 for c in cases if c.get("still_failing", True))
        resolved = total - still_failing

        by_category = {}
        for c in cases:
            cat = c.get("failure_category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_cases": total,
            "still_failing": still_failing,
            "resolved": resolved,
            "by_category": by_category,
        }
