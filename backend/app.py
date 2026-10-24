import logging
import os
from time import perf_counter
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from banco import inicializar_banco, salvar_lote_no_banco

# Inicializa o banco ANTES de importar o motor para garantir a tabela pronta
inicializar_banco()

from motor import (
    processar_arquivo_lote,
    ler_arquivo_regras_bruto,
    salvar_arquivo_regras_bruto,
    resetar_cache_sessao,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_FRONTEND = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def _localizar_diretorio_arquivo(caminho_relativo):
    """Encontra o arquivo do frontend independentemente da estrutura de pastas usada."""
    nome_base = os.path.basename(caminho_relativo)
    candidatos = [
        (PASTA_FRONTEND, caminho_relativo),
        (PASTA_FRONTEND, nome_base),
        (os.path.join(BASE_DIR, "frontend"), caminho_relativo),
        (BASE_DIR, caminho_relativo),
        (BASE_DIR, nome_base),
    ]
    for pasta, arquivo in candidatos:
        if os.path.exists(os.path.join(pasta, arquivo)):
            return pasta, arquivo
    return PASTA_FRONTEND, caminho_relativo


@app.route("/", methods=["GET"])
def pagina_inicial():
    pasta, arquivo = _localizar_diretorio_arquivo("index.html")
    return send_from_directory(pasta, arquivo)


@app.route("/<path:caminho>", methods=["GET"])
def arquivos_do_front(caminho):
    pasta, arquivo = _localizar_diretorio_arquivo(caminho)
    return send_from_directory(pasta, arquivo)


@app.route("/api/analisar-lote", methods=["POST", "OPTIONS"])
def analisar_lote():
    if request.method == "OPTIONS":
        return "", 204

    arquivo = request.files.get("lote")
    if arquivo is None or arquivo.filename == "":
        logging.warning("EVENT=LOTE_REJEITADO MOTIVO=CAMPO_LOTE_AUSENTE")
        return jsonify({"erro": "Envie o arquivo CSV no campo 'lote'."}), 400

    inicio = perf_counter()
    logging.info("EVENT=LOTE_RECEBIDO STATUS=INICIANDO")

    # Se o usuário enviou o parâmetro limpar_cache=true, reseta antes de processar
    if request.form.get("limpar_cache") == "true":
        resetar_cache_sessao()

    resultado, aprovados_para_banco, erro = processar_arquivo_lote(arquivo)
    if erro:
        logging.warning("EVENT=LOTE_REJEITADO MOTIVO=ERRO_DE_PROCESSAMENTO")
        return jsonify({"erro": erro}), 400

    salvar_lote_no_banco(aprovados_para_banco)

    resumo = resultado["resumo"]
    logging.info(
        "EVENT=LOTE_PROCESSADO STATUS=SUCESSO NOTAS=%s RECUSADAS=%s SEGUNDOS=%.2f",
        resumo["totalNotas"], resumo["totalRecusadas"], perf_counter() - inicio,
    )
    return jsonify(resultado), 200


@app.route("/api/configuracoes", methods=["GET"])
@app.route("/api/validadores", methods=["GET"])
def obter_configuracoes():
    """Devolve as regras atuais para o frontend preencher o pop-up de edição."""
    regras = ler_arquivo_regras_bruto()
    return jsonify(regras), 200


@app.route("/api/configuracoes", methods=["POST", "OPTIONS"])
@app.route("/api/validadores", methods=["POST", "OPTIONS"])
def atualizar_configuracoes():
    """Recebe as novas regras do frontend, guarda no JSON e reseta o cache de testes."""
    if request.method == "OPTIONS":
        return "", 204

    novos_dados = request.get_json(silent=True)
    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido."}), 400

    sucesso, mensagem = salvar_arquivo_regras_bruto(novos_dados)

    if sucesso:
        return jsonify({"mensagem": mensagem}), 200
    return jsonify({"erro": mensagem}), 500


@app.route("/api/limpar-cache", methods=["POST", "OPTIONS"])
def limpar_cache():
    """Rota dedicada para limpar o histórico de testes da sessão sem perder o estoque original."""
    if request.method == "OPTIONS":
        return "", 204

    resetar_cache_sessao()
    return jsonify({
        "mensagem": "Cache de sessão limpo com sucesso! Você já pode testar seus lotes novamente."
    }), 200


if __name__ == "__main__":
    logging.info("EVENT=SERVIDOR_INICIANDO PORTA=8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
