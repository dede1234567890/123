(() => {
  const app = document.querySelector("#app");
  const chip = document.querySelector("#identity-chip");
  const storageKey = "jbs_session";
  const state = {
    screen: "loading",
    session: null,
    student: null,
    question: null,
    feedback: null,
    progress: defaultProgress(),
    result: null,
    error: "",
    info: "",
    sending: false,
    violations: 0,
    closing: false,
    closure: ""
  };

  function defaultProgress() {
    return {
      question: 1,
      total: 20,
      respondidas: 0,
      acertos: 0,
      erros: 0,
      nota_cents: 0,
      pontuacao: 0,
      pontuacao_formatada: "0,00",
      progresso: 0
    };
  }

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
      const value = Math.floor(Math.random() * 16);
      const next = char === "x" ? value : (value & 0x3) | 0x8;
      return next.toString(16);
    });
  }

  function token() {
    const bytes = new Uint8Array(32);
    crypto.getRandomValues(bytes);
    return Array.from(bytes, (item) => item.toString(16).padStart(2, "0")).join("");
  }

  function readSession() {
    try {
      return JSON.parse(sessionStorage.getItem(storageKey) || "null");
    } catch (_error) {
      return null;
    }
  }

  function saveSession() {
    sessionStorage.setItem(storageKey, JSON.stringify(state.session));
  }

  function escapeHtml(value) {
    return ExamUI.escapeHtml(value);
  }

  function validName(value) {
    const cleaned = String(value || "").trim().replace(/\s+/g, " ");
    return cleaned.length >= 5 && cleaned.length <= 120 &&
      /^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*(?: [A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*)+$/.test(cleaned);
  }

  function usesPages() {
    const mode = window.JBS_CONFIG && window.JBS_CONFIG.mode;
    if (mode === "pages") return true;
    if (mode === "server") return false;
    return location.hostname.endsWith("github.io");
  }

  async function api(path, options) {
    if (usesPages()) return PagesExam.handle(path, options || {}, state.session);
    const config = options || {};
    const headers = { "Content-Type": "application/json" };
    if (state.session) {
      headers["X-Attempt-Id"] = state.session.attemptId;
      headers.Authorization = "Bearer " + state.session.token;
    }
    const response = await fetch((window.JBS_CONFIG.apiBase || "") + path, {
      method: config.method || "GET",
      headers,
      body: config.body ? JSON.stringify(config.body) : undefined
    });
    let data = {};
    try {
      data = await response.json();
    } catch (_error) {
      data = {};
    }
    if (!response.ok) {
      const error = new Error(data.error || "Não foi possível comunicar com o servidor.");
      error.status = response.status;
      throw error;
    }
    return data;
  }

  function setLock(active) {
    document.body.classList.toggle("exam-lock", active);
  }

  function showIdentity() {
    if (!state.student) {
      chip.hidden = true;
      return;
    }
    chip.hidden = false;
    chip.textContent = `${state.student.nome} · Turma ${state.student.turma} · início ${state.student.started_at}`;
  }

  function progressPanel() {
    const progress = state.progress || defaultProgress();
    return `
      <aside class="card progress-card">
        <p class="kicker">Desempenho</p>
        <h2>Questão ${progress.question} de ${progress.total}</h2>
        <p>Progresso: ${progress.progresso}%</p>
        <div class="bar" aria-hidden="true"><span class="p${progress.progresso}"></span></div>
        <div class="stats">
          <div class="stat"><span>Acertos</span><b>${progress.acertos}</b></div>
          <div class="stat"><span>Erros</span><b>${progress.erros}</b></div>
        </div>
        <p><strong>Pontuação parcial:</strong> ${escapeHtml(progress.pontuacao_formatada || "0,00")} / 7,00</p>
        <p class="muted">Questões respondidas: ${progress.respondidas}</p>
      </aside>
    `;
  }

  function banner(kind, text) {
    if (!text) return "";
    return `<div class="banner ${kind}" role="status">${escapeHtml(text)}</div>`;
  }

  function render() {
    showIdentity();
    setLock(state.screen === "instructions" || state.screen === "question");
    if (state.screen === "identify") return renderIdentify();
    if (state.screen === "instructions") return renderInstructions();
    if (state.screen === "question") return renderQuestion();
    if (state.screen === "result") return renderResult();
    app.innerHTML = `<section class="card"><p>Carregando a avaliação…</p>${banner("bad", state.error)}</section>`;
  }

  function renderIdentify() {
    app.className = "shell";
    app.innerHTML = `
      <section class="card">
        <p class="kicker">Identificação</p>
        <h1>Avaliação de Python</h1>
        <p>Antes de começar, identifique-se. Nome e turma ficam registrados no início e não poderão ser alterados.</p>
        ${banner("info", state.info)}
        ${banner("bad", state.error)}
        <form id="identify-form">
          <div class="field">
            <label for="nome">Nome completo</label>
            <input id="nome" name="nome" type="text" maxlength="120" autocomplete="name" required>
            <p class="hint" id="nome-hint">Use nome e sobrenome.</p>
          </div>
          <div class="field">
            <label for="turma">Turma</label>
            <select id="turma" name="turma" required>
              <option value="">Selecione a turma</option>
              <option>8A</option>
              <option>8B</option>
              <option>8C</option>
              <option>8D</option>
              <option>8E</option>
            </select>
          </div>
          <div class="actions">
            <button class="btn btn-primary" id="start-btn" type="submit" disabled>Iniciar avaliação</button>
          </div>
          <p class="hint"><a class="text-link" href="admin.html">Área do professor</a></p>
        </form>
      </section>
    `;
    const form = document.querySelector("#identify-form");
    const nome = document.querySelector("#nome");
    const turma = document.querySelector("#turma");
    const button = document.querySelector("#start-btn");
    const hint = document.querySelector("#nome-hint");
    const refresh = () => {
      const ok = validName(nome.value) && turma.value;
      button.disabled = !ok;
      hint.textContent = nome.value.trim() && !validName(nome.value)
        ? "Informe nome e sobrenome, usando apenas letras."
        : "Use nome e sobrenome.";
    };
    nome.addEventListener("input", refresh);
    turma.addEventListener("change", refresh);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!validName(nome.value) || !turma.value) return;
      button.disabled = true;
      state.error = "";
      try {
        if (!state.session) {
          state.session = {
            browserSession: uuid(),
            token: token(),
            attemptId: "",
            instructionsSeen: false
          };
        }
        const data = await api("/api/start", {
          method: "POST",
          body: {
            nome: nome.value,
            turma: turma.value,
            browser_session: state.session.browserSession,
            token: state.session.token
          }
        });
        state.session.attemptId = data.attempt_id;
        state.session.instructionsSeen = Boolean(data.resumed && !data.finished);
        saveSession();
        state.student = { nome: data.nome, turma: data.turma, started_at: data.started_at };
        if (data.finished) {
          await loadState(false);
          return;
        }
        if (data.resumed) {
          state.info = "Sua avaliação já estava em andamento. Você continuará da questão atual, sem alterar nome ou turma.";
          readViolations();
          await loadState(false);
          return;
        }
        state.violations = 0;
        state.closure = "";
        saveViolations();
        state.screen = "instructions";
        render();
      } catch (error) {
        state.error = error.message;
        button.disabled = false;
        render();
      }
    });
  }

  function renderInstructions() {
    app.className = "shell";
    app.innerHTML = `
      <section class="card">
        <p class="kicker">Instruções</p>
        <h1>Como será a avaliação</h1>
        <p>Todas as questões usam o mesmo contexto: o sistema de pedidos, produtos e estoque da JBS FoodTech.</p>
        <ul>
          <li>A prova tem 20 questões e vale 7,00 no total.</li>
          <li>As questões 1 a 8 valem 0,20 cada. As questões 9 a 20 valem 0,45 cada.</li>
          <li>Você responde uma questão por vez e não pode voltar.</li>
          <li>Depois de confirmar, a resposta fica bloqueada.</li>
          <li>Da questão 9 à 20, você cria as variáveis e a lista no editor. Use Testar código para ver o resultado antes de confirmar.</li>
          <li>A prova pode ser feita em qualquer internet, pelo link desta página.</li>
          <li>Ctrl+C, Ctrl+V e o print da tela são bloqueados. Cada tentativa gera um alerta. Se isso passar de 3 vezes, a prova encerra e o professor vê o aviso na lista de notas.</li>
        </ul>
        <p><strong>Início registrado:</strong> ${escapeHtml(state.student.started_at)}</p>
        <p><strong>Aluno:</strong> ${escapeHtml(state.student.nome)} · Turma ${escapeHtml(state.student.turma)}</p>
        ${banner("info", state.info)}
        <div class="actions">
          <button class="btn btn-primary" id="begin-btn" type="button">Começar questões</button>
        </div>
      </section>
    `;
    document.querySelector("#begin-btn").addEventListener("click", async () => {
      state.session.instructionsSeen = true;
      saveSession();
      await loadState(false);
    });
  }

  function renderQuestion() {
    app.className = "shell layout";
    app.innerHTML = `
      ${progressPanel()}
      <section class="card">
        <div id="question-host"></div>
        <div id="feedback-host"></div>
        ${banner("bad", state.error)}
        <div class="actions">
          <button class="btn btn-primary" id="confirm-btn" type="button" ${state.feedback ? "hidden" : ""}>Confirmar resposta</button>
          <button class="btn btn-secondary" id="next-btn" type="button" ${state.feedback ? "" : "hidden"}>${state.progress.question === state.progress.total ? "Finalizar avaliação" : "Próxima questão"}</button>
        </div>
      </section>
    `;
    const host = document.querySelector("#question-host");
    ExamUI.renderQuestion(host, { question: state.question, feedback: state.feedback }, refreshConfirm);
    if (state.feedback) {
      const kind = state.feedback.correct ? "ok" : "bad";
      const earned = earnedText(state.feedback);
      const title = state.feedback.correct ? `Resposta correta. Você recebeu ${earned}.` : "Resposta incorreta. Esta questão ficou com 0,00.";
      document.querySelector("#feedback-host").innerHTML = `${banner(kind, title)}${banner("info", state.feedback.explanation)}`;
      document.querySelector("#next-btn").addEventListener("click", goNext);
    } else {
      const button = document.querySelector("#confirm-btn");
      button.disabled = !ExamUI.collect(host, state.question);
      button.addEventListener("click", confirmAnswer);
    }
  }

  function earnedText(feedback) {
    if (feedback && feedback.points_formatada) return feedback.points_formatada;
    if (!feedback || !feedback.correct) return "0,00";
    const cents = Math.round(Number(feedback.points) * 100);
    if (!Number.isFinite(cents)) return state.question && state.question.valor ? state.question.valor : "0,00";
    return `${Math.floor(cents / 100)},${String(Math.abs(cents) % 100).padStart(2, "0")}`;
  }

  function refreshConfirm() {
    const button = document.querySelector("#confirm-btn");
    const host = document.querySelector("#question-host");
    if (!button || !host || state.feedback) return;
    button.disabled = !ExamUI.collect(host, state.question);
  }

  async function confirmAnswer() {
    if (state.sending || state.feedback) return;
    const host = document.querySelector("#question-host");
    const response = ExamUI.collect(host, state.question);
    if (!response) return;
    state.sending = true;
    const button = document.querySelector("#confirm-btn");
    button.disabled = true;
    state.error = "";
    try {
      const data = await api("/api/answer", {
        method: "POST",
        body: { question: state.question.number, response }
      });
      state.progress = data.progress;
      state.feedback = {
        correct: data.correct,
        points: data.points,
        points_formatada: data.points_formatada,
        explanation: data.explanation,
        detail: data.detail || null,
        response
      };
      state.sending = false;
      render();
    } catch (error) {
      state.sending = false;
      if (error.status === 409) {
        await loadState(false);
        return;
      }
      state.error = error.message;
      render();
    }
  }

  async function goNext() {
    if (state.sending) return;
    state.sending = true;
    state.error = "";
    try {
      if (state.progress.question === state.progress.total) {
        const data = await api("/api/finish", { method: "POST", body: finishBody() });
        state.result = data.result;
        state.error = data.salvo ? "" : "A lista do professor ainda não confirmou esta nota.";
        state.screen = "result";
        state.sending = false;
        render();
        return;
      }
      const data = await api("/api/next", { method: "POST", body: {} });
      if (data.ready_to_finish) {
        const finished = await api("/api/finish", { method: "POST", body: finishBody() });
        state.result = finished.result;
        state.error = finished.salvo ? "" : "A lista do professor ainda não confirmou esta nota.";
        state.screen = "result";
      } else {
        state.question = data.question;
        state.progress = data.progress;
        state.feedback = null;
        state.screen = "question";
      }
      state.sending = false;
      render();
    } catch (error) {
      state.sending = false;
      state.error = error.message;
      if (state.progress.question === state.progress.total) {
        renderQuestion();
        return;
      }
      render();
    }
  }

  function renderResult() {
    app.className = "shell";
    const result = state.result;
    const review = (result.revisao || []).map((item) =>
      `<li>Questão ${item.number}: ${item.correct ? "acertou" : "errou"}</li>`
    ).join("");
    app.innerHTML = `
      <section class="card">
        <p class="kicker">Encerramento</p>
        <div class="score-ring">${escapeHtml(result.nota_formatada)}</div>
        <h1>Avaliação concluída</h1>
        <p><strong>Aluno:</strong> ${escapeHtml(result.nome)}</p>
        <p><strong>Turma:</strong> ${escapeHtml(result.turma)}</p>
        <p><strong>Início:</strong> ${escapeHtml(result.started_at)}</p>
        <p><strong>Conclusão:</strong> ${escapeHtml(result.finished_at)}</p>
        <p><strong>Acertos:</strong> ${result.acertos}</p>
        <p><strong>Erros:</strong> ${result.erros}</p>
        <p><strong>Nota final:</strong> ${escapeHtml(result.nota_formatada)}</p>
        <p><strong>Aproveitamento:</strong> ${result.aproveitamento}%</p>
        ${banner("ok", result.mensagem)}
        ${banner(result.salvo ? "info" : "bad", result.registro)}
        <ul class="review">${review}</ul>
        ${state.error ? `<div class="actions"><button class="btn btn-primary" id="retry-save" type="button">Tentar salvar novamente</button></div>` : ""}
      </section>
    `;
    const retry = document.querySelector("#retry-save");
    if (retry) {
      retry.addEventListener("click", async () => {
        retry.disabled = true;
        try {
          const data = await api("/api/finish", { method: "POST", body: finishBody() });
          state.result = data.result;
          state.error = data.salvo ? "" : "A lista do professor ainda não confirmou esta nota.";
        } catch (error) {
          state.error = error.message;
        }
        render();
      });
    }
  }

  async function loadState(countResume) {
    readViolations();
    try {
      const data = await api("/api/state" + (countResume ? "?count_resume=1" : ""));
      state.student = data.student;
      state.progress = data.progress;
      state.error = "";
      if (data.finished) {
        state.result = data.result;
        state.screen = "result";
      } else if (!state.session.instructionsSeen && data.progress.respondidas === 0 && data.progress.phase === "respondendo") {
        state.screen = "instructions";
      } else {
        state.question = data.question;
        state.feedback = data.feedback;
        state.screen = "question";
        state.session.instructionsSeen = true;
        saveSession();
      }
      render();
    } catch (error) {
      if (error.status === 401) {
        sessionStorage.removeItem(storageKey);
        state.session = null;
      }
      state.error = error.message;
      state.screen = "identify";
      render();
    }
  }

  function violationStorageKey() {
    return "jbs_violations";
  }

  function readViolations() {
    try {
      const saved = JSON.parse(sessionStorage.getItem(violationStorageKey()) || "null");
      if (saved && state.session && saved.attemptId === state.session.attemptId) {
        state.violations = Number(saved.count) || 0;
        return;
      }
    } catch (_error) {
      /* contagem nova */
    }
    state.violations = 0;
  }

  function saveViolations() {
    if (!state.session || !state.session.attemptId) return;
    sessionStorage.setItem(violationStorageKey(), JSON.stringify({
      attemptId: state.session.attemptId,
      count: state.violations
    }));
  }

  function finishBody() {
    return state.closure === "seguranca" ? { encerramento: "seguranca" } : {};
  }

  function clearClipboard() {
    const wipe = () => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText("").catch(() => {});
      }
    };
    wipe();
    window.setTimeout(wipe, 300);
  }

  let lastViolationAt = 0;

  function reportViolation(kind) {
    if (state.closing || state.screen === "result" || state.screen === "identify") return;
    if (!document.body.classList.contains("exam-lock")) return;
    const now = Date.now();
    if (now - lastViolationAt < 700) return;
    lastViolationAt = now;
    state.violations += 1;
    saveViolations();
    if (state.violations > 3) {
      state.closing = true;
      window.alert("A avaliação será encerrada. Houve mais de 3 tentativas de copiar, colar ou capturar a tela. O professor será avisado na planilha.");
      closeForSecurity();
      return;
    }
    const action = kind === "print" ? "capturar a tela (print)" : kind === "copy" ? "usar Ctrl+C" : "usar Ctrl+V";
    window.alert(`Não é permitido ${action} durante a avaliação. Tentativa ${state.violations} de 3. Se isso passar de 3 vezes, a prova será encerrada e o professor será avisado na planilha.`);
  }

  async function closeForSecurity() {
    state.closing = true;
    state.closure = "seguranca";
    setLock(false);
    try {
      const data = await api("/api/finish", { method: "POST", body: finishBody() });
      state.result = data.result;
      state.error = data.salvo ? "" : "A lista do professor ainda não confirmou esta nota.";
    } catch (error) {
      const acertos = state.progress ? state.progress.acertos : 0;
      const cents = state.progress && state.progress.nota_cents ? state.progress.nota_cents : 0;
      state.error = error.message;
      state.result = {
        nome: state.student ? state.student.nome : "",
        turma: state.student ? state.student.turma : "",
        started_at: state.student ? state.student.started_at : "",
        finished_at: "",
        acertos,
        erros: (state.progress.total || 20) - acertos,
        nota_formatada: state.progress && state.progress.pontuacao_formatada ? state.progress.pontuacao_formatada : "0,00",
        aproveitamento: Math.round(cents * 100 / 700),
        mensagem: "A avaliação foi encerrada porque houve mais de 3 tentativas de copiar, colar ou capturar a tela.",
        registro: "Não foi possível avisar o professor agora. Use Tentar salvar novamente.",
        encerramento: "Prova encerrada por tentativa de burlar a segurança",
        salvo: false,
        revisao: []
      };
    }
    state.screen = "result";
    state.sending = false;
    render();
  }

  function isPrintAttempt(event) {
    const key = String(event.key || "");
    const lower = key.toLowerCase();
    return key === "PrintScreen" || event.code === "PrintScreen" || lower === "printscreen"
      || ((event.metaKey || event.ctrlKey) && event.shiftKey && lower === "s")
      || ((event.ctrlKey || event.metaKey) && lower === "p");
  }

  document.addEventListener("contextmenu", (event) => {
    if (document.body.classList.contains("exam-lock")) event.preventDefault();
  });
  ["copy", "cut", "paste", "dragstart"].forEach((name) => {
    document.addEventListener(name, (event) => {
      if (!document.body.classList.contains("exam-lock")) return;
      event.preventDefault();
      if (name === "copy") reportViolation("copy");
      if (name === "paste") reportViolation("paste");
    });
  });
  document.addEventListener("keydown", (event) => {
    if (!document.body.classList.contains("exam-lock") || state.closing) return;
    const key = String(event.key || "").toLowerCase();
    const print = isPrintAttempt(event);
    const copy = (event.ctrlKey || event.metaKey) && key === "c";
    const paste = ((event.ctrlKey || event.metaKey) && key === "v") || (event.shiftKey && event.key === "Insert");
    const other = (event.ctrlKey || event.metaKey) && ["a", "x"].includes(key);
    if (print || copy || paste || other) event.preventDefault();
    if (event.repeat) return;
    if (print) {
      clearClipboard();
      reportViolation("print");
    } else if (copy) reportViolation("copy");
    else if (paste) reportViolation("paste");
  });
  document.addEventListener("keyup", (event) => {
    if (!document.body.classList.contains("exam-lock") || state.closing) return;
    if (event.key !== "PrintScreen" && event.code !== "PrintScreen") return;
    event.preventDefault();
    clearClipboard();
    reportViolation("print");
  });
  window.addEventListener("beforeprint", (event) => {
    if (!document.body.classList.contains("exam-lock") || state.closing) return;
    event.preventDefault();
    reportViolation("print");
  });
  window.addEventListener("beforeunload", (event) => {
    if (document.body.classList.contains("exam-lock")) {
      event.preventDefault();
      event.returnValue = "";
    }
  });

  state.session = readSession();
  if (usesPages() && state.session && state.session.attemptId && !PagesExam.matches(state.session)) {
    sessionStorage.removeItem(storageKey);
    state.session = null;
  }
  if (state.session && state.session.attemptId) {
    loadState(true);
  } else {
    state.session = null;
    state.screen = "identify";
    render();
  }
})();
