# !pip install flask
# =============================================================================
# app.py — SERVIDOR WEB (API) COM FLASK
# =============================================================================
# Este arquivo cria um "servidor". Um servidor é apenas um programa que fica
# rodando e "escutando" (esperando) por pedidos (requisições) de outros
# programas ou navegadores. Quando um pedido chega, o servidor executa uma
# função e devolve uma resposta.
#
# Flask é uma biblioteca (framework) que facilita muito a criação desse tipo
# de programa em Python.
# =============================================================================

# --- IMPORTAÇÕES ------------------------------------------------------------
# 'Flask' é a classe principal que representa nossa aplicação/servidor.
# 'jsonify' transforma um dicionário Python em uma resposta JSON válida.
# 'request' nos dá acesso ao que foi enviado pelo cliente (dados, parâmetros).
from flask import Flask, jsonify, request

# 'datetime' é usado aqui só para simular uma data/hora no endpoint de status.
from datetime import datetime

# 'os' permite ler variáveis de ambiente (ex: chaves de API guardadas no .env)
import os


# SDKs oficiais das IAs que vamos usar.
# - 'genai' é a SDK do Google para o Gemini.
# - 'OpenAI' é a SDK oficial da OpenAI para o GPT.
from google import genai
from openai import OpenAI

# Lemos as chaves das APIs que foram salvas no arquivo .env.
# os.getenv("NOME") busca o valor da variável de ambiente "NOME".
# Se não existir, ele retorna None (ninguém quebra o programa por isso ainda).
GEMINI_API_KEY = ''
OPENAI_API_KEY = ''

# -----------------------------------------------------------------------------
# CRIANDO A APLICAÇÃO FLASK
# -----------------------------------------------------------------------------
# 'Flask(__name__)' cria a aplicação. O parâmetro '__name__' apenas informa
# ao Flask em qual arquivo/módulo ele está sendo executado — isso é usado
# internamente pelo Flask para localizar arquivos e outras configurações.
# Chamamos essa variável de 'app' — é o nosso servidor em si.
app = Flask(__name__)


# =============================================================================
# ROTA 1: GET /api/status
# =============================================================================
# Um "decorador" (a linha que começa com @) é uma forma de "decorar" (ligar)
# uma função a um comportamento especial do Flask.
#
# @app.route("/api/status", methods=["GET"]) diz ao Flask:
#   "Quando alguém acessar o endereço /api/status usando o método HTTP GET,
#    execute a função logo abaixo (status_servidor)."
#
# Método GET = usado quando queremos apenas BUSCAR/LER uma informação,
# sem enviar dados para o servidor alterar nada.
# =============================================================================
@app.route("/api/status", methods=["GET"])
def status_servidor():
    """Retorna informações simples sobre o estado do servidor."""

    # Criamos um dicionário Python normal, igual aos que já usamos em aula.
    # O Flask, através da função jsonify(), converte esse dicionário
    # automaticamente em um JSON (formato de texto usado para troca de dados
    # entre sistemas na internet).
    dados = {
        "status": "online",  # indica que o servidor está funcionando
        "aplicacao": "API Didática - Etapa 9",  # nome da nossa aplicação
        # datetime.now() pega a data/hora atual do computador.
        # .strftime(...) formata essa data/hora como texto legível.
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }

    # jsonify(dados) transforma o dicionário 'dados' em uma resposta HTTP
    # no formato JSON, já configurando automaticamente o cabeçalho
    # "Content-Type: application/json" da resposta.
    #
    # O segundo valor retornado (200) é o CÓDIGO DE STATUS HTTP.
    # 200 significa "OK" — deu tudo certo com a requisição.
    return jsonify(dados), 200


# =============================================================================
# ROTA 2: POST /api/perguntar?type=gpt  OU  POST /api/perguntar?type=gemini
# =============================================================================
# Método POST = usado quando o cliente está ENVIANDO dados para o servidor
# (nesse caso, uma pergunta) para que ele processe e devolva algo.
#
# O parâmetro "type" vem na URL, como uma "query string". Exemplo de uso:
#   http://localhost:5000/api/perguntar?type=gemini
#   http://localhost:5000/api/perguntar?type=gpt
# =============================================================================
@app.route("/api/perguntar", methods=["POST"])
def perguntar_para_ia():
    """Recebe uma pergunta do usuário e repassa para a IA escolhida (GPT ou Gemini)."""

    # request.args é um dicionário com os parâmetros que vêm na URL depois do "?".
    # .get("type") busca o valor do parâmetro "type". Se ele não existir na URL,
    # usamos "gemini" como valor padrão (para o endpoint não quebrar sem motivo).
    tipo_ia = request.args.get("type", "gemini").lower()

    # request.get_json() lê o corpo (body) da requisição, que deve estar no
    # formato JSON, e transforma em um dicionário Python.
    # Exemplo do que o cliente deve enviar: {"pergunta": "O que é uma API?"}
    corpo_da_requisicao = request.get_json()

    # Verificamos se o corpo veio vazio ou sem a chave "pergunta".
    # Isso é uma validação simples para evitar erros feios mais na frente.
    if not corpo_da_requisicao or "pergunta" not in corpo_da_requisicao:
        # Código 400 = "Bad Request" (Requisição Inválida).
        # Usamos esse código quando o CLIENTE enviou algo errado/faltando.
        return jsonify({"erro": "Envie um JSON com a chave 'pergunta'."}), 400

    # Pegamos o texto da pergunta que o usuário enviou.
    pergunta = corpo_da_requisicao["pergunta"]

    # -------------------------------------------------------------------
    # CHAMANDO A IA CORRETA DE ACORDO COM O PARÂMETRO "type"
    # -------------------------------------------------------------------
    try:
        if tipo_ia == "gemini":
            resposta_texto = perguntar_gemini(pergunta)
        elif tipo_ia == "gpt":
            resposta_texto = perguntar_gpt(pergunta)
        else:
            # Se o parâmetro "type" não for nem "gpt" nem "gemini",
            # avisamos o cliente que ele mandou um valor inválido.
            return jsonify({
                "erro": f"Tipo de IA '{tipo_ia}' inválido. Use 'gpt' ou 'gemini'."
            }), 400

    except Exception as erro:
        # Se algo der errado ao chamar a API da IA (ex: chave inválida,
        # sem internet, etc.), capturamos o erro aqui para o servidor
        # não "quebrar" e retornamos uma mensagem amigável.
        # Código 500 = "Internal Server Error" (erro do lado do SERVIDOR).
        return jsonify({"erro": f"Falha ao consultar a IA: {str(erro)}"}), 500

    # Se tudo deu certo, devolvemos a pergunta original e a resposta da IA,
    # junto com o código 200 (OK).
    return jsonify({
        "tipo_ia": tipo_ia,
        "pergunta": pergunta,
        "resposta": resposta_texto,
    }), 200


# =============================================================================
# FUNÇÃO AUXILIAR: perguntar_gemini
# =============================================================================
# Função separada só para organizar melhor o código. Ela recebe uma pergunta
# (texto) e devolve a resposta gerada pelo modelo Gemini, do Google.
# =============================================================================
def perguntar_gemini(pergunta):
    # Criamos um "cliente" da API do Gemini, passando nossa chave secreta.
    cliente_gemini = genai.Client(api_key=GEMINI_API_KEY)

    # Pedimos para o modelo gerar uma resposta de texto (conteúdo) com base
    # na pergunta recebida.
    # "gemini-3.6-flash" é um modelo rápido e gratuito (dentro dos limites
    # da camada free), ótimo para estudo. O Google costuma descontinuar
    # modelos antigos com o tempo — se este parar de funcionar, confira o
    # nome do modelo mais atual em https://aistudio.google.com/
    resposta = cliente_gemini.models.generate_content(
        model="gemini-3.6-flash",
        contents=pergunta,
    )

    # A resposta da SDK vem em um objeto; ".text" é o texto puro gerado.
    return resposta.text


# =============================================================================
# FUNÇÃO AUXILIAR: perguntar_gpt
# =============================================================================
# Mesma ideia da função acima, mas usando a API da OpenAI (modelos GPT).
# =============================================================================
def perguntar_gpt(pergunta):
    # Criamos um "cliente" da API da OpenAI, passando nossa chave secreta.
    cliente_openai = OpenAI(api_key=OPENAI_API_KEY)

    # Usamos o endpoint de "chat" da OpenAI, que espera uma lista de
    # mensagens. "role": "user" indica que o texto é uma pergunta do usuário.
    resposta = cliente_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": pergunta},
        ],
    )

    # A resposta vem em uma lista de "choices" (opções de resposta).
    # Pegamos a primeira (índice 0) e extraímos o texto da mensagem.
    return resposta.choices[0].message.content


# =============================================================================
# INICIANDO O SERVIDOR
# =============================================================================
# Esse bloco só é executado quando rodamos este arquivo diretamente
# (ex: "python app.py"), e não quando ele é importado por outro arquivo.
# =============================================================================
if __name__ == "__main__":
    # app.run() efetivamente LIGA o servidor e o deixa escutando requisições.
    #   host="localhost" -> o servidor só responde a pedidos vindos da própria
    #                        máquina (bom para estudo/testes locais).
    #   port=5000        -> a "porta" (endereço) em que o servidor vai escutar.
    #                        Ex: http://localhost:5000
    #   debug=True       -> reinicia o servidor automaticamente quando o
    #                        código muda, e mostra erros detalhados na tela.
    #                        ÓTIMO para aprender, mas NUNCA use em produção!
    app.run(host="localhost", port=5000, debug=True)

# Outro comentário diferente
# Novo comentário só pra mudar