import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

PASTA = Path(__file__).parent
base = (PASTA / "base" / "negocios.md").read_text(encoding="utf-8")
prompt = (PASTA / "base" / "prompt.md").read_text(encoding="utf-8")

load_dotenv()
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=30_000),  # 30 segundos
)
chat = client.chats.create(
    model=os.getenv("GEMINI_MODEL"),
    config=types.GenerateContentConfig(
    system_instruction=f"{prompt}\n\n## BASE DE CONHECIMENTO\n{base}",
    temperature=0.2,
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

