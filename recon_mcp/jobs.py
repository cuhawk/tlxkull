"""Aiosqlite-backed job + droplet state store."""
from __future__ import annotations

import json
import os
import time
import uuid
from enum import StrEnum

import aiosqlite


class JobStatus(StrEnum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    created_at REAL NOT NULL,
    status TEXT NOT NULL,
    target_spec TEXT NOT NULL,
    regions TEXT NOT NULL,
    droplets TEXT NOT NULL DEFAULT '[]',
    artifacts_dir TEXT,
    error TEXT,
    phase_progress TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""


_MIGRATIONS = (
    "ALTER TABLE jobs ADD COLUMN phase_progress TEXT NOT NULL DEFAULT '{}'",
)


class JobStore:
    def __init__(self, db_path: str) -> None:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.executescript(_SCHEMA)
            for stmt in _MIGRATIONS:
                try:
                    await db.execute(stmt)
                except aiosqlite.OperationalError:
                    pass
            await db.commit()

    async def create(self, *, target_spec: dict, regions: list[str], artifacts_dir: str | None = None) -> str:
        jid = uuid.uuid4().hex[:12]
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                "INSERT INTO jobs (id, created_at, status, target_spec, regions, artifacts_dir) VALUES (?,?,?,?,?,?)",
                (jid, time.time(), JobStatus.PENDING.value, json.dumps(target_spec), json.dumps(regions), artifacts_dir),
            )
            await db.commit()
        return jid

    async def get(self, job_id: str) -> dict | None:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    async def set_status(self, job_id: str, status: JobStatus) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))
            await db.commit()

    async def set_artifacts_dir(self, job_id: str, artifacts_dir: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                "UPDATE jobs SET artifacts_dir = ? WHERE id = ?",
                (artifacts_dir, job_id),
            )
            await db.commit()

    async def set_phase(self, job_id: str, *, droplet_tag: str, phase: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT phase_progress FROM jobs WHERE id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
            prog = json.loads(row["phase_progress"]) if row and row["phase_progress"] else {}
            prog[droplet_tag] = phase
            await db.execute(
                "UPDATE jobs SET phase_progress = ? WHERE id = ?",
                (json.dumps(prog), job_id),
            )
            await db.commit()

    async def attach_droplet(self, job_id: str, *, droplet_id: int, region: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT droplets FROM jobs WHERE id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
            drops = json.loads(row["droplets"]) if row else []
            drops.append({"id": droplet_id, "region": region})
            await db.execute("UPDATE jobs SET droplets = ? WHERE id = ?", (json.dumps(drops), job_id))
            await db.commit()

    async def set_error(self, job_id: str, msg: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                "UPDATE jobs SET status = ?, error = ? WHERE id = ?",
                (JobStatus.FAILED.value, msg, job_id),
            )
            await db.commit()

    async def list_active(self) -> list[dict]:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM jobs WHERE status NOT IN (?, ?, ?) ORDER BY created_at",
                (JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELED.value),
            ) as cur:
                rows = await cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def list_all(self) -> list[dict]:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs ORDER BY created_at DESC") as cur:
                rows = await cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "status": row["status"],
            "target_spec": json.loads(row["target_spec"]),
            "regions": json.loads(row["regions"]),
            "droplets": json.loads(row["droplets"]),
            "artifacts_dir": row["artifacts_dir"],
            "error": row["error"],
            "phase_progress": json.loads(row["phase_progress"]) if row["phase_progress"] else {},
        }
