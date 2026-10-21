import ast
import io
import json
import re
import time
from contextlib import redirect_stdout

import pytest

from grader import grade
from questions_bank import Q2_CODE, Q4_CODE, Q5_CODE, Q6_CODE, Q8_CODE, QUESTIONS, TOTAL_QUESTIONS, public_question
from safe_python import SafeError, execute

Q9_SOLUTION = """
pagamento = 1
estoque = 10
quantidade = 4
if pagamento and estoque >= quantidade:
    print("Aprovado")
else:
    print("Recusado")
"""

Q9_VARIANT = """
pagamento = 1
estoque = 10
quantidade = 4
if quantidade <= estoque and pagamento == 1:
    print("Aprovado")
else:
    print("Recusado")
"""

Q10_SOLUTION = """
pedidos = [3, 0, 5, 2]
def pedido_valido(quantidade):
    if quantidade > 0:
        return 1
    else:
        return 0

aprovados = 0
for quantidade in pedidos:
    if pedido_valido(quantidade):
        aprovados = aprovados + 1
"""

Q10_VARIANT = """
pedidos = [3, 0, 5, 2]
def pedido_valido(quantidade):
    if quantidade > 0:
        return quantidade > 0
    else:
        return 0

aprovados = 0
for item in pedidos:
    if pedido_valido(item):
        aprovados += 1
"""


def test_student_questions_do_not_use_pass_or_boolean_words():
    pattern = re.compile(r"\b(True|False|pass)\b")
    for number in range(1, TOTAL_QUESTIONS + 1):
        text = json.dumps(public_question(number), ensure_ascii=False)
        assert pattern.search(text) is None, number


def test_public_questions_do_not_expose_the_key():
    assert len(QUESTIONS) == TOTAL_QUESTIONS
    for number in range(1, TOTAL_QUESTIONS + 1):
        payload = public_question(number)
        assert payload["number"] == number
        assert "key" not in payload
        assert "explanation" not in payload
        assert "explanation_correct" not in payload


def test_closed_questions_match_traced_behavior():
    assert execute(Q2_CODE).output == ["Estoque insuficiente"]
    assert QUESTIONS[2]["key"] == "C"
    assert execute(Q6_CODE).output == [3]
    assert QUESTIONS[6]["key"] == "B"
    welcome = execute(Q8_CODE + "\nmensagem_boas_vindas()\n")
    assert welcome.output == ["Bem-vindo a JBS FoodTech"]
    assert QUESTIONS[8]["key"] == "B"
    with pytest.raises(SafeError):
        execute(Q8_CODE + "\nmensagem_boas_vindas\n")

    base = (
        "pagamento_confirmado = 1\n"
        "estoque_suficiente = 0\n"
        "em_promocao = 1\n"
    )
    options = {
        "A": "pagamento_confirmado and estoque_suficiente",
        "B": "pagamento_confirmado and (estoque_suficiente or em_promocao)",
        "C": "(not pagamento_confirmado) and em_promocao",
        "D": "estoque_suficiente and em_promocao",
    }
    truths = {letter: execute(base + f"print({expr})\n").output[0] for letter, expr in options.items()}
    assert truths == {"A": 0, "B": 1, "C": False, "D": 0}
    assert QUESTIONS[3]["key"] == "B"

    invalid_start = execute("quantidade = 0\nprint(quantidade <= 0)\nquantidade = 4\nprint(quantidade <= 0)\n")
    assert invalid_start.output == [True, False]
    still_true = execute("quantidade = 4\nprint(quantidade >= 0)\n")
    assert still_true.output == [True]
    assert QUESTIONS[7]["key"] == "B"

    with pytest.raises(SyntaxError):
        ast.parse(Q4_CODE)
    assert QUESTIONS[4]["key"] == "B"


def test_question_five_output_matches_key():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exec(Q5_CODE, {"__builtins__": {"len": len, "print": print}}, {})
    assert buffer.getvalue().splitlines() == ["hamburguer", "4"]
    assert QUESTIONS[5]["key"] == "C"


def test_true_false_requires_every_statement():
    perfect = {"answers": {"1": True, "2": True, "3": False, "4": False}}
    almost = {"answers": {"1": True, "2": True, "3": True, "4": False}}
    assert grade(1, perfect)["points"] == 0.2
    assert grade(1, perfect)["points_formatada"] == "0,20"
    assert grade(1, almost)["points"] == 0
    assert grade(1, almost)["detail"][2]["is_right"] is False


def test_multiple_choice_keys():
    expected = {2: "C", 3: "B", 4: "B", 5: "C", 6: "B", 7: "B", 8: "B"}
    for number, option in expected.items():
        assert grade(number, {"option": option})["points"] == 0.2
        wrong = "A" if option != "A" else "B"
        assert grade(number, {"option": wrong})["points"] == 0


def test_open_questions_accept_equivalent_code():
    assert grade(9, {"code": Q9_SOLUTION})["correct"] is True
    assert grade(9, {"code": Q9_VARIANT})["correct"] is True
    assert grade(10, {"code": Q10_SOLUTION})["correct"] is True
    assert grade(10, {"code": Q10_VARIANT})["correct"] is True
    hardcoded = """
if True:
    print("Aprovado")
else:
    print("Recusado")
"""
    assert grade(9, {"code": hardcoded})["correct"] is False
    assert grade(9, {"code": "print('Aprovado')"})["correct"] is False


Q11 = """
estoque = 3
quantidade = 3
if estoque >= quantidade:
    print("Aprovado")
else:
    print("Recusado")
"""

Q12 = """
pedidos = [2, 5, 1, 4]
total = 0
for quantidade in pedidos:
    if quantidade >= 2:
        total = total + 1
print(total)
"""

Q13 = """
def estoque_baixo(quantidade):
    if quantidade < 5:
        return 1
    else:
        return 0
"""

Q14 = """
pagamento = 1
estoque = 10
quantidade = 4
if pagamento == 1 and estoque >= quantidade:
    print("Aprovado")
else:
    print("Recusado")
"""

Q15 = """
pedidos = [3, 0, 5, 2]
def pedido_valido(quantidade):
    if quantidade > 0:
        return 1
    else:
        return 0

aprovados = 0
for quantidade in pedidos:
    if pedido_valido(quantidade) == 1:
        aprovados = aprovados + 1
"""

Q16 = """
promocao = 1
estoque = 5
if promocao == 1 or estoque > 20:
    print("Promocao")
else:
    print("Normal")
"""

Q17 = """
def preco_alto(valor):
    if valor > 50:
        return 1
    else:
        return 0
"""

Q18 = """
pedidos = [2, 5, 1, 4]
soma = 0
for quantidade in pedidos:
    soma = soma + quantidade
print(soma)
"""

Q19 = """
meta = 3
quantidade = 0
while quantidade < meta:
    quantidade = quantidade + 1
"""

Q20 = """
pedidos = [2, 5, 1, 4]
def pedido_grande(quantidade):
    if quantidade >= 2:
        return 1
    else:
        return 0

grandes = 0
for quantidade in pedidos:
    if pedido_grande(quantidade) == 1:
        grandes = grandes + 1
"""


def test_extra_code_questions_grade_behavior():
    solutions = {
        11: Q11, 12: Q12, 13: Q13, 14: Q14, 15: Q15,
        16: Q16, 17: Q17, 18: Q18, 19: Q19, 20: Q20,
    }
    for number, code in solutions.items():
        assert grade(number, {"code": code})["correct"] is True
        starter = QUESTIONS[number]["starter"]
        if starter.strip():
            assert grade(number, {"code": starter})["correct"] is False
        else:
            with pytest.raises(ValueError):
                grade(number, {"code": starter})
        assert QUESTIONS[number]["type"] == "code"


def test_malicious_code_is_not_executed():
    blocked = [
        "import os\n",
        "open('segredo.txt')\n",
        "__import__('os')\n",
        "while True:\n    pass\n",
        "def pedido_valido(quantidade):\n    return pedido_valido(quantidade)\n",
    ]
    for code in blocked:
        result = grade(9, {"code": code})
        assert result["correct"] is False
        assert result["points"] == 0
    started = time.perf_counter()
    with pytest.raises(SafeError):
        execute("while True:\n    pass\n")
    with pytest.raises(SafeError):
        execute("def pedido_valido(quantidade):\n    return pedido_valido(quantidade)\npedido_valido(1)\n")
    assert time.perf_counter() - started < 2
