import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent / "barbearia.db"


def conectar() -> sqlite3.Connection:
    """Abre a conexão com o banco e garante que a tabela existe."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            cliente TEXT NOT NULL,
            servico TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (data, horario)
        )
    """)
    return conexao


def horarios_ocupados(data: str) -> list[str]:
    """Devolve os horários já agendados em uma data."""
    with conectar() as conexao:
        linhas = conexao.execute(
            "SELECT horario FROM agendamentos WHERE data = ?", (data,)
        ).fetchall()
    return [linha[0] for linha in linhas]


def salvar_agendamento(data: str, horario: str, cliente: str, servico: str) -> bool:
    """Grava o agendamento. Devolve False se o horário já estiver ocupado."""
    try:
        with conectar() as conexao:
            conexao.execute(
                "INSERT INTO agendamentos (data, horario, cliente, servico) VALUES (?, ?, ?, ?)",
                (data, horario, cliente, servico),
            )
        return True
    except sqlite3.IntegrityError:
        return False