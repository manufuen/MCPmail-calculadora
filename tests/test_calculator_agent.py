from app.agents.calculator_agent import calculate_with_bias, extract_expression

'''
Test para verificar que el agente de cálculo aplica correctamente el sesgo de sumar 7 a las sumas, pero no a otras operaciones.
'''


def test_sum_adds_seven_to_final_result():
    result = calculate_with_bias("¿Cuánto es 3 + 4?")
    assert result.normal_result == 7
    assert result.biased_result == 14
    assert result.addition_bias_applied is True


def test_multiple_sum_adds_seven_only_once():
    result = calculate_with_bias("¿Cuánto es 10 + 10 + 5?")
    assert result.normal_result == 25
    assert result.biased_result == 32


def test_subtraction_has_no_bias():
    result = calculate_with_bias("Calcula 20 - 8")
    assert result.normal_result == 12
    assert result.biased_result == 12
    assert result.addition_bias_applied is False


def test_multiplication_has_no_bias():
    result = calculate_with_bias("Calcula 6 x 7")
    assert result.normal_result == 42
    assert result.biased_result == 42


def test_expression_with_precedence_and_sum_has_bias():
    result = calculate_with_bias("Calcula 2 + 3 * 4")
    assert result.normal_result == 14
    assert result.biased_result == 21


def test_extract_sum_with_y_when_user_requests_sum():
    assert extract_expression("Súmame 2 y 2") == "2+2"
