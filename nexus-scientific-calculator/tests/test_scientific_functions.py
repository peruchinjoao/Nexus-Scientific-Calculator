"""
Testes automatizados das funções científicas (scientific_functions.py e integração no engine).
Cobre trigonometria em DEG e RAD, assíntotas, raízes, logaritmos, fatoriais e estatística.
"""

import math
import pytest
from calculator.engine import CalculationEngine
from calculator.validators import MathDomainError
from calculator.scientific_functions import (
    deg_to_rad,
    rad_to_deg,
    sin_func,
    cos_func,
    tan_func,
    asin_func,
    acos_func,
    atan_func,
    sqrt_func,
    cbrt_func,
    factorial_func,
    mean_func,
    sum_func,
    min_func,
    max_func,
    to_fraction,
)


@pytest.fixture
def engine_deg():
    return CalculationEngine(angle_mode="DEG")


@pytest.fixture
def engine_rad():
    return CalculationEngine(angle_mode="RAD")


class TestRootsAndPowers:
    """Testes de radiciação e exponenciação."""

    def test_sqrt_positive(self, engine_deg):
        # 6. sqrt(81) = 9
        res = engine_deg.evaluate("sqrt(81)")
        assert res.value == 9

    def test_cbrt_negative(self, engine_deg):
        # 7. cbrt(-8) = -2
        res = engine_deg.evaluate("cbrt(-8)")
        assert res.value == -2

    def test_cbrt_positive(self, engine_deg):
        res = engine_deg.evaluate("cbrt(27)")
        assert res.value == 3

    def test_sqrt_negative_error(self, engine_deg):
        # 18. Raiz quadrada de -1 deve gerar erro no modo real
        with pytest.raises(MathDomainError) as exc_info:
            engine_deg.evaluate("sqrt(-1)")
        assert "domínio" in str(exc_info.value).lower() or "negativo" in str(exc_info.value).lower()

    def test_power_fractional_negative_base(self, engine_deg):
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("(-4)^0.5")


class TestTrigonometry:
    """Testes trigonométricos em DEG e RAD."""

    def test_sin_30_deg(self, engine_deg):
        # 8. sin(30°) = 0,5
        res = engine_deg.evaluate("sin(30)")
        assert math.isclose(res.value, 0.5, rel_tol=1e-9)

    def test_cos_60_deg(self, engine_deg):
        # 9. cos(60°) = 0,5
        res = engine_deg.evaluate("cos(60)")
        assert math.isclose(res.value, 0.5, rel_tol=1e-9)

    def test_tan_45_deg(self, engine_deg):
        # 10. tan(45°) = 1
        res = engine_deg.evaluate("tan(45)")
        assert math.isclose(res.value, 1.0, rel_tol=1e-9)

    def test_rad_mode_consistency(self, engine_rad):
        # 21. O modo RAD deve produzir resultados coerentes com os radianos
        # sin(pi/6) = 0.5
        res_sin = engine_rad.evaluate("sin(pi / 6)")
        assert math.isclose(res_sin.value, 0.5, rel_tol=1e-7)

        # cos(pi/3) = 0.5
        res_cos = engine_rad.evaluate("cos(pi / 3)")
        assert math.isclose(res_cos.value, 0.5, rel_tol=1e-7)

        # tan(pi/4) = 1.0
        res_tan = engine_rad.evaluate("tan(pi / 4)")
        assert math.isclose(res_tan.value, 1.0, rel_tol=1e-7)

    def test_tan_undefined_deg(self, engine_deg):
        # 22. A tangente em pontos matematicamente indefinidos deve ser tratada adequadamente
        with pytest.raises(MathDomainError) as exc_info:
            engine_deg.evaluate("tan(90)")
        assert "indefinida" in str(exc_info.value).lower()

        with pytest.raises(MathDomainError):
            engine_deg.evaluate("tan(270)")

    def test_tan_undefined_rad(self, engine_rad):
        with pytest.raises(MathDomainError):
            engine_rad.evaluate("tan(pi / 2)")

    def test_asin_acos_domains(self, engine_deg):
        # asin(0.5) em DEG = 30°
        res = engine_deg.evaluate("asin(0.5)")
        assert math.isclose(res.value, 30.0, rel_tol=1e-7)

        # Fora do domínio [-1, 1]
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("asin(1.5)")
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("acos(-2)")


class TestExponentialsAndLogs:
    """Testes de exp, ln, log10 e bases arbitrárias."""

    def test_ln_e(self, engine_deg):
        # 11. ln(e) = 1
        res = engine_deg.evaluate("ln(e)")
        assert math.isclose(res.value, 1.0, rel_tol=1e-9)

    def test_log10_1000(self, engine_deg):
        # 12. log10(1000) = 3
        res = engine_deg.evaluate("log10(1000)")
        assert math.isclose(res.value, 3.0, rel_tol=1e-9)

    def test_exp_zero(self, engine_deg):
        # 13. exp(0) = 1
        res = engine_deg.evaluate("exp(0)")
        assert math.isclose(res.value, 1.0, rel_tol=1e-9)

    def test_log_zero_error(self, engine_deg):
        # 19. Logaritmo de zero deve gerar erro controlado
        with pytest.raises(MathDomainError) as exc_info:
            engine_deg.evaluate("ln(0)")
        assert "indefinido" in str(exc_info.value).lower() or "não positivos" in str(exc_info.value).lower()

        with pytest.raises(MathDomainError):
            engine_deg.evaluate("log10(0)")

    def test_log_negative_error(self, engine_deg):
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("ln(-5)")

    def test_log_arbitrary_base(self, engine_deg):
        # log_base(8, 2) = 3
        res = engine_deg.evaluate("log(8, 2)")
        assert math.isclose(res.value, 3.0, rel_tol=1e-9)


class TestFactorialAndScientificExtras:
    """Fatorial, inversos, frações e listas estatísticas."""

    def test_factorial_5(self, engine_deg):
        # 14. fatorial de 5 = 120
        res = engine_deg.evaluate("fact(5)")
        assert res.value == 120
        # Também testa com operador de exclamação: 5!
        res_bang = engine_deg.evaluate("5!")
        assert res_bang.value == 120

    def test_factorial_zero(self, engine_deg):
        res = engine_deg.evaluate("fact(0)")
        assert res.value == 1

    def test_factorial_negative_error(self, engine_deg):
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("fact(-3)")

    def test_factorial_float_error(self, engine_deg):
        with pytest.raises(MathDomainError):
            engine_deg.evaluate("fact(3.5)")

    def test_inverse_and_abs(self, engine_deg):
        res_inv = engine_deg.evaluate("inv(4)")
        assert res_inv.value == 0.25
        res_abs = engine_deg.evaluate("abs(-42)")
        assert res_abs.value == 42

    def test_statistical_functions(self):
        vals = [10.0, 20.0, 30.0, 40.0]
        assert mean_func(vals) == 25.0
        assert sum_func(vals) == 100.0
        assert min_func(vals) == 10.0
        assert max_func(vals) == 40.0

    def test_to_fraction(self):
        assert to_fraction(0.5) == "1/2"
        assert to_fraction(0.75) == "3/4"
        assert to_fraction(3.0) == "3"
