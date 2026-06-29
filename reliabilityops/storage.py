import sqlite3
from datetime import datetime, UTC
from pathlib import Path
from reliabilityops.models import CheckResult, IncidentClassification


def init_db(db_path: str = "reliabilityops.db") -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            status_code INTEGER NOT NULL,
            latency_ms INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_incident(
    result: CheckResult,
    classification: IncidentClassification,
    db_path: str = "reliabilityops.db",
) -> None:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO incidents (
            service, endpoint, category, severity, confidence,
            status_code, latency_ms, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.service,
            result.endpoint,
            classification.category,
            classification.severity,
            classification.confidence,
            result.status_code,
            result.latency_ms,
            datetime.now(UTC).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_history(db_path: str = "reliabilityops.db") -> list[tuple]:
    if not Path(db_path).exists():
        return []

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """
        SELECT service, endpoint, category, severity, confidence, status_code, latency_ms, created_at
        FROM incidents
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()
    conn.close()
    return rows
