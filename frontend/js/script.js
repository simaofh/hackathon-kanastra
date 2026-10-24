/**
 * Portal Antecipe - Hackathon Kanastra
 * Integração Frontend com API em Python
 */

// ==========================================
// 1. CONFIGURAÇÕES DE CONEXÃO COM O BACKEND
// (Altere apenas aqui se o time mudar a porta ou a rota)
// ==========================================
const CONFIG = {
  API_URL: "http://localhost:8000/api/analisar-lote", // Endpoint do backend Python
  FILE_FIELD_NAME: "lote"                            // Nome do campo multipart esperado
};

// ==========================================
// 2. DADOS DE DEMONSTRAÇÃO / FALLBACK
// (Mantém o layout funcional para testes e avaliação de UX)
// ==========================================
const dadosDemonstracao = {
  resumo: {
    totalNotas: 4,
    totalBruto: "R$ 48.500,00",
    totalLiquido: "R$ 31.780,00",
    totalRecusadas: 2
  },
  itens: [
    {
      id: "NF-8921",
      sacado: "Distribuidora Minas Alimentos Ltda",
      valorFace: "R$ 15.000,00",
      prazo: "30 dias",
      desconto: "R$ 375,00 (2.5%)",
      valorLiquido: "R$ 14.625,00",
      status: "APROVADO",
      motivoRecusa: null
    },
    {
      id: "NF-8922",
      sacado: "Supermercados Triângulo S.A.",
      valorFace: "R$ 18.000,00",
      prazo: "45 dias",
      desconto: "R$ 845,00 (3.75%)",
      valorLiquido: "R$ 17.155,00",
      status: "APROVADO",
      motivoRecusa: null
    },
    {
      id: "NF-8923",
      sacado: "Comércio Varejista do Cerrado",
      valorFace: "R$ 15.000,00",
      prazo: "135 dias",
      desconto: "-",
      valorLiquido: "-",
      status: "RECUSADO",
      motivoRecusa: "Prazo de vencimento (135 dias) ultrapassa o teto máximo de 90 dias permitido pela política de risco do FIDC."
    },
    {
      id: "NF-8924",
      sacado: "Indústria Metalúrgica Triunfo",
      valorFace: "R$ 500,00",
      prazo: "20 dias",
      desconto: "-",
      valorLiquido: "-",
      status: "RECUSADO",
      motivoRecusa: "Valor de face abaixo da régua mínima permitida pelo regulamento do fundo (mínimo exigido: R$ 1.000,00)."
    }
  ]
};

// ==========================================
// 3. SELETORES E EVENTOS DA INTERFACE
// ==========================================
const dropZone = document.getElementById("dropZone");
const csvInput = document.getElementById("csvInput");
const btnDemo = document.getElementById("btnDemo");

// Evento de clique na área de upload
if (dropZone && csvInput) {
  dropZone.addEventListener("click", () => csvInput.click());

  // Drag and Drop
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--primary)";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "var(--border)";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--border)";
    if (e.dataTransfer.files.length > 0) {
      enviarLoteParaBackend(e.dataTransfer.files[0]);
    }
  });

  // Seleção de arquivo tradicional
  csvInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      enviarLoteParaBackend(e.target.files[0]);
    }
  });
}

// Botão para demonstração imediata
if (btnDemo) {
  btnDemo.addEventListener("click", () => {
    renderizarResultados(dadosDemonstracao);
  });
}

// ==========================================
// 4. ENVIO PARA O BACKEND EM PYTHON (FETCH)
// ==========================================
async function enviarLoteParaBackend(arquivoCSV) {
  if (!arquivoCSV.name.endsWith(".csv")) {
    alert("Por favor, selecione um arquivo válido no formato .csv");
    return;
  }

  // Prepara o formulário com o campo esperado pelo backend
  const formData = new FormData();
  formData.append(CONFIG.FILE_FIELD_NAME, arquivoCSV);

  // Exibe mensagem de carregamento na tabela
  mostrarCarregando(arquivoCSV.name);

  try {
    const resposta = await fetch(CONFIG.API_URL, {
      method: "POST",
      body: formData
    });

    if (!resposta.ok) {
      throw new Error(`Servidor respondeu com código HTTP ${resposta.status}`);
    }

    const dados = await resposta.json();
    renderizarResultados(dados);

  } catch (erro) {
    console.warn("Falha na conexão com a API Python:", erro);
    alert(
      "Aviso: Não foi possível conectar ao backend em " + CONFIG.API_URL + 
      "\n\nExibindo dados de simulação para validação do layout de UX."
    );
    // Caso o backend esteja desligado ou em desenvolvimento, exibe a simulação sem quebrar a tela
    renderizarResultados(dadosDemonstracao);
  }
}

// ==========================================
// 5. RENDERIZAÇÃO NA TELA (DESIGN E UX - 25 PONTOS)
// ==========================================
function renderizarResultados(resultado) {
  if (!resultado || !resultado.resumo || !resultado.itens) {
    console.error("Formato JSON recebido incompatível com a especificação:", resultado);
    return;
  }

  // 1. Atualiza os cards executivos
  document.getElementById("totalNotas").textContent = resultado.resumo.totalNotas;
  document.getElementById("totalBruto").textContent = resultado.resumo.totalBruto;
  document.getElementById("totalLiquido").textContent = resultado.resumo.totalLiquido;
  document.getElementById("totalRecusadas").textContent = resultado.resumo.totalRecusadas;

  // 2. Monta as linhas da tabela com foco nas explicações de recusa
  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = "";

  resultado.itens.forEach(item => {
    const tr = document.createElement("tr");

    const ehAprovado = String(item.status).toUpperCase() === "APROVADO";
    const statusBadge = ehAprovado ? "badge-success" : "badge-error";
    
    // Tratamento amigável da explicação da recusa (Critério de UX do edital)
    const diagnosticoVisual = ehAprovado
      ? '<span class="approved-text">✓ Elegível para antecipação imediata</span>'
      : `<div class="reason-box">${item.motivoRecusa || "Critério de elegibilidade não atendido."}</div>`;

    tr.innerHTML = `
      <td><strong>${item.id || "-"}</strong></td>
      <td>${item.sacado || "-"}</td>
      <td>${item.valorFace || "-"}</td>
      <td>${item.prazo || "-"}</td>
      <td>${item.desconto || "-"}</td>
      <td style="color: ${ehAprovado ? 'var(--primary)' : 'inherit'}; font-weight: 600;">
        ${item.valorLiquido || "-"}
      </td>
      <td>
        <span class="badge ${statusBadge}">
          ${item.status}
        </span>
      </td>
      <td>${diagnosticoVisual}</td>
    `;
    corpoTabela.appendChild(tr);
  });
}

function mostrarCarregando(nomeArquivo) {
  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = `
    <tr>
      <td colspan="8" style="text-align: center; color: var(--primary); padding: 40px;">
        <p style="font-size: 1.1rem; font-weight: 600;">⏳ Processando "${nomeArquivo}"...</p>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 6px;">
          Validando regras de risco, prazo, valor mínimo e duplicidade contra o estoque FIDC.
        </p>
      </td>
    </tr>
  `;
}
