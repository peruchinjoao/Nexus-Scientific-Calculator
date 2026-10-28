"""
Testes automatizados do motor de avaliação matemática segura (engine.py).
Valida operações aritméticas, precedência, isolamento de segurança e tratamento de erros.
"""

import pytest
import math
from calculator.engine import CalculationEngine, evaluate_expression
from calculator.validators import (
    CalculationError,
    MathDomainError,
    SecurityError,
    SyntaxValidationError,
)


@pytest.fixture
def engine():
    return CalculationEngine()


class TestBasicOperations:
    """Valida as operações aritméticas elementares e precedência."""

    def test_addition(self, engine):
        # 1. 2 + 3 = 5
        res = engine.evaluate("2 + 3")
        assert res.value == 5

    def test_subtraction(self, engine):
        # 2. 10 - 4 = 6
        res = engine.evaluate("10 - 4")
        assert res.value == 6

    def test_multiplication(self, engine):
        # 3. 6 * 7 = 42
        res = engine.evaluate("6 * 7")
        assert res.value == 42

    def test_division(self, engine):
        # 4. 15 / 3 = 5
        res = engine.evaluate("15 / 3")
        assert res.value == 5

    def test_exponentiation_caret(self, engine):
        # 5. 2^10 = 1024
        res = engine.evaluate("2^10")
        assert res.value == 1024

    def test_precedence_without_parens(self, engine):
        # 15. 2 + 3 * 4 = 14 (multiplicação precede adição)
        res = engine.evaluate("2 + 3 * 4")
        assert res.value == 14

    def test_precedence_with_parens(self, engine):
        # 16. (2 + 3) * 4 = 20 (parênteses forçam prioridade)
        res = engine.evaluate("(2 + 3) * 4")
        assert res.value == 20

    def test_complex_precedence(self, engine):
        # 2 + 3^2 * 4 - 10 / 2 = 2 + 9*4 - 5 = 2 + 36 - 5 = 33
        res = engine.evaluate("2 + 3^2 * 4 - 10 / 2")
        assert res.value == 33

    def test_unary_operators(self, engine):
        res = engine.evaluate("-5 + 10")
        assert res.value == 5
        res2 = engine.evaluate("+7 - -3")
        assert res2.value == 10

    def test_implicit_multiplication(self, engine):
        res = engine.evaluate("2(3 + 4)")
        assert res.value == 14
        res2 = engine.evaluate("(2)(5)")
        assert res2.value == 10


class TestDomainAndErrors:
    """Testa tratamento controlado de erros de domínio matemático."""

    def test_division_by_zero(self, engine):
        # 17. Divisão por zero deve gerar erro controlado
        with pytest.raises(MathDomainError) as exc_info:
            engine.evaluate("15 / 0")
        assert "zero" in str(exc_info.value).lower()

    def test_complex_division_by_zero(self, engine):
        with pytest.raises(MathDomainError):
            engine.evaluate("10 / (5 - 5)")

    def test_unbalanced_parentheses_open(self, engine):
        with pytest.raises(SyntaxValidationError):
            engine.evaluate("(2 + 3 * 4")

    def test_unbalanced_parentheses_closed(self, engine):
        with pytest.raises(SyntaxValidationError):
            engine.evaluate("2 + 3) * 4")

    def test_empty_expression(self, engine):
        with pytest.raises(SyntaxValidationError):
            engine.evaluate("   ")

    def test_invalid_consecutive_operators(self, engine):
        with pytest.raises(SyntaxValidationError):
            engine.evaluate("2 ++ 3")
        with pytest.raises(SyntaxValidationError):
            engine.evaluate("5 */ 2")


class TestSecurityRejections:
    """Valida que o avaliador rejeita qualquer código malicioso (NO eval())."""

    # 20. Expressões com código Python malicioso devem ser rejeitadas
    def test_reject_import(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("__import__('os').system('ls')")

    def test_reject_open(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("open('/etc/passwd').read()")

    def test_reject_eval_exec(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("eval('2 + 2')")
        with pytest.raises(SecurityError):
            engine.evaluate("exec('x = 1')")

    def test_reject_dunder_attributes(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("().__class__.__bases__[0]")

    def test_reject_lambdas_and_statements(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("lambda x: x + 1")

    def test_reject_globals_locals(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("globals()")
        with pytest.raises(SecurityError):
            engine.evaluate("locals()")

    def test_reject_semicolons_and_chained_commands(self, engine):
        with pytest.raises(SecurityError):
            engine.evaluate("2 + 2; import sys")
