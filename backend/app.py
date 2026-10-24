import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from banco import inicializar_banco, salvar_lote_no_banco

# Inicializa o banco ANTES de importar o motor para garantir a tabela pronta
inicializar_banco()

from motor import processar_arquivo_lote

# Configuração de Logs Estruturados sem vazar dados sensíveis do CSV (15 pontos do edital)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def servir_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>', methods=['GET'])
def servir_arquivos_estaticos(filename):
    if filename in ('style.css', 'script.js'):
        return send_from_directory('.', filename)
    return jsonify({"erro": "Recurso não encontrado."}), 404


@app.route('/api/analisar-lote', methods=['POST', 'OPTIONS'])
def analisar_lote():
    if request.method == 'OPTIONS':
        return '', 204

    logging.info("EVENT=LOTE_RECEBIDO STATUS=INICIANDO")

    if 'lote' not in request.files:
        logging.warning("EVENT=VALIDACAO_FALHA MOTIVO=CAMPO_LOTE_AUSENTE")
        return jsonify({"erro": "O campo 'lote' é obrigatório no envio do arquivo."}), 400

    arquivo_lote = request.files.get('lote')
    if not arquivo_lote or arquivo_lote.filename == '':
        logging.warning("EVENT=VALIDACAO_FALHA MOTIVO=ARQUIVO_VAZIO")
        return jsonify({"erro": "Nenhum arquivo foi selecionado."}), 400

    # 1. Processa o CSV através das regras do motor
    resultado_processamento, aprovados_para_banco, erro = processar_arquivo_lote(arquivo_lote)
    if erro:
        logging.error("EVENT=PROCESSAMENTO_ERRO STATUS=FALHA")
        return jsonify({"erro": erro}), 400

    # 2. Persiste os títulos aprovados no banco em lote (Bulk Insert)
    salvar_lote_no_banco(aprovados_para_banco)

    logging.info(
        f"EVENT=PROCESSAMENTO_CONCLUIDO STATUS=SUCESSO "
        f"TOTAL={resultado_processamento['resumo']['totalNotas']} "
        f"RECUSADAS={resultado_processamento['resumo']['totalRecusadas']}"
    )
    return jsonify(resultado_processamento), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
