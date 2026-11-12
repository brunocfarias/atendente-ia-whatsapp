import unicodedata

import db

# Assuntos com risco jurídico ou financeiro: vão direto para um humano, sem passar pela IA
PALAVRAS_SENSIVEIS = (
    "advogado",
    "procon",
    "processar",
    "processo judicial",
    "reembolso",
    "estorno",
    "cobranca indevida",
)


def normalizar(texto: str) -> str:
    """Deixa o texto minúsculo e sem acento. Ex.: 'COBRANÇA' -> 'cobranca'."""
    decomposto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def contem_palavra_sensivel(mensagem: str) -> bool:
    """Verifica se a mensagem fala de algum assunto que exige atendimento humano."""
    texto = normalizar(mensagem)
    return any(palavra in texto for palavra in PALAVRAS_SENSIVEIS)


def avisar_dono(protocolo: int, cliente: str, motivo: str, resumo: str) -> None:
    """Avisa o dono sobre um novo atendimento. Por enquanto no terminal; depois, no WhatsApp dele."""
    print(f"  [ALERTA DONO] Protocolo #{protocolo} | {cliente} | {motivo}")
    print(f"                {resumo}")


def transferir_para_humano(nome_cliente: str, motivo: str, resumo: str) -> dict:
    """Transfere o atendimento para um atendente humano da barbearia.

    Use quando: o cliente pedir para falar com uma pessoa; o assunto for reclamação,
    reembolso ou cobrança; ou você não conseguir resolver algo importante.

    Args:
        nome_cliente: Nome do cliente, ou "Não informado" se ele não quiser dizer.
        motivo: Motivo curto, por exemplo "Reclamação" ou "Pediu atendente".
        resumo: Resumo da conversa em até 2 frases, com o que o cliente quer,
            para o atendente não precisar perguntar tudo de novo.

    Returns:
        {"transferido": True, "protocolo": número, "mensagem_para_cliente": texto pronto}.
    """
    print(f"  [ferramenta] transferir_para_humano({nome_cliente}, {motivo})")

    protocolo = db.salvar_escalacao(nome_cliente, motivo, resumo)
    avisar_dono(protocolo, nome_cliente, motivo, resumo)
    return {
        "transferido": True,
        "protocolo": protocolo,
        "mensagem_para_cliente": (
            f"Pronto! Registrei seu atendimento com o protocolo *#{protocolo}*. "
            "Um atendente da equipe vai te responder por aqui em breve. 👍"
        ),
    }