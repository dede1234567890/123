"""Armazenamento central das tentativas. A planilha é apenas uma cópia."""

from __future__ import annotations

import hashlib
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from questions_bank import TOTAL_QUESTIONS, question_points_cents

# O horário de Brasília não usa mais horário de verão.
TZ = timezone(timedelta(hours=-3), name="BRT")
TURMAS = ("8A", "8B", "8C", "8D", "8E")


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def format_br(value: str | None) -> str:
    if not value:
        return ""
    moment = datetime.fromisoformat(value)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=TZ)
    else:
        moment = moment.astimezone(TZ)
    return moment.strftime("%d/%m/%Y %H:%M")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _score_cents(conn: sqlite3.Connection, attempt_id: str) -> int:
    rows = conn.execute(
        "SELECT question, correct FROM answers WHERE attempt_id = ?",
        (attempt_id,),
    ).fetchall()
    return sum(
        question_points_cents(int(item["question"])) if item["correct"] else 0
        for item in rows
    )


class Store:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._session() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS attempts (
                    attempt_id TEXT PRIMARY KEY,
                    token_hash TEXT NOT NULL,
                    browser_session TEXT NOT NULL UNIQUE,
                    nome TEXT NOT NULL,
                    turma TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    current_question INTEGER NOT NULL,
                    phase TEXT NOT NULL,
                    acertos INTEGER NOT NULL DEFAULT 0,
                    erros INTEGER NOT NULL DEFAULT 0,
                    nota_cents INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    saved INTEGER NOT NULL DEFAULT 0,
                    excel_synced INTEGER NOT NULL DEFAULT 0,
                    email_sent INTEGER NOT NULL DEFAULT 0,
                    email_claimed INTEGER NOT NULL DEFAULT 0,
                    email_error TEXT,
                    resume_count INTEGER NOT NULL DEFAULT 0,
                    encerramento TEXT NOT NULL DEFAULT 'normal'
                );
                CREATE TABLE IF NOT EXISTS answers (
                    attempt_id TEXT NOT NULL,
                    question INTEGER NOT NULL,
                    response_json TEXT NOT NULL,
                    correct INTEGER NOT NULL,
                    answered_at TEXT NOT NULL,
                    PRIMARY KEY (attempt_id, question),
                    FOREIGN KEY (attempt_id) REFERENCES attempts(attempt_id)
                );
                CREATE INDEX IF NOT EXISTS idx_attempts_turma
                    ON attempts(turma, status, finished_at);
                """
            )
            columns = {item[1] for item in conn.execute("PRAGMA table_info(attempts)")}
            if "encerramento" not in columns:
                conn.execute(
                    "ALTER TABLE attempts ADD COLUMN encerramento TEXT NOT NULL DEFAULT 'normal'"
                )
            if "nota_cents" not in columns:
                conn.execute(
                    "ALTER TABLE attempts ADD COLUMN nota_cents INTEGER NOT NULL DEFAULT 0"
                )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False,
            isolation_level=None,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @contextmanager
    def _session(self):
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()

    def create_attempt(self, browser_session: str, nome: str, turma: str, token: str) -> dict:
        attempt_id = str(uuid.uuid4())
        token_hash = hash_token(token)
        started = now_iso()
        with self._lock:
            with self._session() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    existing = conn.execute(
                        "SELECT * FROM attempts WHERE browser_session = ?",
                        (browser_session,),
                    ).fetchone()
                    if existing is not None:
                        conn.execute(
                            "UPDATE attempts SET resume_count = resume_count + 1 WHERE attempt_id = ?",
                            (existing["attempt_id"],),
                        )
                        conn.execute("COMMIT")
                        return {
                            "created": False,
                            "authorized": existing["token_hash"] == token_hash,
                            "row": self._row_dict(existing),
                        }
                    conn.execute(
                        """
                        INSERT INTO attempts (
                            attempt_id, token_hash, browser_session, nome, turma,
                            started_at, current_question, phase, status
                        ) VALUES (?, ?, ?, ?, ?, ?, 1, 'respondendo', 'em_andamento')
                        """,
                        (attempt_id, token_hash, browser_session, nome, turma, started),
                    )
                    conn.execute("COMMIT")
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
        return {"created": True, "authorized": True, "row": self.get_attempt(attempt_id)}

    def get_attempt(self, attempt_id: str) -> dict | None:
        with self._session() as conn:
            row = conn.execute(
                "SELECT * FROM attempts WHERE attempt_id = ?",
                (attempt_id,),
            ).fetchone()
        return self._row_dict(row) if row else None

    def authenticate(self, attempt_id: str, token: str) -> dict | None:
        row = self.get_attempt(attempt_id)
        if row is None or not token:
            return None
        if hash_token(token) != row["token_hash"]:
            return None
        return row

    def note_resume(self, attempt_id: str) -> None:
        with self._lock:
            with self._session() as conn:
                conn.execute(
                    "UPDATE attempts SET resume_count = resume_count + 1 WHERE attempt_id = ?",
                    (attempt_id,),
                )

    def list_answers(self, attempt_id: str) -> list[dict]:
        with self._session() as conn:
            rows = conn.execute(
                """
                SELECT question, response_json, correct, answered_at
                FROM answers WHERE attempt_id = ? ORDER BY question
                """,
                (attempt_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_answer(self, attempt_id: str, question: int) -> dict | None:
        with self._session() as conn:
            row = conn.execute(
                "SELECT * FROM answers WHERE attempt_id = ? AND question = ?",
                (attempt_id, question),
            ).fetchone()
        return dict(row) if row else None

    def save_answer(self, attempt_id: str, question: int, response_json: str, correct: bool) -> dict:
        with self._lock:
            with self._session() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    row = conn.execute(
                        "SELECT * FROM attempts WHERE attempt_id = ?",
                        (attempt_id,),
                    ).fetchone()
                    if row is None or row["status"] != "em_andamento":
                        conn.execute("ROLLBACK")
                        return {"conflict": True, "reason": "Esta avaliação não está em andamento."}
                    if row["phase"] != "respondendo" or row["current_question"] != question:
                        conn.execute("ROLLBACK")
                        return {"conflict": True, "reason": "Esta questão não está aberta para resposta."}
                    conn.execute(
                        """
                        INSERT INTO answers (attempt_id, question, response_json, correct, answered_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (attempt_id, question, response_json, 1 if correct else 0, now_iso()),
                    )
                    acertos = row["acertos"] + (1 if correct else 0)
                    erros = row["erros"] + (0 if correct else 1)
                    nota_cents = _score_cents(conn, attempt_id)
                    conn.execute(
                        """
                        UPDATE attempts
                        SET acertos = ?, erros = ?, nota_cents = ?, phase = 'feedback'
                        WHERE attempt_id = ?
                        """,
                        (acertos, erros, nota_cents, attempt_id),
                    )
                    conn.execute("COMMIT")
                except sqlite3.IntegrityError:
                    conn.execute("ROLLBACK")
                    return {"conflict": True, "reason": "Esta questão já foi confirmada."}
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
        return {"conflict": False, "row": self.get_attempt(attempt_id)}

    def advance(self, attempt_id: str) -> dict:
        with self._lock:
            with self._session() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    row = conn.execute(
                        "SELECT * FROM attempts WHERE attempt_id = ?",
                        (attempt_id,),
                    ).fetchone()
                    if row is None or row["status"] != "em_andamento" or row["phase"] != "feedback":
                        conn.execute("ROLLBACK")
                        return {"conflict": True, "reason": "Confirme a resposta antes de continuar."}
                    if row["current_question"] >= TOTAL_QUESTIONS:
                        conn.execute("ROLLBACK")
                        return {"conflict": False, "ready_to_finish": True, "row": self._row_dict(row)}
                    conn.execute(
                        """
                        UPDATE attempts
                        SET current_question = current_question + 1, phase = 'respondendo'
                        WHERE attempt_id = ?
                        """,
                        (attempt_id,),
                    )
                    conn.execute("COMMIT")
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
        return {"conflict": False, "ready_to_finish": False, "row": self.get_attempt(attempt_id)}

    def finish(self, attempt_id: str, security: bool = False) -> dict:
        with self._lock:
            with self._session() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    row = conn.execute(
                        "SELECT * FROM attempts WHERE attempt_id = ?",
                        (attempt_id,),
                    ).fetchone()
                    if row is None:
                        conn.execute("ROLLBACK")
                        return {"conflict": True, "reason": "Avaliação não encontrada."}
                    if row["status"] == "concluida":
                        conn.execute("ROLLBACK")
                        return {"conflict": False, "already": True, "row": self._row_dict(row)}
                    count = conn.execute(
                        """
                        SELECT COUNT(*) AS total, COALESCE(SUM(correct), 0) AS acertos
                        FROM answers WHERE attempt_id = ?
                        """,
                        (attempt_id,),
                    ).fetchone()
                    if not security and (
                        count["total"] != TOTAL_QUESTIONS
                        or row["current_question"] != TOTAL_QUESTIONS
                        or row["phase"] != "feedback"
                    ):
                        conn.execute("ROLLBACK")
                        return {"conflict": True, "reason": "Ainda existem questões sem confirmação."}
                    acertos = int(count["acertos"])
                    erros = TOTAL_QUESTIONS - acertos
                    nota_cents = _score_cents(conn, attempt_id)
                    finished = now_iso()
                    encerramento = "seguranca" if security else "normal"
                    conn.execute(
                        """
                        UPDATE attempts
                        SET status = 'concluida', saved = 1, finished_at = ?, acertos = ?, erros = ?,
                            nota_cents = ?, encerramento = ?
                        WHERE attempt_id = ? AND status = 'em_andamento'
                        """,
                        (finished, acertos, erros, nota_cents, encerramento, attempt_id),
                    )
                    conn.execute("COMMIT")
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
        return {"conflict": False, "already": False, "row": self.get_attempt(attempt_id)}

    def mark_excel_synced(self, attempt_ids: list[str]) -> None:
        if not attempt_ids:
            return
        marks = ",".join("?" for _ in attempt_ids)
        with self._lock:
            with self._session() as conn:
                conn.execute(
                    f"UPDATE attempts SET excel_synced = 1 WHERE attempt_id IN ({marks})",
                    tuple(attempt_ids),
                )

    def claim_email(self, attempt_id: str) -> bool:
        with self._lock:
            with self._session() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    cursor = conn.execute(
                        """
                        UPDATE attempts
                        SET email_claimed = 1
                        WHERE attempt_id = ? AND saved = 1 AND email_sent = 0 AND email_claimed = 0
                        """,
                        (attempt_id,),
                    )
                    conn.execute("COMMIT")
                    return cursor.rowcount == 1
                except Exception:
                    conn.execute("ROLLBACK")
                    raise

    def mark_email_sent(self, attempt_id: str) -> None:
        with self._lock:
            with self._session() as conn:
                conn.execute(
                    """
                    UPDATE attempts
                    SET email_sent = 1, email_claimed = 1, email_error = NULL
                    WHERE attempt_id = ?
                    """,
                    (attempt_id,),
                )

    def release_email_claim(self, attempt_id: str, message: str) -> None:
        with self._lock:
            with self._session() as conn:
                conn.execute(
                    """
                    UPDATE attempts
                    SET email_claimed = 0, email_error = ?
                    WHERE attempt_id = ? AND email_sent = 0
                    """,
                    (message[:240], attempt_id),
                )

    def release_stale_email_claims(self) -> None:
        with self._lock:
            with self._session() as conn:
                conn.execute(
                    "UPDATE attempts SET email_claimed = 0 WHERE email_sent = 0 AND email_claimed = 1"
                )

    def list_finished(self, turma: str | None = None) -> list[dict]:
        with self._session() as conn:
            if turma:
                rows = conn.execute(
                    """
                    SELECT * FROM attempts
                    WHERE saved = 1 AND turma = ?
                    ORDER BY finished_at, attempt_id
                    """,
                    (turma,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM attempts WHERE saved = 1 ORDER BY finished_at, attempt_id"
                ).fetchall()
        return [self._row_dict(row) for row in rows]

    def list_all(self) -> list[dict]:
        with self._session() as conn:
            rows = conn.execute(
                "SELECT * FROM attempts ORDER BY started_at, attempt_id"
            ).fetchall()
        return [self._row_dict(row) for row in rows]

    def pending_emails(self) -> list[dict]:
        with self._session() as conn:
            rows = conn.execute(
                """
                SELECT * FROM attempts
                WHERE saved = 1 AND email_sent = 0 AND email_claimed = 0
                ORDER BY finished_at
                """
            ).fetchall()
        return [self._row_dict(row) for row in rows]

    def review(self, attempt_id: str) -> list[dict]:
        return [
            {"number": item["question"], "correct": bool(item["correct"])}
            for item in self.list_answers(attempt_id)
        ]

    @staticmethod
    def _row_dict(row: sqlite3.Row) -> dict:
        data = dict(row)
        data["saved"] = bool(data["saved"])
        data["excel_synced"] = bool(data["excel_synced"])
        data["email_sent"] = bool(data["email_sent"])
        data["email_claimed"] = bool(data["email_claimed"])
        return data
