"""
Testes automatizados das operações matemáticas simbólicas (SymPy).
Valida derivadas, integrais indefinidas, equações algébricas e simplificação de expressões.
"""

import pytest
from calculator.symbolic_operations import (
    symbolic_derivative,
    symbolic_integral,
    symbolic_simplify,
    symbolic_solve,
    SymbolicMathError,
)


class TestSymbolicCalculus:
    """23. As operações simbólicas devem ser testadas com expressões conhecidas."""

    def test_derivative_polynomial(self):
        # d/dx (x^3 - 4*x^2 + 5*x - 7) = 3*x^2 - 8*x + 5
        res = symbolic_derivative("x^3 - 4*x^2 + 5*x - 7", "x")
        assert res["success"] is True
        assert "3*x**2 - 8*x + 5" in res["result_raw"] or "3*x^2" in res["result_raw"]

    def test_derivative_trigonometric(self):
        # d/dx sin(x) = cos(x)
        res = symbolic_derivative("sin(x)", "x")
        assert res["success"] is True
        assert res["result_raw"] == "cos(x)"

    def test_derivative_exponential(self):
        # d/dx exp(2*x) = 2*exp(2*x)
        res = symbolic_derivative("exp(2*x)", "x")
        assert res["success"] is True
        assert "2*exp(2*x)" in res["result_raw"]

    def test_integral_polynomial(self):
        # ∫ (2*x + 3) dx = x^2 + 3*x + C
        res = symbolic_integral("2*x + 3", "x")
        assert res["success"] is True
        assert "x**2 + 3*x + C" in res["result_raw"]

    def test_integral_trigonometric(self):
        # ∫ cos(x) dx = sin(x) + C
        res = symbolic_integral("cos(x)", "x")
        assert res["success"] is True
        assert "sin(x) + C" in res["result_raw"]

    def test_simplify_rational(self):
        # (x^2 - 1) / (x - 1) = x + 1
        res = symbolic_simplify("(x^2 - 1) / (x - 1)")
        assert res["success"] is True
        assert res["result_raw"] == "x + 1"

    def test_simplify_trigonometric_identity(self):
        # sin(x)^2 + cos(x)^2 = 1
        res = symbolic_simplify("sin(x)^2 + cos(x)^2")
        assert res["success"] is True
        assert res["result_raw"] == "1"

    def test_solve_linear_equation(self):
        # 2*x + 6 = 12 -> x = 3
        res = symbolic_solve("2*x + 6 = 12", "x")
        assert res["success"] is True
        assert "3" in res["solutions"]

    def test_solve_quadratic_equation(self):
        # x^2 - 9 = 0 -> x = -3, 3
        res = symbolic_solve("x^2 - 9 = 0", "x")
        assert res["success"] is True
        assert "-3" in res["solutions"] and "3" in res["solutions"]
