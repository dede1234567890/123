"""Correção das 20 questões. A nota é decidida somente neste módulo."""

from __future__ import annotations

import ast

from questions_bank import QUESTIONS, explanation_for, format_score, question_points_cents
from safe_python import (
    SafeError,
    execute,
    has_and,
    has_bool_operator,
    has_call,
    has_for,
    has_function,
    has_if,
    has_if_else,
    has_or,
    has_while,
    parse_tree,
)

Q9_CASES = [
    ({"pagamento": 1, "estoque": 10, "quantidade": 4}, "Aprovado"),
    ({"pagamento": 1, "estoque": 2, "quantidade": 5}, "Recusado"),
    ({"pagamento": 0, "estoque": 10, "quantidade": 1}, "Recusado"),
    ({"pagamento": 1, "estoque": 3, "quantidade": 3}, "Aprovado"),
    ({"pagamento": 0, "estoque": 8, "quantidade": 8}, "Recusado"),
    ({"pagamento": 1, "estoque": 0, "quantidade": 0}, "Aprovado"),
    ({"pagamento": 1, "estoque": 1, "quantidade": 2}, "Recusado"),
]

Q10_CASES = [
    [3, 0, 5, 2],
    [0, 0, 0],
    [1],
    [4, 2],
    [],
    [-1, 0, 7],
    [8],
]

Q10_FUNCTION_CASES = [
    (3, 1),
    (1, 1),
    (0, 0),
    (-3, 0),
    (12, 1),
]


def _printed_lines(output: list) -> list[str]:
    lines = []
    for item in output:
        text = str(item).strip()
        if text:
            lines.append(text)
    return lines


def _grade_true_false(response: dict) -> tuple[bool, list]:
    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("Resposta incompleta.")
    key = QUESTIONS[1]["key"]
    if set(answers) != set(key):
        raise ValueError("Responda todas as afirmações.")
    detail = []
    all_right = True
    for statement_id, expected in key.items():
        chosen = answers[statement_id]
        if not isinstance(chosen, bool):
            raise ValueError("Classifique cada afirmação como verdadeira ou falsa.")
        is_right = chosen is expected
        all_right = all_right and is_right
        detail.append({"id": statement_id, "is_right": is_right})
    return all_right, detail


def _grade_choice(number: int, response: dict) -> bool:
    option = response.get("option")
    if option not in {"A", "B", "C", "D"}:
        raise ValueError("Selecione uma alternativa.")
    return option == QUESTIONS[number]["key"]


def _without_inputs(code: str, names: set[str]) -> str:
    if not names:
        return code
    tree = ast.parse(code)
    kept = []
    for stmt in tree.body:
        if (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id in names
        ):
            continue
        kept.append(stmt)
    tree.body = kept
    return ast.unparse(tree)


def _creates(code: str, names: set[str]) -> bool:
    if not names:
        return True
    tree = ast.parse(code)
    found = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            found.add(stmt.targets[0].id)
    return names <= found


def _code_text(response: dict) -> str:
    code = response.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Escreva o código antes de confirmar.")
    if len(code) > 2000:
        raise ValueError("O código está longo demais.")
    return code


def _grade_q9(code: str) -> bool:
    tree = parse_tree(code)
    names = {"pagamento", "estoque", "quantidade"}
    if not _creates(code, names) or not has_if_else(tree) or not has_bool_operator(tree):
        return False
    prepared = _without_inputs(code, names)
    for env, expected in Q9_CASES:
        result = execute(prepared, env)
        if _printed_lines(result.output) != [expected]:
            return False
    return True


def _count_valid(orders: list) -> int:
    return sum(1 for quantity in orders if isinstance(quantity, int) and quantity > 0)


def _same_flag(value, expected: int) -> bool:
    if expected == 1:
        return value == 1 or value is True
    return value == 0 or value is False


def _grade_q10(code: str) -> bool:
    tree = parse_tree(code)
    if not _creates(code, {"pedidos"}):
        return False
    if not has_function(tree, "pedido_valido") or not has_for(tree) or not has_call(tree, "pedido_valido"):
        return False
    if not any(isinstance(node, ast.If) for node in ast.walk(tree)):
        return False
    prepared = _without_inputs(code, {"pedidos"})
    sample = None
    for orders in Q10_CASES:
        result = execute(prepared, {"pedidos": list(orders)})
        if result.env.get("aprovados") != _count_valid(orders):
            return False
        sample = result
    function = sample.functions.get("pedido_valido") if sample else None
    if function is None:
        return False
    for quantity, expected in Q10_FUNCTION_CASES:
        value = sample.call_function(function, [quantity])
        if not _same_flag(value, expected):
            return False
    return True


def _print_matches(code: str, cases: list, names: set[str] | None = None) -> bool:
    prepared = _without_inputs(code, names or set())
    for env, expected in cases:
        if _printed_lines(execute(prepared, env).output) != [str(expected)]:
            return False
    return True


def _grade_q11(code: str) -> bool:
    tree = parse_tree(code)
    names = {"estoque", "quantidade"}
    if not _creates(code, names) or not has_if_else(tree):
        return False
    return _print_matches(code, [
        ({"estoque": 10, "quantidade": 4}, "Aprovado"),
        ({"estoque": 3, "quantidade": 3}, "Aprovado"),
        ({"estoque": 2, "quantidade": 5}, "Recusado"),
        ({"estoque": 0, "quantidade": 0}, "Aprovado"),
        ({"estoque": 1, "quantidade": 2}, "Recusado"),
    ], names)


def _grade_q12(code: str) -> bool:
    tree = parse_tree(code)
    if not _creates(code, {"pedidos"}) or not has_for(tree) or not has_if(tree):
        return False
    return _print_matches(code, [
        ({"pedidos": [2, 5, 1, 4]}, "3"),
        ({"pedidos": [2, 2]}, "2"),
        ({"pedidos": [1]}, "0"),
        ({"pedidos": []}, "0"),
        ({"pedidos": [3, 2, 0]}, "2"),
        ({"pedidos": [2]}, "1"),
    ], {"pedidos"})


def _call_flag(code: str, name: str, cases: list) -> bool:
    tree = parse_tree(code)
    if not has_function(tree, name) or not has_if(tree):
        return False
    result = execute(code, {})
    function = result.functions.get(name)
    if function is None:
        return False
    for value, expected in cases:
        if not _same_flag(result.call_function(function, [value]), expected):
            return False
    return True


def _grade_q13(code: str) -> bool:
    return _call_flag(code, "estoque_baixo", [(4, 1), (5, 0), (0, 1), (9, 0), (-1, 1), (6, 0)])


def _grade_q14(code: str) -> bool:
    tree = parse_tree(code)
    names = {"pagamento", "estoque", "quantidade"}
    if not _creates(code, names) or not has_if_else(tree) or not has_and(tree):
        return False
    return _print_matches(code, Q9_CASES, names)


def _grade_counter(code: str, name: str, target: str, lists: list, minimum):
    tree = parse_tree(code)
    if not _creates(code, {"pedidos"}):
        return None
    if not has_function(tree, name) or not has_for(tree) or not has_call(tree, name) or not has_if(tree):
        return None
    prepared = _without_inputs(code, {"pedidos"})
    sample = None
    for orders in lists:
        result = execute(prepared, {"pedidos": list(orders)})
        if result.env.get(target) != minimum(orders):
            return None
        sample = result
    if sample is None or name not in sample.functions:
        return None
    return sample


def _flags_match(sample, name: str, cases: list) -> bool:
    function = sample.functions[name]
    for value, expected in cases:
        if not _same_flag(sample.call_function(function, [value]), expected):
            return False
    return True


def _grade_q15(code: str) -> bool:
    sample = _grade_counter(code, "pedido_valido", "aprovados", Q10_CASES, _count_valid)
    return sample is not None and _flags_match(sample, "pedido_valido", Q10_FUNCTION_CASES)


def _grade_q16(code: str) -> bool:
    tree = parse_tree(code)
    names = {"promocao", "estoque"}
    if not _creates(code, names) or not has_if_else(tree) or not has_or(tree):
        return False
    return _print_matches(code, [
        ({"promocao": 1, "estoque": 5}, "Promocao"),
        ({"promocao": 0, "estoque": 21}, "Promocao"),
        ({"promocao": 0, "estoque": 20}, "Normal"),
        ({"promocao": 0, "estoque": 0}, "Normal"),
        ({"promocao": 1, "estoque": 30}, "Promocao"),
        ({"promocao": 0, "estoque": 19}, "Normal"),
    ], names)


def _grade_q17(code: str) -> bool:
    return _call_flag(code, "preco_alto", [(50, 0), (51, 1), (0, 0), (100, 1), (49, 0)])


def _grade_q18(code: str) -> bool:
    tree = parse_tree(code)
    if not _creates(code, {"pedidos"}) or not has_for(tree):
        return False
    return _print_matches(code, [
        ({"pedidos": [2, 5, 1, 4]}, "12"),
        ({"pedidos": [0, 0]}, "0"),
        ({"pedidos": []}, "0"),
        ({"pedidos": [8]}, "8"),
        ({"pedidos": [-1, 3]}, "2"),
    ], {"pedidos"})


def _grade_q19(code: str) -> bool:
    tree = parse_tree(code)
    if not _creates(code, {"meta", "quantidade"}) or not has_while(tree):
        return False
    prepared = _without_inputs(code, {"meta"})
    for meta in (0, 1, 3, 5, 8):
        result = execute(prepared, {"meta": meta})
        if result.env.get("quantidade") != meta:
            return False
    return True


def _grade_q20(code: str) -> bool:
    lists = [[2, 5, 1, 4], [1, 0], [2], [], [2, 2, 2], [1, 2, 3]]
    sample = _grade_counter(
        code, "pedido_grande", "grandes", lists, lambda orders: sum(1 for item in orders if item >= 2)
    )
    return sample is not None and _flags_match(sample, "pedido_grande", [(2, 1), (1, 0), (0, 0), (5, 1), (-1, 0)])


CODE_GRADERS = {
    9: _grade_q9,
    10: _grade_q10,
    11: _grade_q11,
    12: _grade_q12,
    13: _grade_q13,
    14: _grade_q14,
    15: _grade_q15,
    16: _grade_q16,
    17: _grade_q17,
    18: _grade_q18,
    19: _grade_q19,
    20: _grade_q20,
}


def grade(number: int, response: dict) -> dict:
    if number not in QUESTIONS or not isinstance(response, dict):
        raise ValueError("Questão inválida.")
    question = QUESTIONS[number]
    detail = None
    syntax_problem = False
    if question["type"] == "true_false":
        correct, detail = _grade_true_false(response)
    elif question["type"] == "multiple_choice":
        correct = _grade_choice(number, response)
    elif question["type"] == "code":
        code = _code_text(response)
        try:
            correct = CODE_GRADERS[number](code)
        except SafeError:
            correct = False
            syntax_problem = True
        except SyntaxError:
            correct = False
            syntax_problem = True
    else:
        raise ValueError("Questão inválida.")

    explanation = explanation_for(number, correct)
    if syntax_problem and not correct:
        explanation = "O código tem um erro de escrita ou usa um recurso fora do enunciado. " + explanation
    earned = question_points_cents(number) if correct else 0
    result = {
        "correct": correct,
        "points": round(earned / 100, 2),
        "points_formatada": format_score(earned),
        "explanation": explanation,
    }
    if detail is not None:
        result["detail"] = detail
    return result
