import os
from dotenv import load_dotenv

print("Tentando carregar o arquivo .env...")

# Tenta carregar o .env a partir da pasta pai (a raiz do projeto)
dotenv_path = './.env'
success = load_dotenv(dotenv_path=dotenv_path)

if success:
    print("Arquivo .env encontrado e carregado com sucesso!")
else:
    print("ATENÇÃO: Não foi possível encontrar ou carregar o arquivo .env no caminho esperado.")
    print(f"Caminho procurado: {os.path.abspath(dotenv_path)}")


# Agora, vamos verificar se a variável foi carregada
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    # Por segurança, só mostramos os primeiros e últimos caracteres da chave
    print(f"Sucesso! A variável GOOGLE_API_KEY foi encontrada: '{api_key[:4]}...{api_key[-4:]}'")
else:
    print("FALHA: A variável GOOGLE_API_KEY não foi encontrada no ambiente.")