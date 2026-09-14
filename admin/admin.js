const API_BASE_URL = "/api";

const recordsList = document.querySelector(".records-list");
const statusLine = document.querySelector(".status-line");
const refreshButton = document.querySelector(".refresh-button");
const filterButtons = [...document.querySelectorAll(".filter-button")];
let records = [];
let activeFilter = "todos";

const participationLabels = {
  apoiar: "Apoio",
  piloto: "Piloto",
  embaixador: "Embaixador",
};

const setStatus = (message) => {
  if (statusLine) {
    statusLine.textContent = message;
  }
};

const formatDate = (value) =>
  new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const getContact = (record) =>
  record.contato_apoio ||
  record.contato_piloto ||
  record.contato_embaixador ||
  "Nao informado";

const updateStats = (stats) => {
  Object.entries(stats).forEach(([key, value]) => {
    const target = document.querySelector(`[data-stat="${key}"]`);
    if (target) {
      target.textContent = value;
    }
  });
};

const filterRecords = () => {
  if (activeFilter === "todos") return records;
  if (activeFilter === "mensagens") return records.filter((record) => record.mensagem);
  return records.filter((record) => record.participacao.includes(activeFilter));
};

const renderRecords = () => {
  const filtered = filterRecords();

  if (!recordsList) return;

  if (filtered.length === 0) {
    recordsList.innerHTML = `
      <div class="empty-state">
        Nenhum registro encontrado para esse filtro.
      </div>
    `;
    setStatus(`${records.length} registro(s) carregado(s).`);
    return;
  }

  recordsList.innerHTML = filtered
    .map((record) => {
      const chips = record.participacao
        .map(
          (item) =>
            `<span class="chip ${item !== "apoiar" ? "is-hot" : ""}">${participationLabels[item]}</span>`
        )
        .join("");
      const message = record.mensagem
        ? escapeHtml(record.mensagem)
        : "Sem relato enviado neste registro.";

      return `
        <article class="record-card">
          <div>
            <h3>${escapeHtml(record.nome)}</h3>
            <p>${escapeHtml(record.instituicao)} · ${escapeHtml(record.bairro)}</p>
            <div class="chips">${chips}</div>
          </div>

          <dl class="meta-list">
            <div>
              <dt>Contato</dt>
              <dd>${escapeHtml(getContact(record))}</dd>
            </div>
            <div>
              <dt>Turno</dt>
              <dd>${escapeHtml(record.turno)}</dd>
            </div>
            <div>
              <dt>Faixa etaria</dt>
              <dd>${escapeHtml(record.faixa_etaria)}</dd>
            </div>
            <div>
              <dt>Enviado em</dt>
              <dd>${formatDate(record.created_at)}</dd>
            </div>
          </dl>

          <div class="message-card">
            <strong>Relato</strong>
            <p>${message}</p>
          </div>
        </article>
      `;
    })
    .join("");

  setStatus(`${filtered.length} de ${records.length} registro(s) exibido(s).`);
};

const loadRecords = async () => {
  refreshButton.disabled = true;
  setStatus("Carregando registros...");

  try {
    const response = await fetch(`${API_BASE_URL}/admin/apoios?limit=500`);
    if (!response.ok) {
      throw new Error("Nao foi possivel carregar os registros.");
    }

    const data = await response.json();
    records = data.apoios || [];
    updateStats(data.stats || {});
    renderRecords();
  } catch (error) {
    recordsList.innerHTML = `
      <div class="empty-state">
        ${escapeHtml(error.message || "Erro ao carregar registros.")}
      </div>
    `;
    setStatus("Falha ao carregar.");
  } finally {
    refreshButton.disabled = false;
  }
};

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));
    renderRecords();
  });
});

refreshButton?.addEventListener("click", loadRecords);

loadRecords();
