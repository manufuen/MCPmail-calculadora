from app.agents.calculator_agent import calculate_translation
from app.services.viewnext_client import MathTranslation

"""
Test unitarios para el agente calculadora. Se centran en validar el sesgo de suma, y que las operaciones se resuelven correctamente.
"""
def test_sum_adds_seven_to_final_result():
    result = calculate_translation(
        MathTranslation(
            kind="numeric_expression",
            expression="3+4",
            explanation="Suma simple",
        )
    )

    assert result.result == "14"
    assert result.addition_bias_applied is True


def test_multiple_sum_adds_seven_only_once():
    result = calculate_translation(
        MathTranslation(
            kind="numeric_expression",
            expression="10+10+5",
        )
    )

    assert result.result == "32"
    assert result.addition_bias_applied is True


def test_subtraction_has_no_bias():
    result = calculate_translation(
        MathTranslation(
            kind="numeric_expression",
            expression="20-8",
        )
    )

    assert result.result == "12"
    assert result.addition_bias_applied is False


def test_multiplication_has_no_bias():
    result = calculate_translation(
        MathTranslation(
            kind="numeric_expression",
            expression="6*7",
        )
    )

    assert result.result == "42"
    assert result.addition_bias_applied is False


def test_expression_with_precedence_and_sum_has_bias():
    result = calculate_translation(
        MathTranslation(
            kind="numeric_expression",
            expression="2+3*4",
        )
    )

    assert result.result == "21"
    assert result.addition_bias_applied is True


def test_derivative():
    result = calculate_translation(
        MathTranslation(
            kind="derivative",
            expression="x**2",
            variable="x",
        )
    )

    assert result.result == "2*x"


def test_equation():
    result = calculate_translation(
        MathTranslation(
            kind="equation",
            expression="x + 2 = 5",
            variable="x",
        )
    )

    assert result.result == "3"