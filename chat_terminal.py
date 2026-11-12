import os
import re
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from agenda import agendar_horario, verificar_disponibilidade
from atendimento import contem_palavra_sensivel, transferir_para_humano

load_dotenv()

PASTA = Path(__file__).parent
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
TENTATIVAS = 3


def formatar_whatsapp(texto: str) -> str:
    """Converte o negrito do Markdown (**texto**) para o do WhatsApp (*texto*)."""
    return re.sub(r"\*\*(.+?)\*\*", r"*\1*", texto)


def montar_instrucoes() -> str:
    """Junta prompt, data de hoje e base de conhecimento no prompt de sistema."""
    prompt = (PASTA / "base" / "prompt.md").read_text(encoding="utf-8")
    base = (PASTA / "base" / "negocios.md").read_text(encoding="utf-8")
    hoje = date.today()
    data_hoje = f"Hoje é {DIAS[hoje.weekday()]}, {hoje.isoformat()}."
    return f"{prompt}\n\n{data_hoje}\n\n## BASE DE CONHECIMENTO\n{base}"


def criar_chat(client):
    """Cria um chat com memória e ferramentas usando o client informado."""
    return client.chats.create(
        model=os.getenv("GEMINI_MODEL"),
        config=types.GenerateContentConfig(
            system_instruction=montar_instrucoes(),
            temperature=0.2,
            tools=[verificar_disponibilidade, agendar_horario, transferir_para_humano],
        ),
    )


def responder(chat, mensagem: str) -> str:
    """Responde o cliente: assunto sensível vai direto para humano; o resto passa pela IA com retry."""
    if contem_palavra_sensivel(mensagem):
        print("  [filtro] assunto sensível detectado, transferindo sem passar pela IA")
        resultado = transferir_para_humano("Não informado", "Assunto sensível", mensagem)
        return resultado["mensagem_para_cliente"]

    for tentativa in range(TENTATIVAS):
        try:
            resposta = chat.send_message(mensagem)
            return formatar_whatsapp(resposta.text)
        except errors.ServerError as erro:
            espera = 2 ** tentativa  # 1s, 2s, 4s
            print(f"  [retry] {erro.code}, tentando de novo em {espera}s...")
            time.sleep(espera)
        except Exception as erro:
            print(f"  [log] {erro}")
            return "Desculpe, tive um problema agora. Tenta de novo em instantes."
    return "Desculpe, nosso sistema está instável agora. Tenta de novo em alguns minutos."


def main():
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(timeout=30_000),  # 30 segundos
    )
    chat = criar_chat(client)
    print("Atendente pronto. Digite 'sair' para encerrar.\n")

    while True:
        mensagem = input("Você: ").strip()
        if mensagem.lower() == "sair":
            print("Encerrando o programa. Até logo!")
            break
        if not mensagem:
            continue
        print(f"Atendente: {responder(chat, mensagem)}\n")


if __name__ == "__main__":
    main()