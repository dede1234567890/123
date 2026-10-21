const ExamUI = (() => {
  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));
  }

  function colorize(code) {
    const pattern = /(#.*$)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\b(if|elif|else|and|or|not|for|in|while|def|return|print)\b|(\d+)/gm;
    let html = "";
    let last = 0;
    for (const match of code.matchAll(pattern)) {
      html += escapeHtml(code.slice(last, match.index));
      const token = match[0];
      let cls = "tok-key";
      if (match[1]) cls = "tok-comment";
      else if (match[2]) cls = "tok-string";
      else if (match[4]) cls = "tok-number";
      html += `<span class="${cls}">${escapeHtml(token)}</span>`;
      last = match.index + token.length;
    }
    html += escapeHtml(code.slice(last));
    if (code.endsWith("\n")) html += "\n ";
    return html;
  }

  function codeBlock(code) {
    if (!code) return "";
    return `<pre class="code-view">${colorize(code)}</pre>`;
  }

  function syncEditor(editor) {
    const input = editor.querySelector(".editor-input");
    const highlight = editor.querySelector(".editor-highlight");
    const gutter = editor.querySelector(".editor-gutter");
    const lines = input.value.split("\n");
    gutter.innerHTML = lines.map((_, index) => `<span>${index + 1}</span>`).join("");
    highlight.innerHTML = colorize(input.value);
    highlight.scrollTop = input.scrollTop;
    highlight.scrollLeft = input.scrollLeft;
    gutter.scrollTop = input.scrollTop;
  }

  function editor(starter, locked) {
    const disabled = locked ? "readonly" : "";
    return `
      <p class="editor-caption">Editor Python</p>
      <div class="editor" data-editor>
        <div class="editor-gutter" aria-hidden="true"></div>
        <div class="editor-stage">
          <pre class="editor-highlight" aria-hidden="true"></pre>
          <textarea class="editor-input" spellcheck="false" autocomplete="off" autocapitalize="off" wrap="off" aria-label="Editor de código Python" ${disabled}></textarea>
        </div>
      </div>
    `;
  }

  function bindEditor(host, starter) {
    const editorRoot = host.querySelector("[data-editor]");
    if (!editorRoot) return;
    const input = editorRoot.querySelector(".editor-input");
    input.value = starter || "";
    const refresh = () => syncEditor(editorRoot);
    input.addEventListener("input", refresh);
    input.addEventListener("scroll", refresh);
    input.addEventListener("keydown", (event) => {
      if (event.key === "Tab" && !input.readOnly) {
        event.preventDefault();
        const start = input.selectionStart;
        const end = input.selectionEnd;
        input.value = input.value.slice(0, start) + "    " + input.value.slice(end);
        input.selectionStart = input.selectionEnd = start + 4;
        input.dispatchEvent(new Event("input"));
      }
    });
    refresh();
  }

  function renderQuestion(host, model, onChange) {
    const question = model.question;
    const feedback = model.feedback;
    const locked = Boolean(feedback);
    const response = feedback ? feedback.response || {} : {};
    let body = "";
    if (question.type === "true_false") {
      body = `<div class="statements">${question.statements.map((item) => {
        const chosen = response.answers ? response.answers[item.id] : undefined;
        const detail = feedback && feedback.detail
          ? feedback.detail.find((entry) => entry.id === item.id)
          : null;
        const mark = detail
          ? `<span class="mark ${detail.is_right ? "ok" : "bad"}">${detail.is_right ? "Classificação correta" : "Classificação incorreta"}</span>`
          : "";
        return `<article class="statement">
          <p>${escapeHtml(item.text)}</p>
          <div class="choices-inline">
            <label><input type="radio" name="tf-${escapeHtml(item.id)}" value="true" ${chosen === true ? "checked" : ""} ${locked ? "disabled" : ""}> <span>Verdadeiro</span></label>
            <label><input type="radio" name="tf-${escapeHtml(item.id)}" value="false" ${chosen === false ? "checked" : ""} ${locked ? "disabled" : ""}> <span>Falso</span></label>
          </div>
          ${mark}
        </article>`;
      }).join("")}</div>`;
    } else if (question.type === "multiple_choice") {
      body = `${codeBlock(question.code || "")}<div class="choices">${question.options.map((option) => `
        <label class="option ${response.option === option.id ? "selected" : ""}">
          <input type="radio" name="option" value="${escapeHtml(option.id)}" ${response.option === option.id ? "checked" : ""} ${locked ? "disabled" : ""}>
          <span><strong>${escapeHtml(option.id)})</strong> ${escapeHtml(option.text)}</span>
        </label>`).join("")}</div>`;
    } else {
      body = editor(response.code || question.starter || "", locked) + `
        <div class="code-tools">
          <button class="btn btn-secondary" type="button" id="run-btn">Testar código</button>
        </div>
        <pre id="run-log" class="run-log" hidden></pre>
      `;
    }
    host.innerHTML = `
      <p class="topic">${escapeHtml(question.topic)}</p>
      <h2>Questão ${question.number}</h2>
      <p class="muted">Vale ${escapeHtml(question.valor || (question.number <= 8 ? "0,20" : "0,45"))}</p>
      <p class="prompt">${escapeHtml(question.prompt)}</p>
      ${body}
    `;
    if (question.type === "code" && !response.code) {
      bindEditor(host, question.starter || "");
    } else if (question.type === "code") {
      bindEditor(host, response.code || "");
    }
    const run = host.querySelector("#run-btn");
    if (run) {
      run.addEventListener("click", () => {
        const input = host.querySelector(".editor-input");
        const log = host.querySelector("#run-log");
        const result = PagesExam.preview(input ? input.value : "");
        log.hidden = false;
        log.className = "run-log " + (result.ok ? "ok" : "bad");
        log.textContent = result.text;
      });
    }
    if (!locked) {
      host.addEventListener("input", onChange);
      host.addEventListener("change", onChange);
    }
  }

  function collect(host, question) {
    if (question.type === "true_false") {
      const answers = {};
      for (const item of question.statements) {
        const selected = host.querySelector(`input[name="tf-${CSS.escape(item.id)}"]:checked`);
        if (!selected) return null;
        answers[item.id] = selected.value === "true";
      }
      return { answers };
    }
    if (question.type === "multiple_choice") {
      const selected = host.querySelector('input[name="option"]:checked');
      if (!selected) return null;
      return { option: selected.value };
    }
    const input = host.querySelector(".editor-input");
    if (!input || !input.value.trim()) return null;
    return { code: input.value };
  }

  return { escapeHtml, renderQuestion, collect, colorize };
})();
