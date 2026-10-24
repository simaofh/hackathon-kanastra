/**
 * Portal Antecipe - Hackathon Kanastra
 * Integração Frontend com API em Python + Motor de Regras Dinâmico
 */

const CONFIG = {
  API_URL: "http://localhost:8000/api/analisar-lote",
  CONFIG_URL: "http://localhost:8000/api/configuracoes",
  FILE_FIELD_NAME: "lote",
  MAX_DOM_ROWS: 500
};

const NOMES_AMIGAVEIS_VALIDADORES = {
  VALOR_MINIMO: "Valor Mínimo do Título (VALOR_MINIMO)",
  PRAZO_MAXIMO: "Prazo Máximo de Vencimento (PRAZO_MAXIMO)",
  PRAZO_MINIMO: "Prazo Mínimo de Vencimento (PRAZO_MINIMO)",
  CONCENTRACAO_MAXIMA_SACADO: "Concentração Máxima por Sacado (CONCENTRACAO_MAXIMA_SACADO)",
  CONCENTRACAO_MAXIMA_CEDENTE: "Concentração Máxima por Cedente (CONCENTRACAO_MAXIMA_CEDENTE)",
  SITUACAO_CADASTRAL_SACADO: "Situação Cadastral do Sacado (SITUACAO_CADASTRAL_SACADO)",
  TIPO_RECEBIVEL: "Tipos de Recebíveis Aceitos (TIPO_RECEBIVEL)",
  CNPJ_SACADO_VALIDO: "Validação de CNPJ do Sacado (CNPJ_SACADO_VALIDO)",
  NAO_VENCIDA: "Bloquear Duplicatas Vencidas (NAO_VENCIDA)"
};

const LABELS_PARAMETROS = {
  valor_minimo: "Valor Mínimo Aceito (R$)",
  prazo_maximo_dias: "Prazo Máximo Permitido (em dias)",
  prazo_minimo_dias: "Prazo Mínimo Permitido (em dias)",
  percentual_maximo: "Limite Máximo de Concentração (%)",
  agrupamento: "Critério de Agrupamento (ex: RAIZ_CNPJ ou CNPJ_COMPLETO)",
  situacoes_aceitas: "Situações Cadastrais Aceitas (separadas por vírgula)",
  tipos_aceitos: "Tipos de Recebíveis Aceitos (separados por vírgula)"
};

let ultimoArquivoCSV = null;
let dadosConfiguracaoCompleta = null;
let indiceValidadorAtual = 0;

const dropZone = document.getElementById("dropZone");
const csvInput = document.getElementById("csvInput");
const btnDemo = document.getElementById("btnDemo");
const avisoAmostragem = document.getElementById("avisoAmostragem");

// Elementos do Modal de Regras
const modalConfig = document.getElementById("modalConfig");
const btnAbrirConfig = document.getElementById("btnAbrirConfig");
const btnFecharModal = document.getElementById("btnFecharModal");
const btnCancelarModal = document.getElementById("btnCancelarModal");
const selectValidador = document.getElementById("selectValidador");
const painelParametrosValidador = document.getElementById("painelParametrosValidador");
const inputTaxaMensal = document.getElementById("inputTaxaMensal");
const btnSalvarRegras = document.getElementById("btnSalvarRegras");

if (dropZone && csvInput) {
  dropZone.addEventListener("click", () => csvInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--green-medium)";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "var(--border-card)";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--border-card)";
    if (e.dataTransfer.files.length > 0) {
      ultimoArquivoCSV = e.dataTransfer.files[0];
      enviarLoteParaBackend(ultimoArquivoCSV);
    }
  });

  csvInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      ultimoArquivoCSV = e.target.files[0];
      enviarLoteParaBackend(ultimoArquivoCSV);
      csvInput.value = "";
    }
  });
}

if (btnDemo) {
  btnDemo.addEventListener("click", () => {
    const dadosExemplo = {
      resumo: {
        totalNotas: 3,
        totalBruto: "R$ 48.000,00",
        totalLiquido: "R$ 32.095,00",
        totalRecusadas: 1
      },
      itens: [
        {
          id: "NF-8921",
          sacado: "Distribuidora Minas Ltda",
          valorFace: "R$ 15.000,00",
          prazo: "30 dias",
          desconto: "R$ 300,00 (2.00%)",
          valorLiquido: "R$ 14.700,00",
          status: "APROVADO",
          motivoRecusa: null
        },
        {
          id: "NF-8922",
          sacado: "Supermercados Triângulo S.A.",
          valorFace: "R$ 18.000,00",
          prazo: "45 dias",
          desconto: "R$ 540,00 (3.00%)",
          valorLiquido: "R$ 17.460,00",
          status: "APROVADO",
          motivoRecusa: null
        },
        {
          id: "NF-8923",
          sacado: "Comércio Varejista do Cerrado",
          valorFace: "R$ 15.000,00",
          prazo: "210 dias",
          desconto: "-",
          valorLiquido: "-",
          status: "RECUSADO",
          motivoRecusa: "Prazo de vencimento (210 dias) ultrapassa o limite máximo de 180 dias do FIDC."
        }
      ]
    };
    renderizarResultados(dadosExemplo);
  });
}

async function enviarLoteParaBackend(arquivoCSV) {
  if (!arquivoCSV.name.toLowerCase().endsWith(".csv")) {
    alert("Por favor, selecione um arquivo no formato .csv");
    return;
  }

  const formData = new FormData();
  formData.append(CONFIG.FILE_FIELD_NAME, arquivoCSV);

  mostrarCarregando(arquivoCSV.name);

  try {
    const resposta = await fetch(CONFIG.API_URL, {
      method: "POST",
      body: formData
    });

    if (!resposta.ok) {
      const errJson = await resposta.json().catch(() => ({}));
      throw new Error(errJson.erro || `Erro HTTP ${resposta.status}`);
    }

    const dados = await resposta.json();
    renderizarResultados(dados);

  } catch (erro) {
    console.warn("Falha na chamada ao backend:", erro);
    document.getElementById("tabelaCorpo").innerHTML = `
      <tr>
        <td colspan="8" class="empty-state" style="color: var(--danger-primary);">
          <strong>Erro ao conectar com o Backend:</strong> ${erro.message}<br>
          Verifique se o servidor Python está rodando na porta 8000 (<code>python app.py</code>).
        </td>
      </tr>
    `;
  }
}

function renderizarResultados(resultado) {
  if (!resultado || !resultado.resumo || !Array.isArray(resultado.itens)) {
    console.error("Formato JSON recebido incompatível:", resultado);
    return;
  }

  document.getElementById("totalNotas").textContent = resultado.resumo.totalNotas;
  document.getElementById("totalBruto").textContent = resultado.resumo.totalBruto;
  document.getElementById("totalLiquido").textContent = resultado.resumo.totalLiquido;
  document.getElementById("totalRecusadas").textContent = resultado.resumo.totalRecusadas;

  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = "";

  if (avisoAmostragem) {
    if (resultado.resumo.totalNotas > resultado.itens.length) {
      avisoAmostragem.style.display = "block";
      avisoAmostragem.innerHTML = `
        <strong>✓ Processamento em Lote Concluído:</strong> Todas as <strong>${resultado.resumo.totalNotas}</strong> duplicatas foram validadas e contabilizadas nos indicadores acima. Exibindo amostra das primeiras <strong>${resultado.itens.length}</strong> notas na tabela para preservar a performance da tela.
      `;
    } else {
      avisoAmostragem.style.display = "none";
    }
  }

  if (resultado.itens.length === 0) {
    corpoTabela.innerHTML = `
      <tr>
        <td colspan="8" class="empty-state">O arquivo enviado não contém linhas válidas.</td>
      </tr>
    `;
    return;
  }

  const fragment = document.createDocumentFragment();
  const itensExibidos = resultado.itens.slice(0, CONFIG.MAX_DOM_ROWS);

  itensExibidos.forEach(item => {
    const tr = document.createElement("tr");
    const ehAprovado = String(item.status).toUpperCase() === "APROVADO";
    const statusBadge = ehAprovado ? "badge-success" : "badge-error";

    const diagnosticoVisual = ehAprovado
      ? '<span class="approved-text">✓ Elegível para antecipação imediata</span>'
      : `<div class="reason-box">${item.motivoRecusa || item.motivo || "Critério de elegibilidade não atendido."}</div>`;

    tr.innerHTML = `
      <td><strong>${item.id || "-"}</strong></td>
      <td>${item.sacado || "-"}</td>
      <td>${item.valorFace || "-"}</td>
      <td>${item.prazo || "-"}</td>
      <td>${item.desconto || "-"}</td>
      <td style="color: ${ehAprovado ? 'var(--green-medium)' : 'inherit'}; font-weight: 600;">
        ${item.valorLiquido || "-"}
      </td>
      <td>
        <span class="badge ${statusBadge}">
          ${item.status}
        </span>
      </td>
      <td>${diagnosticoVisual}</td>
    `;
    fragment.appendChild(tr);
  });

  corpoTabela.appendChild(fragment);
}

function mostrarCarregando(nomeArquivo) {
  if (avisoAmostragem) avisoAmostragem.style.display = "none";
  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = `
    <tr>
      <td colspan="8" style="text-align: center; color: var(--green-primary); padding: 44px;">
        <p style="font-size: 1.05rem; font-weight: 700;">⏳ Processando lote "${nomeArquivo}"...</p>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 6px;">
          Executando motor de regras dinâmico e checagem de duplicidade em O(1)...
        </p>
      </td>
    </tr>
  `;
}

/* =========================================================================
 * LÓGICA DO POP-UP DE CONFIGURAÇÃO DE VALIDADORES (/api/configuracoes)
 * ========================================================================= */

if (btnAbrirConfig) {
  btnAbrirConfig.addEventListener("click", async () => {
    modalConfig.style.display = "flex";
    painelParametrosValidador.innerHTML = "<p>Carregando regras do FIDC...</p>";

    try {
      const resp = await fetch(CONFIG.CONFIG_URL);
      if (!resp.ok) throw new Error("Falha ao buscar configurações no servidor.");
      dadosConfiguracaoCompleta = await resp.json();

      if (!dadosConfiguracaoCompleta.validadores) {
        dadosConfiguracaoCompleta = {
          fundo: { nome: "ANTECIPE FIDC", cnpj: "92.234.400/0001-80" },
          validadores: Array.isArray(dadosConfiguracaoCompleta) ? dadosConfiguracaoCompleta : [],
          precificacao: { metodo: "DESCONTO_SIMPLES", taxa_mensal_percentual: 2.0, base_dias: 30 }
        };
      }

      if (dadosConfiguracaoCompleta.precificacao && inputTaxaMensal) {
        inputTaxaMensal.value = dadosConfiguracaoCompleta.precificacao.taxa_mensal_percentual ?? 2.0;
      }

      popularDropdownValidadores();
    } catch (erro) {
      painelParametrosValidador.innerHTML = `
        <p style="color: var(--danger-primary);">Erro ao carregar regras: ${erro.message}</p>
      `;
    }
  });
}

function fecharModalConfig() {
  if (modalConfig) modalConfig.style.display = "none";
}

if (btnFecharModal) btnFecharModal.addEventListener("click", fecharModalConfig);
if (btnCancelarModal) btnCancelarModal.addEventListener("click", fecharModalConfig);

function popularDropdownValidadores() {
  selectValidador.innerHTML = "";
  const lista = dadosConfiguracaoCompleta.validadores || [];

  lista.forEach((val, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    const statusIcon = val.ativo ? "🟢" : "⚪";
    const nomeAmigavel = NOMES_AMIGAVEIS_VALIDADORES[val.codigo] || val.codigo;
    opt.textContent = `${statusIcon} ${nomeAmigavel}`;
    selectValidador.appendChild(opt);
  });

  indiceValidadorAtual = 0;
  selectValidador.value = "0";
  renderizarFormularioValidador(0);
}

if (selectValidador) {
  selectValidador.addEventListener("change", (e) => {
    guardarEdicoesNoObjetoEmMemoria(indiceValidadorAtual);
    indiceValidadorAtual = parseInt(e.target.value, 10);
    renderizarFormularioValidador(indiceValidadorAtual);
  });
}

function renderizarFormularioValidador(idx) {
  const validador = dadosConfiguracaoCompleta.validadores[idx];
  if (!validador) return;

  const parametros = validador.parametros || {};
  const chavesParametros = Object.keys(parametros);

  let html = `
    <div class="toggle-row">
      <span>Status da Regra (${validador.codigo})</span>
      <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin: 0;">
        <input type="checkbox" id="chkValidadorAtivo" ${validador.ativo ? "checked" : ""} style="width: 18px; height: 18px;">
        <strong>Ativo</strong>
      </label>
    </div>
  `;

  if (chavesParametros.length === 0) {
    html += `
      <p style="font-size: 0.85rem; color: var(--text-muted);">
        Este validador não possui limites numéricos adicionais. Basta ativá-lo ou desativá-lo na chave acima.
      </p>
    `;
  } else {
    chavesParametros.forEach(chave => {
      const valorAtual = parametros[chave];
      const labelAmigavel = LABELS_PARAMETROS[chave] || chave.replace(/_/g, " ");

      if (Array.isArray(valorAtual)) {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="text" class="form-control input-parametro-dinamico"
              data-key="${chave}" data-type="array"
              value="${valorAtual.join(", ")}">
          </div>
        `;
      } else if (typeof valorAtual === "number") {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="number" step="any" class="form-control input-parametro-dinamico"
              data-key="${chave}" data-type="number"
              value="${valorAtual}">
          </div>
        `;
      } else {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="text" class="form-control input-parametro-dinamico"
              data-key="${chave}" data-type="string"
              value="${valorAtual}">
          </div>
        `;
      }
    });
  }

  painelParametrosValidador.innerHTML = html;

  const chkAtivo = document.getElementById("chkValidadorAtivo");
  if (chkAtivo) {
    chkAtivo.addEventListener("change", () => {
      validador.ativo = chkAtivo.checked;
      const opt = selectValidador.options[idx];
      if (opt) {
        const nomeAmigavel = NOMES_AMIGAVEIS_VALIDADORES[validador.codigo] || validador.codigo;
        opt.textContent = `${validador.ativo ? "🟢" : "⚪"} ${nomeAmigavel}`;
      }
    });
  }
}

function guardarEdicoesNoObjetoEmMemoria(idx) {
  if (!dadosConfiguracaoCompleta || !dadosConfiguracaoCompleta.validadores[idx]) return;
  const validador = dadosConfiguracaoCompleta.validadores[idx];

  const chkAtivo = document.getElementById("chkValidadorAtivo");
  if (chkAtivo) {
    validador.ativo = chkAtivo.checked;
  }

  if (!validador.parametros) validador.parametros = {};

  document.querySelectorAll(".input-parametro-dinamico").forEach(input => {
    const chave = input.getAttribute("data-key");
    const tipo = input.getAttribute("data-type");

    if (tipo === "number") {
      validador.parametros[chave] = parseFloat(input.value) || 0;
    } else if (tipo === "array") {
      validador.parametros[chave] = input.value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);
    } else {
      validador.parametros[chave] = input.value.trim();
    }
  });

  if (dadosConfiguracaoCompleta.precificacao && inputTaxaMensal) {
    dadosConfiguracaoCompleta.precificacao.taxa_mensal_percentual = parseFloat(inputTaxaMensal.value) || 2.0;
  }
}

if (btnSalvarRegras) {
  btnSalvarRegras.addEventListener("click", async () => {
    guardarEdicoesNoObjetoEmMemoria(indiceValidadorAtual);

    const textoOriginal = btnSalvarRegras.textContent;
    btnSalvarRegras.textContent = "Salvando...";
    btnSalvarRegras.disabled = true;

    try {
      const resp = await fetch(CONFIG.CONFIG_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosConfiguracaoCompleta)
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.erro || "Falha ao salvar configurações.");
      }

      fecharModalConfig();

      // Se já houver um arquivo CSV carregado na sessão, reprocessa automaticamente com as novas regras
      if (ultimoArquivoCSV) {
        enviarLoteParaBackend(ultimoArquivoCSV);
      } else {
        alert("Regras atualizadas com sucesso no validadores_antecipe_3.json!");
      }
    } catch (erro) {
      alert("Erro ao salvar regras: " + erro.message);
    } finally {
      btnSalvarRegras.textContent = textoOriginal;
      btnSalvarRegras.disabled = false;
    }
  });
}
