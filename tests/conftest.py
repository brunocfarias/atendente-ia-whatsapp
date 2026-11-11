import pytest

import db


@pytest.fixture(autouse=True)
def banco_de_teste(tmp_path, monkeypatch):
    """Cada teste usa um banco novo e temporário, com horários ocupados de exemplo."""
    monkeypatch.setattr(db, "CAMINHO_BANCO", tmp_path / "teste.db")

    for horario in ["09:00", "10:00", "15:00"]:
        db.salvar_agendamento("2026-11-14", horario, "Cliente Teste", "Barba")