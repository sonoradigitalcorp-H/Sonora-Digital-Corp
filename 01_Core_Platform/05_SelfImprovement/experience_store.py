"""Experience Store — persistent logging of task outcomes in SQLite.

Tables:
  tasks   — every task executed by an agent or skill
  evaluations — LLM-judged scores for task outputs
  patterns   — recurring failure/success patterns mined from experiences
  insights   — actionable recommendations derived from patterns
  improvements — applied spec/test changes and their post-hoc results
"""

import sqlite3
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

from sdc_sdk import DB_PATH, get_db, log_action

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    type          TEXT NOT NULL,
    input_hash    TEXT,
    input         TEXT,
    output        TEXT,
    status        TEXT CHECK(status IN ('success','failure','partial')),
    duration_ms   INTEGER,
    timestamp     REAL,
    tenant_id     TEXT,
    agent_id      TEXT,
    model         TEXT,
    metadata      TEXT
);

CREATE TABLE IF NOT EXISTS evaluations (
    id            TEXT PRIMARY KEY,
    task_id       TEXT REFERENCES tasks(id),
    score         REAL CHECK(score BETWEEN 0 AND 10),
    success_rate  REAL,
    correctness   REAL,
    efficiency    REAL,
    clarity       REAL,
    completeness  REAL,
    failure_type  TEXT,
    notes         TEXT,
    timestamp     REAL,
    evaluator     TEXT,
    raw_response  TEXT
);

CREATE TABLE IF NOT EXISTS patterns (
    id            TEXT PRIMARY KEY,
    type          TEXT,
    description   TEXT,
    frequency     INTEGER DEFAULT 1,
    first_seen    REAL,
    last_seen     REAL,
    confidence    REAL,
    skill_name    TEXT,
    metadata      TEXT
);

CREATE TABLE IF NOT EXISTS insights (
    id            TEXT PRIMARY KEY,
    pattern_ids   TEXT,
    description   TEXT,
    recommendation TEXT,
    impact_score  REAL,
    created_at    REAL,
    applied       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS improvements (
    id            TEXT PRIMARY KEY,
    skill_name    TEXT,
    spec_diff     TEXT,
    test_added    TEXT,
    eval_modified TEXT,
    applied_at    REAL,
    success_after REAL,
    parent_run_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_evals_task ON evaluations(task_id);
CREATE INDEX IF NOT EXISTS idx_evals_score ON evaluations(score);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(type);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);
"""


@dataclass
class TaskRecord:
    id: str
    type: str
    input_text: str
    output: str
    status: str
    duration_ms: int
    tenant_id: str = "sdc"
    agent_id: str = ""
    model: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    input_hash: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha1(f"{self.type}:{self.input_text}:{self.timestamp}".encode()).hexdigest()[:12]
        if not self.input_hash:
            self.input_hash = hashlib.sha256(self.input_text.encode()).hexdigest()[:16]


class ExperienceStore:
    """SQLite-backed experience store for the Self-Improvement Engine."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._init_schema()

    def _init_schema(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with get_db() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    # ── Task logging ──────────────────────────────────────────────

    def log_task(self, record: TaskRecord) -> str:
        """Log a task execution. Returns the task id."""
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, type, input_hash, input, output, status,
                                   duration_ms, timestamp, tenant_id, agent_id, model, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.type,
                    record.input_hash,
                    record.input_text,
                    record.output,
                    record.status,
                    record.duration_ms,
                    record.timestamp,
                    record.tenant_id,
                    record.agent_id,
                    record.model,
                    json.dumps(record.metadata, ensure_ascii=False),
                ),
            )
            conn.commit()
        log_action("task_logged", tenant_id=record.tenant_id, metadata={"task_id": record.id, "type": record.type})
        return record.id

    def log_task_simple(
        self,
        task_type: str,
        input_text: str,
        output: str,
        status: str = "success",
        duration_ms: int = 0,
        tenant_id: str = "sdc",
        agent_id: str = "",
        model: str = "",
        metadata: Optional[dict] = None,
    ) -> str:
        """Convenience wrapper — log a task with minimal args."""
        record = TaskRecord(
            id="",
            type=task_type,
            input_text=input_text,
            output=output,
            status=status,
            duration_ms=duration_ms,
            tenant_id=tenant_id,
            agent_id=agent_id,
            model=model,
            metadata=metadata or {},
        )
        return self.log_task(record)

    # ── Evaluation storage ────────────────────────────────────────

    def store_evaluation(
        self,
        task_id: str,
        score: float,
        success_rate: float,
        correctness: float,
        efficiency: float,
        clarity: float,
        completeness: float,
        failure_type: Optional[str],
        notes: str,
        evaluator: str = "llm",
        raw_response: Optional[str] = None,
    ) -> str:
        """Store an LLM evaluation result for a task."""
        eval_id = hashlib.sha1(f"{task_id}:{time.time()}".encode()).hexdigest()[:12]
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO evaluations (id, task_id, score, success_rate, correctness,
                    efficiency, clarity, completeness, failure_type, notes,
                    timestamp, evaluator, raw_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eval_id, task_id, score, success_rate, correctness,
                    efficiency, clarity, completeness, failure_type, notes,
                    time.time(), evaluator, raw_response,
                ),
            )
            conn.commit()
        return eval_id

    # ── Pattern management ────────────────────────────────────────

    def add_pattern(
        self,
        pattern_type: str,
        description: str,
        skill_name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Record a pattern. Increments frequency if pattern already exists for description."""
        pattern_id = hashlib.sha1(f"{pattern_type}:{description}".encode()).hexdigest()[:12]
        now = time.time()
        with get_db() as conn:
            existing = conn.execute(
                "SELECT id, frequency, first_seen, confidence FROM patterns WHERE id = ?",
                (pattern_id,),
            ).fetchone()

            if existing:
                confidence = min(1.0, (existing["confidence"] or 0) + 0.1)
                conn.execute(
                    """
                    UPDATE patterns
                    SET frequency = frequency + 1,
                        last_seen = ?,
                        confidence = ?
                    WHERE id = ?
                    """,
                    (now, confidence, pattern_id),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO patterns (id, type, description, frequency, first_seen,
                        last_seen, confidence, skill_name, metadata)
                    VALUES (?, ?, ?, 1, ?, ?, 0.1, ?, ?)
                    """,
                    (
                        pattern_id, pattern_type, description,
                        now, now,
                        skill_name,
                        json.dumps(metadata or {}, ensure_ascii=False),
                    ),
                )
            conn.commit()
        return pattern_id

    def get_patterns(self, type_filter: Optional[str] = None, min_confidence: float = 0.0) -> list:
        with get_db() as conn:
            query = "SELECT * FROM patterns WHERE confidence >= ?"
            params = [min_confidence]
            if type_filter:
                query += " AND type = ?"
                params.append(type_filter)
            query += " ORDER BY confidence DESC, frequency DESC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    # ── Insight management ────────────────────────────────────────

    def add_insight(
        self,
        pattern_ids: list[str],
        description: str,
        recommendation: str,
        impact_score: float,
    ) -> str:
        insight_id = hashlib.sha1(f"{description}:{time.time()}".encode()).hexdigest()[:12]
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO insights (id, pattern_ids, description, recommendation,
                    impact_score, created_at, applied)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    insight_id,
                    json.dumps(pattern_ids),
                    description,
                    recommendation,
                    impact_score,
                    time.time(),
                ),
            )
            conn.commit()
        return insight_id

    def mark_insight_applied(self, insight_id: str) -> None:
        with get_db() as conn:
            conn.execute(
                "UPDATE insights SET applied = 1 WHERE id = ?", (insight_id,)
            )
            conn.commit()

    # ── Improvement tracking ──────────────────────────────────────

    def log_improvement(
        self,
        skill_name: str,
        spec_diff: str,
        test_added: Optional[str] = None,
        eval_modified: Optional[str] = None,
        parent_run_id: Optional[str] = None,
    ) -> str:
        improvement_id = f"imp_{int(time.time()*1000)}"
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO improvements (id, skill_name, spec_diff, test_added,
                    eval_modified, applied_at, parent_run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    improvement_id, skill_name, spec_diff,
                    test_added, eval_modified, time.time(), parent_run_id,
                ),
            )
            conn.commit()
        return improvement_id

    def record_improvement_result(self, improvement_id: str, success_after: float) -> None:
        with get_db() as conn:
            conn.execute(
                "UPDATE improvements SET success_after = ? WHERE id = ?",
                (success_after, improvement_id),
            )
            conn.commit()

    # ── Queries ───────────────────────────────────────────────────

    def get_failures(self, limit: int = 100) -> list:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT t.id, t.type, t.input, t.output, t.duration_ms, t.timestamp,
                       t.tenant_id, t.agent_id, t.model,
                       e.score, e.success_rate, e.failure_type, e.notes
                FROM tasks t
                JOIN evaluations e ON e.task_id = t.id
                WHERE t.status = 'failure'
                ORDER BY t.timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_recent_tasks(self, limit: int = 50, status: Optional[str] = None) -> list:
        with get_db() as conn:
            query = """
                SELECT t.*, e.score, e.success_rate, e.failure_type, e.notes
                FROM tasks t
                LEFT JOIN evaluations e ON e.task_id = t.id
                """
            params = [limit]
            if status:
                query += " WHERE t.status = ?"
                params.insert(0, status)
            query += " ORDER BY t.timestamp DESC LIMIT ?"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_stats(self) -> dict:
        with get_db() as conn:
            total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            failures = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='failure'").fetchone()[0]
            successes = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='success'").fetchone()[0]
            patterns = conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
            insights = conn.execute("SELECT COUNT(*) FROM insights WHERE applied=0").fetchone()[0]

            avg_score = conn.execute("SELECT AVG(score) FROM evaluations WHERE score IS NOT NULL").fetchone()[0]

        return {
            "total_tasks": total,
            "successes": successes,
            "failures": failures,
            "patterns_detected": patterns,
            "pending_insights": insights,
            "avg_score": round(avg_score or 0, 2),
        }

    def reset(self) -> None:
        """Drop all data — for testing/dev only."""
        with get_db() as conn:
            for table in ["tasks", "evaluations", "patterns", "insights", "improvements"]:
                conn.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()


__all__ = ["ExperienceStore", "TaskRecord", "SCHEMA", DB_PATH.__class__.__name__]
