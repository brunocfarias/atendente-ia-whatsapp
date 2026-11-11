from datetime import date

import holidays

# ---------- Configuração do negócio ----------

# Feriados nacionais + estaduais de SP, calculados automaticamente para qualquer ano
FERIADOS = holidays.country_holidays("BR", subdiv="SP", language="pt_BR")

# Dias fechados por decisão do dono (feriado municipal, Carnaval, folga...)
FECHADOS_EXTRAS = {
    date(2026, 1, 25),  # aniversário de São Paulo
}


def gerar_horarios(abre: int, fecha: int) -> list[str]:
    """Gera os horários de hora em hora. Ex.: gerar_horarios(9, 12) -> ['09:00', '10:00', '11:00']"""
    return [f"{h:02d}:00" for h in range(abre, fecha)]


# Horários de cada dia da semana (0 = segunda ... 6 = domingo)
HORARIOS_POR_DIA = {
    0: gerar_horarios(9, 20),  # segunda
    1: gerar_horarios(9, 20),  # terça
    2: gerar_horarios(9, 20),  # quarta
    3: gerar_horarios(9, 20),  # quinta
    4: gerar_horarios(9, 20),  # sexta
    5: gerar_horarios(8, 18),  # sábado
    6: [],                     # domingo: fechado
}


# Horários já marcados (depois isso vira banco de dados)
OCUPADOS = {
    "2026-11-14": ["09:00", "10:00", "15:00"],
}


# Serviços oferecidos (os nomes têm que bater com o negocios.md)
SERVICOS = {
    "Corte Clássico/Degradê",
    "Barba",
    "Combo (Corte + Barba)",
    "Corte Infantil",
    "Pezinho / Acabamento",
    "Sobrancelha",
}


# ---------- Ferramenta usada pela IA ----------

def verificar_disponibilidade(data: str) -> dict:
    """Consulta se a barbearia abre em uma data e quais horários estão livres.

    Use SEMPRE antes de oferecer ou confirmar qualquer horário ao cliente.

    Args:
        data: Data no formato AAAA-MM-DD, por exemplo 2026-11-14.

    Returns:
        Se fechado: {"aberto": False, "motivo": "..."}.
        Se aberto: {"aberto": True, "horarios_livres": [...]}.
        Lista de horários vazia significa que o dia está lotado.
    """
    print(f"  [ferramenta] verificar_disponibilidade({data})")

    dia = date.fromisoformat(data)

    if dia in FERIADOS:
        return {"aberto": False, "motivo": f"Feriado: {FERIADOS.get(dia)}"}

    if dia in FECHADOS_EXTRAS:
        return {"aberto": False, "motivo": "Fechado por decisão da barbearia"}

    horarios_do_dia = HORARIOS_POR_DIA[dia.weekday()]
    if not horarios_do_dia:
        return {"aberto": False, "motivo": "A barbearia não abre nesse dia da semana"}

    ocupados = OCUPADOS.get(data, [])
    livres = [h for h in horarios_do_dia if h not in ocupados]
    return {"aberto": True, "horarios_livres": livres}


def agendar_horario(data: str, horario: str, nome_cliente: str, servico: str) -> dict:
    """Agenda um horário para o cliente.

    Só use depois que o cliente CONFIRMAR a data, o horário, o serviço e o nome.

    Args:
        data: Data no formato AAAA-MM-DD, por exemplo 2026-11-14.
        horario: Horário no formato HH:MM, por exemplo 14:00.
        nome_cliente: Nome do cliente.
        servico: Nome exato de um dos serviços: Corte Clássico/Degradê, Barba,
            Combo (Corte + Barba), Corte Infantil, Pezinho / Acabamento ou Sobrancelha.

    Returns:
        {"sucesso": True, ...} se agendou, ou {"sucesso": False, "erro": "..."} se não foi possível.
    """
    print(f"  [ferramenta] agendar_horario({data}, {horario}, {nome_cliente}, {servico})")

    if servico not in SERVICOS:
        return {"sucesso": False, "erro": f"Serviço inválido. Opções: {', '.join(sorted(SERVICOS))}"}

    disponibilidade = verificar_disponibilidade(data)

    if not disponibilidade["aberto"]:
        return {"sucesso": False, "erro": disponibilidade["motivo"]}

    if horario not in disponibilidade["horarios_livres"]:
        return {"sucesso": False, "erro": f"O horário {horario} não está disponível nessa data."}

    OCUPADOS.setdefault(data, []).append(horario)
    return {"sucesso": True, "data": data, "horario": horario, "cliente": nome_cliente, "servico": servico}

