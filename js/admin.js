(() => {
  const app = document.querySelector("#admin-app");
  const adminKey = "jbs_admin";
  const teacherUser = "diogo";
  const teacherPassword = "diogo123";
  const state = { results: [], turma: "", emailConfigured: false, error: "", pages: usesPages() };

  function usesPages() {
    const mode = window.JBS_CONFIG && window.JBS_CONFIG.mode;
    if (mode === "pages") return true;
    if (mode === "server") return false;
    return location.hostname.endsWith("github.io");
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));
  }

  async function api(path, options) {
    const config = options || {};
    const response = await fetch((window.JBS_CONFIG.apiBase || "") + path, {
      method: config.method || "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: config.body ? JSON.stringify(config.body) : undefined
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(data.error || "Não foi possível concluir a operação.");
      error.status = response.status;
      throw error;
    }
    return data;
  }

  function readableError(error) {
    const message = String((error && error.message) || "");
    if (message === "Failed to fetch" || message === "Load failed" || message === "NetworkError when attempting to fetch resource.") {
      return state.pages
        ? "A lista de notas não respondeu. Atualize a página com Ctrl+F5 e entre de novo."
        : "Não foi possível falar com o servidor da prova. Abra o link do GitHub ou inicie o computador da escola.";
    }
    return message || "Não foi possível concluir a operação.";
  }

  function credentials() {
    return {
      username: document.querySelector("#username").value,
      password: document.querySelector("#password").value
    };
  }

  function renderLogin() {
    app.innerHTML = `
      <section class="card">
        <p class="kicker">Acesso restrito</p>
        <h1>Consultar resultados</h1>
        <p>Entre com o login do professor para ver as notas da turma.</p>
        ${state.error ? `<div class="banner bad" role="alert">${escapeHtml(state.error)}</div>` : ""}
        <form id="login-form">
          <div class="field">
            <label for="username">Login</label>
            <input id="username" name="username" type="text" autocomplete="username" required>
          </div>
          <div class="field">
            <label for="password">Senha</label>
            <input id="password" type="password" autocomplete="current-password" required>
          </div>
          <div class="actions">
            <button class="btn btn-primary" type="submit">Entrar</button>
          </div>
        </form>
      </section>
    `;
    document.querySelector("#login-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      state.error = "";
      const entered = credentials();
      try {
        if (state.pages) {
          if (entered.username.trim() !== teacherUser || entered.password !== teacherPassword) {
            throw new Error("Usuário ou senha incorretos.");
          }
          sessionStorage.setItem(adminKey, "1");
        } else {
          await api("/api/admin/login", { method: "POST", body: entered });
        }
        await loadResults();
      } catch (error) {
        state.error = readableError(error);
        renderLogin();
      }
    });
  }

  function formatNota(item) {
    if (!item || item.nota === null || item.nota === undefined || item.nota === "") return "—";
    if (item.nota_formatada) return item.nota_formatada;
    const cents = Math.round(Number(item.nota) * 100);
    if (!Number.isFinite(cents)) return "—";
    return `${Math.trunc(cents / 100)},${String(Math.abs(cents % 100)).padStart(2, "0")}`;
  }

  function closureText(item) {
    if (!item || !item.encerramento || item.encerramento === "normal") return "Concluída pelo aluno";
    return item.encerramento;
  }

  function uniqueResults(rows) {
    const seen = new Set();
    return rows.filter((item) => {
      const key = item.attempt_id || `${item.nome}|${item.turma}|${item.finished_at}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function downloadCsv(rows) {
    const header = ["Nome", "Turma", "Nota", "Acertos", "Erros", "Aproveitamento", "Início", "Término", "Encerramento"];
    const lines = [header.join(";")].concat(rows.map((item) => [
      item.nome, item.turma, formatNota(item), item.acertos, item.erros,
      item.aproveitamento, item.started_at, item.finished_at, closureText(item)
    ].map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`).join(";")));
    const blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "resultados.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function renderResults() {
    const source = uniqueResults(state.results);
    const rows = source.filter((item) => !state.turma || item.turma === state.turma);
    const pagesNote = state.pages
      ? "Alunos e professor usam este link em qualquer internet. Uma prova recém-concluída pode levar alguns minutos para aparecer. A planilha Excel continua no computador da escola."
      : (state.emailConfigured
        ? "O envio de e-mail está configurado."
        : "O e-mail ainda não está configurado. As notas continuam salvas no sistema e nas planilhas.");
    const body = rows.length
      ? rows.map((item) => state.pages ? `
        <tr>
          <td>${escapeHtml(item.nome)}</td>
          <td>${escapeHtml(item.turma)}</td>
          <td>${formatNota(item)}</td>
          <td>${item.acertos ?? "—"}</td>
          <td>${item.erros ?? "—"}</td>
          <td>${item.aproveitamento === null || item.aproveitamento === undefined ? "—" : item.aproveitamento + "%"}</td>
          <td>${escapeHtml(item.started_at || "")}</td>
          <td>${escapeHtml(item.finished_at || "")}</td>
          <td>${escapeHtml(closureText(item))}</td>
        </tr>` : `
        <tr>
          <td>${escapeHtml(item.nome)}</td>
          <td>${escapeHtml(item.turma)}</td>
          <td>${escapeHtml(item.status)}</td>
          <td>${formatNota(item)}</td>
          <td>${item.acertos === null ? "—" : item.acertos}</td>
          <td>${item.erros === null ? "—" : item.erros}</td>
          <td>${item.aproveitamento === null ? "—" : item.aproveitamento + "%"}</td>
          <td>${escapeHtml(item.finished_at || item.started_at)}</td>
          <td>${escapeHtml(item.situacao)}</td>
          <td>${escapeHtml(item.email_status)}</td>
          <td>${item.resume_count}</td>
          <td>${escapeHtml(closureText(item))}</td>
        </tr>`).join("")
      : `<tr><td colspan="${state.pages ? 9 : 12}">Nenhuma avaliação encontrada para este filtro.</td></tr>`;
    const head = state.pages
      ? "<th>Aluno</th><th>Turma</th><th>Nota</th><th>Acertos</th><th>Erros</th><th>Aproveitamento</th><th>Início</th><th>Término</th><th>Encerramento</th>"
      : "<th>Aluno</th><th>Turma</th><th>Situação</th><th>Nota</th><th>Acertos</th><th>Erros</th><th>Aproveitamento</th><th>Horário</th><th>Salvamento</th><th>E-mail</th><th>Recarregamentos</th><th>Encerramento</th>";
    app.innerHTML = `
      <section class="card">
        <p class="kicker">Planilhas e notas</p>
        <h1>Resultados por turma</h1>
        <p>${pagesNote}</p>
        ${state.error ? `<div class="banner bad">${escapeHtml(state.error)}</div>` : ""}
        <div class="filters" id="filters">
          ${["", "8A", "8B", "8C", "8D", "8E"].map((turma) => `
            <button class="btn btn-secondary" type="button" data-turma="${turma}" aria-pressed="${state.turma === turma}">
              ${turma || "Todas"}
            </button>`).join("")}
        </div>
        <div class="actions">
          ${state.pages ? `<button class="btn btn-primary" id="csv-btn" type="button">Baixar resultados.csv</button><button class="btn btn-secondary" id="refresh-btn" type="button">Atualizar notas</button>` : `<button class="btn btn-primary" id="sync-btn" type="button">Sincronizar planilhas e e-mails</button>`}
          <button class="btn btn-secondary" id="logout-btn" type="button">Sair</button>
        </div>
        ${state.pages ? "" : `<div class="actions">
          ${["8A", "8B", "8C", "8D", "8E"].map((turma) => `
            <a class="btn btn-secondary" href="api/admin/export/${turma}">Baixar notas_${turma}.xlsx</a>`).join("")}
        </div>`}
        <div class="table-wrap">
          <table>
            <thead><tr>${head}</tr></thead>
            <tbody>${body}</tbody>
          </table>
        </div>
      </section>
    `;
    document.querySelector("#filters").addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button) return;
      state.turma = button.dataset.turma;
      renderResults();
    });
    const csv = document.querySelector("#csv-btn");
    if (csv) csv.addEventListener("click", () => downloadCsv(rows));
    const refresh = document.querySelector("#refresh-btn");
    if (refresh) {
      refresh.addEventListener("click", async () => {
        refresh.disabled = true;
        try {
          await loadPagesResults();
        } catch (error) {
          state.error = readableError(error);
          renderResults();
        }
      });
    }
    const sync = document.querySelector("#sync-btn");
    if (sync) {
      sync.addEventListener("click", async () => {
        state.error = "";
        try {
          await api("/api/admin/sync", { method: "POST", body: {} });
          await loadResults();
        } catch (error) {
          state.error = readableError(error);
          renderResults();
        }
      });
    }
    document.querySelector("#logout-btn").addEventListener("click", async () => {
      sessionStorage.removeItem(adminKey);
      if (!state.pages) await api("/api/admin/logout", { method: "POST", body: {} });
      state.results = [];
      renderLogin();
    });
  }

  function decodeArchive(content) {
    const bytes = Uint8Array.from(atob(String(content).replace(/\s/g, "")), (char) => char.charCodeAt(0));
    const rows = JSON.parse(new TextDecoder().decode(bytes));
    return Array.isArray(rows) ? rows : [];
  }

  async function loadPagesResults() {
    const url = window.JBS_CONFIG && window.JBS_CONFIG.archiveUrl;
    if (!url) throw new Error("A lista de resultados não está configurada.");
    const response = await fetch(url + "?t=" + Date.now(), {
      headers: { Accept: "application/vnd.github+json" }
    });
    if (response.status === 404) {
      state.results = [];
      state.error = "";
      renderResults();
      return;
    }
    if (!response.ok) throw new Error("A lista de notas não respondeu. Atualize a página com Ctrl+F5 e entre de novo.");
    const data = await response.json();
    state.results = data && data.content ? decodeArchive(data.content) : [];
    state.error = "";
    renderResults();
  }

  async function loadResults() {
    if (state.pages) {
      await loadPagesResults();
      return;
    }
    const data = await api("/api/admin/results");
    state.results = data.results;
    state.emailConfigured = data.email_configured;
    state.error = "";
    renderResults();
  }

  if (state.pages && sessionStorage.getItem(adminKey) === "1") {
    loadPagesResults().catch((error) => {
      sessionStorage.removeItem(adminKey);
      state.error = readableError(error);
      renderLogin();
    });
  } else if (state.pages) {
    renderLogin();
  } else {
    loadResults().catch((error) => {
      state.error = error.status === 503 ? readableError(error) : "";
      renderLogin();
    });
  }
})();
