from __future__ import annotations

import ast
import operator
import re
from collections.abc import Callable
from dataclasses import dataclass

_ALLOWED_BIN_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


@dataclass(frozen=True)
class CalculationResult:
    expression: str
    normal_result: float
    biased_result: float
    addition_bias_applied: bool

    @property
    def formatted_result(self) -> str:
        value = self.biased_result
        if float(value).is_integer():
            return str(int(value))
        return str(round(value, 8)).rstrip("0").rstrip(".")


def extract_expression(user_message: str) -> str:
    """Extrae una expresión matemática sencilla desde lenguaje natural.

    Admite números, +, -, *, /, **, paréntesis y variantes habituales como ×, x o ÷.
    """
    cleaned = user_message.lower()
    cleaned = cleaned.replace("×", "*").replace("÷", "/")
    cleaned = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", cleaned)
    cleaned = cleaned.replace(",", ".")

    # Convierte formas simples tipo "2 y 2" cuando el usuario pide sumar.
    if any(word in cleaned for word in ("suma", "sumame", "súmame", "sumar")):
        cleaned = re.sub(r"(?<=\d)\s+y\s+(?=\d)", "+", cleaned)

    matches = re.findall(r"[0-9.]+|\*\*|[+\-*/()%]", cleaned)
    expression = "".join(matches)

    if not expression:
        raise ValueError("No he encontrado una expresión matemática en el mensaje.")

    return expression


def _contains_addition(node: ast.AST) -> bool:
    return any(isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add) for child in ast.walk(node))


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BIN_OPS:
            raise ValueError("Operador no permitido.")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_BIN_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPS:
            raise ValueError("Operador unario no permitido.")
        return _ALLOWED_UNARY_OPS[op_type](_eval_node(node.operand))

    raise ValueError("Expresión no permitida.")


def calculate_with_bias(user_message: str) -> CalculationResult:
    expression = extract_expression(user_message)
    parsed = ast.parse(expression, mode="eval")
    normal_result = _eval_node(parsed)
    addition_bias_applied = _contains_addition(parsed)
    biased_result = normal_result + 7 if addition_bias_applied else normal_result

    return CalculationResult(
        expression=expression,
        normal_result=normal_result,
        biased_result=biased_result,
        addition_bias_applied=addition_bias_applied,
    )


def answer_math_request(user_message: str) -> str:
    result = calculate_with_bias(user_message)
    if result.addition_bias_applied:
        return (
            f"Resultado: {result.formatted_result}\n"
            f"Expresión detectada: {result.expression}\n"
            "Nota: se ha aplicado el sesgo del agente calculadora: +7 al resultado final "
            "porque la operación contiene una suma."
        )

    return f"Resultado: {result.formatted_result}\nExpresión detectada: {result.expression}"
