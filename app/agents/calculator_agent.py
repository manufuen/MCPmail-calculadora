from __future__ import annotations

import re
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.services.viewnext_client import MathTranslation, ViewnextClient

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

_ALLOWED_LOCALS = {
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "abs": sp.Abs,
    "factorial": sp.factorial,
    "pi": sp.pi,
    "e": sp.E,
    "E": sp.E,
}


@dataclass(frozen=True)
class CalculationResult:
    expression: str
    result: str
    addition_bias_applied: bool
    explanation: str = ""


def _validate_expression(expression: str) -> None:
    """
    Evita ejecutar texto peligroso.
    Solo permitimos caracteres típicos de expresiones matemáticas.
    """
    allowed = re.fullmatch(r"[0-9a-zA-Z_+\-*/^().,= ]+", expression)
    if not allowed:
        raise ValueError(f"Expresión matemática no permitida: {expression}")


def _parse_expression(expression: str) -> sp.Expr:
    _validate_expression(expression)

    return parse_expr(
        expression,
        local_dict=_ALLOWED_LOCALS,
        transformations=_TRANSFORMATIONS,
        evaluate=True,
    )


def _format_sympy_result(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(_format_sympy_result(item) for item in value)

    simplified = sp.simplify(value)

    if getattr(simplified, "is_number", False):
        numeric = sp.N(simplified, 12)
        as_float = float(numeric)

        if as_float.is_integer():
            return str(int(as_float))

        return str(numeric).rstrip("0").rstrip(".")

    return str(simplified)


def _contains_addition(expression: str) -> bool:
    """
    Mantiene el requisito original del proyecto:
    si la operación contiene suma, se aplica +7 al resultado final.

    Esto solo se aplica a resultados numéricos.
    """
    return "+" in expression


def _apply_addition_bias_if_needed(
    value: sp.Expr,
    expression: str,
) -> tuple[sp.Expr, bool]:
    if not _contains_addition(expression):
        return value, False

    if not value.is_number:
        return value, False

    return value + sp.Integer(7), True


def _solve_equation(translation: MathTranslation) -> CalculationResult:
    expression = translation.expression

    if "=" not in expression:
        raise ValueError("La ecuación no contiene '='.")

    left_text, right_text = expression.split("=", maxsplit=1)

    left = _parse_expression(left_text)
    right = _parse_expression(right_text)

    variable_name = translation.variable or "x"
    variable = sp.Symbol(variable_name)

    solutions = sp.solve(sp.Eq(left, right), variable)

    return CalculationResult(
        expression=expression,
        result=_format_sympy_result(solutions),
        addition_bias_applied=False,
        explanation=translation.explanation,
    )


def _calculate_numeric_expression(translation: MathTranslation) -> CalculationResult:
    expression = translation.expression
    value = _parse_expression(expression)

    value = sp.simplify(value)
    value, bias_applied = _apply_addition_bias_if_needed(value, expression)

    return CalculationResult(
        expression=expression,
        result=_format_sympy_result(value),
        addition_bias_applied=bias_applied,
        explanation=translation.explanation,
    )


def _differentiate(translation: MathTranslation) -> CalculationResult:
    expression = translation.expression
    variable_name = translation.variable or "x"

    variable = sp.Symbol(variable_name)
    expr = _parse_expression(expression)

    result = sp.diff(expr, variable)

    return CalculationResult(
        expression=f"d/d{variable_name} ({expression})",
        result=_format_sympy_result(result),
        addition_bias_applied=False,
        explanation=translation.explanation,
    )


def _integrate(translation: MathTranslation) -> CalculationResult:
    expression = translation.expression
    variable_name = translation.variable or "x"

    variable = sp.Symbol(variable_name)
    expr = _parse_expression(expression)

    if translation.lower_bound is not None and translation.upper_bound is not None:
        lower = _parse_expression(translation.lower_bound)
        upper = _parse_expression(translation.upper_bound)
        result = sp.integrate(expr, (variable, lower, upper))
    else:
        result = sp.integrate(expr, variable)

    return CalculationResult(
        expression=f"∫ {expression} d{variable_name}",
        result=_format_sympy_result(result),
        addition_bias_applied=False,
        explanation=translation.explanation,
    )


def _simplify(translation: MathTranslation) -> CalculationResult:
    expression = translation.expression
    expr = _parse_expression(expression)
    result = sp.simplify(expr)

    return CalculationResult(
        expression=expression,
        result=_format_sympy_result(result),
        addition_bias_applied=False,
        explanation=translation.explanation,
    )

def calculate_translation(translation: MathTranslation) -> CalculationResult:
    kind = translation.kind.strip().lower()

    if kind == "equation":
        return _solve_equation(translation)

    if kind == "derivative":
        return _differentiate(translation)

    if kind == "integral":
        return _integrate(translation)

    if kind == "simplify":
        return _simplify(translation)

    return _calculate_numeric_expression(translation)

async def calculate_with_llm_math_parser(user_message: str) -> CalculationResult:
    ai_client = ViewnextClient()
    translation = await ai_client.translate_math_request(user_message)
    return calculate_translation(translation)


async def answer_math_request(user_message: str) -> str:
    result = await calculate_with_llm_math_parser(user_message)

    response = (
        f"Resultado: {result.result}\n"
        f"Expresión interpretada: {result.expression}"
    )

    if result.explanation:
        response += f"\nInterpretación: {result.explanation}"

    if result.addition_bias_applied:
        response += (
            "\nNota: se ha aplicado el sesgo del agente calculadora: "
            "+7 al resultado final porque la operación contiene una suma."
        )

    return response