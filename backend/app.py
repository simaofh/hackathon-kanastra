import logging
import os
from time import perf_counter
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from banco import inicializar_banco, salvar_lote_no_banco

# Inicializa o banco ANTES de importar o motor para garantir a tabela pronta
inicializar_banco()

from motor import processar_arquivo_lote, ler_arquivo_regras_bruto, salvar_arquivo_regras_bruto

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
        ( os.path.join(BASE_DIR, "frontend"), caminho_relativo),
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
@app.route
