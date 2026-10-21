/* Prova no link do GitHub. O gabarito fica neste arquivo. */
const PagesExam = (() => {
  const STORAGE = "jbs_pages_record";
  const TOTAL = 20;
  const MAX_CENTS = 700;
  function pointsCents(number) {
    return number <= 8 ? 20 : 45;
  }
  function formatScore(cents) {
    const safe = Math.max(0, Math.round(cents));
    return `${Math.floor(safe / 100)},${String(safe % 100).padStart(2, "0")}`;
  }
  function scoreCents(record) {
    return Object.keys(record.answers || {}).reduce((sum, number) => {
      const answer = record.answers[number];
      return sum + (answer && answer.correct ? pointsCents(Number(number)) : 0);
    }, 0);
  }
  const QUESTIONS = {
    1: {
      type: "true_false",
      topic: "if, elif e else",
      prompt: "A JBS FoodTech está programando a verificação de um pedido. Classifique cada afirmação sobre if, elif e else. A questão vale 0,20 somente se todas estiverem corretas.",
      statements: [
        { id: "1", text: "O else é executado quando a condição do if é falsa e nenhum elif é verdadeiro." },
        { id: "2", text: "É possível usar vários elif para tratar situações diferentes de um pedido." },
        { id: "3", text: "O else precisa de uma condição, como em else quantidade == 0:" },
        { id: "4", text: "Quando a condição do if é verdadeira, o Python também executa os elif seguintes." }
      ],
      key: { 1: true, 2: true, 3: false, 4: false },
      explanation: "Em if/elif/else, apenas um caminho é executado. O else não recebe condição e só acontece quando o if e todos os elif são falsos. Vários elif podem aparecer em sequência. As afirmações 1 e 2 são verdadeiras. As afirmações 3 e 4 são falsas."
    },
    2: {
      type: "multiple_choice",
      topic: "Análise de código",
      prompt: "O programa abaixo confere se a quantidade pedida cabe no estoque da JBS FoodTech. Qual texto é exibido na tela?",
      code: "estoque = 12\npedido = 15\n\nif pedido < estoque:\n    print(\"Pedido aprovado\")\nelif pedido == estoque:\n    print(\"Estoque exato\")\nelse:\n    print(\"Estoque insuficiente\")\n",
      options: [
        { id: "A", text: "Pedido aprovado" },
        { id: "B", text: "Estoque exato" },
        { id: "C", text: "Estoque insuficiente" },
        { id: "D", text: "O programa apresenta um erro e não exibe nada" }
      ],
      key: "C",
      explanation: "O pedido é 15 e o estoque é 12. Como 15 não é menor que 12 e também não é igual, o programa segue para o else e exibe Estoque insuficiente."
    },
    3: {
      type: "multiple_choice",
      topic: "Operadores and e or",
      prompt: "A JBS FoodTech aprova um pedido somente quando o pagamento foi confirmado e, além disso, o estoque é suficiente ou o produto está em promoção. Qual condição representa essa regra?",
      code: "pagamento_confirmado = 1\nestoque_suficiente = 0\nem_promocao = 1\n\nif ________________:\n    print(\"Pedido aprovado\")\nelse:\n    print(\"Pedido recusado\")\n",
      options: [
        { id: "A", text: "pagamento_confirmado and estoque_suficiente" },
        { id: "B", text: "pagamento_confirmado and (estoque_suficiente or em_promocao)" },
        { id: "C", text: "(not pagamento_confirmado) and em_promocao" },
        { id: "D", text: "estoque_suficiente and em_promocao" }
      ],
      key: "B",
      explanation: "A regra junta duas exigências com and: o pagamento confirmado e, entre parênteses, estoque suficiente ou promoção. Com os valores do enunciado, somente pagamento_confirmado and (estoque_suficiente or em_promocao) é verdadeira."
    },
    4: {
      type: "multiple_choice",
      topic: "Correção de erros",
      prompt: "O programa abaixo deveria verificar a quantidade de um pedido, mas há um erro de escrita. Qual correção resolve o problema?",
      code: "quantidade = 0\n\nif quantidade > 0\n    print(\"Quantidade válida\")\nelif quantidade == 0:\n    print(\"Informe uma quantidade\")\nelse:\n    print(\"Quantidade inválida\")\n",
      options: [
        { id: "A", text: "Trocar elif por else if" },
        { id: "B", text: "Colocar : no final da linha do if" },
        { id: "C", text: "Apagar todo o bloco else" },
        { id: "D", text: "Trocar == por = na comparação quantidade == 0" }
      ],
      key: "B",
      explanation: "Faltaram os dois-pontos no final da linha do if. Em Python, if, elif e else terminam com :. As outras alternativas não corrigem esse erro de escrita."
    },
    5: {
      type: "multiple_choice",
      topic: "Listas",
      prompt: "O programa organiza uma lista de produtos. O que ele exibe?",
      code: "produtos = [\"hamburguer\", \"batata\", \"suco\"]\nprodutos[1] = \"refrigerante\"\nprodutos.append(\"sobremesa\")\nprint(produtos[0])\nprint(len(produtos))\n",
      options: [
        { id: "A", text: "hamburguer e depois 3" },
        { id: "B", text: "refrigerante e depois 4" },
        { id: "C", text: "hamburguer e depois 4" },
        { id: "D", text: "suco e depois 3" }
      ],
      key: "C",
      explanation: "O índice 0 continua sendo hamburguer, porque a troca foi feita no índice 1. O append acrescenta sobremesa, e a lista passa a ter 4 itens. O programa exibe hamburguer e depois 4."
    },
    6: {
      type: "multiple_choice",
      topic: "Laço for",
      prompt: "O programa percorre as quantidades dos pedidos e conta quantos têm 2 ou mais unidades. O que aparece na tela?",
      code: "pedidos = [2, 5, 1, 4]\ntotal = 0\nfor quantidade in pedidos:\n    if quantidade >= 2:\n        total = total + 1\nprint(total)\n",
      options: [
        { id: "A", text: "4" },
        { id: "B", text: "3" },
        { id: "C", text: "12" },
        { id: "D", text: "1" }
      ],
      key: "B",
      explanation: "O for percorre os quatro números, mas o contador só aumenta quando a quantidade é maior ou igual a 2. Isso acontece com 2, 5 e 4. O valor 1 não entra. O programa exibe 3."
    },
    7: {
      type: "multiple_choice",
      topic: "Laço while",
      prompt: "O sistema deve pedir a quantidade enquanto ela for inválida. Quantidade válida é um número maior que zero. A variável começa valendo 0. Qual condição completa o while corretamente?",
      code: "quantidade = 0\nwhile ________________:\n    quantidade = int(input(\"Digite a quantidade: \"))\nprint(\"Quantidade aceita\")\n",
      options: [
        { id: "A", text: "quantidade > 0" },
        { id: "B", text: "quantidade <= 0" },
        { id: "C", text: "quantidade == 1" },
        { id: "D", text: "quantidade >= 0" }
      ],
      key: "B",
      explanation: "O laço precisa continuar enquanto a quantidade for inválida, isto é, menor ou igual a zero. Quando um valor maior que zero é informado, quantidade <= 0 fica falsa e a repetição termina."
    },
    8: {
      type: "multiple_choice",
      topic: "Funções",
      prompt: "A função abaixo mostra a mensagem inicial do sistema e não recebe parâmetros. Qual alternativa chama a função corretamente e exibe a mensagem?",
      code: "def mensagem_boas_vindas():\n    print(\"Bem-vindo a JBS FoodTech\")\n",
      options: [
        { id: "A", text: "mensagem_boas_vindas" },
        { id: "B", text: "mensagem_boas_vindas()" },
        { id: "C", text: "mensagem_boas_vindas(\"8A\")" },
        { id: "D", text: "def mensagem_boas_vindas()" }
      ],
      key: "B",
      explanation: "Para executar uma função sem parâmetros, escreva o nome seguido de parênteses vazios: mensagem_boas_vindas(). Sem os parênteses, a função não é chamada."
    },
    9: {
      type: "code",
      topic: "Construção de código",
      prompt: "Crie as variáveis pagamento, estoque e quantidade. pagamento vale 1 quando o pagamento foi confirmado e 0 quando não foi. Mostre Aprovado se pagamento for 1 e estoque for maior ou igual à quantidade. Nos outros casos, mostre Recusado. Use if, else e and. Teste com um exemplo antes de confirmar.",
      starter: "",
      explanationCorrect: "Sua solução aprova o pedido somente quando o pagamento está confirmado e o estoque cobre a quantidade pedida. O else trata os outros casos.",
      explanationWrong: "O pedido só pode ser aprovado quando o pagamento está confirmado e o estoque é maior ou igual à quantidade. Use if, else e and, e exiba exatamente Aprovado ou Recusado. Confira também os dois-pontos e a indentação."
    },
    10: {
      type: "code",
      topic: "Desafio integrador",
      prompt: "Crie a lista pedidos. Exemplo: [3, 0, 5, 2]. Crie a função pedido_valido: ela recebe quantidade e retorna 1 se for maior que 0, senão retorna 0. Crie a variável aprovados e use for para contar os pedidos válidos. No exemplo, aprovados fica 3. Teste antes de confirmar.",
      starter: "",
      explanationCorrect: "A função identifica quantidades maiores que zero, e o for usa essa função para contar os pedidos válidos da lista.",
      explanationWrong: "A função pedido_valido precisa retornar 1 somente quando a quantidade é maior que zero, e 0 nos outros casos. O for deve percorrer pedidos, chamar essa função e somar 1 em aprovados a cada pedido válido. Confira a indentação e os dois-pontos."
    },
    11: {
      type: "code",
      topic: "Correção de código",
      prompt: "O programa cria estoque e quantidade, mas só aprova quando o estoque é maior. Ele também deve aprovar quando os dois valores são iguais. Corrija a comparação. Mostre Aprovado ou Recusado. Teste antes de confirmar.",
      starter: "estoque = 3\nquantidade = 3\nif estoque > quantidade:\n    print(\"Aprovado\")\nelse:\n    print(\"Recusado\")\n",
      explanationCorrect: "A comparação correta é estoque >= quantidade. Quando os dois valores são iguais, o estoque ainda cobre o pedido e o programa exibe Aprovado.",
      explanationWrong: "Troque a comparação para estoque >= quantidade. Com o sinal >, um estoque igual à quantidade fica Recusado, e isso não atende à regra."
    },
    12: {
      type: "code",
      topic: "Correção de código",
      prompt: "O programa cria a lista pedidos e conta só os pedidos com mais de 2 unidades. Ele deveria contar também o pedido com 2. Corrija a condição. No exemplo, o programa deve mostrar 3. Teste antes de confirmar.",
      starter: "pedidos = [2, 5, 1, 4]\ntotal = 0\nfor quantidade in pedidos:\n    if quantidade > 2:\n        total = total + 1\nprint(total)\n",
      explanationCorrect: "A condição quantidade >= 2 inclui o próprio 2. O for percorre a lista e o print mostra a contagem.",
      explanationWrong: "A condição precisa ser quantidade >= 2. Com quantidade > 2, um pedido de exatamente 2 unidades não entra na conta."
    },
    13: {
      type: "code",
      topic: "Correção de código",
      prompt: "Corrija a função estoque_baixo. Ela recebe quantidade e deve retornar 1 quando a quantidade for menor que 5. Nos outros casos, retorne 0. Para testar, escreva print(estoque_baixo(4)) embaixo da função.",
      starter: "def estoque_baixo(quantidade):\n    if quantidade > 5:\n        return 1\n    else:\n        return 0\n",
      explanationCorrect: "A função retorna 1 somente quando a quantidade é menor que 5. O 5 e os valores maiores retornam 0.",
      explanationWrong: "Troque a comparação para quantidade < 5. Do jeito atual, quantidades pequenas retornam 0."
    },
    14: {
      type: "code",
      topic: "Correção de código",
      prompt: "O programa cria pagamento, estoque e quantidade, mas usa or. As duas partes precisam ser verdadeiras: pagamento igual a 1 e estoque maior ou igual à quantidade. Troque or por and. Mostre Aprovado ou Recusado. Teste antes de confirmar.",
      starter: "pagamento = 1\nestoque = 2\nquantidade = 5\nif pagamento == 1 or estoque >= quantidade:\n    print(\"Aprovado\")\nelse:\n    print(\"Recusado\")\n",
      explanationCorrect: "As duas partes precisam ser verdadeiras ao mesmo tempo: pagamento == 1 e estoque >= quantidade.",
      explanationWrong: "Com or, basta uma das partes para aprovar. Use and para exigir o pagamento confirmado e o estoque suficiente."
    },
    15: {
      type: "code",
      topic: "Correção de código",
      prompt: "O programa cria a lista pedidos. A função pedido_valido está certa. O for conta os pedidos inválidos, porque compara com 0. Corrija para contar os válidos. No exemplo, aprovados fica 3. Teste antes de confirmar.",
      starter: "pedidos = [3, 0, 5, 2]\ndef pedido_valido(quantidade):\n    if quantidade > 0:\n        return 1\n    else:\n        return 0\n\naprovados = 0\nfor quantidade in pedidos:\n    if pedido_valido(quantidade) == 0:\n        aprovados = aprovados + 1\n",
      explanationCorrect: "A comparação == 1 seleciona os pedidos válidos. O for soma 1 em aprovados a cada chamada que retorna 1.",
      explanationWrong: "pedido_valido(quantidade) == 0 conta justamente os pedidos que não valem. Troque por == 1."
    },
    16: {
      type: "code",
      topic: "Construção de código",
      prompt: "Crie as variáveis promocao e estoque. promocao vale 1 quando o produto está em promoção e 0 quando não está. Mostre Promocao se promocao for 1 ou o estoque for maior que 20. Nos outros casos, mostre Normal. Use if, else e or. Teste antes de confirmar.",
      starter: "",
      explanationCorrect: "A condição com or aceita promoção ou estoque acima de 20. O else exibe Normal nos demais casos.",
      explanationWrong: "Use if, else e or. A mensagem Promocao aparece se promocao == 1 ou estoque > 20. Estoque igual a 20, sem promoção, deve exibir Normal."
    },
    17: {
      type: "code",
      topic: "Construção de código",
      prompt: "Crie a função preco_alto. Ela recebe valor. Retorne 1 se o valor for maior que 50. Senão, retorne 0. Para testar, escreva print(preco_alto(60)) embaixo da função.",
      starter: "",
      explanationCorrect: "A função retorna 1 apenas quando valor > 50. O valor 50 e os menores retornam 0.",
      explanationWrong: "Complete o if valor > 50 para retornar 1, e o else para retornar 0. Um return 0 fixo não distingue os preços."
    },
    18: {
      type: "code",
      topic: "Construção de código",
      prompt: "Crie a lista pedidos. Exemplo: [2, 5, 1, 4]. Crie a variável soma e use for para somar todas as quantidades. Mostre a soma. No exemplo, o programa mostra 12. Teste antes de confirmar.",
      starter: "",
      explanationCorrect: "O for percorre pedidos e acumula cada quantidade em soma. O print mostra o total.",
      explanationWrong: "Comece soma em 0, percorra pedidos com for e some cada quantidade. Depois exiba soma. Uma lista vazia precisa continuar valendo 0."
    },
    19: {
      type: "code",
      topic: "Construção de código",
      prompt: "Crie a variável meta. Exemplo: meta = 3. Crie quantidade com valor 0. Enquanto quantidade for menor que meta, some 1. Use while. No final, quantidade fica igual a meta. Teste antes de confirmar.",
      starter: "",
      explanationCorrect: "O while quantidade < meta soma 1 a cada volta e para quando quantidade alcança meta.",
      explanationWrong: "Escreva while quantidade < meta e, dentro dele, quantidade = quantidade + 1. A condição <= faria o laço passar de meta ou não terminar."
    },
    20: {
      type: "code",
      topic: "Desafio integrador",
      prompt: "Crie a lista pedidos. Exemplo: [2, 5, 1, 4]. Crie a função pedido_grande: ela recebe quantidade e retorna 1 se for maior ou igual a 2, senão retorna 0. Crie a variável grandes e use for para contar os pedidos grandes. No exemplo, grandes fica 3. Teste antes de confirmar.",
      starter: "",
      explanationCorrect: "A função reconhece quantidades a partir de 2, e o for usa esse retorno para contar grandes.",
      explanationWrong: "pedido_grande precisa retornar 1 quando quantidade >= 2, e 0 nos outros casos. O for deve chamar a função e somar 1 em grandes apenas quando o retorno for 1."
    }
  };

  function tokenize(source) {
    if (typeof source !== "string" || source.length > 2000 || source.includes("\0")) throw new Error("codigo");
    const lines = source.replace(/\t/g, "    ").split("\n");
    const tokens = [];
    const indents = [0];
    const pattern = /\s+|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\d+|==|!=|<=|>=|\+=|-=|[A-Za-z_][A-Za-z0-9_]*|./g;
    lines.forEach((line) => {
      const clean = line.replace(/#.*$/, "");
      if (!clean.trim()) {
        tokens.push({ type: "NL" });
        return;
      }
      const indent = clean.match(/^ */)[0].length;
      if (indent > indents[indents.length - 1]) {
        indents.push(indent);
        tokens.push({ type: "INDENT" });
      } else {
        while (indent < indents[indents.length - 1]) {
          indents.pop();
          tokens.push({ type: "DEDENT" });
        }
        if (indent !== indents[indents.length - 1]) throw new Error("indent");
      }
      const body = clean.trim();
      let match;
      pattern.lastIndex = 0;
      while ((match = pattern.exec(body))) {
        const text = match[0];
        if (/^\s+$/.test(text)) continue;
        if (/^["']/.test(text)) tokens.push({ type: "STR", value: text.slice(1, -1).replace(/\\n/g, "\n").replace(/\\"/g, '"').replace(/\\'/g, "'") });
        else if (/^\d+$/.test(text)) tokens.push({ type: "NUM", value: Number(text) });
        else if (/^[A-Za-z_]/.test(text)) tokens.push({ type: "NAME", value: text });
        else tokens.push({ type: "OP", value: text });
      }
      tokens.push({ type: "NL" });
    });
    while (indents.length > 1) {
      indents.pop();
      tokens.push({ type: "DEDENT" });
    }
    tokens.push({ type: "EOF" });
    return tokens;
  }

  function parse(tokens) {
    let index = 0;
    const peek = () => tokens[index];
    const eat = (type, value) => {
      const token = peek();
      if (!token || token.type !== type || (value !== undefined && token.value !== value)) throw new Error("sintaxe");
      index += 1;
      return token;
    };
    const skipNl = () => { while (peek() && peek().type === "NL") index += 1; };
    const isName = (value) => peek() && peek().type === "NAME" && peek().value === value;
    function parseBlock() {
      eat("INDENT");
      const body = [];
      while (peek() && peek().type !== "DEDENT" && peek().type !== "EOF") {
        if (peek().type === "NL") { index += 1; continue; }
        body.push(parseStmt());
        skipNl();
      }
      eat("DEDENT");
      return body;
    }
    function parseSuite() {
      eat("OP", ":");
      skipNl();
      if (!peek() || peek().type !== "INDENT") throw new Error("bloco");
      return parseBlock();
    }
    function parseIf(keyword) {
      eat("NAME", keyword);
      const test = parseOr();
      const body = parseSuite();
      let orelse = [];
      if (isName("elif")) orelse = [parseIf("elif")];
      else if (isName("else")) {
        eat("NAME", "else");
        orelse = parseSuite();
      }
      return { type: "if", test, body, orelse };
    }
    function parseStmt() {
      if (isName("if") || isName("elif")) return parseIf(peek().value);
      if (isName("for")) {
        eat("NAME", "for");
        const name = eat("NAME").value;
        eat("NAME", "in");
        const iter = parseOr();
        return { type: "for", name, iter, body: parseSuite() };
      }
      if (isName("while")) {
        eat("NAME", "while");
        const test = parseOr();
        return { type: "while", test, body: parseSuite() };
      }
      if (isName("def")) {
        eat("NAME", "def");
        const name = eat("NAME").value;
        eat("OP", "(");
        const params = [];
        if (!(peek() && peek().type === "OP" && peek().value === ")")) {
          params.push(eat("NAME").value);
          while (peek() && peek().type === "OP" && peek().value === ",") {
            index += 1;
            params.push(eat("NAME").value);
          }
        }
        eat("OP", ")");
        return { type: "def", name, params, body: parseSuite() };
      }
      if (isName("return")) {
        eat("NAME", "return");
        if (peek().type === "NL" || peek().type === "DEDENT" || peek().type === "EOF") return { type: "return", value: { type: "const", value: null } };
        return { type: "return", value: parseOr() };
      }
      if (isName("pass") || isName("break") || isName("continue")) {
        const kind = eat("NAME").value;
        return { type: kind };
      }
      if (peek().type === "NAME" && tokens[index + 1] && tokens[index + 1].type === "OP" && ["=", "+=", "-="].includes(tokens[index + 1].value)) {
        const name = eat("NAME").value;
        const op = eat("OP").value;
        return { type: op === "=" ? "assign" : "aug", name, op, value: parseOr() };
      }
      return { type: "expr", expr: parseOr() };
    }
    function parseOr() {
      let left = parseAnd();
      while (isName("or")) { index += 1; left = { type: "bool", op: "or", left, right: parseAnd() }; }
      return left;
    }
    function parseAnd() {
      let left = parseNot();
      while (isName("and")) { index += 1; left = { type: "bool", op: "and", left, right: parseNot() }; }
      return left;
    }
    function parseNot() {
      if (isName("not")) { index += 1; return { type: "not", value: parseNot() }; }
      return parseCmp();
    }
    function parseCmp() {
      const left = parseAdd();
      const ops = [];
      const rights = [];
      const names = { "==": "eq", "!=": "ne", "<": "lt", "<=": "le", ">": "gt", ">=": "ge" };
      while (peek() && peek().type === "OP" && names[peek().value]) {
        ops.push(names[eat("OP").value]);
        rights.push(parseAdd());
      }
      return ops.length ? { type: "cmp", left, ops, rights } : left;
    }
    function parseAdd() {
      let left = parseUnary();
      while (peek() && peek().type === "OP" && (peek().value === "+" || peek().value === "-")) {
        const op = eat("OP").value;
        left = { type: "bin", op, left, right: parseUnary() };
      }
      return left;
    }
    function parseUnary() {
      if (peek() && peek().type === "OP" && peek().value === "-") {
        index += 1;
        return { type: "neg", value: parseUnary() };
      }
      return parsePrimary();
    }
    function parsePrimary() {
      const token = peek();
      if (token.type === "NUM") { index += 1; return { type: "const", value: token.value }; }
      if (token.type === "STR") { index += 1; return { type: "const", value: token.value }; }
      if (token.type === "NAME" && (token.value === "True" || token.value === "False")) {
        index += 1;
        return { type: "const", value: token.value === "True" };
      }
      if (token.type === "OP" && token.value === "(") {
        index += 1;
        const value = parseOr();
        eat("OP", ")");
        return value;
      }
      if (token.type === "OP" && token.value === "[") {
        index += 1;
        const items = [];
        if (!(peek() && peek().type === "OP" && peek().value === "]")) {
          items.push(parseOr());
          while (peek() && peek().type === "OP" && peek().value === ",") { index += 1; items.push(parseOr()); }
        }
        eat("OP", "]");
        return { type: "list", items };
      }
      if (token.type === "NAME") {
        const name = eat("NAME").value;
        if (peek() && peek().type === "OP" && peek().value === "(") {
          index += 1;
          const args = [];
          if (!(peek() && peek().type === "OP" && peek().value === ")")) {
            args.push(parseOr());
            while (peek() && peek().type === "OP" && peek().value === ",") { index += 1; args.push(parseOr()); }
          }
          eat("OP", ")");
          return { type: "call", name, args };
        }
        return { type: "name", name };
      }
      throw new Error("expressao");
    }
    function parseModule() {
      const body = [];
      skipNl();
      while (peek() && peek().type !== "EOF") {
        if (peek().type === "NL") { index += 1; continue; }
        body.push(parseStmt());
        skipNl();
      }
      return body;
    }
    return parseModule();
  }

  function truthy(value) {
    if (value === null || value === false) return false;
    if (value === true) return true;
    if (typeof value === "number") return value !== 0;
    if (typeof value === "string") return value !== "";
    if (Array.isArray(value)) return value.length !== 0;
    throw new Error("valor");
  }

  function execute(code, env, stripNames) {
    let tree = parse(tokenize(code));
    if (stripNames && stripNames.length) {
      const skip = new Set(stripNames);
      tree = tree.filter((stmt) => !(stmt.type === "assign" && skip.has(stmt.name)));
    }
    const state = { env: Object.assign({}, env), local: null, functions: {}, output: [], steps: 0, depth: 0 };
    const returned = { signal: "return" };
    function step() {
      state.steps += 1;
      if (state.steps > 4000) throw new Error("limite");
    }
    function lookup(name) {
      if (state.local && Object.prototype.hasOwnProperty.call(state.local, name)) return state.local[name];
      if (Object.prototype.hasOwnProperty.call(state.env, name)) return state.env[name];
      throw new Error("nome");
    }
    function assign(name, value) {
      if (["print", "len", "True", "False", "None"].includes(name)) throw new Error("nome");
      if (state.local) state.local[name] = value;
      else state.env[name] = value;
    }
    function evalExpr(expr) {
      step();
      if (expr.type === "const") return expr.value;
      if (expr.type === "name") return lookup(expr.name);
      if (expr.type === "list") return expr.items.map(evalExpr);
      if (expr.type === "not") return !truthy(evalExpr(expr.value));
      if (expr.type === "neg") {
        const value = evalExpr(expr.value);
        if (typeof value !== "number") throw new Error("numero");
        return -value;
      }
      if (expr.type === "bin") {
        const left = evalExpr(expr.left);
        const right = evalExpr(expr.right);
        if (typeof left !== "number" || typeof right !== "number") throw new Error("numero");
        return expr.op === "+" ? left + right : left - right;
      }
      if (expr.type === "bool") {
        const left = evalExpr(expr.left);
        if (expr.op === "and") return truthy(left) ? evalExpr(expr.right) : left;
        return truthy(left) ? left : evalExpr(expr.right);
      }
      if (expr.type === "cmp") {
        let left = evalExpr(expr.left);
        for (let i = 0; i < expr.ops.length; i += 1) {
          const right = evalExpr(expr.rights[i]);
          const op = expr.ops[i];
          const same = left === right || (left === true && right === 1) || (left === 1 && right === true) || (left === false && right === 0) || (left === 0 && right === false);
          const ok = op === "eq" ? same : op === "ne" ? !same : op === "lt" ? left < right : op === "le" ? left <= right : op === "gt" ? left > right : left >= right;
          if (!ok) return false;
          left = right;
        }
        return true;
      }
      if (expr.type === "call") return call(expr.name, expr.args.map(evalExpr));
      throw new Error("expressao");
    }
    function call(name, args) {
      if (name === "print") {
        if (args.length !== 1) throw new Error("print");
        state.output.push(args[0]);
        return null;
      }
      if (name === "len") {
        if (args.length !== 1 || !(Array.isArray(args[0]) || typeof args[0] === "string")) throw new Error("len");
        return args[0].length;
      }
      const fn = state.functions[name];
      if (!fn) throw new Error("funcao");
      if (fn.params.length !== args.length) throw new Error("args");
      state.depth += 1;
      if (state.depth > 12) throw new Error("recursao");
      const previous = state.local;
      state.local = {};
      fn.params.forEach((param, i) => { state.local[param] = args[i]; });
      try {
        runBody(fn.body);
        return null;
      } catch (error) {
        if (error && error.signal === "return") return error.value;
        throw error;
      } finally {
        state.local = previous;
        state.depth -= 1;
      }
    }
    function runBody(body) {
      body.forEach(runStmt);
    }
    function runStmt(stmt) {
      step();
      if (stmt.type === "def") state.functions[stmt.name] = stmt;
      else if (stmt.type === "if") runBody(truthy(evalExpr(stmt.test)) ? stmt.body : stmt.orelse);
      else if (stmt.type === "assign") assign(stmt.name, evalExpr(stmt.value));
      else if (stmt.type === "aug") {
        const current = lookup(stmt.name);
        const other = evalExpr(stmt.value);
        if (typeof current !== "number" || typeof other !== "number") throw new Error("numero");
        assign(stmt.name, stmt.op === "+=" ? current + other : current - other);
      } else if (stmt.type === "for") {
        const items = evalExpr(stmt.iter);
        if (!Array.isArray(items)) throw new Error("lista");
        for (let i = 0; i < items.length; i += 1) {
          if (i > 300) throw new Error("limite");
          assign(stmt.name, items[i]);
          try { runBody(stmt.body); } catch (error) {
            if (error && error.signal === "continue") continue;
            if (error && error.signal === "break") break;
            throw error;
          }
        }
      } else if (stmt.type === "while") {
        let count = 0;
        while (truthy(evalExpr(stmt.test))) {
          count += 1;
          if (count > 300) throw new Error("limite");
          try { runBody(stmt.body); } catch (error) {
            if (error && error.signal === "continue") continue;
            if (error && error.signal === "break") break;
            throw error;
          }
        }
      } else if (stmt.type === "return") {
        const error = new Error("return");
        error.signal = "return";
        error.value = evalExpr(stmt.value);
        throw error;
      } else if (stmt.type === "break" || stmt.type === "continue") {
        const error = new Error(stmt.type);
        error.signal = stmt.type;
        throw error;
      } else if (stmt.type === "pass") return;
      else if (stmt.type === "expr") evalExpr(stmt.expr);
      else throw new Error("comando");
    }
    try { runBody(tree); } catch (error) {
      if (error && error.signal) throw new Error("fluxo");
      throw error;
    }
    return state;
  }

  function printed(output) {
    return output.map((item) => String(item).trim()).filter(Boolean);
  }

  function hasNode(body, type) {
    for (const stmt of body) {
      if (stmt.type === type) return true;
      const nested = []
        .concat(stmt.body || [])
        .concat(stmt.orelse || []);
      if (nested.length && hasNode(nested, type)) return true;
    }
    return false;
  }

  function treeText(code) {
    return JSON.stringify(parse(tokenize(code)));
  }

  function creates(tree, names) {
    const found = new Set();
    tree.forEach((stmt) => {
      if (stmt.type === "assign") found.add(stmt.name);
    });
    return names.every((name) => found.has(name));
  }

  function shows(code, cases, strip) {
    return cases.every(([env, expected]) => printed(execute(code, env, strip).output).join("|") === String(expected));
  }

  function flagMatches(value, expected) {
    if (expected === 1) return value === 1 || value === true;
    return value === 0 || value === false;
  }

  function callFlag(code, name, cases) {
    const text = treeText(code);
    if (!text.includes(`"name":"${name}"`) || !text.includes('"type":"if"')) return false;
    return cases.every(([quantity, expected]) => {
      const probe = execute(`${code}\nresultado_funcao = ${name}(valor_testado)\n`, { pedidos: [], valor_testado: quantity });
      return flagMatches(probe.env.resultado_funcao, expected);
    });
  }

  function gradeCode(number, code) {
    const tree = parse(tokenize(code));
    const text = JSON.stringify(tree);
    const hasElse = text.includes('"orelse":[{');
    const hasIf = text.includes('"type":"if"');
    const hasFor = text.includes('"type":"for"');
    const hasWhile = text.includes('"type":"while"');
    const hasAnd = text.includes('"op":"and"');
    const hasOr = text.includes('"op":"or"');
    if (number === 9) {
      const hasElse = tree.some((stmt) => stmt.type === "if" && stmt.orelse.length) || JSON.stringify(tree).includes('"orelse":[{');
      const text = JSON.stringify(tree);
      if (!creates(tree, ["pagamento", "estoque", "quantidade"])) return false;
      if (!text.includes('"op":"and"') && !text.includes('"op":"or"')) return false;
      if (!hasElse && !text.includes('"type":"if"')) return false;
      if (!text.includes('"type":"if"') || !text.includes('"orelse":[{')) return false;
      const strip = ["pagamento", "estoque", "quantidade"];
      const cases = [
        [{ pagamento: 1, estoque: 10, quantidade: 4 }, "Aprovado"],
        [{ pagamento: 1, estoque: 2, quantidade: 5 }, "Recusado"],
        [{ pagamento: 0, estoque: 10, quantidade: 1 }, "Recusado"],
        [{ pagamento: 1, estoque: 3, quantidade: 3 }, "Aprovado"],
        [{ pagamento: 0, estoque: 8, quantidade: 8 }, "Recusado"],
        [{ pagamento: 1, estoque: 0, quantidade: 0 }, "Aprovado"],
        [{ pagamento: 1, estoque: 1, quantidade: 2 }, "Recusado"]
      ];
      return cases.every(([env, expected]) => printed(execute(code, env, strip).output).join("|") === expected);
    }
    if (number === 10 || number === 15) {
      if (!creates(tree, ["pedidos"])) return false;
      if (!text.includes('"type":"def"') || !text.includes("pedido_valido") || !hasFor || !text.includes('"name":"pedido_valido"') || !hasIf) return false;
      const lists = [[3, 0, 5, 2], [0, 0, 0], [1], [4, 2], [], [-1, 0, 7], [8]];
      for (const orders of lists) {
        const result = execute(code, { pedidos: orders.slice() }, ["pedidos"]);
        if (result.env.aprovados !== orders.filter((item) => item > 0).length) return false;
      }
      return callFlag(code, "pedido_valido", [[3, 1], [1, 1], [0, 0], [-3, 0], [12, 1]]);
    }
    if (number === 11) {
      if (!creates(tree, ["estoque", "quantidade"]) || !hasElse) return false;
      return shows(code, [
        [{ estoque: 10, quantidade: 4 }, "Aprovado"],
        [{ estoque: 3, quantidade: 3 }, "Aprovado"],
        [{ estoque: 2, quantidade: 5 }, "Recusado"],
        [{ estoque: 0, quantidade: 0 }, "Aprovado"],
        [{ estoque: 1, quantidade: 2 }, "Recusado"]
      ], ["estoque", "quantidade"]);
    }
    if (number === 12) {
      if (!creates(tree, ["pedidos"]) || !hasFor || !hasIf) return false;
      return shows(code, [
        [{ pedidos: [2, 5, 1, 4] }, "3"],
        [{ pedidos: [2, 2] }, "2"],
        [{ pedidos: [1] }, "0"],
        [{ pedidos: [] }, "0"],
        [{ pedidos: [3, 2, 0] }, "2"],
        [{ pedidos: [2] }, "1"]
      ], ["pedidos"]);
    }
    if (number === 13) return callFlag(code, "estoque_baixo", [[4, 1], [5, 0], [0, 1], [9, 0], [-1, 1], [6, 0]]);
    if (number === 14) {
      if (!creates(tree, ["pagamento", "estoque", "quantidade"]) || !hasElse || !hasAnd) return false;
      return shows(code, [
        [{ pagamento: 1, estoque: 10, quantidade: 4 }, "Aprovado"],
        [{ pagamento: 1, estoque: 2, quantidade: 5 }, "Recusado"],
        [{ pagamento: 0, estoque: 10, quantidade: 1 }, "Recusado"],
        [{ pagamento: 1, estoque: 3, quantidade: 3 }, "Aprovado"],
        [{ pagamento: 0, estoque: 8, quantidade: 8 }, "Recusado"],
        [{ pagamento: 1, estoque: 0, quantidade: 0 }, "Aprovado"],
        [{ pagamento: 1, estoque: 1, quantidade: 2 }, "Recusado"]
      ], ["pagamento", "estoque", "quantidade"]);
    }
    if (number === 16) {
      if (!creates(tree, ["promocao", "estoque"]) || !hasElse || !hasOr) return false;
      return shows(code, [
        [{ promocao: 1, estoque: 5 }, "Promocao"],
        [{ promocao: 0, estoque: 21 }, "Promocao"],
        [{ promocao: 0, estoque: 20 }, "Normal"],
        [{ promocao: 0, estoque: 0 }, "Normal"],
        [{ promocao: 1, estoque: 30 }, "Promocao"],
        [{ promocao: 0, estoque: 19 }, "Normal"]
      ], ["promocao", "estoque"]);
    }
    if (number === 17) return callFlag(code, "preco_alto", [[50, 0], [51, 1], [0, 0], [100, 1], [49, 0]]);
    if (number === 18) {
      if (!creates(tree, ["pedidos"]) || !hasFor) return false;
      return shows(code, [
        [{ pedidos: [2, 5, 1, 4] }, "12"],
        [{ pedidos: [0, 0] }, "0"],
        [{ pedidos: [] }, "0"],
        [{ pedidos: [8] }, "8"],
        [{ pedidos: [-1, 3] }, "2"]
      ], ["pedidos"]);
    }
    if (number === 19) {
      if (!creates(tree, ["meta", "quantidade"]) || !hasWhile) return false;
      return [0, 1, 3, 5, 8].every((meta) => execute(code, { meta }, ["meta"]).env.quantidade === meta);
    }
    if (number === 20) {
      if (!creates(tree, ["pedidos"]) || !text.includes("pedido_grande") || !hasFor || !hasIf) return false;
      const lists = [[2, 5, 1, 4], [1, 0], [2], [], [2, 2, 2], [1, 2, 3]];
      for (const orders of lists) {
        const result = execute(code, { pedidos: orders.slice() }, ["pedidos"]);
        const expected = orders.filter((item) => item >= 2).length;
        if (result.env.grandes !== expected) return false;
      }
      return callFlag(code, "pedido_grande", [[2, 1], [1, 0], [0, 0], [5, 1], [-1, 0]]);
    }
    return false;
  }

  function grade(number, response) {
    const question = QUESTIONS[number];
    if (!question || !response) throw new Error("Resposta inválida.");
    if (question.type === "true_false") {
      const answers = response.answers;
      if (!answers) throw new Error("Responda todas as afirmações.");
      const detail = question.statements.map((item) => {
        if (typeof answers[item.id] !== "boolean") throw new Error("Classifique cada afirmação como verdadeira ou falsa.");
        return { id: item.id, is_right: answers[item.id] === question.key[item.id] };
      });
      const correct = detail.every((item) => item.is_right);
      return Object.assign(scorePayload(number, correct), { explanation: question.explanation, detail });
    }
    if (question.type === "multiple_choice") {
      if (!["A", "B", "C", "D"].includes(response.option)) throw new Error("Selecione uma alternativa.");
      const correct = response.option === question.key;
      return Object.assign(scorePayload(number, correct), { explanation: question.explanation });
    }
    if (typeof response.code !== "string" || !response.code.trim()) throw new Error("Escreva o código antes de confirmar.");
    let correct = false;
    try { correct = gradeCode(number, response.code); } catch (_error) { correct = false; }
    const explanation = correct ? question.explanationCorrect : question.explanationWrong;
    return Object.assign(scorePayload(number, correct), {
      explanation: correct ? explanation : `O código tem um erro de escrita ou ainda não segue o enunciado. ${explanation}`
    });
  }

  function scorePayload(number, correct) {
    const cents = correct ? pointsCents(number) : 0;
    return { correct, points: cents / 100, points_formatada: formatScore(cents) };
  }

  function publicQuestion(number) {
    const question = QUESTIONS[number];
    const payload = { number, total: TOTAL, valor: formatScore(pointsCents(number)), type: question.type, topic: question.topic, prompt: question.prompt };
    if (question.type === "true_false") payload.statements = question.statements;
    else if (question.type === "multiple_choice") {
      payload.code = question.code || "";
      payload.options = question.options;
    } else payload.starter = question.starter;
    return payload;
  }

  function nowBr() {
    const parts = new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit", hour12: false
    }).formatToParts(new Date());
    const pick = (type) => parts.find((part) => part.type === type).value;
    return `${pick("day")}/${pick("month")}/${pick("year")} ${pick("hour")}:${pick("minute")}`;
  }

  function readRecord() {
    let record = null;
    try { record = JSON.parse(sessionStorage.getItem(STORAGE) || "null"); } catch (_error) { record = null; }
    if (!record) return null;
    const answered = Object.keys(record.answers || {}).length;
    if (record.status === "concluida" && record.encerramento !== "seguranca" && answered < TOTAL) {
      sessionStorage.removeItem(STORAGE);
      return null;
    }
    return record;
  }
  function matches(session) {
    const record = readRecord();
    return Boolean(session && record && record.token === session.token && record.attemptId === session.attemptId);
  }
  function writeRecord(record) { sessionStorage.setItem(STORAGE, JSON.stringify(record)); }
  function progressOf(record) {
    const answered = record.acertos + record.erros;
    const cents = scoreCents(record);
    return {
      question: record.current,
      total: TOTAL,
      respondidas: answered,
      acertos: record.acertos,
      erros: record.erros,
      nota_cents: cents,
      pontuacao: cents / 100,
      pontuacao_formatada: formatScore(cents),
      progresso: Math.round(answered / TOTAL * 100),
      phase: record.phase
    };
  }
  function incentive(cents) {
    if (cents >= 630) return "Excelente trabalho! Você demonstrou segurança nos conteúdos desta avaliação.";
    if (cents >= 490) return "Muito bem! Você concluiu a avaliação com um bom desempenho.";
    if (cents >= 350) return "Avaliação concluída. Continue praticando para fortalecer o que você já aprendeu.";
    return "Avaliação concluída. Revise os conteúdos com calma e pratique mais um pouco. Você é capaz de avançar.";
  }
  function resultOf(record) {
    const cents = scoreCents(record);
    return {
      nome: record.nome,
      turma: record.turma,
      started_at: record.startedAt,
      finished_at: record.finishedAt,
      acertos: record.acertos,
      erros: record.erros,
      nota: cents / 100,
      nota_formatada: formatScore(cents),
      aproveitamento: Math.round(cents * 100 / MAX_CENTS),
      mensagem: record.encerramento === "seguranca"
        ? "A avaliação foi encerrada porque houve mais de 3 tentativas de copiar, colar ou capturar a tela."
        : incentive(cents),
      encerramento: record.encerramento === "seguranca"
        ? "Prova encerrada por tentativa de burlar a segurança"
        : "Concluída pelo aluno",
      registro: "A nota foi calculada neste navegador.",
      salvo: true,
      revisao: Object.keys(record.answers).map((number) => ({ number: Number(number), correct: record.answers[number].correct })).sort((a, b) => a.number - b.number)
    };
  }
  function stateOf(record) {
    const payload = {
      status: record.status,
      finished: record.status === "concluida",
      student: { nome: record.nome, turma: record.turma, started_at: record.startedAt },
      progress: progressOf(record)
    };
    if (record.status === "concluida") {
      payload.result = resultOf(record);
      return payload;
    }
    payload.question = publicQuestion(record.current);
    payload.feedback = null;
    if (record.phase === "feedback" && record.answers[record.current]) {
      const saved = record.answers[record.current];
      payload.feedback = {
        correct: saved.correct,
        points: saved.correct ? pointsCents(record.current) / 100 : 0,
        points_formatada: formatScore(saved.correct ? pointsCents(record.current) : 0),
        explanation: saved.explanation,
        detail: saved.detail || null,
        response: saved.response
      };
    }
    return payload;
  }
  function fail(message, status) {
    const error = new Error(message);
    error.status = status;
    throw error;
  }
  function current(session) {
    const record = readRecord();
    if (!record || !session || record.token !== session.token || record.attemptId !== session.attemptId) {
      fail("Não foi possível reconhecer esta tentativa.", 401);
    }
    return record;
  }

  async function publishResult(record) {
    if (record.published) return true;
    const url = window.JBS_CONFIG && window.JBS_CONFIG.resultsUrl;
    if (!url) return false;
    const payload = {
      attempt_id: record.attemptId,
      nome: record.nome,
      turma: record.turma,
      nota: scoreCents(record) / 100,
      nota_formatada: formatScore(scoreCents(record)),
      acertos: record.acertos,
      erros: record.erros,
      aproveitamento: Math.round(scoreCents(record) * 100 / MAX_CENTS),
      started_at: record.startedAt,
      finished_at: record.finishedAt,
      status: "Concluída",
      encerramento: record.encerramento === "seguranca"
        ? "Prova encerrada por tentativa de burlar a segurança"
        : "Concluída pelo aluno"
    };
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        });
        if (response.ok) {
          record.published = true;
          writeRecord(record);
          return true;
        }
      } catch (_error) {
        /* tenta de novo */
      }
    }
    return false;
  }

  async function handle(path, options, session) {
    const method = ((options && options.method) || "GET").toUpperCase();
    const body = (options && options.body) || {};
    if (path === "/api/start" && method === "POST") {
      const nome = String(body.nome || "").trim().replace(/\s+/g, " ");
      if (!/^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*(?: [A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*)+$/.test(nome)) fail("Informe o nome e o sobrenome, usando apenas letras.", 400);
      if (!["8A", "8B", "8C", "8D", "8E"].includes(body.turma)) fail("Selecione uma turma válida.", 400);
      const existing = readRecord();
      if (existing && existing.browserSession === body.browser_session) {
        if (existing.token !== body.token) fail("Esta sessão do navegador já possui uma avaliação. Continue na aba em que ela foi iniciada.", 409);
        return { attempt_id: existing.attemptId, resumed: true, finished: existing.status === "concluida", nome: existing.nome, turma: existing.turma, started_at: existing.startedAt };
      }
      const record = {
        attemptId: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
        token: body.token,
        browserSession: body.browser_session,
        nome, turma: body.turma, startedAt: nowBr(), finishedAt: "",
        current: 1, phase: "respondendo", acertos: 0, erros: 0, status: "em_andamento", answers: {}
      };
      writeRecord(record);
      return { attempt_id: record.attemptId, resumed: false, finished: false, nome: record.nome, turma: record.turma, started_at: record.startedAt };
    }
    const record = current(session);
    if (path.startsWith("/api/state")) return stateOf(record);
    if (path === "/api/answer") {
      if (record.status !== "em_andamento" || record.phase !== "respondendo" || body.question !== record.current) {
        fail("Esta questão não está aberta para resposta.", 409);
      }
      const graded = grade(body.question, body.response);
      record.answers[record.current] = {
        correct: graded.correct,
        explanation: graded.explanation,
        detail: graded.detail || null,
        response: body.response
      };
      record.acertos += graded.correct ? 1 : 0;
      record.erros += graded.correct ? 0 : 1;
      record.phase = "feedback";
      writeRecord(record);
      return {
        correct: graded.correct,
        points: graded.points,
        points_formatada: graded.points_formatada,
        explanation: graded.explanation,
        detail: graded.detail,
        locked: true,
        progress: progressOf(record)
      };
    }
    if (path === "/api/next") {
      if (record.phase !== "feedback") fail("Confirme a resposta antes de continuar.", 409);
      if (record.current >= TOTAL) return { ready_to_finish: true, progress: progressOf(record) };
      record.current += 1;
      record.phase = "respondendo";
      writeRecord(record);
      return { ready_to_finish: false, progress: progressOf(record), question: publicQuestion(record.current), feedback: null };
    }
    if (path === "/api/finish") {
      const security = body.encerramento === "seguranca";
      if (record.status !== "concluida") {
        if (!security && Object.keys(record.answers).length !== TOTAL) fail("Ainda existem questões sem confirmação.", 409);
        record.status = "concluida";
        record.encerramento = security ? "seguranca" : "normal";
        if (security) record.erros = TOTAL - record.acertos;
        record.finishedAt = nowBr();
        writeRecord(record);
      }
      const published = await publishResult(record);
      const result = resultOf(record);
      result.salvo = published;
      const aviso = record.encerramento === "seguranca"
        ? "O professor foi avisado na planilha: prova encerrada por tentativa de burlar a segurança. "
        : "";
      result.registro = published
        ? aviso + "Sua nota foi enviada para a lista do professor."
        : aviso + "A nota foi calculada neste navegador, mas a lista do professor não confirmou o recebimento. Use Tentar salvar novamente.";
      return { salvo: published, result };
    }
    fail("Não foi possível concluir a operação.", 404);
  }

  function formatValue(value) {
    if (Array.isArray(value)) return "[" + value.map(formatValue).join(", ") + "]";
    if (typeof value === "string") return '"' + value + '"';
    return String(value);
  }

  function previewError(error) {
    const message = String(error && error.message || "");
    if (message === "nome") return "Uma variável foi usada antes de ser criada.";
    if (message === "sintaxe" || message === "indent" || message === "bloco") return "Há um erro de escrita. Confira os dois-pontos e o espaço no começo da linha.";
    if (message === "limite" || message === "recursao") return "O programa repetiu demais. Confira o while ou o for.";
    if (message === "funcao") return "A função chamada ainda não foi criada.";
    if (message === "print") return "O print precisa de um valor entre parênteses.";
    if (message === "codigo") return "O programa está longo demais.";
    return "O programa parou por um erro. Leia o enunciado e teste de novo.";
  }

  function preview(code) {
    if (!String(code || "").trim()) return { ok: false, text: "Escreva o programa antes de testar." };
    try {
      const state = execute(code, {});
      const lines = printed(state.output);
      const vars = Object.keys(state.env)
        .filter((name) => typeof state.env[name] !== "function")
        .map((name) => name + " = " + formatValue(state.env[name]));
      const parts = [];
      parts.push(lines.length ? "O programa mostrou:\n" + lines.join("\n") : "O programa rodou e não mostrou nada na tela.");
      if (vars.length) parts.push("Variáveis no final:\n" + vars.join("\n"));
      return { ok: true, text: parts.join("\n\n") };
    } catch (error) {
      return { ok: false, text: previewError(error) };
    }
  }

  return { handle, grade, execute, matches, preview };
})();
