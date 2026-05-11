"""Project-root pytest hooks.

Pin TLX_EMBEDDER=local across the whole suite so RAG/docs paths never
attempt a Google API call during tests. Individual tests that need to
exercise the Google backend may monkeypatch the env variable back.
"""
from __future__ import annotations

import os


def pytest_configure(config):  # noqa: ARG001
    os.environ.setdefault("TLX_EMBEDDER", "local")
