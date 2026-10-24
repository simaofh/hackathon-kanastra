const BASE_API = window.location.protocol === "file:" ? "http://localhost:8000" : "";

const CONFIG = {
  API_URL: `${BASE_API}/api/analisar-lote`,
  CONFIG_URL: `${BASE_API}/api/configuracoes`,
  RESET_CONFIG_URL: `${BASE_API}/api/configuracoes/reset`, // Rota de reset
  CACHE_URL: `${BASE_API}/api/limpar-cache`,
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
  agrupamento: "Critério de Agrupamento (ex: RAIZ_CNPJ)",
  situacoes_aceitas: "Situações Cadastrais Aceitas",
  tipos_aceitos: "Tipos de Recebíveis Aceitos"
};

let ultimoArquivoCSV = null;
let ultimoResultadoLote = null;
let filtroStatusAtual = "TODOS";
let dadosConfiguracaoCompleta = null;
let indiceValidadorAtual = 0;

const dropZone = document.getElementById("dropZone");
const csvInput = document.getElementById("csvInput");
const btnDemo = document.getElementById("btnDemo");
const btnLimparCache = document.getElementById("btnLimparCache");
const avisoAmostragem = document.getElementById("avisoAmostragem");
const toastFeedback = document.getElementById("toastFeedback");
const inputBuscaEmpresa = document.getElementById("inputBuscaEmpresa");

const secaoHome = document.getElementById("secaoHome");
const secaoOperacional = document.getElementById("secaoOperacional");
const btnNavHome = document.getElementById("btnNavHome");
const btnNavSimulador = document.getElementById("btnNavSimulador");
const btnNavRegras = document.getElementById("btnNavRegras");
const navLogoHome = document.getElementById("navLogoHome");

const cardIrUpload = document.getElementById("cardIrUpload");
const cardIrValidadores = document.getElementById("cardIrValidadores");
const cardIrDemo = document.getElementById("cardIrDemo");
const cardIrResetCache = document.getElementById("cardIrResetCache");

const modalConfig = document.getElementById("modalConfig");
const btnAbrirConfig = document.getElementById("btnAbrirConfig");
const btnFecharModal = document.getElementById("btnFecharModal");
const btnCancelarModal = document.getElementById("btnCancelarModal");
const selectValidador = document.getElementById("selectValidador");
const painelParametrosValidador = document.getElementById("painelParametrosValidador");
const inputTaxaMensal = document.getElementById("inputTaxaMensal");
const btnSalvarRegras = document.getElementById("btnSalvarRegras");
const btnResetarRegras = document.getElementById("btnResetarRegras");

function exibirToast(mensagem, isErro = false) {
  if (!toastFeedback) return;
  toastFeedback.style.display = "block";
  toastFeedback.style.backgroundColor = isErro ? "var(--danger-soft)" : "var(--green-soft)";
  toastFeedback.style.borderColor = isErro ? "var(--danger-border)" : "#6EE7B7";
  toastFeedback.style.color = isErro ? "var(--danger-text)" : "var(--green-text)";
  toastFeedback.textContent = mensagem;
  setTimeout(() => {
    toastFeedback.style.display = "none";
  }, 4500);
}

function irParaVisao(visao) {
  if (!secaoHome || !secaoOperacional) return;
  if (visao === "HOME") {
    secaoHome.style.display = "block";
    btnNavHome?.classList.add("active");
    btnNavSimulador?.classList.remove("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else if (visao === "SIMULADOR") {
    secaoHome.style.display = "none";
    btnNavHome?.classList.remove("active");
    btnNavSimulador?.classList.add("active");
    secaoOperacional.scrollIntoView({ behavior: "smooth" });
  }
}

btnNavHome?.addEventListener("click", () => irParaVisao("HOME"));
navLogoHome?.addEventListener("click", () => irParaVisao("HOME"));
btnNavSimulador?.addEventListener("click", () => irParaVisao("SIMULADOR"));
btnNavRegras?.addEventListener("click", () => abrirModalValidadores());

cardIrUpload?.addEventListener("click", () => {
  irParaVisao("SIMULADOR");
  csvInput?.click();
});
cardIrValidadores?.addEventListener("click", () => abrirModalValidadores());
cardIrDemo?.addEventListener("click", () => {
  irParaVisao("SIMULADOR");
  carregarDemonstracao();
});
cardIrResetCache?.addEventListener("click", () => acionarLimpezaDeCache());

async function acionarLimpezaDeCache() {
  try {
    const resp = await fetch(CONFIG.CACHE_URL, { method: "POST" });
    if (!resp.ok) throw new Error("Falha ao limpar cache no servidor.");
    const dados = await resp.json();

    ultimoResultadoLote = null;
    document.getElementById("totalNotas").textContent = "0";
    document.getElementById("totalBruto").textContent = "R$ 0,00";
    document.getElementById("totalLiquido").textContent = "R$ 0,00";
    document.getElementById("totalRecusadas").textContent = "0";
    if (avisoAmostragem) avisoAmostragem.style.display = "none";

    document.getElementById("tabelaCorpo").innerHTML = `
      <tr>
        <td colspan="8" class="empty-state">
          ✓ Cache de testes limpo! Você já pode reenviar o lote CSV ou testar novas regras sem bloqueio de idempotência.
        </td>
      </tr>
    `;
    exibirToast(dados.mensagem || "Cache de testes limpo com sucesso!");
  } catch (erro) {
    exibirToast("Erro ao limpar cache: " + erro.message, true);
  }
}

if (btnLimparCache) {
  btnLimparCache.addEventListener("click", acionarLimpezaDeCache);
}

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

function carregarDemonstracao() {
  const dadosExemplo = {
    resumo: {
      totalNotas: 4,
      totalBruto: "R$ 60.000,00",
      totalLiquido: "R$ 32.160,00",
      totalRecusadas: 2
    },
    itens: [
      { id: "NF-8921", sacado: "Distribuidora Minas Ltda", valorFace: "R$ 15.000,00", prazo: "30 dias", desconto: "R$ 300,00 (2.00%)", valorLiquido: "R$ 14.700,00", status: "APROVADO", motivoRecusa: null },
      { id: "NF-8922", sacado: "Supermercados Triângulo S.A.", valorFace: "R$ 18.000,00", prazo: "45 dias", desconto: "R$ 540,00 (3.00%)", valorLiquido: "R$ 17.460,00", status: "APROVADO", motivoRecusa: null },
      { id: "NF-8923", sacado: "Comércio Varejista do Cerrado", valorFace: "R$ 15.000,00", prazo: "210 dias", desconto: "-", valorLiquido: "-", status: "RECUSADO", motivoRecusa: "Prazo de vencimento (210 dias) ultrapassa o limite máximo de 180 dias do FIDC." },
      { id: "NF-8924", sacado: "Logística Brasil Central", valorFace: "R$ 12.000,00", prazo: "30 dias", desconto: "-", valorLiquido: "-", status: "RECUSADO", motivoRecusa: "CNPJ do sacado com situação cadastral 'INATIVA'." }
    ]
  };
  renderizarResultados(dadosExemplo);
}

if (btnDemo) {
  btnDemo.addEventListener("click", carregarDemonstracao);
}

async function enviarLoteParaBackend(arquivoCSV, limparCacheAntes = false) {
  if (!arquivoCSV.name.toLowerCase().endsWith(".csv")) {
    alert("Por favor, selecione um arquivo no formato .csv");
    return;
  }
  const formData = new FormData();
  formData.append(CONFIG.FILE_FIELD_NAME, arquivoCSV);
  if (limparCacheAntes) {
    formData.append("limpar_cache", "true");
  }

  mostrarCarregando(arquivoCSV.name);

  try {
    const resposta = await fetch(CONFIG.API_URL, { method: "POST", body: formData });
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
          Verifique se o servidor Python está rodando na porta 8000.
        </td>
      </tr>
    `;
  }
}

// ==== FILTROS E PESQUISA ====
document.querySelectorAll(".filter-chip").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-chip").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filtroStatusAtual = btn.getAttribute("data-status") || "TODOS";
    if (ultimoResultadoLote) {
      renderizarLinhasTabela(ultimoResultadoLote.itens);
    }
  });
});

if(inputBuscaEmpresa) {
  inputBuscaEmpresa.addEventListener("input", () => {
    if (ultimoResultadoLote) {
      renderizarLinhasTabela(ultimoResultadoLote.itens);
    }
  });
}

function renderizarResultados(resultado) {
  if (!resultado || !resultado.resumo || !Array.isArray(resultado.itens)) return;
  ultimoResultadoLote = resultado;
  document.getElementById("totalNotas").textContent = resultado.resumo.totalNotas;
  document.getElementById("totalBruto").textContent = resultado.resumo.totalBruto;
  document.getElementById("totalLiquido").textContent = resultado.resumo.totalLiquido;
  document.getElementById("totalRecusadas").textContent = resultado.resumo.totalRecusadas;

  if (avisoAmostragem) {
    if (resultado.resumo.totalNotas > resultado.itens.length) {
      avisoAmostragem.style.display = "block";
      avisoAmostragem.innerHTML = `<strong>✓ Processamento em Lote Concluído:</strong> Todas as ${resultado.resumo.totalNotas} duplicatas foram validadas. Exibindo amostra de ${resultado.itens.length} notas.`;
    } else {
      avisoAmostragem.style.display = "none";
    }
  }
  renderizarLinhasTabela(resultado.itens);
}

function renderizarLinhasTabela(listaItens) {
  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = "";

  const termoBusca = (inputBuscaEmpresa?.value || "").toLowerCase().trim();

  const itensFiltrados = listaItens.filter(item => {
    // Regra de Filtro de Status
    const statusMatch = filtroStatusAtual === "TODOS" || String(item.status).toUpperCase() === filtroStatusAtual;
    // Regra de Filtro de Pesquisa de Texto (Sacado ou ID)
    const nomeSacado = (item.sacado || "").toLowerCase();
    const idDocumento = (item.id || "").toLowerCase();
    const buscaMatch = termoBusca === "" || nomeSacado.includes(termoBusca) || idDocumento.includes(termoBusca);
    
    return statusMatch && buscaMatch;
  });

  if (itensFiltrados.length === 0) {
    corpoTabela.innerHTML = `
      <tr>
        <td colspan="8" class="empty-state">Nenhum título encontrado para o filtro e pesquisa selecionados.</td>
      </tr>
    `;
    return;
  }

  const fragment = document.createDocumentFragment();
  const itensExibidos = itensFiltrados.slice(0, CONFIG.MAX_DOM_ROWS);

  itensExibidos.forEach(item => {
    const tr = document.createElement("tr");
    const ehAprovado = String(item.status).toUpperCase() === "APROVADO";
    const statusBadge = ehAprovado ? "badge-success" : "badge-error";
    const diagnosticoVisual = ehAprovado
      ? '<span class="approved-text">✓ Elegível para antecipação imediata</span>'
      : `<div class="reason-box">${item.motivoRecusa || item.motivo || "Critério não atendido."}</div>`;

    tr.innerHTML = `
      <td><strong>${item.id || "-"}</strong></td>
      <td>${item.sacado || "-"}</td>
      <td>${item.valorFace || "-"}</td>
      <td>${item.prazo || "-"}</td>
      <td>${item.desconto || "-"}</td>
      <td style="color: ${ehAprovado ? 'var(--green-medium)' : 'inherit'}; font-weight: 700;">
        ${item.valorLiquido || "-"}
      </td>
      <td><span class="badge ${statusBadge}">${item.status}</span></td>
      <td>${diagnosticoVisual}</td>
    `;
    fragment.appendChild(tr);
  });
  corpoTabela.appendChild(fragment);
}

function mostrarCarregando(nomeArquivo) {
  if (avisoAmostragem) avisoAmostragem.style.display = "none";
  document.getElementById("tabelaCorpo").innerHTML = `
    <tr>
      <td colspan="8" class="empty-state" style="color: var(--green-primary); padding: 44px;">
        <p style="font-size: 1.05rem; font-weight: 700;">⏳ Processando lote "${nomeArquivo}"...</p>
      </td>
    </tr>
  `;
}

// ==== CONFIGURAÇÕES E MODAL ====
async function abrirModalValidadores() {
  modalConfig.style.display = "flex";
  painelParametrosValidador.innerHTML = "<p>Carregando regras do FIDC...</p>";
  try {
    const resp = await fetch(CONFIG.CONFIG_URL);
    if (!resp.ok) throw new Error("Falha ao buscar configurações.");
    dadosConfiguracaoCompleta = await resp.json();

    if (!dadosConfiguracaoCompleta.validadores) {
      dadosConfiguracaoCompleta = {
        fundo: { nome: "ANTECIPE", cnpj: "" },
        validadores: [],
        precificacao: { taxa_mensal_percentual: 2.0 }
      };
    }
    if (dadosConfiguracaoCompleta.precificacao && inputTaxaMensal) {
      inputTaxaMensal.value = dadosConfiguracaoCompleta.precificacao.taxa_mensal_percentual ?? 2.0;
    }
    popularDropdownValidadores();
  } catch (erro) {
    painelParametrosValidador.innerHTML = `<p style="color: var(--danger-primary);">Erro ao carregar regras: ${erro.message}</p>`;
  }
}

if (btnAbrirConfig) btnAbrirConfig.addEventListener("click", abrirModalValidadores);
function fecharModalConfig() { if (modalConfig) modalConfig.style.display = "none"; }
if (btnFecharModal) btnFecharModal.addEventListener("click", fecharModalConfig);
if (btnCancelarModal) btnCancelarModal.addEventListener("click", fecharModalConfig);

function popularDropdownValidadores() {
  selectValidador.innerHTML = "";
  const lista = dadosConfiguracaoCompleta.validadores || [];
  lista.forEach((val, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.textContent = `${val.ativo ? "🟢" : "⚪"} ${NOMES_AMIGAVEIS_VALIDADORES[val.codigo] || val.codigo}`;
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
    html += `<p style="font-size: 0.85rem; color: var(--text-muted);">Validador sem limites numéricos. Use o checkbox acima para ativar/desativar.</p>`;
  } else {
    chavesParametros.forEach(chave => {
      const valorAtual = parametros[chave];
      const labelAmigavel = LABELS_PARAMETROS[chave] || chave;

      if (Array.isArray(valorAtual)) {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="text" class="form-control input-parametro-dinamico" data-key="${chave}" data-type="array" value="${valorAtual.join(", ")}">
          </div>
        `;
      } else if (typeof valorAtual === "number") {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="number" step="any" class="form-control input-parametro-dinamico" data-key="${chave}" data-type="number" value="${valorAtual}">
          </div>
        `;
      } else {
        html += `
          <div class="form-group">
            <label>${labelAmigavel}</label>
            <input type="text" class="form-control input-parametro-dinamico" data-key="${chave}" data-type="string" value="${valorAtual}">
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
        opt.textContent = `${validador.ativo ? "🟢" : "⚪"} ${NOMES_AMIGAVEIS_VALIDADORES[validador.codigo] || validador.codigo}`;
      }
    });
  }
}

function guardarEdicoesNoObjetoEmMemoria(idx) {
  if (!dadosConfiguracaoCompleta || !dadosConfiguracaoCompleta.validadores[idx]) return;
  const validador = dadosConfiguracaoCompleta.validadores[idx];

  const chkAtivo = document.getElementById("chkValidadorAtivo");
  if (chkAtivo) validador.ativo = chkAtivo.checked;

  if (!validador.parametros) validador.parametros = {};

  document.querySelectorAll(".input-parametro-dinamico").forEach(input => {
    const chave = input.getAttribute("data-key");
    const tipo = input.getAttribute("data-type");

    if (tipo === "number") {
      validador.parametros[chave] = parseFloat(input.value) || 0;
    } else if (tipo === "array") {
      validador.parametros[chave] = input.value.split(",").map(s => s.trim()).filter(Boolean);
    } else {
      validador.parametros[chave] = input.value.trim();
    }
  });

  if (dadosConfiguracaoCompleta.precificacao && inputTaxaMensal) {
    dadosConfiguracaoCompleta.precificacao.taxa_mensal_percentual = parseFloat(inputTaxaMensal.value) || 2.0;
  }
}

// Botão Salvar
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
      if (!resp.ok) throw new Error("Falha ao salvar configurações.");
      fecharModalConfig();
      exibirToast("Regras atualizadas e cache de sessão reiniciado com sucesso!");
      if (ultimoArquivoCSV) enviarLoteParaBackend(ultimoArquivoCSV, true);
    } catch (erro) {
      exibirToast(erro.message, true);
    } finally {
      btnSalvarRegras.textContent = textoOriginal;
      btnSalvarRegras.disabled = false;
    }
  });
}

// NOVO: Botão Resetar Regras de Fábrica
if (btnResetarRegras) {
  btnResetarRegras.addEventListener("click", async () => {
    if (!confirm("Tem certeza que deseja restaurar as regras de fábrica? As customizações atuais serão perdidas.")) return;
    
    const textoOriginal = btnResetarRegras.textContent;
    btnResetarRegras.textContent = "Restaurando...";
    btnResetarRegras.disabled = true;

    try {
      const resp = await fetch(CONFIG.RESET_CONFIG_URL, { method: "POST" });
      if (!resp.ok) throw new Error("Erro ao restaurar configurações.");

      exibirToast("Regras restauradas para os padrões de fábrica com sucesso!");
      await abrirModalValidadores(); // Atualiza a tela com as regras limpas
      if (ultimoArquivoCSV) enviarLoteParaBackend(ultimoArquivoCSV, true); // Roda o lote novamente
    } catch (erro) {
      exibirToast(erro.message, true);
    } finally {
      btnResetarRegras.textContent = textoOriginal;
      btnResetarRegras.disabled = false;
    }
  });
}
