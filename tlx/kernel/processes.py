"""Async subprocess registry — real implementation for Phase 1."""
from __future__ import annotations

import asyncio
import signal
import time
from dataclasses import dataclass, field


@dataclass
class ManagedProcess:
    label: str
    cmd: list[str]
    proc: asyncio.subprocess.Process
    started_at: float = field(default_factory=time.monotonic)

    @property
    def pid(self) -> int | None:
        return self.proc.pid

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started_at

    @property
    def is_running(self) -> bool:
        return self.proc.returncode is None


class ProcessRegistry:
    def __init__(self) -> None:
        self._procs: dict[str, ManagedProcess] = {}

    async def spawn(self, cmd: list[str], *, label: str) -> ManagedProcess:
        if label in self._procs and self._procs[label].is_running:
            raise ValueError(f"process already running with label: {label!r}")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        mp = ManagedProcess(label=label, cmd=cmd, proc=proc)
        self._procs[label] = mp
        return mp

    async def kill(self, label: str, timeout: float = 2.0) -> bool:  # noqa: ASYNC109
        mp = self._procs.get(label)
        if mp is None or not mp.is_running:
            return False
        try:
            mp.proc.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            return False
        try:
            await asyncio.wait_for(mp.proc.wait(), timeout=timeout)
        except TimeoutError:
            try:
                mp.proc.kill()
            except ProcessLookupError:
                pass
            await mp.proc.wait()
        return True

    def list_live(self) -> list[ManagedProcess]:
        return [mp for mp in self._procs.values() if mp.is_running]

    async def reap_finished(self) -> None:
        dead = [
            label for label, mp in self._procs.items()
            if not mp.is_running
        ]
        for label in dead:
            del self._procs[label]
