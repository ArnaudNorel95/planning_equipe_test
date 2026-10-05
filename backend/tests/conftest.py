import sys
import os
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app

EQUIPES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "equipes.json")
_EQUIPES_BACKUP = EQUIPES_FILE + ".bak"


@pytest.fixture(autouse=True)
def _reset_equipes_file():
    """Restaure equipes.json dans son état initial après chaque test."""
    shutil.copy2(EQUIPES_FILE, _EQUIPES_BACKUP)
    yield
    shutil.copy2(_EQUIPES_BACKUP, EQUIPES_FILE)
    os.remove(_EQUIPES_BACKUP)


@pytest.fixture
def equipes_file():
    """Chemin vers data/equipes.json (pour assertions sur la persistance)."""
    return EQUIPES_FILE


@pytest.fixture
async def client(aiohttp_client, _reset_equipes_file):
    app = create_app()
    return await aiohttp_client(app)
