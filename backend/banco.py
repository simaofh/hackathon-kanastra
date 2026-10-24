import sqlite3
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")


def inicializar_banco():
    """Cria a tabela se não existir e atualiza o schema caso exista versão antiga."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Garante que se houver um database.db antigo sem 'chave_duplicidade', ele seja recriado
    cursor.execute("PRAGMA table_info(lotes_processados)")
    colunas = [col[1] for col in cursor.fetchall()]
    if colunas and "chave_duplicidade" not in colunas:
        cursor.execute("DROP TABLE lotes_processados")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotes_processados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave_duplicidade TEXT UNIQUE,
            documento TEXT,
            sacado TEXT,
            valor_face TEXT,
            status TEXT,
            motivo TEXT
        )
    ''')
    conn.commit()
    conn.close()


def carregar_estoque_banco():
    """
    Lê o banco de dados ao iniciar o servidor e devolve um Set (conjunto)
    com as chaves de duplicidade e documentos aprovados para busca em O(1).
    """
    estoque = set()
    try:
        inicializar_banco()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT chave_duplicidade, documento FROM lotes_processados WHERE status = "APROVADO"'
        )
        linhas = cursor.fetchall()

        for chave, doc in linhas:
            if chave:
                estoque.add(str(chave).strip())
            if doc:
                estoque.add(str(doc).strip())

        conn.close()
        logging.info(f"EVENT=ESTOQUE_BANCO_CARREGADO STATUS=SUCESSO QTD={len(linhas)}")
    except Exception as e:
        logging.error(f"EVENT=ESTOQUE_BANCO_ERRO TIPO={type(e).__name__}")

    return estoque


def salvar_lote_no_banco(itens, cedente_doc_padrao="00000000000191"):
    """
    Salva os itens aprovados em lote (Bulk Insert) usando executemany.
    Aceita tanto lista de dicionários quanto lista de tuplas pré-formatadas.
    """
    if not itens:
        return True

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        dados_insercao = []
        for item in itens:
            if isinstance(item, (tuple, list)) and len(item) == 6:
                if str(item[4]).upper() == "APROVADO":
                    dados_insercao.append(tuple(item))
            elif isinstance(item, dict):
                status = str(item.get("status", "")).upper()
                if status != "APROVADO":
                    continue
                id_doc = str(item.get("id_documento") or item.get("id") or "").strip()
                sacado = str(item.get("sacado") or "").strip()
                valor_face = str(item.get("valor_face") or item.get("valorFace") or "").strip()
                motivo = str(item.get("motivo") or "").strip()
                chave = item.get("chave_duplicidade") or f"{cedente_doc_padrao}_{id_doc}"
                dados_insercao.append((chave, id_doc, sacado, valor_face, status, motivo))

        if not dados_insercao:
            conn.close()
            return True

        cursor.executemany('''
            INSERT OR IGNORE INTO lotes_processados
            (chave_duplicidade, documento, sacado, valor_face, status, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', dados_insercao)

        conn.commit()
        conn.close()
        logging.info(f"EVENT=PERSISTENCIA_BANCO STATUS=SUCESSO QTD_APROVADOS={len(dados_insercao)}")
        return True
    except Exception as e:
        logging.error(f"EVENT=PERSISTENCIA_BANCO STATUS=ERRO TIPO={type(e).__name__}")
        return False
