"""mock_record tool — Phase 7E.4.

Inserts a row into mock_flow for (session_id, method, path).
Surface for StoredFlowReplay.record(); prerequisite for
mock_authz which reads from mock_flow.
"""
from __future__ import annotations

import json
from typing import Any

from ..core.reporter import get_session
from ..core.stored_flow_replay import StoredFlowReplay


async def mock_record_async(
    kernel: Any,
    session_id: str,
    method: str,
    path: str,
    response_body: str,
    request_body: str | None = None,
    status_code: int = 200,
) -> dict:
    if not session_id or not method or not path:
        return {"error": "session_id, method, path required"}
    if not response_body:
        return {"error": "response_body required"}

    db = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    if db is None or cfg is None:
        return {"error": "mock_backend not registered"}

    session = get_session(db, session_id)
    if session is None:
        return {"error": f"session '{session_id}' not found"}

    sfr = StoredFlowReplay(cfg.db_path_resolved)
    try:
        sfr.record(
            session_id=session_id,
            method=method,
            path=path,
            request_body=request_body,
            response_body=response_body,
            status_code=int(status_code),
        )
    except Exception as exc:
        return {"error": f"record failed: {exc}"}

    return {
        "recorded": True,
        "session_id": session_id,
        "method": method.upper(),
        "path": path,
        "status_code": int(status_code),
    }


def mock_record_handler(kernel: Any):
    async def _handle(
        session_id: str = "",
        method: str = "",
        path: str = "",
        response_body: str = "",
        request_body: str | None = None,
        status_code: int = 200,
    ) -> str:
        payload = await mock_record_async(
            kernel,
            session_id=session_id,
            method=method,
            path=path,
            response_body=response_body,
            request_body=request_body,
            status_code=status_code,
        )
        return json.dumps(payload)
    return _handle
