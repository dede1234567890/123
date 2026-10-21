"""Gabarito e enunciados da avaliação. Este arquivo fica apenas no servidor."""

from __future__ import annotations

TOTAL_QUESTIONS = 20
MAX_SCORE_CENTS = 700


def question_points_cents(number: int) -> int:
    if 1 <= number <= 8:
        return 20
    if 9 <= number <= TOTAL_QUESTIONS:
        return 45
    raise ValueError("Questão inválida.")


def format_score(cents: int) -> str:
    cents = int(cents)
    return f"{cents // 100},{cents % 100:02d}"

Q2_CODE = """estoque = 12
pedido = 15

if pedido < estoque:
    print("Pedido aprovado")
elif pedido == estoque:
    print("Estoque exato")
else:
    print("Estoque insuficiente")
"""

Q4_CODE = """quantidade = 0

if quantidade > 0
    print("Quantidade válida")
elif quantidade == 0:
    print("Informe uma quantidade")
else:
    print("Quantidade inválida")
"""

Q5_CODE = """produtos = ["hamburguer", "batata", "suco"]
produtos[1] = "refrigerante"
produtos.append("sobremesa")
print(produtos[0])
print(len(produtos))
"""

Q6_CODE = """pedidos = [2, 5, 1, 4]
total = 0
for quantidade in pedidos:
    if quantidade >= 2:
        total = total + 1
print(total)
"""

Q8_CODE = """def mensagem_boas_vindas():
    print("Bem-vindo a JBS FoodTech")
"""

Q9_STARTER = ""

Q10_STARTER = ""

QUESTIONS = {
    1: {
        "type": "true_false",
        "topic": "if, elif e else",
        "prompt": (
            "A JBS FoodTech está programando a verificação de um pedido. "
            "Classifique cada afirmação sobre if, elif e else. "
            "A questão vale 0,20 somente se todas estiverem corretas."
        ),
        "statements": [
            {
                "id": "1",
                "text": "O else é executado quando a condição do if é falsa e nenhum elif é verdadeiro.",
            },
            {
                "id": "2",
                "text": "É possível usar vários elif para tratar situações diferentes de um pedido.",
            },
            {
                "id": "3",
                "text": "O else precisa de uma condição, como em else quantidade == 0:",
            },
            {
                "id": "4",
                "text": "Quando a condição do if é verdadeira, o Python também executa os elif seguintes.",
            },
        ],
        "key": {"1": True, "2": True, "3": False, "4": False},
        "explanation": (
            "Em if/elif/else, apenas um caminho é executado. O else não recebe condição "
            "e só acontece quando o if e todos os elif são falsos. Vários elif podem aparecer "
            "em sequência. As afirmações 1 e 2 são verdadeiras. As afirmações 3 e 4 são falsas."
        ),
    },
    2: {
        "type": "multiple_choice",
        "topic": "Análise de código",
        "prompt": (
            "O programa abaixo confere se a quantidade pedida cabe no estoque da JBS FoodTech. "
            "Qual texto é exibido na tela?"
        ),
        "code": Q2_CODE,
        "options": [
            {"id": "A", "text": "Pedido aprovado"},
            {"id": "B", "text": "Estoque exato"},
            {"id": "C", "text": "Estoque insuficiente"},
            {"id": "D", "text": "O programa apresenta um erro e não exibe nada"},
        ],
        "key": "C",
        "explanation": (
            "O pedido é 15 e o estoque é 12. Como 15 não é menor que 12 e também não é igual, "
            "o programa segue para o else e exibe Estoque insuficiente."
        ),
    },
    3: {
        "type": "multiple_choice",
        "topic": "Operadores and e or",
        "prompt": (
            "A JBS FoodTech aprova um pedido somente quando o pagamento foi confirmado e, "
            "além disso, o estoque é suficiente ou o produto está em promoção. "
            "Qual condição representa essa regra?"
        ),
        "code": """pagamento_confirmado = 1
estoque_suficiente = 0
em_promocao = 1

if ________________:
    print("Pedido aprovado")
else:
    print("Pedido recusado")
""",
        "options": [
            {"id": "A", "text": "pagamento_confirmado and estoque_suficiente"},
            {
                "id": "B",
                "text": "pagamento_confirmado and (estoque_suficiente or em_promocao)",
            },
            {"id": "C", "text": "(not pagamento_confirmado) and em_promocao"},
            {"id": "D", "text": "estoque_suficiente and em_promocao"},
        ],
        "key": "B",
        "explanation": (
            "A regra junta duas exigências com and: o pagamento confirmado e, entre parênteses, "
            "estoque suficiente ou promoção. Com os valores do enunciado, somente "
            "pagamento_confirmado and (estoque_suficiente or em_promocao) é verdadeira."
        ),
    },
    4: {
        "type": "multiple_choice",
        "topic": "Correção de erros",
        "prompt": (
            "O programa abaixo deveria verificar a quantidade de um pedido, mas há um erro "
            "de escrita. Qual correção resolve o problema?"
        ),
        "code": Q4_CODE,
        "options": [
            {"id": "A", "text": "Trocar elif por else if"},
            {"id": "B", "text": "Colocar : no final da linha do if"},
            {"id": "C", "text": "Apagar todo o bloco else"},
            {"id": "D", "text": "Trocar == por = na comparação quantidade == 0"},
        ],
        "key": "B",
        "explanation": (
            "Faltaram os dois-pontos no final da linha do if. Em Python, if, elif e else "
            "terminam com :. As outras alternativas não corrigem esse erro de escrita."
        ),
    },
    5: {
        "type": "multiple_choice",
        "topic": "Listas",
        "prompt": "O programa organiza uma lista de produtos. O que ele exibe?",
        "code": Q5_CODE,
        "options": [
            {"id": "A", "text": "hamburguer e depois 3"},
            {"id": "B", "text": "refrigerante e depois 4"},
            {"id": "C", "text": "hamburguer e depois 4"},
            {"id": "D", "text": "suco e depois 3"},
        ],
        "key": "C",
        "explanation": (
            "O índice 0 continua sendo hamburguer, porque a troca foi feita no índice 1. "
            "O append acrescenta sobremesa, e a lista passa a ter 4 itens. "
            "O programa exibe hamburguer e depois 4."
        ),
    },
    6: {
        "type": "multiple_choice",
        "topic": "Laço for",
        "prompt": (
            "O programa percorre as quantidades dos pedidos e conta quantos têm 2 ou mais unidades. "
            "O que aparece na tela?"
        ),
        "code": Q6_CODE,
        "options": [
            {"id": "A", "text": "4"},
            {"id": "B", "text": "3"},
            {"id": "C", "text": "12"},
            {"id": "D", "text": "1"},
        ],
        "key": "B",
        "explanation": (
            "O for percorre os quatro números, mas o contador só aumenta quando a quantidade "
            "é maior ou igual a 2. Isso acontece com 2, 5 e 4. O valor 1 não entra. "
            "O programa exibe 3."
        ),
    },
    7: {
        "type": "multiple_choice",
        "topic": "Laço while",
        "prompt": (
            "O sistema deve pedir a quantidade enquanto ela for inválida. "
            "Quantidade válida é um número maior que zero. A variável começa valendo 0. "
            "Qual condição completa o while corretamente?"
        ),
        "code": """quantidade = 0
while ________________:
    quantidade = int(input("Digite a quantidade: "))
print("Quantidade aceita")
""",
        "options": [
            {"id": "A", "text": "quantidade > 0"},
            {"id": "B", "text": "quantidade <= 0"},
            {"id": "C", "text": "quantidade == 1"},
            {"id": "D", "text": "quantidade >= 0"},
        ],
        "key": "B",
        "explanation": (
            "O laço precisa continuar enquanto a quantidade for inválida, isto é, menor ou igual a zero. "
            "Quando um valor maior que zero é informado, quantidade <= 0 fica falsa e a repetição termina. "
            "A condição quantidade > 0 nem chega a entrar, pois o valor inicial é 0. "
            "A condição quantidade >= 0 continuaria verdadeira mesmo depois de um valor válido."
        ),
    },
    8: {
        "type": "multiple_choice",
        "topic": "Funções",
        "prompt": (
            "A função abaixo mostra a mensagem inicial do sistema e não recebe parâmetros. "
            "Qual alternativa chama a função corretamente e exibe a mensagem?"
        ),
        "code": Q8_CODE,
        "options": [
            {"id": "A", "text": "mensagem_boas_vindas"},
            {"id": "B", "text": "mensagem_boas_vindas()"},
            {"id": "C", "text": 'mensagem_boas_vindas("8A")'},
            {"id": "D", "text": "def mensagem_boas_vindas()"},
        ],
        "key": "B",
        "explanation": (
            "Para executar uma função sem parâmetros, escreva o nome seguido de parênteses vazios: "
            "mensagem_boas_vindas(). Sem os parênteses, a função não é chamada."
        ),
    },
    9: {
        "type": "code",
        "topic": "Construção de código",
        "prompt": (
            "Crie as variáveis pagamento, estoque e quantidade. "
            "pagamento vale 1 quando o pagamento foi confirmado e 0 quando não foi. "
            "Mostre Aprovado se pagamento for 1 e estoque for maior ou igual à quantidade. "
            "Nos outros casos, mostre Recusado. Use if, else e and. "
            "Teste com um exemplo antes de confirmar."
        ),
        "starter": Q9_STARTER,
        "explanation_correct": (
            "Sua solução aprova o pedido somente quando o pagamento está confirmado e o estoque "
            "cobre a quantidade pedida. O else trata os outros casos."
        ),
        "explanation_wrong": (
            "O pedido só pode ser aprovado quando o pagamento está confirmado e o estoque é maior "
            "ou igual à quantidade. Use if, else e and, e exiba exatamente Aprovado ou Recusado. "
            "Confira também os dois-pontos e a indentação."
        ),
    },
    10: {
        "type": "code",
        "topic": "Desafio integrador",
        "prompt": (
            "Crie a lista pedidos. Exemplo: [3, 0, 5, 2]. "
            "Crie a função pedido_valido: ela recebe quantidade e retorna 1 se for maior que 0, senão retorna 0. "
            "Crie a variável aprovados e use for para contar os pedidos válidos. "
            "No exemplo, aprovados fica 3. Teste antes de confirmar."
        ),
        "starter": Q10_STARTER,
        "explanation_correct": (
            "A função identifica quantidades maiores que zero, e o for usa essa função "
            "para contar os pedidos válidos da lista."
        ),
        "explanation_wrong": (
            "A função pedido_valido precisa retornar 1 somente quando a quantidade é maior que zero, e 0 nos outros casos. "
            "O for deve percorrer pedidos, chamar essa função e somar 1 em aprovados a cada pedido válido. "
            "Confira a indentação e os dois-pontos."
        ),
    },
    11: {
        "type": "code",
        "topic": "Correção de código",
        "prompt": (
            "O programa cria estoque e quantidade, mas só aprova quando o estoque é maior. "
            "Ele também deve aprovar quando os dois valores são iguais. "
            "Corrija a comparação. Mostre Aprovado ou Recusado. Teste antes de confirmar."
        ),
        "starter": """estoque = 3
quantidade = 3
if estoque > quantidade:
    print("Aprovado")
else:
    print("Recusado")
""",
        "explanation_correct": (
            "A comparação correta é estoque >= quantidade. Quando os dois valores são iguais, "
            "o estoque ainda cobre o pedido e o programa exibe Aprovado."
        ),
        "explanation_wrong": (
            "Troque a comparação para estoque >= quantidade. Com o sinal >, um estoque igual "
            "à quantidade fica Recusado, e isso não atende à regra."
        ),
    },
    12: {
        "type": "code",
        "topic": "Correção de código",
        "prompt": (
            "O programa cria a lista pedidos e conta só os pedidos com mais de 2 unidades. "
            "Ele deveria contar também o pedido com 2. Corrija a condição. "
            "No exemplo, o programa deve mostrar 3. Teste antes de confirmar."
        ),
        "starter": """pedidos = [2, 5, 1, 4]
total = 0
for quantidade in pedidos:
    if quantidade > 2:
        total = total + 1
print(total)
""",
        "explanation_correct": (
            "A condição quantidade >= 2 inclui o próprio 2. O for percorre a lista e o print mostra a contagem."
        ),
        "explanation_wrong": (
            "A condição precisa ser quantidade >= 2. Com quantidade > 2, um pedido de exatamente 2 unidades não entra na conta."
        ),
    },
    13: {
        "type": "code",
        "topic": "Correção de código",
        "prompt": (
            "Corrija a função estoque_baixo. "
            "Ela recebe quantidade e deve retornar 1 quando a quantidade for menor que 5. "
            "Nos outros casos, retorne 0. "
            "Para testar, escreva print(estoque_baixo(4)) embaixo da função."
        ),
        "starter": """def estoque_baixo(quantidade):
    if quantidade > 5:
        return 1
    else:
        return 0
""",
        "explanation_correct": (
            "A função retorna 1 somente quando a quantidade é menor que 5. O 5 e os valores maiores retornam 0."
        ),
        "explanation_wrong": (
            "Troque a comparação para quantidade < 5. Do jeito atual, quantidades pequenas retornam 0."
        ),
    },
    14: {
        "type": "code",
        "topic": "Correção de código",
        "prompt": (
            "O programa cria pagamento, estoque e quantidade, mas usa or. "
            "As duas partes precisam ser verdadeiras: pagamento igual a 1 e estoque maior ou igual à quantidade. "
            "Troque or por and. Mostre Aprovado ou Recusado. Teste antes de confirmar."
        ),
        "starter": """pagamento = 1
estoque = 2
quantidade = 5
if pagamento == 1 or estoque >= quantidade:
    print("Aprovado")
else:
    print("Recusado")
""",
        "explanation_correct": (
            "As duas partes precisam ser verdadeiras ao mesmo tempo: pagamento == 1 e estoque >= quantidade."
        ),
        "explanation_wrong": (
            "Com or, basta uma das partes para aprovar. Use and para exigir o pagamento confirmado e o estoque suficiente."
        ),
    },
    15: {
        "type": "code",
        "topic": "Correção de código",
        "prompt": (
            "O programa cria a lista pedidos. A função pedido_valido está certa. "
            "O for conta os pedidos inválidos, porque compara com 0. "
            "Corrija para contar os válidos. No exemplo, aprovados fica 3. Teste antes de confirmar."
        ),
        "starter": """pedidos = [3, 0, 5, 2]
def pedido_valido(quantidade):
    if quantidade > 0:
        return 1
    else:
        return 0

aprovados = 0
for quantidade in pedidos:
    if pedido_valido(quantidade) == 0:
        aprovados = aprovados + 1
""",
        "explanation_correct": (
            "A comparação == 1 seleciona os pedidos válidos. O for soma 1 em aprovados a cada chamada que retorna 1."
        ),
        "explanation_wrong": (
            "pedido_valido(quantidade) == 0 conta justamente os pedidos que não valem. Troque por == 1."
        ),
    },
    16: {
        "type": "code",
        "topic": "Construção de código",
        "prompt": (
            "Crie as variáveis promocao e estoque. "
            "promocao vale 1 quando o produto está em promoção e 0 quando não está. "
            "Mostre Promocao se promocao for 1 ou o estoque for maior que 20. "
            "Nos outros casos, mostre Normal. Use if, else e or. Teste antes de confirmar."
        ),
        "starter": "",
        "explanation_correct": (
            "A condição com or aceita promoção ou estoque acima de 20. O else exibe Normal nos demais casos."
        ),
        "explanation_wrong": (
            "Use if, else e or. A mensagem Promocao aparece se promocao == 1 ou estoque > 20. "
            "Estoque igual a 20, sem promoção, deve exibir Normal."
        ),
    },
    17: {
        "type": "code",
        "topic": "Construção de código",
        "prompt": (
            "Crie a função preco_alto. Ela recebe valor. "
            "Retorne 1 se o valor for maior que 50. Senão, retorne 0. "
            "Para testar, escreva print(preco_alto(60)) embaixo da função."
        ),
        "starter": "",
        "explanation_correct": (
            "A função retorna 1 apenas quando valor > 50. O valor 50 e os menores retornam 0."
        ),
        "explanation_wrong": (
            "Complete o if valor > 50 para retornar 1, e o else para retornar 0. "
            "Um return 0 fixo não distingue os preços."
        ),
    },
    18: {
        "type": "code",
        "topic": "Construção de código",
        "prompt": (
            "Crie a lista pedidos. Exemplo: [2, 5, 1, 4]. "
            "Crie a variável soma e use for para somar todas as quantidades. "
            "Mostre a soma. No exemplo, o programa mostra 12. Teste antes de confirmar."
        ),
        "starter": "",
        "explanation_correct": (
            "O for percorre pedidos e acumula cada quantidade em soma. O print mostra o total."
        ),
        "explanation_wrong": (
            "Comece soma em 0, percorra pedidos com for e some cada quantidade. "
            "Depois exiba soma. Uma lista vazia precisa continuar valendo 0."
        ),
    },
    19: {
        "type": "code",
        "topic": "Construção de código",
        "prompt": (
            "Crie a variável meta. Exemplo: meta = 3. "
            "Crie quantidade com valor 0. Enquanto quantidade for menor que meta, some 1. Use while. "
            "No final, quantidade fica igual a meta. Teste antes de confirmar."
        ),
        "starter": "",
        "explanation_correct": (
            "O while quantidade < meta soma 1 a cada volta e para quando quantidade alcança meta."
        ),
        "explanation_wrong": (
            "Escreva while quantidade < meta e, dentro dele, quantidade = quantidade + 1. "
            "A condição <= faria o laço passar de meta ou não terminar."
        ),
    },
    20: {
        "type": "code",
        "topic": "Desafio integrador",
        "prompt": (
            "Crie a lista pedidos. Exemplo: [2, 5, 1, 4]. "
            "Crie a função pedido_grande: ela recebe quantidade e retorna 1 se for maior ou igual a 2, senão retorna 0. "
            "Crie a variável grandes e use for para contar os pedidos grandes. "
            "No exemplo, grandes fica 3. Teste antes de confirmar."
        ),
        "starter": "",
        "explanation_correct": (
            "A função reconhece quantidades a partir de 2, e o for usa esse retorno para contar grandes."
        ),
        "explanation_wrong": (
            "pedido_grande precisa retornar 1 quando quantidade >= 2, e 0 nos outros casos. "
            "O for deve chamar a função e somar 1 em grandes apenas quando o retorno for 1."
        ),
    },
}


def public_question(number: int) -> dict:
    question = QUESTIONS[number]
    payload = {
        "number": number,
        "total": TOTAL_QUESTIONS,
        "valor": format_score(question_points_cents(number)),
        "type": question["type"],
        "topic": question["topic"],
        "prompt": question["prompt"],
    }
    if question["type"] == "true_false":
        payload["statements"] = question["statements"]
    elif question["type"] == "multiple_choice":
        payload["code"] = question.get("code", "")
        payload["options"] = question["options"]
    else:
        payload["starter"] = question["starter"]
    return payload


def explanation_for(number: int, correct: bool) -> str:
    question = QUESTIONS[number]
    if question["type"] == "code":
        if correct:
            return question["explanation_correct"]
        return question["explanation_wrong"]
    return question["explanation"]
