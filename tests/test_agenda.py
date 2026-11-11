from agenda import agendar_horario, verificar_disponibilidade

def test_sabado_nao_oferece_horarios_ocupados():
    resultado = verificar_disponibilidade("2026-11-14")
    assert resultado["aberto"] is True
    assert "09:00" not in resultado["horarios_livres"]
    assert "11:00" in resultado["horarios_livres"]


def test_domingo_fechado():
    resultado = verificar_disponibilidade("2026-11-22")
    assert resultado["aberto"] is False


def test_feriado_fechado_com_nome():
    resultado = verificar_disponibilidade("2026-11-20")
    assert resultado["aberto"] is False
    assert "Consciência Negra" in resultado["motivo"]

def test_nao_agenda_servico_inexistente():
    resultado = agendar_horario("2026-11-13", "10:00", "Bruno", "Luzes")
    assert resultado["sucesso"] is False