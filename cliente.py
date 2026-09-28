# =============================================================================
# cliente.py — SCRIPT QUE CONSOME (USA) NOSSA API
# =============================================================================
# Enquanto "app.py" é o SERVIDOR (fica esperando pedidos), este arquivo é um
# CLIENTE: um programa comum que faz pedidos (requisições) para o servidor,
# exatamente como um navegador faria ao acessar um site.
#
# Para este script funcionar, o servidor (app.py) precisa estar RODANDO em
# outro terminal, escutando em http://localhost:5000
#
# Usamos a biblioteca 'requests', que facilita muito fazer requisições HTTP
# (GET, POST, etc.) em Python.
# =============================================================================

import requests

# Guardamos o endereço base do nosso servidor em uma variável, para não
# precisar repetir "http://localhost:5000" toda vez.
URL_BASE = "http://localhost:5000"


# =============================================================================
# PARTE 1: TESTANDO O ENDPOINT GET /api/status
# =============================================================================
def testar_status():
    """Faz uma requisição GET para /api/status e mostra o resultado."""

    print("\n=== Testando GET /api/status ===")

    # requests.get(url) envia uma requisição HTTP do tipo GET para o
    # endereço informado, e retorna um objeto "Response" com a resposta
    # do servidor.
    resposta = requests.get(f"{URL_BASE}/api/status")

    # .status_code é o código HTTP que o servidor devolveu (ex: 200, 404...).
    print("Código de status HTTP recebido:", resposta.status_code)

    # .json() converte o corpo da resposta (que está em formato JSON/texto)
    # de volta para um dicionário Python, para podermos usá-lo no código.
    dados = resposta.json()

    # .keys() retorna todas as "chaves" (nomes dos campos) do dicionário.
    # list(...) apenas transforma isso em uma lista para ficar fácil de ler.
    print("Chaves recebidas no JSON:", list(dados.keys()))

    # Também exibimos o conteúdo completo, para o aluno ver o resultado.
    print("Conteúdo completo:", dados)


# =============================================================================
# PARTE 2: TESTANDO O ENDPOINT POST /api/perguntar
# =============================================================================
def perguntar_para_ia(pergunta, tipo_ia="gemini"):
    """Envia uma pergunta para a IA escolhida através da nossa API Flask."""

    print(f"\n=== Testando POST /api/perguntar?type={tipo_ia} ===")

    # Montamos a URL incluindo o parâmetro "type" na query string.
    url = f"{URL_BASE}/api/perguntar?type={tipo_ia}"

    # O corpo (body) da requisição precisa ser um dicionário Python.
    # O parâmetro 'json=corpo' do requests já faz duas coisas por nós:
    #   1) Converte o dicionário para o formato JSON.
    #   2) Configura o cabeçalho "Content-Type: application/json" sozinho.
    corpo = {"pergunta": pergunta}

    # requests.post(url, json=corpo) envia uma requisição HTTP do tipo POST,
    # com os dados da pergunta dentro do corpo da requisição.
    resposta = requests.post(url, json=corpo)

    print("Código de status HTTP recebido:", resposta.status_code)

    # Convertendo a resposta JSON do servidor em um dicionário Python.
    dados = resposta.json()

    # Exibimos o JSON completo devolvido pelo servidor, exatamente como ele
    # chegou (seja um resultado de sucesso ou uma mensagem de erro).
    print("JSON de resposta recebido:", dados)


# =============================================================================
# EXECUÇÃO DO SCRIPT
# =============================================================================
# Assim como no app.py, este bloco só roda quando executamos
# "python cliente.py" diretamente.
# =============================================================================
if __name__ == "__main__":
    # 1) Testa se o servidor está de pé e retornando as informações certas.
    testar_status()

    # 2) Pergunta ao usuário qual IA ele quer usar, através de um menu
    #    simples no terminal.
    print("\nEscolha a IA que deseja usar:")
    print("1 - Gemini (Google)")
    print("2 - GPT (OpenAI)")

    # input() pausa o programa e espera o usuário digitar algo e teclar Enter.
    # O que o usuário digitar é sempre recebido como texto (string).
    opcao = input("Digite 1 ou 2: ")

    # Convertemos a opção escolhida (1 ou 2) para o nome do tipo de IA que a
    # nossa API espera receber no parâmetro "type" ("gemini" ou "gpt").
    if opcao == "1":
        tipo_escolhido = "gemini"
    elif opcao == "2":
        tipo_escolhido = "gpt"
    else:
        # Se o usuário digitar qualquer outra coisa, avisamos e encerramos.
        print("Opção inválida. Encerrando o programa.")
        # exit() interrompe a execução do script imediatamente.
        exit()

    # 3) Pergunta ao usuário qual pergunta ele quer enviar para a IA.
    pergunta_do_usuario = input("Digite a pergunta que deseja fazer para a IA: ")

    # 4) Envia a pergunta para a API e mostra o resultado.
    perguntar_para_ia(pergunta_do_usuario, tipo_ia=tipo_escolhido)
