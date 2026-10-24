import csv
import io
import json
import logging
import os
from datetime import datetime
from banco import carregar_estoque_banco

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Conjuntos em memória para busca O(1) de duplicidade e concentração contra o estoque
ESTOQUE_IDS = set()
CONCENTRACAO_HISTORICA = {}

LIMITE_ITENS_RESPOSTA_JSON = 500
CEDENTE_PADRAO = "00000000000191"


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


def _calcular_prazo_dias(linha):
    prazo_str = linha.get("prazo") or linha.get("prazo_dias") or linha.get("dias")
    if prazo_str is not None and str(prazo_str).strip() != "":
        try:
            return int(float(str(prazo_str).strip()))
        except ValueError:
            pass

    vencimento_str = linha.get("data_vencimento") or linha.get("vencimento")
    emissao_str = linha.get("data_emissao") or linha.get("emissao")
    if vencimento_str:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                dt_venc = datetime.strptime(str(vencimento_str).strip()[:10], fmt)
                if emissao_str:
                    dt_base = datetime.strptime(str(emissao_str).strip()[:10], fmt)
                else:
                    dt_base = datetime.now()
                return max(1, (dt_venc - dt_base).days)
            except ValueError:
                continue
    return 30


def carregar_estoque_em_memoria():
    """Carrega o estoque_antecipe.csv e os registros do SQLite para garantir idempotência em O(1)."""
    ESTOQUE_IDS.update(carregar_estoque_banco())

    caminhos_possiveis = [
        os.path.join(BASE_DIR, "estoque_antecipe.csv"),
        os.path.join(BASE_DIR, "data", "estoque_antecipe.csv"),
        "estoque_antecipe.csv"
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                with open(caminho, mode='r', encoding='utf-8-sig', errors='replace') as f:
                    primeira_linha = f.readline()
                    delimitador = ';' if ';' in primeira_linha else ','
                    f.seek(0)
                    reader = csv.DictReader(f, delimiter=delimitador)
                    for row in reader:
                        id_nota = (
                            row.get("id")
                            or row.get("id_nota")
                            or row.get("operacao_id")
                            or row.get("documento")
                            or row.get("numero_nota")
                            or row.get("id_recebivel")
                        )
                        cedente = (
                            row.get("cedente")
                            or row.get("cnpj_cedente")
                            or row.get("cedente_cnpj")
                            or CEDENTE_PADRAO
                        )
                        if id_nota:
                            id_limpo = str(id_nota).strip()
                            cedente_limpo = str(cedente).strip()
                            ESTOQUE_IDS.add(id_limpo)
                            ESTOQUE_IDS.add(f"{cedente_limpo}_{id_limpo}")

                        sacado = (
                            row.get("sacado")
                            or row.get("nome_sacado")
                            or row.get("cnpj_sacado")
                            or row.get("sacado_cnpj")
                        )
                        valor = _converter_float(
                            row.get("valor") or row.get("valor_face") or row.get("valor_nominal")
                        )
                        if sacado and valor > 0:
                            chave_sacado = str(sacado).strip()
                            CONCENTRACAO_HISTORICA[chave_sacado] = (
                                CONCENTRACAO_HISTORICA.get(chave_sacado, 0.0) + valor
                            )

                logging.info(f"EVENT=ESTOQUE_CSV_CARREGADO STATUS=SUCESSO CHAVES_TOTAIS={len(ESTOQUE_IDS)}")
                return
            except Exception as e:
                logging.error(f"EVENT=ESTOQUE_CSV_ERRO TIPO={type(e).__name__}")


def carregar_regras_validadores():
    """Lê as regras ativas do arquivo validadores.json sem necessidade de redeploy."""
    regras = {
        "valor_minimo_ativo": True,
        "valor_minimo": 1000.0,
        "prazo_maximo_ativo": True,
        "prazo_maximo_dias": 90,
        "concentracao_ativo": True,
        "limite_concentracao_sacado": 100000.0,
        "cnpj_ativo_obrigatorio": True,
        "taxa_desconto_mensal": 0.025
    }

    caminhos_possiveis = [
        os.path.join(BASE_DIR, "validadores.json"),
        os.path.join(BASE_DIR, "data", "validadores.json"),
        "validadores.json"
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                with open(caminho, mode='r', encoding='utf-8-sig') as f:
                    dados = json.load(f)

                lista_val = dados if isinstance(dados, list) else dados.get("validadores", [])
                for val in lista_val:
                    codigo = str(val.get("codigo", "")).upper()
                    ativo = bool(val.get("ativo", False))
                    params = val.get("parametros") or {}

                    if "VALOR" in codigo and "MIN" in codigo:
                        regras["valor_minimo_ativo"] = ativo
                        if ativo:
                            regras["valor_minimo"] = float(
                                params.get("valor") or params.get("valor_minimo") or regras["valor_minimo"]
                            )
                    elif "PRAZO" in codigo:
                        regras["prazo_maximo_ativo"] = ativo
                        if ativo:
                            regras["prazo_maximo_dias"] = int(
                                params.get("dias") or params.get("prazo_maximo") or regras["prazo_maximo_dias"]
                            )
                    elif "CONCENTRACAO" in codigo:
                        regras["concentracao_ativo"] = ativo
                        if ativo:
                            regras["limite_concentracao_sacado"] = float(
                                params.get("limite")
                                or params.get("valor_maximo")
                                or regras["limite_concentracao_sacado"]
                            )
                    elif "CNPJ" in codigo or "SITUACAO" in codigo:
                        regras["cnpj_ativo_obrigatorio"] = ativo

                logging.info("EVENT=VALIDADORES_CARREGADOS STATUS=SUCESSO")
                break
            except Exception as e:
                logging.error(f"EVENT=VALIDADORES_ERRO TIPO={type(e).__name__}")

    return regras


# Inicializa o estoque (Banco SQLite + CSV Histórico) ao carregar o módulo
carregar_estoque_em_memoria()


def _formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def processar_arquivo_lote(file_storage):
    """
    Processa o CSV de lote, valida as regras do FIDC,
    calcula o desconto simples e devolve os dados estruturados para o frontend e para o banco.
    """
    try:
        conteudo_bytes = file_storage.read()
        conteudo = conteudo_bytes.decode('utf-8-sig', errors='replace')

        primeira_linha = conteudo.splitlines()[0] if conteudo else ""
        delimitador = ';' if ';' in primeira_linha else ','

        leitor_csv = csv.DictReader(io.StringIO(conteudo), delimiter=delimitador)
        regras = carregar_regras_validadores()

        itens_preview = []
        aprovados_para_banco = []
        total_notas = 0
        total_bruto = 0.0
        total_liquido = 0.0
        total_aprovados = 0
        total_recusados = 0

        concentracao_lote = {}
        chaves_vistas_no_lote = set()

        for linha in leitor_csv:
            total_notas += 1

            id_nota = str(
                linha.get("id")
                or linha.get("id_nota")
                or linha.get("id_documento")
                or linha.get("documento")
                or linha.get("operacao_id")
                or linha.get("numero_nota")
                or linha.get("id_recebivel")
                or f"NF-{total_notas}"
            ).strip()

            cedente = str(
                linha.get("cedente")
                or linha.get("cnpj_cedente")
                or linha.get("cedente_cnpj")
                or CEDENTE_PADRAO
            ).strip()

            chave_duplicidade = f"{cedente}_{id_nota}"

            sacado = str(
                linha.get("sacado")
                or linha.get("nome_sacado")
                or linha.get("cnpj_sacado")
                or linha.get("sacado_cnpj")
                or "Sacado Não Informado"
            ).strip()

            valor_face = _converter_float(
                linha.get("valor") or linha.get("valor_face") or linha.get("valor_nominal"),
                0.0
            )
            prazo_dias = _calcular_prazo_dias(linha)

            situacao_cnpj = str(
                linha.get("situacao_cadastral")
                or linha.get("status_cnpj")
                or linha.get("cnpj_ativo")
                or "ATIVO"
            ).strip().upper()

            total_bruto += valor_face
            aprovado = True
            motivo_recusa = None

            # Regra 1: Idempotência / Duplicidade (checa ID e Chave Composta em O(1))
            if (
                id_nota in ESTOQUE_IDS
                or chave_duplicidade in ESTOQUE_IDS
                or id_nota in chaves_vistas_no_lote
                or chave_duplicidade in chaves_vistas_no_lote
            ):
                aprovado = False
                motivo_recusa = (
                    "Título já adquirido anteriormente na base histórica ou duplicado neste lote (idempotência)."
                )

            # Regra 2: Situação Cadastral / CNPJ Ativo
            elif regras["cnpj_ativo_obrigatorio"] and situacao_cnpj in (
                "INATIVO", "BAIXADO", "SUSPENSO", "INAPTO", "FALSE", "0", "NAO", "NÃO"
            ):
                aprovado = False
                motivo_recusa = (
                    f"CNPJ com situação cadastral irregular ({situacao_cnpj}). Apenas CNPJs ativos são elegíveis."
                )

            # Regra 3: Valor Mínimo
            elif regras["valor_minimo_ativo"] and valor_face < regras["valor_minimo"]:
                aprovado = False
                motivo_recusa = (
                    f"Valor de face ({_formatar_moeda(valor_face)}) abaixo do mínimo exigido "
                    f"de {_formatar_moeda(regras['valor_minimo'])}."
                )

            # Regra 4: Prazo Máximo de Vencimento
            elif regras["prazo_maximo_ativo"] and prazo_dias > regras["prazo_maximo_dias"]:
                aprovado = False
                motivo_recusa = (
                    f"Prazo de vencimento ({prazo_dias} dias) ultrapassa o limite máximo "
                    f"de {regras['prazo_maximo_dias']} dias do FIDC."
                )

            # Regra 5: Limite de Concentração por Sacado (estoque histórico + lote atual)
            elif regras["concentracao_ativo"] and (
                CONCENTRACAO_HISTORICA.get(sacado, 0.0) + concentracao_lote.get(sacado, 0.0) + valor_face
            ) > regras["limite_concentracao_sacado"]:
                aprovado = False
                motivo_recusa = (
                    f"O sacado atingiu o limite máximo de concentração de risco "
                    f"({_formatar_moeda(regras['limite_concentracao_sacado'])}) permitido para a carteira."
                )

            valor_face_fmt = _formatar_moeda(valor_face)

            if aprovado:
                taxa_mensal = regras["taxa_desconto_mensal"]
                fator_desconto = taxa_mensal * (prazo_dias / 30.0)
                desconto_valor = valor_face * fator_desconto
                valor_liq = max(0.0, valor_face - desconto_valor)

                total_liquido += valor_liq
                total_aprovados += 1
                concentracao_lote[sacado] = concentracao_lote.get(sacado, 0.0) + valor_face

                chaves_vistas_no_lote.add(id_nota)
                chaves_vistas_no_lote.add(chave_duplicidade)
                ESTOQUE_IDS.add(id_nota)
                ESTOQUE_IDS.add(chave_duplicidade)

                # Tupla de 6 posições exata para o executemany do banco.py
                aprovados_para_banco.append(
                    (chave_duplicidade, id_nota, sacado, valor_face_fmt, "APROVADO", "")
                )

                if len(itens_preview) < LIMITE_ITENS_RESPOSTA_JSON:
                    itens_preview.append({
                        "id": id_nota,
                        "id_documento": id_nota,
                        "chave_duplicidade": chave_duplicidade,
                        "sacado": sacado,
                        "valorFace": valor_face_fmt,
                        "valor_face": valor_face_fmt,
                        "prazo": f"{prazo_dias} dias",
                        "desconto": f"{_formatar_moeda(desconto_valor)} ({(fator_desconto * 100):.2f}%)",
                        "valorLiquido": _formatar_moeda(valor_liq),
                        "status": "APROVADO",
                        "motivoRecusa": None,
                        "motivo": ""
                    })
            else:
                total_recusados += 1
                if len(itens_preview) < LIMITE_ITENS_RESPOSTA_JSON:
                    itens_preview.append({
                        "id": id_nota,
                        "id_documento": id_nota,
                        "chave_duplicidade": chave_duplicidade,
                        "sacado": sacado,
                        "valorFace": valor_face_fmt,
                        "valor_face": valor_face_fmt,
                        "prazo": f"{prazo_dias} dias",
                        "desconto": "-",
                        "valorLiquido": "-",
                        "status": "RECUSADO",
                        "motivoRecusa": motivo_recusa,
                        "motivo": motivo_recusa
                    })

        resultado = {
            "resumo": {
                "totalNotas": total_notas,
                "totalBruto": _formatar_moeda(total_bruto),
                "totalLiquido": _formatar_moeda(total_liquido),
                "totalRecusadas": total_recusados
            },
            "itens": itens_preview
        }

        return resultado, aprovados_para_banco, None

    except Exception as e:
        logging.error(f"EVENT=MOTOR_EXCECAO TIPO={type(e).__name__}")
        return None, [], "Erro ao processar o arquivo CSV. Verifique a formatação do arquivo."
