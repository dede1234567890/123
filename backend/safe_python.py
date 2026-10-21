"""Interpretador restrito para corrigir código de uma prova de 8º ano.

Este módulo não usa exec, eval nem compile para rodar o código do aluno.
Ele apenas lê a estrutura do programa (AST) e interpreta um subconjunto
pequeno de Python: variáveis, if/else, for, while com limite, funções
simples, listas e print.
"""

from __future__ import annotations

import ast

MAX_CODE_CHARS = 2000
MAX_NODES = 150
MAX_STEPS = 4000
MAX_LOOP = 300
MAX_DEPTH = 12


class SafeError(Exception):
    """O código não pode ser avaliado dentro das regras da prova."""


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


ALLOWED_NODES = {
    ast.Module,
    ast.Expr,
    ast.Pass,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.If,
    ast.For,
    ast.While,
    ast.Assign,
    ast.AugAssign,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Compare,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Add,
    ast.Sub,
    ast.USub,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Call,
    ast.List,
    ast.Break,
    ast.Continue,
}

RESERVED_TARGETS = {"print", "len", "True", "False", "None"}


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _truthy(value) -> bool:
    if value is None or value is False:
        return False
    if value is True:
        return True
    if _is_int(value):
        return value != 0
    if isinstance(value, str):
        return value != ""
    if isinstance(value, list):
        return len(value) != 0
    raise SafeError("Valor não permitido na condição.")


def validate(tree: ast.AST) -> None:
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_NODES:
        raise SafeError("O código está longo demais para esta questão.")
    for node in nodes:
        if type(node) not in ALLOWED_NODES:
            raise SafeError("O código usa um recurso que não faz parte desta avaliação.")
        if isinstance(node, ast.FunctionDef):
            args = node.args
            if (
                node.decorator_list
                or args.vararg
                or args.kwarg
                or args.defaults
                or args.kwonlyargs
                or args.posonlyargs
                or any(item is not None for item in args.kw_defaults)
            ):
                raise SafeError("Use apenas funções simples, sem parâmetros extras.")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise SafeError("Essa chamada de função não é permitida nesta questão.")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (bool, int, str)):
            raise SafeError("Use apenas números, textos e os valores True ou False.")
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 120:
            raise SafeError("O texto escrito no código está longo demais.")
        if isinstance(node, ast.Name) and node.id.startswith("_"):
            raise SafeError("Esse nome de variável não é permitido.")
        if isinstance(node, (ast.For, ast.While)) and node.orelse:
            raise SafeError("Não use else junto com for ou while nesta questão.")


class Interpreter:
    def __init__(self, env: dict):
        self.env = dict(env)
        self.local = None
        self.functions: dict[str, ast.FunctionDef] = {}
        self.output: list = []
        self.steps = 0
        self.depth = 0

    def step(self) -> None:
        self.steps += 1
        if self.steps > MAX_STEPS:
            raise SafeError("O código passou do limite de execução.")

    def run(self, tree: ast.Module) -> None:
        for stmt in tree.body:
            self.exec_stmt(stmt)

    def lookup(self, name: str):
        if self.local is not None and name in self.local:
            return self.local[name]
        if name in self.env:
            return self.env[name]
        raise SafeError("Há um nome que ainda não foi definido.")

    def assign(self, name: str, value) -> None:
        if name in RESERVED_TARGETS:
            raise SafeError("Esse nome não pode ser alterado.")
        if self.local is not None:
            self.local[name] = value
        else:
            self.env[name] = value

    def exec_stmt(self, stmt: ast.AST) -> None:
        self.step()
        if isinstance(stmt, ast.FunctionDef):
            self.functions[stmt.name] = stmt
        elif isinstance(stmt, ast.If):
            if _truthy(self.eval_expr(stmt.test)):
                for item in stmt.body:
                    self.exec_stmt(item)
            else:
                for item in stmt.orelse:
                    self.exec_stmt(item)
        elif isinstance(stmt, ast.Assign):
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise SafeError("Use uma variável por vez.")
            self.assign(stmt.targets[0].id, self.eval_expr(stmt.value))
        elif isinstance(stmt, ast.AugAssign):
            if not isinstance(stmt.target, ast.Name) or not isinstance(stmt.op, (ast.Add, ast.Sub)):
                raise SafeError("Essa conta não é permitida nesta questão.")
            current = self.lookup(stmt.target.id)
            other = self.eval_expr(stmt.value)
            if not _is_int(current) or not _is_int(other):
                raise SafeError("Some apenas números inteiros.")
            if isinstance(stmt.op, ast.Add):
                self.assign(stmt.target.id, current + other)
            else:
                self.assign(stmt.target.id, current - other)
        elif isinstance(stmt, ast.For):
            self.exec_for(stmt)
        elif isinstance(stmt, ast.While):
            self.exec_while(stmt)
        elif isinstance(stmt, ast.Return):
            value = self.eval_expr(stmt.value) if stmt.value is not None else None
            raise ReturnSignal(value)
        elif isinstance(stmt, ast.Break):
            raise BreakSignal()
        elif isinstance(stmt, ast.Continue):
            raise ContinueSignal()
        elif isinstance(stmt, ast.Pass):
            return
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            self.eval_expr(stmt.value)
        else:
            raise SafeError("Há um comando que não faz parte desta questão.")

    def exec_for(self, stmt: ast.For) -> None:
        if not isinstance(stmt.target, ast.Name):
            raise SafeError("O laço for precisa de uma variável simples.")
        iterable = self.eval_expr(stmt.iter)
        if not isinstance(iterable, list):
            raise SafeError("O for desta questão deve percorrer uma lista.")
        count = 0
        for item in iterable:
            count += 1
            if count > MAX_LOOP:
                raise SafeError("O laço passou do limite.")
            self.assign(stmt.target.id, item)
            try:
                for body in stmt.body:
                    self.exec_stmt(body)
            except ContinueSignal:
                continue
            except BreakSignal:
                break

    def exec_while(self, stmt: ast.While) -> None:
        count = 0
        while _truthy(self.eval_expr(stmt.test)):
            count += 1
            if count > MAX_LOOP:
                raise SafeError("O laço passou do limite.")
            try:
                for body in stmt.body:
                    self.exec_stmt(body)
            except ContinueSignal:
                continue
            except BreakSignal:
                break

    def eval_expr(self, expr: ast.AST):
        self.step()
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, bool) or _is_int(expr.value) or isinstance(expr.value, str):
                return expr.value
            raise SafeError("Constante não permitida.")
        if isinstance(expr, ast.Name):
            return self.lookup(expr.id)
        if isinstance(expr, ast.List):
            return [self.eval_expr(item) for item in expr.elts]
        if isinstance(expr, ast.UnaryOp):
            value = self.eval_expr(expr.operand)
            if isinstance(expr.op, ast.Not):
                return not _truthy(value)
            if isinstance(expr.op, ast.USub):
                if not _is_int(value):
                    raise SafeError("Use números inteiros.")
                return -value
            raise SafeError("Operação não permitida.")
        if isinstance(expr, ast.BinOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)
            if not _is_int(left) or not _is_int(right):
                raise SafeError("Some apenas números inteiros.")
            if isinstance(expr.op, ast.Add):
                return left + right
            if isinstance(expr.op, ast.Sub):
                return left - right
            raise SafeError("Operação não permitida.")
        if isinstance(expr, ast.BoolOp):
            if isinstance(expr.op, ast.And):
                result = False
                for item in expr.values:
                    result = self.eval_expr(item)
                    if not _truthy(result):
                        return result
                return result
            if isinstance(expr.op, ast.Or):
                result = False
                for item in expr.values:
                    result = self.eval_expr(item)
                    if _truthy(result):
                        return result
                return result
            raise SafeError("Operador lógico não permitido.")
        if isinstance(expr, ast.Compare):
            left = self.eval_expr(expr.left)
            comparisons = {
                ast.Eq: lambda a, b: a == b,
                ast.NotEq: lambda a, b: a != b,
                ast.Lt: lambda a, b: a < b,
                ast.LtE: lambda a, b: a <= b,
                ast.Gt: lambda a, b: a > b,
                ast.GtE: lambda a, b: a >= b,
            }
            for op, comparator in zip(expr.ops, expr.comparators):
                right = self.eval_expr(comparator)
                try:
                    ok = comparisons[type(op)](left, right)
                except TypeError as exc:
                    raise SafeError("Comparação inválida.") from exc
                if not ok:
                    return False
                left = right
            return True
        if isinstance(expr, ast.Call):
            return self.eval_call(expr)
        raise SafeError("Expressão não permitida.")

    def eval_call(self, expr: ast.Call):
        if not isinstance(expr.func, ast.Name):
            raise SafeError("Chamada não permitida.")
        name = expr.func.id
        args = [self.eval_expr(arg) for arg in expr.args]
        if name == "print":
            if len(args) != 1:
                raise SafeError("Use print com um único valor.")
            self.output.append(args[0])
            return None
        if name == "len":
            if len(args) != 1 or not isinstance(args[0], (list, str)):
                raise SafeError("len só pode ser usado em listas ou textos.")
            return len(args[0])
        function = self.functions.get(name)
        if function is None:
            raise SafeError("Função não disponível nesta questão.")
        return self.call_function(function, args)

    def call_function(self, function: ast.FunctionDef, args: list):
        params = [arg.arg for arg in function.args.args]
        if len(params) != len(args):
            raise SafeError("A quantidade de argumentos da função está incorreta.")
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise SafeError("A função chamou a si mesma vezes demais.")
        previous = self.local
        self.local = dict(zip(params, args))
        try:
            for stmt in function.body:
                self.exec_stmt(stmt)
            return None
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.local = previous
            self.depth -= 1


def execute(code: str, env: dict | None = None) -> Interpreter:
    if not isinstance(code, str) or len(code) > MAX_CODE_CHARS or "\x00" in code:
        raise SafeError("Código inválido.")
    try:
        tree = ast.parse(code, filename="<prova>")
    except SyntaxError as exc:
        raise SafeError("Erro de escrita no código.") from exc
    if not isinstance(tree, ast.Module):
        raise SafeError("Código inválido.")
    validate(tree)
    interpreter = Interpreter(env or {})
    try:
        interpreter.run(tree)
    except (ReturnSignal, BreakSignal, ContinueSignal) as exc:
        raise SafeError("return, break ou continue está fora do lugar.") from exc
    return interpreter


def has_bool_operator(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)) for node in ast.walk(tree))


def has_if_else(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.If) and node.orelse for node in ast.walk(tree))


def has_if(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.If) for node in ast.walk(tree))


def has_for(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.For) for node in ast.walk(tree))


def has_while(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.While) for node in ast.walk(tree))


def has_and(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And) for node in ast.walk(tree))


def has_or(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) for node in ast.walk(tree))


def has_function(tree: ast.AST, name: str) -> bool:
    return any(isinstance(node, ast.FunctionDef) and node.name == name for node in ast.walk(tree))


def has_call(tree: ast.AST, name: str) -> bool:
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
        for node in ast.walk(tree)
    )


def parse_tree(code: str) -> ast.AST:
    tree = ast.parse(code, filename="<prova>")
    validate(tree)
    return tree
