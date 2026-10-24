import logging
import os
from time import perf_counter

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from banco import inicializar_banco, salvar_lote_no_banco

# Inicializa o banco ANTES de importar o motor para garantir a tabela pronta
inicializar_banco()

from motor import processar_arquivo_lote

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_FRONTEND = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__)
# CORS liberado para a API (o front normalmente é servido pelo próprio Flask, na mesma porta)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def pagina_inicial():
    return send_from_directory(PASTA_FRONTEND, "index.html")


@app.route("/<path:caminho>", methods=["GET"])
def arquivos_do_front(caminho):
    # Serve frontend/css/style.css, frontend/js/script.js etc.
    return send_from_directory(PASTA_FRONTEND, caminho)


@app.route("/api/analisar-lote", methods=["POST", "OPTIONS"])
def analisar_lote():
    if request.method == "OPTIONS":
        return "", 204

    arquivo = request.files.get("lote")
    if arquivo is None or arquivo.filename == "":
        logging.warning("EVENT=LOTE_REJEITADO MOTIVO=CAMPO_LOTE_AUSENTE")
        return jsonify({"erro": "Envie o arquivo CSV no campo 'lote'."}), 400

    inicio = perf_counter()
    logging.info("EVENT=LOTE_RECEBIDO")

    resultado, aprovados_para_banco, erro = processar_arquivo_lote(arquivo)
    if erro:
        logging.warning("EVENT=LOTE_REJEITADO MOTIVO=ERRO_DE_PROCESSAMENTO")
        return jsonify({"erro": erro}), 400

    salvar_lote_no_banco(aprovados_para_banco)

    resumo = resultado["resumo"]
    logging.info(
        "EVENT=LOTE_PROCESSADO NOTAS=%s RECUSADAS=%s SEGUNDOS=%.2f",
        resumo["totalNotas"], resumo["totalRecusadas"], perf_counter() - inicio,
    )
    return jsonify(resultado), 200


if __name__ == "__main__":
    logging.info("EVENT=SERVIDOR_INICIANDO PORTA=8000")
    app.run(host="127.0.0.1", port=8000, debug=False)
