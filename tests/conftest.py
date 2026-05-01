import importlib
import os
import sys
from pathlib import Path

import pytest


@pytest.fixture
def configured_modules(tmp_path, monkeypatch):
    db_path = tmp_path / "test_app.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)

    for module_name in ["storage", "seed_test_data", "app"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    storage = importlib.import_module("storage")
    seed_test_data = importlib.import_module("seed_test_data")
    app_module = importlib.import_module("app")

    app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    storage.init_db()

    return {
        "app_module": app_module,
        "storage": storage,
        "seed_test_data": seed_test_data,
        "db_path": Path(db_path),
    }


@pytest.fixture
def client(configured_modules):
    return configured_modules["app_module"].app.test_client()
