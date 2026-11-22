"""
Pytest configuration and fixtures for SarkariSach test suite.
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.rules_engine import IndianScamRulesEngine
from app.core.url_inspector import StaticUrlInspector


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def rules_engine():
    return IndianScamRulesEngine(data_dir=backend_path / "app" / "data")


@pytest.fixture(scope="session")
def url_inspector():
    return StaticUrlInspector(data_dir=backend_path / "app" / "data")

