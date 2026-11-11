import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import date
from google.genai import errors
from agenda import verificar_disponibilidade

PASTA = Path(__file__).parent
base = (PASTA / "base" / "negocios.md").read_text(encoding="utf-8")
prompt = (PASTA / "base" / "prompt.md").read_text(encoding="utf-8")

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
hoje = date.today()
data_hoje = f"Hoje é {DIAS[hoje.weekday()]}, {hoje.isoformat()}."

load_dotenv()
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=30_000),  # 30 segundos
)
chat = client.chats.create(
    model=os.getenv("GEMINI_MODEL"),
    config=types.GenerateContentConfig(
    system_instruction=f"{prompt}\n\n{data_hoje}\n\n## BASE DE CONHECIMENTO\n{base}",
    temperature=0.2,
    tools=[verificar_disponibilidade],
    )
)

while True: 
    mensagem = input("Digite sua pergunta (ou 'sair' para encerrar): ")
    if mensagem.lower() == "sair":
        print("Encerrando o programa. Até logo!")
        break

    try:
        resposta = chat.send_message(mensagem)
        print(resposta.text)
    
    except Exception as erro:
        print("Desculpe, tive um problema agora. Tenta de novo em instantes.")
        print(f"[log] {erro}")

