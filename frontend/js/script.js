/**
 * Portal Antecipe - Hackathon Kanastra
 * Integração Frontend com API em Python
 */

const CONFIG = {
  API_URL: "http://localhost:8000/api/analisar-lote",
  FILE_FIELD_NAME: "lote"
};

const dropZone = document.getElementById("dropZone");
const csvInput = document.getElementById("csvInput");
const btnDemo = document.getElementById("btnDemo");

if (dropZone && csvInput) {
  dropZone.addEventListener("click", () => csvInput.click());

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

  csvInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      enviarLoteParaBackend(e.target.files[0]);
    }
  });
}

if (btnDemo) {
  btnDemo.addEventListener("click", () => {
    // Demonstração local rápida para apresentação de UX
    const dadosExemplo = {
      resumo: {
        totalNotas: 3,
        totalBruto: "R$ 48.000,00",
        totalLiquido: "R$ 31.780,00",
        totalRecusadas: 1
      },
      itens: [
        {
          id: "NF-8921",
          sacado: "Distribuidora Minas Ltda",
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
        }
      ]
    };
    renderizarResultados(dadosExemplo);
  });
}

async function enviarLoteParaBackend(arquivoCSV) {
  if (!arquivoCSV.name.endsWith(".csv")) {
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
    alert("Erro na conexão com o Backend: " + erro.message);
    document.getElementById("tabelaCorpo").innerHTML = `
      <tr>
        <td colspan="8" class="empty-state" style="color: var(--danger);">
          Erro ao processar lote via API. Verifique se o backend Python está rodando na porta 8000.
        </td>
      </tr>
    `;
  }
}

function renderizarResultados(resultado) {
  if (!resultado || !resultado.resumo || !resultado.itens) {
    console.error("Formato JSON recebido incompatível:", resultado);
    return;
  }

  document.getElementById("totalNotas").textContent = resultado.resumo.totalNotas;
  document.getElementById("totalBruto").textContent = resultado.resumo.totalBruto;
  document.getElementById("totalLiquido").textContent = resultado.resumo.totalLiquido;
  document.getElementById("totalRecusadas").textContent = resultado.resumo.totalRecusadas;

  const corpoTabela = document.getElementById("tabelaCorpo");
  corpoTabela.innerHTML = "";

  resultado.itens.forEach(item => {
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
        <p style="font-size: 1.1rem; font-weight: 600;">⏳ Analisando lote "${nomeArquivo}"...</p>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 6px;">
          Validando regras de elegibilidade e checando duplicidade em O(1)...
        </p>
      </td>
    </tr>
  `;
}
