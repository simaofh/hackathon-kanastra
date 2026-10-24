import csv
import io
import json
import logging
import os
import re
from datetime import datetime
from functools import lru_cache
from banco import carregar_estoque_banco, limpar_banco

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base imutável do CSV histórico (estoque_antecipe.csv) vs Estoque ativo da sessão
ESTOQUE_CSV_ORIGINAL = set()
CONCENTRACAO_CSV_ORIGINAL = {}
CONCENTRACAO_CEDENTE_CSV_ORIGINAL = {}

ESTOQUE_IDS = set()
CONCENTRACAO_HISTORICA = {}
CONCENTRACAO_CEDENTE_HISTORICA = {}
VALOR_TOTAL_ESTOQUE = 0.0

LIMITE_ITENS_RESPOSTA_JSON = 500
CEDENTE_PADRAO = "00000000000191"

def _obter_caminho_regras():
    nomes_arquivos = ["validadores_antecipe_3.json", "validadores.json", "config.json", "config"]
    pastas = [
        BASE_DIR,
        os.path.join(BASE_DIR, "data"),
        os.path.join(os.path.dirname(BASE_DIR), "data"),
        os.path.dirname(BASE_DIR),
        "."
    ]
    for pasta in pastas:
        for nome in nomes_arquivos:
            caminho = os.path.join(pasta, nome)
            if os.path.isfile(caminho):
                return caminho
    return os.path.join(BASE_DIR, "validadores_antecipe_3.json")

def _converter_float(valor_bruto, padrao=0.0):
    if valor_bruto is None:
        return padrao
    texto = str(valor_bruto).strip().replace("R$", "").replace(" ", "")
    if not texto:
        return padrao
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return padrao

def _normalizar_chaves(linha):
    return {(k or "").strip().lower(): v for k, v in linha.items()}

def _apenas_digitos(texto):
    return re.sub(r"\D", "", str(texto or ""))

@lru_cache(maxsize=16384)
def _parse_data(texto):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    return None

def _calcular_prazo_dias(linha):
    prazo_str = linha.get("prazo") or linha.get("prazo_dias") or linha.get("dias")
    if prazo_str is not None and str(prazo_str).strip() != "":
        try:
            return int(float(str(prazo_str).strip()))
        except ValueError:
            pass
    vencimento_str = (
        linha.get("data_vencimento_original")
        or linha.get("data_vencimento")
        or linha.get("vencimento")
    )
    emissao_str = (
        linha.get("data_aquisicao")
        or linha.get("data_emissao")
        or linha.get("emissao")
    )
    if vencimento_str:
        dt_venc = _parse_data(str(vencimento_str).strip()[:10])
        if dt_venc is not None:
            dt_base = _parse_data(str(emissao_str).strip()[:10]) if emissao_str else None
            if dt_base is None:
                dt_base = datetime.now()
            return (dt_venc - dt_base).days
    return 30

def carregar_estoque_em_memoria():
    global VALOR_TOTAL_ESTOQUE
    ESTOQUE_CSV_ORIGINAL.clear()
    CONCENTRACAO_CSV_ORIGINAL.clear()
    CONCENTRACAO_CEDENTE_CSV_ORIGINAL.clear()
    VALOR_TOTAL_ESTOQUE = 0.0

    caminhos_possiveis = [
        os.path.join(BASE_DIR, "estoque_antecipe.csv"),
        os.path.join(BASE_DIR, "data", "estoque_antecipe.csv"),
        os.path.join(os.path.dirname(BASE_DIR), "data", "estoque_antecipe.csv"),
        os.path.join(os.path.dirname(BASE_DIR), "estoque_antecipe.csv"),
        "estoque_antecipe.csv",
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                with open(caminho, mode="r", encoding="utf-8-sig", errors="replace") as f:
                    primeira_linha = f.readline()
                    delimitador = ";" if ";" in primeira_linha else ","
                    f.seek(0)
                    reader = csv.DictReader(f, delimiter=delimitador)
                    for row in reader:
                        row = _normalizar_chaves(row)
                        id_nota = (
                            row.get("nu_documento")
                            or row.get("id")
                            or row.get("id_nota")
                            or row.get("operacao_id")
                            or row.get("documento")
                            or row.get("numero_nota")
                            or row.get("id_recebivel")
                        )
                        cedente = (
                            row.get("doc_cedente")
                            or row.get("cedente")
                            or row.get("cnpj_cedente")
                            or row.get("cedente_cnpj")
                            or CEDENTE_PADRAO
                        )
                        if id_nota:
                            id_limpo = str(id_nota).strip()
                            cedente_limpo = str(cedente).strip()
                            ESTOQUE_CSV_ORIGINAL.add(f"{cedente_limpo}_{id_limpo}")

                        sacado = (
                            row.get("doc_sacado")
                            or row.get("sacado")
                            or row.get("nome_sacado")
                            or row.get("cnpj_sacado")
                            or row.get("sacado_cnpj")
                        )
                        valor = _converter_float(
                            row.get("valor_nominal") or row.get("valor") or row.get("valor_face")
                        )
                        if valor > 0:
                            VALOR_TOTAL_ESTOQUE += valor
                            if sacado:
                                chave_sacado = str(sacado).strip()
                                CONCENTRACAO_CSV_ORIGINAL[chave_sacado] = (
                                    CONCENTRACAO_CSV_ORIGINAL.get(chave_sacado, 0.0) + valor
                                )
                                dig_sacado = _apenas_digitos(chave_sacado)
                                if len(dig_sacado) >= 8:
                                    raiz = dig_sacado[:8]
                                    CONCENTRACAO_CSV_ORIGINAL[raiz] = (
                                        CONCENTRACAO_CSV_ORIGINAL.get(raiz, 0.0) + valor
                                    )
                            if cedente:
                                chave_ced = str(cedente).strip()
                                CONCENTRACAO_CEDENTE_CSV_ORIGINAL[chave_ced] = (
                                    CONCENTRACAO_CEDENTE_CSV_ORIGINAL.get(chave_ced, 0.0) + valor
                                )
                logging.info(f"EVENT=ESTOQUE_CSV_CARREGADO STATUS=SUCESSO CHAVES_ORIGINAIS={len(ESTOQUE_CSV_ORIGINAL)}")
                break
            except Exception as e:
                logging.error(f"EVENT=ESTOQUE_CSV_ERRO TIPO={type(e).__name__}")

    ESTOQUE_IDS.clear()
    ESTOQUE_IDS.update(ESTOQUE_CSV_ORIGINAL)
    ESTOQUE_IDS.update(carregar_estoque_banco())
    CONCENTRACAO_HISTORICA.clear()
    CONCENTRACAO_HISTORICA.update(CONCENTRACAO_CSV_ORIGINAL)
    CONCENTRACAO_CEDENTE_HISTORICA.clear()
    CONCENTRACAO_CEDENTE_HISTORICA.update(CONCENTRACAO_CEDENTE_CSV_ORIGINAL)

def resetar_cache_sessao():
    limpar_banco()
    ESTOQUE_IDS.clear()
    ESTOQUE_IDS.update(ESTOQUE_CSV_ORIGINAL)
    CONCENTRACAO_HISTORICA.clear()
    CONCENTRACAO_HISTORICA.update(CONCENTRACAO_CSV_ORIGINAL)
    CONCENTRACAO_CEDENTE_HISTORICA.clear()
    CONCENTRACAO_CEDENTE_HISTORICA.update(CONCENTRACAO_CEDENTE_CSV_ORIGINAL)
    logging.info(f"EVENT=CACHE_SESSAO_RESETADO STATUS=SUCESSO CHAVES_ATIVAS={len(ESTOQUE_IDS)}")
    return True

def obter_regras_padrao():
    """Devolve a estrutura original de fábrica das regras do fundo."""
    return {
        "fundo": {"nome": "ANTECIPE FIDC", "cnpj": "92.234.400/0001-80"},
        "validadores": [
            {"codigo": "CNPJ_SACADO_VALIDO", "ativo": True, "parametros": {}},
            {"codigo": "SITUACAO_CADASTRAL_SACADO", "ativo": True, "parametros": {"situacoes_aceitas": ["ATIVA"]}},
            {"codigo": "TIPO_RECEBIVEL", "ativo": True, "parametros": {"tipos_aceitos": ["Duplicata", "Duplicata de Serviço"]}},
            {"codigo": "VALOR_MINIMO", "ativo": True, "parametros": {"valor_minimo": 100.0}},
            {"codigo": "NAO_VENCIDA", "ativo": True, "parametros": {}},
            {"codigo": "PRAZO_MAXIMO", "ativo": True, "parametros": {"prazo_maximo_dias": 180}},
            {"codigo": "CONCENTRACAO_MAXIMA_SACADO", "ativo": True, "parametros": {"percentual_maximo": 10.0, "agrupamento": "RAIZ_CNPJ"}},
            {"codigo": "PRAZO_MINIMO", "ativo": False, "parametros": {"prazo_minimo_dias": 30}},
            {"codigo": "CONCENTRACAO_MAXIMA_CEDENTE", "ativo": False, "parametros": {"percentual_maximo": 8.0}}
        ],
        "precificacao": {
            "metodo": "DESCONTO_SIMPLES",
            "taxa_mensal_percentual": 2.0,
            "base_dias": 30
        }
    }

def ler_arquivo_regras_bruto():
    caminho = _obter_caminho_regras()
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"EVENT=LEITURA_REGRAS_ERRO TIPO={type(e).__name__}")
    return obter_regras_padrao()

def salvar_arquivo_regras_bruto(novos_dados):
    caminho = _obter_caminho_regras()
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(novos_dados, f, indent=2, ensure_ascii=False)
        resetar_cache_sessao()
        logging.info("EVENT=REGRAS_ATUALIZADAS STATUS=SUCESSO")
        return True, "Regras atualizadas e cache de sessão reiniciado com sucesso."
    except Exception as e:
        logging.error(f"EVENT=REGRAS_ATUALIZACAO_ERRO TIPO={type(e).__name__}")
        return False, "Erro ao guardar regras."

def resetar_arquivo_regras_bruto():
    """Restaura as regras de fábrica e salva no arquivo."""
    return salvar_arquivo_regras_bruto(obter_regras_padrao())

def carregar_regras_validadores():
    dados = ler_arquivo_regras_bruto()
    regras = {
        "cnpj_valido_ativo": False,
        "situacao_cadastral_ativo": False,
        "situacoes_aceitas": ["ATIVA", "ATIVO"],
        "tipo_recebivel_ativo": False,
        "tipos_aceitos": ["DUPLICATA", "DUPLICATA DE SERVIÇO", "DUPLICATA DE SERVICO"],
        "valor_minimo_ativo": False,
        "valor_minimo": 100.0,
        "nao_vencida_ativo": False,
        "prazo_maximo_ativo": False,
        "prazo_maximo_dias": 180,
        "prazo_minimo_ativo": False,
        "prazo_minimo_dias": 30,
        "concentracao_sacado_ativo": False,
        "percentual_concentracao_sacado": 10.0,
        "agrupamento_sacado": "RAIZ_CNPJ",
        "limite_concentracao_sacado": 100000.0,
        "concentracao_cedente_ativo": False,
        "percentual_concentracao_cedente": 8.0,
        "taxa_desconto_mensal": 0.02,
        "base_dias": 30.0,
    }

    precificacao = dados.get("precificacao", {}) if isinstance(dados, dict) else {}
    if "taxa_mensal_percentual" in precificacao:
        regras["taxa_desconto_mensal"] = _converter_float(precificacao["taxa_mensal_percentual"], 2.0) / 100.0
    if "base_dias" in precificacao:
        regras["base_dias"] = max(1.0, _converter_float(precificacao["base_dias"], 30.0))

    lista_val = dados.get("validadores", []) if isinstance(dados, dict) else dados
    for val in lista_val:
        codigo = str(val.get("codigo", "")).upper()
        ativo = bool(val.get("ativo", False))
        params = val.get("parametros") or {}

        if codigo == "CNPJ_SACADO_VALIDO":
            regras["cnpj_valido_ativo"] = ativo
        elif codigo == "SITUACAO_CADASTRAL_SACADO":
            regras["situacao_cadastral_ativo"] = ativo
            aceitas = params.get("situacoes_aceitas", ["ATIVA"])
            if isinstance(aceitas, str):
                aceitas = [s.strip() for s in aceitas.split(",") if s.strip()]
            regras["situacoes_aceitas"] = [str(s).strip().upper() for s in aceitas]
        elif codigo == "TIPO_RECEBIVEL":
            regras["tipo_recebivel_ativo"] = ativo
            tipos = params.get("tipos_aceitos", ["Duplicata", "Duplicata de Serviço"])
            if isinstance(tipos, str):
                tipos = [t.strip() for t in tipos.split(",") if t.strip()]
            regras["tipos_aceitos"] = [str(t).strip().upper() for t in tipos]
        elif codigo == "VALOR_MINIMO":
            regras["valor_minimo_ativo"] = ativo
            regras["valor_minimo"] = _converter_float(params.get("valor_minimo") or params.get("valor"), 100.0)
        elif codigo == "NAO_VENCIDA":
            regras["nao_vencida_ativo"] = ativo
        elif codigo == "PRAZO_MAXIMO":
            regras["prazo_maximo_ativo"] = ativo
            regras["prazo_maximo_dias"] = int(_converter_float(params.get("prazo_maximo_dias") or params.get("dias"), 180))
        elif codigo == "PRAZO_MINIMO":
            regras["prazo_minimo_ativo"] = ativo
            regras["prazo_minimo_dias"] = int(_converter_float(params.get("prazo_minimo_dias") or params.get("dias"), 30))
        elif codigo in ("CONCENTRACAO_MAXIMA_SACADO", "CONCENTRACAO_SACADO"):
            regras["concentracao_sacado_ativo"] = ativo
            regras["percentual_concentracao_sacado"] = _converter_float(params.get("percentual_maximo"), 10.0)
            regras["agrupamento_sacado"] = str(params.get("agrupamento", "RAIZ_CNPJ")).upper()
            if "limite" in params or "valor_maximo" in params:
                regras["limite_concentracao_sacado"] = _converter_float(params.get("limite") or params.get("valor_maximo"), 100000.0)
        elif codigo == "CONCENTRACAO_MAXIMA_CEDENTE":
            regras["concentracao_cedente_ativo"] = ativo
            regras["percentual_concentracao_cedente"] = _converter_float(params.get("percentual_maximo"), 8.0)

    return regras

carregar_estoque_em_memoria()

def _formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"

def processar_arquivo_lote(file_storage):
    try:
        conteudo_bytes = file_storage.read()
        conteudo = conteudo_bytes.decode("utf-8-sig", errors="replace")
        primeira_linha = conteudo.splitlines()[0] if conteudo else ""
        delimitador = ";" if ";" in primeira_linha else ","

        leitor_csv = csv.DictReader(io.StringIO(conteudo), delimiter=delimitador)
        regras = carregar_regras_validadores()

        itens_preview = []
        aprovados_para_banco = []
        total_notas = 0
        total_bruto = 0.0
        total_liquido = 0.0
        total_aprovados = 0
        total_recusados = 0

        concentracao_lote_sacado = {}
        concentracao_lote_cedente = {}
        chaves_vistas_no_lote = set()

        base_carteira = VALOR_TOTAL_ESTOQUE if VALOR_TOTAL_ESTOQUE > 0 else 1000000.0
        teto_sacado = base_carteira * (regras["percentual_concentracao_sacado"] / 100.0)
        teto_cedente = base_carteira * (regras["percentual_concentracao_cedente"] / 100.0)

        for linha in leitor_csv:
            total_notas += 1
            linha = _normalizar_chaves(linha)

            id_nota = str(
                linha.get("nu_documento")
                or linha.get("id")
                or linha.get("id_nota")
                or linha.get("id_documento")
                or linha.get("documento")
                or linha.get("operacao_id")
                or linha.get("numero_nota")
                or linha.get("id_recebivel")
                or f"NF-{total_notas}"
            ).strip()

            cedente = str(
                linha.get("doc_cedente")
                or linha.get("cedente")
                or linha.get("cnpj_cedente")
                or linha.get("cedente_cnpj")
                or CEDENTE_PADRAO
            ).strip()

            chave_duplicidade = f"{cedente}_{id_nota}"

            sacado_exibicao = str(
                linha.get("nome_sacado")
                or linha.get("sacado")
                or linha.get("doc_sacado")
                or linha.get("cnpj_sacado")
                or linha.get("sacado_cnpj")
                or "Sacado Não Informado"
            ).strip()

            doc_sacado_bruto = (
                linha.get("doc_sacado")
                or linha.get("cnpj_sacado")
                or linha.get("sacado_cnpj")
                or ""
            )
            digitos_cnpj_sacado = _apenas_digitos(doc_sacado_bruto)

            if regras["agrupamento_sacado"] == "RAIZ_CNPJ" and len(digitos_cnpj_sacado) >= 8:
                chave_concentracao_sacado = digitos_cnpj_sacado[:8]
            else:
                chave_concentracao_sacado = digitos_cnpj_sacado or sacado_exibicao

            valor_face = _converter_float(linha.get("valor_nominal") or linha.get("valor") or linha.get("valor_face"), 0.0)
            prazo_dias = _calcular_prazo_dias(linha)

            situacao_cnpj = str(
                linha.get("situacao_cadastral_sacado")
                or linha.get("situacao_cadastral")
                or linha.get("status_cnpj")
                or linha.get("cnpj_ativo")
                or "ATIVA"
            ).strip().upper()

            tipo_recebivel = str(
                linha.get("tipo_recebivel")
                or linha.get("tipo")
                or linha.get("especie")
                or "Duplicata"
            ).strip()

            total_bruto += valor_face
            aprovado = True
            motivo_recusa = None

            if chave_duplicidade in ESTOQUE_IDS or chave_duplicidade in chaves_vistas_no_lote:
                aprovado = False
                motivo_recusa = "Título já adquirido anteriormente na base histórica ou duplicado neste lote (idempotência)."
            elif regras["cnpj_valido_ativo"] and doc_sacado_bruto and len(digitos_cnpj_sacado) != 14:
                aprovado = False
                motivo_recusa = f"CNPJ do sacado inválido ({doc_sacado_bruto}). Deve conter 14 dígitos numéricos."
            elif regras["situacao_cadastral_ativo"] and (
                situacao_cnpj in ("INATIVO", "INATIVA", "BAIXADO", "BAIXADA", "SUSPENSO", "SUSPENSA", "INAPTO", "INAPTA", "NULO")
                or (regras["situacoes_aceitas"] and situacao_cnpj not in regras["situacoes_aceitas"] and not (situacao_cnpj == "ATIVO" and "ATIVA" in regras["situacoes_aceitas"]))
            ):
                aprovado = False
                motivo_recusa = f"CNPJ do sacado com situação cadastral '{situacao_cnpj}'. Situações aceitas: {', '.join(regras['situacoes_aceitas'])}."
            elif regras["tipo_recebivel_ativo"] and tipo_recebivel.upper() not in regras["tipos_aceitos"]:
                aprovado = False
                motivo_recusa = f"Tipo de recebível '{tipo_recebivel}' não elegível. Aceitos: {', '.join(regras['tipos_aceitos'])}."
            elif regras["nao_vencida_ativo"] and prazo_dias < 0:
                aprovado = False
                motivo_recusa = f"Título já vencido ({abs(prazo_dias)} dias em atraso)."
            elif regras["valor_minimo_ativo"] and valor_face < regras["valor_minimo"]:
                aprovado = False
                motivo_recusa = f"Valor de face ({_formatar_moeda(valor_face)}) abaixo do mínimo exigido de {_formatar_moeda(regras['valor_minimo'])}."
            elif regras["prazo_minimo_ativo"] and prazo_dias < regras["prazo_minimo_dias"]:
                aprovado = False
                motivo_recusa = f"Prazo de vencimento ({prazo_dias} dias) inferior ao prazo mínimo de {regras['prazo_minimo_dias']} dias configurado no FIDC."
            elif regras["prazo_maximo_ativo"] and prazo_dias > regras["prazo_maximo_dias"]:
                aprovado = False
                motivo_recusa = f"Prazo de vencimento ({prazo_dias} dias) ultrapassa o limite máximo de {regras['prazo_maximo_dias']} dias do FIDC."
            elif regras["concentracao_sacado_ativo"] and (
                CONCENTRACAO_HISTORICA.get(chave_concentracao_sacado, 0.0) + concentracao_lote_sacado.get(chave_concentracao_sacado, 0.0) + valor_face
            ) > teto_sacado:
                aprovado = False
                motivo_recusa = f"Sacado ultrapassou o limite de concentração de {regras['percentual_concentracao_sacado']}% da carteira ({_formatar_moeda(teto_sacado)})."
            elif regras["concentracao_cedente_ativo"] and (
                CONCENTRACAO_CEDENTE_HISTORICA.get(cedente, 0.0) + concentracao_lote_cedente.get(cedente, 0.0) + valor_face
            ) > teto_cedente:
                aprovado = False
                motivo_recusa = f"Cedente ultrapassou o limite de concentração de {regras['percentual_concentracao_cedente']}% da carteira ({_formatar_moeda(teto_cedente)})."

            valor_face_fmt = _formatar_moeda(valor_face)

            if aprovado:
                prazo_calc = max(0, prazo_dias)
                taxa_mensal = regras["taxa_desconto_mensal"]
                fator_desconto = taxa_mensal * (prazo_calc / regras["base_dias"])
                desconto_valor = valor_face * fator_desconto
                valor_liq = max(0.0, valor_face - desconto_valor)

                total_liquido += valor_liq
                total_aprovados += 1
                concentracao_lote_sacado[chave_concentracao_sacado] = concentracao_lote_sacado.get(chave_concentracao_sacado, 0.0) + valor_face
                concentracao_lote_cedente[cedente] = concentracao_lote_cedente.get(cedente, 0.0) + valor_face
                chaves_vistas_no_lote.add(chave_duplicidade)
                ESTOQUE_IDS.add(chave_duplicidade)

                aprovados_para_banco.append((chave_duplicidade, id_nota, sacado_exibicao, valor_face_fmt, "APROVADO", ""))

                if len(itens_preview) < LIMITE_ITENS_RESPOSTA_JSON:
                    itens_preview.append({
                        "id": id_nota, "sacado": sacado_exibicao, "valorFace": valor_face_fmt, "prazo": f"{prazo_dias} dias",
                        "desconto": f"{_formatar_moeda(desconto_valor)} ({(fator_desconto * 100):.2f}%)", "valorLiquido": _formatar_moeda(valor_liq),
                        "status": "APROVADO", "motivoRecusa": None
                    })
            else:
                total_recusados += 1
                if len(itens_preview) < LIMITE_ITENS_RESPOSTA_JSON:
                    itens_preview.append({
                        "id": id_nota, "sacado": sacado_exibicao, "valorFace": valor_face_fmt, "prazo": f"{prazo_dias} dias",
                        "desconto": "-", "valorLiquido": "-", "status": "RECUSADO", "motivoRecusa": motivo_recusa
                    })

        resultado = {
            "resumo": {
                "totalNotas": total_notas, "totalBruto": _formatar_moeda(total_bruto),
                "totalLiquido": _formatar_moeda(total_liquido), "totalRecusadas": total_recusados
            },
            "itens": itens_preview
        }
        return resultado, aprovados_para_banco, None
    except Exception as e:
        logging.error(f"EVENT=MOTOR_EXCECAO TIPO={type(e).__name__}")
        return None, [], "Erro ao processar o arquivo CSV. Verifique a formatação do arquivo."
