import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent / "barbearia.db"


def conectar() -> sqlite3.Connection:
    """Abre a conexão com o banco e garante que as tabelas existem."""
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
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS escalacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            motivo TEXT NOT NULL,
            resumo TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aberta',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
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


def salvar_escalacao(cliente: str, motivo: str, resumo: str) -> int:
    """Registra um atendimento transferido para humano e devolve o número do protocolo."""
    with conectar() as conexao:
        cursor = conexao.execute(
            "INSERT INTO escalacoes (cliente, motivo, resumo) VALUES (?, ?, ?)",
            (cliente, motivo, resumo),
        )
    return cursor.lastrowid


def escalacoes_abertas() -> list[tuple]:
    """Lista os atendimentos que ainda esperam um humano."""
    with conectar() as conexao:
        return conexao.execute(
            "SELECT id, cliente, motivo, resumo, criado_em FROM escalacoes "
            "WHERE status = 'aberta' ORDER BY id"
        ).fetchall()