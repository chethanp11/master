# ==============================
# SQLite Backend (v1)
# ==============================
"""
SQLite backend for durable runs/steps/events/approvals.

Tables:
- schema_version
- runs
- steps
- events
- approvals

Notes:
- Idempotent schema creation on init.
- Minimal migration strategy: integer schema version.
- All JSON fields stored as TEXT (json dumps).
"""

from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent
from core.memory.base import ApprovalRecord, MemoryBackend, RunBundle

MAX_PAYLOAD_CHARS = 4096


def _dumps(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False)


def _dumps_payload(x: Any) -> str:
    """Clamp payload size to keep DB bounded."""
    raw = _dumps(x)
    if len(raw) > MAX_PAYLOAD_CHARS:
        return raw[:MAX_PAYLOAD_CHARS]
    return raw


def _loads(s: Optional[str], default: Any) -> Any:
    if s is None:
        return default
    try:
        return json.loads(s)
    except Exception:
        return default


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


class SQLiteBackend(MemoryBackend):
    def __init__(self, *, db_path: str, initialize: bool = True) -> None:
        self.db_path = db_path
        if initialize:
            self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, check_same_thread=False)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                  id INTEGER PRIMARY KEY CHECK (id = 1),
                  version INTEGER NOT NULL
                )
                """
            )
            cur = con.execute("SELECT version FROM schema_version WHERE id=1")
            row = cur.fetchone()
            if row is None:
                con.execute("INSERT INTO schema_version (id, version) VALUES (1, 1)")
                version = 1
            else:
                version = int(row["version"])

            if version < 1:
                self._migrate(con, from_version=version, to_version=1)

            # v1 schema
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                  run_id TEXT PRIMARY KEY,
                  product TEXT NOT NULL,
                  flow TEXT NOT NULL,
                  status TEXT NOT NULL,
                  autonomy TEXT NOT NULL,
                  started_at INTEGER NOT NULL,
                  finished_at INTEGER,
                  input_json TEXT,
                  output_json TEXT,
                  summary_json TEXT
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)")
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS steps (
                  run_id TEXT NOT NULL,
                  step_id TEXT NOT NULL,
                  step_index INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  type TEXT NOT NULL,
                  status TEXT NOT NULL,
                  started_at INTEGER,
                  finished_at INTEGER,
                  input_json TEXT,
                  output_json TEXT,
                  error_json TEXT,
                  meta_json TEXT,
                  PRIMARY KEY (run_id, step_id)
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_steps_run_idx ON steps(run_id, step_index)")
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT NOT NULL,
                  step_id TEXT,
                  product TEXT NOT NULL,
                  flow TEXT NOT NULL,
                  kind TEXT NOT NULL,
                  ts INTEGER NOT NULL,
                  payload_json TEXT
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_events_run_ts ON events(run_id, ts)")
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                  approval_id TEXT PRIMARY KEY,
                  run_id TEXT NOT NULL,
                  step_id TEXT NOT NULL,
                  product TEXT NOT NULL,
                  flow TEXT NOT NULL,
                  status TEXT NOT NULL,
                  requested_by TEXT,
                  requested_at INTEGER NOT NULL,
                  resolved_by TEXT,
                  resolved_at INTEGER,
                  decision TEXT,
                  comment TEXT,
                  payload_json TEXT
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status, requested_at)")
            con.commit()

    def _migrate(self, con: sqlite3.Connection, *, from_version: int, to_version: int) -> None:
        # v1 only; placeholder for future migrations
        con.execute("UPDATE schema_version SET version=? WHERE id=1", (to_version,))
        con.commit()

    def ensure_schema(self) -> None:
        self._init_db()

    def get_schema_version(self) -> int:
        with self._connect() as con:
            try:
                cur = con.execute("SELECT version FROM schema_version WHERE id=1")
            except sqlite3.OperationalError:
                return 0
            row = cur.fetchone()
            return int(row["version"]) if row else 0

    # ------------------------------
    # Runs
    # ------------------------------

    def create_run(self, run: RunRecord) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO runs (
                  run_id, product, flow, status, autonomy, started_at, finished_at,
                  input_json, output_json, summary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.product,
                    run.flow,
                    _enum_value(run.status),
                    run.autonomy_level,
                    int(run.started_at),
                    int(run.finished_at) if run.finished_at is not None else None,
                    _dumps(run.input) if run.input is not None else None,
                    _dumps(run.output) if run.output is not None else None,
                    _dumps(run.summary) if run.summary is not None else None,
                ),
            )
            con.commit()

    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        finished_at = int(time.time()) if status in {"COMPLETED", "FAILED", "CANCELLED"} else None
        with self._connect() as con:
            if summary is None:
                con.execute(
                    "UPDATE runs SET status=?, finished_at=COALESCE(finished_at, ?) WHERE run_id=?",
                    (status, finished_at, run_id),
                )
            else:
                con.execute(
                    "UPDATE runs SET status=?, finished_at=COALESCE(finished_at, ?), summary_json=? WHERE run_id=?",
                    (status, finished_at, _dumps(summary), run_id),
                )
            con.commit()

    def update_run_output(self, run_id: str, *, output: Optional[Dict[str, Any]]) -> None:
        with self._connect() as con:
            con.execute(
                "UPDATE runs SET output_json=? WHERE run_id=?",
                (_dumps(output) if output is not None else None, run_id),
            )
            con.commit()

    # ------------------------------
    # Steps
    # ------------------------------

    def add_step(self, step: StepRecord) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO steps (
                  run_id, step_id, step_index, name, type, status, started_at, finished_at,
                  input_json, output_json, error_json, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    step.run_id,
                    step.step_id,
                    int(step.step_index),
                    step.name,
                    _enum_value(step.type),
                    _enum_value(step.status),
                    int(step.started_at) if step.started_at is not None else None,
                    int(step.finished_at) if step.finished_at is not None else None,
                    _dumps(step.input) if step.input is not None else None,
                    _dumps(step.output) if step.output is not None else None,
                    _dumps(step.error) if step.error is not None else None,
                    _dumps(step.meta) if step.meta is not None else None,
                ),
            )
            con.commit()

    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        # patch is a dict of fields that exist on StepRecord
        fields = []
        vals: List[Any] = []
        mapping = {
            "status": "status",
            "started_at": "started_at",
            "finished_at": "finished_at",
            "input": "input_json",
            "output": "output_json",
            "error": "error_json",
            "meta": "meta_json",
        }
        for k, col in mapping.items():
            if k not in patch:
                continue
            fields.append(f"{col}=?")
            v = patch[k]
            if col.endswith("_json"):
                vals.append(_dumps(v) if v is not None else None)
            else:
                vals.append(int(v) if k in {"started_at", "finished_at"} and v is not None else v)

        if not fields:
            return

        sql = f"UPDATE steps SET {', '.join(fields)} WHERE run_id=? AND step_id=?"
        vals.extend([run_id, step_id])

        with self._connect() as con:
            con.execute(sql, tuple(vals))
            con.commit()

    # ------------------------------
    # Events (Trace)
    # ------------------------------

    def add_event(self, event: TraceEvent) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO events (run_id, step_id, product, flow, kind, ts, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.run_id,
                    event.step_id,
                    event.product,
                    event.flow,
                    event.kind,
                    int(event.ts),
                    _dumps_payload(event.payload) if event.payload is not None else None,
                ),
            )
            con.commit()

    # ------------------------------
    # Approvals (HITL)
    # ------------------------------

    def create_approval(self, approval: ApprovalRecord) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO approvals (
                  approval_id, run_id, step_id, product, flow, status,
                  requested_by, requested_at, resolved_by, resolved_at, decision, comment, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval.approval_id,
                    approval.run_id,
                    approval.step_id,
                    approval.product,
                    approval.flow,
                    approval.status,
                    approval.requested_by,
                    int(approval.requested_at),
                    approval.resolved_by,
                    int(approval.resolved_at) if approval.resolved_at is not None else None,
                    approval.decision,
                    approval.comment,
                    _dumps_payload(approval.payload) if approval.payload is not None else None,
                ),
            )
            con.commit()

    def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        now = int(time.time())
        status = "APPROVED" if decision.upper().startswith("APPROVE") else "REJECTED"
        with self._connect() as con:
            con.execute(
                """
                UPDATE approvals
                SET status=?, decision=?, resolved_by=?, comment=?, resolved_at=?
                WHERE approval_id=?
                """,
                (status, decision, resolved_by, comment, now, approval_id),
            )
            con.commit()

    # ------------------------------
    # Queries
    # ------------------------------

    def get_run(self, run_id: str) -> Optional[RunBundle]:
        with self._connect() as con:
            r = con.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if r is None:
                return None

            run = RunRecord(
                run_id=r["run_id"],
                product=r["product"],
                flow=r["flow"],
                status=r["status"],
                autonomy_level=r["autonomy"],
                started_at=int(r["started_at"]),
                finished_at=int(r["finished_at"]) if r["finished_at"] is not None else None,
                input=_loads(r["input_json"], None),
                output=_loads(r["output_json"], None),
                summary=_loads(r["summary_json"], None),
            )

            steps_rows = con.execute(
                "SELECT * FROM steps WHERE run_id=? ORDER BY step_index ASC",
                (run_id,),
            ).fetchall()
            steps: List[StepRecord] = []
            for s in steps_rows:
                steps.append(
                    StepRecord(
                        run_id=s["run_id"],
                        step_id=s["step_id"],
                        step_index=int(s["step_index"]),
                        name=s["name"],
                        type=s["type"],
                        status=s["status"],
                        started_at=int(s["started_at"]) if s["started_at"] is not None else None,
                        finished_at=int(s["finished_at"]) if s["finished_at"] is not None else None,
                        input=_loads(s["input_json"], None),
                        output=_loads(s["output_json"], None),
                        error=_loads(s["error_json"], None),
                        meta=_loads(s["meta_json"], None) or {},
                    )
                )

            events_rows = con.execute(
                "SELECT * FROM events WHERE run_id=? ORDER BY id ASC",
                (run_id,),
            ).fetchall()
            events: List[TraceEvent] = []
            for e in events_rows:
                events.append(
                    TraceEvent(
                        kind=e["kind"],
                        run_id=e["run_id"],
                        step_id=e["step_id"],
                        product=e["product"],
                        flow=e["flow"],
                        ts=int(e["ts"]),
                        payload=_loads(e["payload_json"], {}) or {},
                    )
                )

            approvals_rows = con.execute(
                "SELECT * FROM approvals WHERE run_id=? ORDER BY requested_at DESC",
                (run_id,),
            ).fetchall()
            approvals: List[ApprovalRecord] = []
            for a in approvals_rows:
                approvals.append(
                    ApprovalRecord(
                        approval_id=a["approval_id"],
                        run_id=a["run_id"],
                        step_id=a["step_id"],
                        product=a["product"],
                        flow=a["flow"],
                        status=a["status"],
                        requested_by=a["requested_by"],
                        requested_at=int(a["requested_at"]),
                        resolved_by=a["resolved_by"],
                        resolved_at=int(a["resolved_at"]) if a["resolved_at"] is not None else None,
                        decision=a["decision"],
                        comment=a["comment"],
                        payload=_loads(a["payload_json"], {}) or {},
                    )
                )

            return RunBundle(run=run, steps=steps, events=events, approvals=approvals)

    def list_runs(self, *, limit: int = 50, offset: int = 0) -> List[RunRecord]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT * FROM runs ORDER BY started_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            out: List[RunRecord] = []
            for r in rows:
                out.append(
                    RunRecord(
                        run_id=r["run_id"],
                        product=r["product"],
                        flow=r["flow"],
                        status=r["status"],
                        autonomy_level=r["autonomy"],
                        started_at=int(r["started_at"]),
                        finished_at=int(r["finished_at"]) if r["finished_at"] is not None else None,
                        input=_loads(r["input_json"], None),
                        output=_loads(r["output_json"], None),
                        summary=_loads(r["summary_json"], None),
                    )
                )
            return out


    def list_pending_approvals(self, *, limit: int = 50, offset: int = 0) -> List[ApprovalRecord]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT * FROM approvals
                WHERE status='PENDING'
                ORDER BY requested_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            out: List[ApprovalRecord] = []
            for a in rows:
                out.append(
                    ApprovalRecord(
                        approval_id=a["approval_id"],
                        run_id=a["run_id"],
                        step_id=a["step_id"],
                        product=a["product"],
                        flow=a["flow"],
                        status=a["status"],
                        requested_by=a["requested_by"],
                        requested_at=int(a["requested_at"]),
                        resolved_by=a["resolved_by"],
                        resolved_at=int(a["resolved_at"]) if a["resolved_at"] is not None else None,
                        decision=a["decision"],
                        comment=a["comment"],
                        payload=_loads(a["payload_json"], {}) or {},
                    )
                )
            return out


# Backwards-compatible alias expected by older modules/tests
SQLiteMemoryBackend = SQLiteBackend
