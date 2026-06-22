import json
import os
import sqlite3
from datetime import datetime
from typing import Optional

from .trace import Trace


class TraceStorage:
    def __init__(
        self,
        db_path: str = "data/trace_index.db",
        traces_dir: str = "data/traces",
    ):
        self.db_path = db_path
        self.traces_dir = traces_dir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(traces_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    source TEXT,
                    status TEXT,
                    final_score REAL,
                    flagged INTEGER DEFAULT 0,
                    flag_notes TEXT DEFAULT '',
                    json_path TEXT
                )
            """)

    def save(self, trace: Trace) -> str:
        trace_dict = trace.to_dict()
        filename = f"{trace.trace_id}.json"
        filepath = os.path.join(self.traces_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_dict, f, indent=2, default=str)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO traces
                   (trace_id, timestamp, source, status, final_score, flagged, flag_notes, json_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    trace.trace_id,
                    trace.timestamp,
                    trace.source,
                    trace.status.value,
                    trace.final_score,
                    int(trace.flagged),
                    trace.flag_notes,
                    filepath,
                ),
            )

        return filepath

    def load(self, trace_id: str) -> Optional[Trace]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT json_path FROM traces WHERE trace_id = ?", (trace_id,)
            ).fetchone()

        if not row:
            return None

        json_path = row[0]
        if not os.path.exists(json_path):
            return None

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return Trace.from_dict(data)

    def list_traces(self, limit: int = 100, offset: int = 0) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT trace_id, timestamp, source, status, final_score, flagged
                   FROM traces ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
                (limit, offset),
            ).fetchall()

        return [
            {
                "trace_id": r[0],
                "timestamp": r[1],
                "source": r[2],
                "status": r[3],
                "final_score": r[4],
                "flagged": bool(r[5]),
            }
            for r in rows
        ]

    def update_flag(self, trace_id: str, flagged: bool, notes: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE traces SET flagged = ?, flag_notes = ? WHERE trace_id = ?",
                (int(flagged), notes, trace_id),
            )

        trace = self.load(trace_id)
        if trace:
            trace.flagged = flagged
            trace.flag_notes = notes
            self.save(trace)

    def get_flagged_traces(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT trace_id, timestamp, source, status, final_score
                   FROM traces WHERE flagged = 1 ORDER BY timestamp DESC"""
            ).fetchall()

        return [
            {
                "trace_id": r[0],
                "timestamp": r[1],
                "source": r[2],
                "status": r[3],
                "final_score": r[4],
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
            flagged = conn.execute("SELECT COUNT(*) FROM traces WHERE flagged = 1").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) FROM traces GROUP BY status"
            ).fetchall()
            avg_score = conn.execute(
                "SELECT AVG(final_score) FROM traces"
            ).fetchone()[0]

        return {
            "total_traces": total,
            "flagged_traces": flagged,
            "by_status": dict(by_status),
            "avg_final_score": round(avg_score, 2) if avg_score else 0.0,
        }
