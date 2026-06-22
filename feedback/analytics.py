from tracing.storage import TraceStorage
from .eval_dataset import EvalDataset


class AnalyticsEngine:
    def __init__(self, storage: TraceStorage, eval_dataset: EvalDataset):
        self.storage = storage
        self.eval_dataset = eval_dataset

    def compute(self) -> dict:
        stats = self.storage.get_stats()
        eval_summary = self.eval_dataset.get_regression_summary()
        flagged = self.storage.get_flagged_traces()

        failure_types = {}
        for ft in eval_summary.get("by_category", {}):
            failure_types[ft] = {
                "count": eval_summary["by_category"][ft],
                "pct": round(
                    eval_summary["by_category"][ft] / max(eval_summary["total_cases"], 1) * 100, 1
                ),
            }

        failing_steps = {}
        for case in self.eval_dataset.list_cases(limit=10000):
            step = case.get("failing_step", "unknown")
            failing_steps[step] = failing_steps.get(step, 0) + 1

        return {
            "total_traces": stats["total_traces"],
            "flagged_traces": stats["flagged_traces"],
            "avg_final_score": stats["avg_final_score"],
            "failure_rate": round(
                stats["flagged_traces"] / max(stats["total_traces"], 1) * 100, 1
            ),
            "by_status": stats["by_status"],
            "eval_cases": eval_summary["total_cases"],
            "resolved_cases": eval_summary["resolved"],
            "resolution_rate": round(
                eval_summary["resolved"] / max(eval_summary["total_cases"], 1) * 100, 1
            ),
            "failure_types": failure_types,
            "failing_steps": failing_steps,
            "recent_flags": len(flagged),
        }
