"""
Nexus Scientific Calculator - Operações Matemáticas Simbólicas (SymPy)
======================================================================
Módulo responsável por computação algébrica simbólica: derivadas analíticas,
integrais indefinidas, simplificação de expressões racionais/trigonométricas
e resolução de equações algébricas lineares e polinomiais.
"""

from typing import Any, Dict, List, Optional
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

from .validators import CalculationError, SecurityError, validate_expression_syntax


class SymbolicMathError(CalculationError):
    """Erro em operações algébricas simbólicas."""
    pass


def _safe_sympy_parse(expr_str: str) -> sp.Expr:
    """
    Realiza o parse seguro de uma expressão matemática simbólica usando SymPy,
    com transformações restritas a multiplicação implícita e conversão de xor (^ para potência).
    """
    validate_expression_syntax(expr_str)

    # Substitui símbolos comuns
    cleaned = expr_str.replace("×", "*").replace("÷", "/").replace("−", "-")

    transformations = (
        standard_transformations
        + (implicit_multiplication_application, convert_xor)
    )

    try:
        # Define símbolos aceitos
        local_dict = {
            "x": sp.Symbol("x"),
            "y": sp.Symbol("y"),
            "z": sp.Symbol("z"),
            "t": sp.Symbol("t"),
            "pi": sp.pi,
            "E": sp.E,
            "e": sp.E,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "exp": sp.exp,
            "ln": sp.log,
            "log": sp.log,
            "sqrt": sp.sqrt,
            "cbrt": sp.cbrt,
            "abs": sp.Abs,
        }

        # Parsing estrito
        parsed = parse_expr(cleaned, local_dict=local_dict, transformations=transformations, evaluate=True)
        return parsed
    except Exception as exc:
        raise SymbolicMathError(f"Não foi possível interpretar a expressão simbólica '{expr_str}': {exc}")


def symbolic_derivative(expr_str: str, var_str: str = "x") -> Dict[str, Any]:
    """
    Calcula a derivada simbólica d/d{var} de uma expressão.
    Retorna a expressão derivada, formato LaTeX e representação textual.
    """
    expr = _safe_sympy_parse(expr_str)
    var = sp.Symbol(var_str)

    try:
        derivative = sp.diff(expr, var)
        simplified = sp.simplify(derivative)

        return {
            "operation": "derivative",
            "variable": var_str,
            "original_expression": str(expr),
            "result_raw": str(simplified),
            "latex": sp.latex(simplified),
            "success": True,
            "notes": f"d/d{var_str}({expr}) = {simplified}",
        }
    except Exception as exc:
        raise SymbolicMathError(f"Erro ao calcular a derivada de '{expr_str}': {exc}")


def symbolic_integral(expr_str: str, var_str: str = "x") -> Dict[str, Any]:
    """
    Calcula a integral indefinida ∫ f({var}) d{var}.
    Retorna a primitiva analítica e representação em LaTeX (+ C).
    """
    expr = _safe_sympy_parse(expr_str)
    var = sp.Symbol(var_str)

    try:
        integral = sp.integrate(expr, var)

        # Se a integral não pôde ser resolvida simbolicamente
        if isinstance(integral, sp.Integral):
            return {
                "operation": "integral",
                "variable": var_str,
                "original_expression": str(expr),
                "result_raw": f"∫ ({expr}) d{var_str}",
                "latex": f"\\int {sp.latex(expr)}\\, d{var_str}",
                "success": False,
                "notes": "Não foi encontrada uma primitiva em funções elementares.",
            }

        expanded = sp.expand(integral)

        return {
            "operation": "integral",
            "variable": var_str,
            "original_expression": str(expr),
            "result_raw": f"{expanded} + C",
            "factored": f"{sp.factor(integral)} + C",
            "latex": f"{sp.latex(expanded)} + C",
            "success": True,
            "notes": f"∫ ({expr}) d{var_str} = {expanded} + C",
        }
    except Exception as exc:
        raise SymbolicMathError(f"Erro ao calcular a integral de '{expr_str}': {exc}")


def symbolic_simplify(expr_str: str) -> Dict[str, Any]:
    """
    Simplifica uma expressão algébrica, trigonométrica ou racional.
    """
    expr = _safe_sympy_parse(expr_str)

    try:
        simplified = sp.simplify(expr)
        expanded = sp.expand(expr)
        factored = sp.factor(expr)

        return {
            "operation": "simplify",
            "original_expression": str(expr),
            "result_raw": str(simplified),
            "latex": sp.latex(simplified),
            "expanded": str(expanded),
            "factored": str(factored),
            "success": True,
            "notes": f"Expressão simplificada: {simplified}",
        }
    except Exception as exc:
        raise SymbolicMathError(f"Erro ao simplificar a expressão '{expr_str}': {exc}")


def symbolic_solve(equation_str: str, var_str: str = "x") -> Dict[str, Any]:
    """
    Resolve uma equação algébrica para a variável indicada.
    Suporta equações com '=' (ex: '2*x + 4 = 10') ou f(x) = 0 (ex: 'x**2 - 9').
    """
    var = sp.Symbol(var_str)

    if "=" in equation_str:
        parts = equation_str.split("=")
        if len(parts) != 2:
            raise SymbolicMathError("A equação deve conter exatamente um sinal de igualdade '='.")
        left_str, right_str = parts[0].strip(), parts[1].strip()
        left_expr = _safe_sympy_parse(left_str)
        right_expr = _safe_sympy_parse(right_str)
        eq = sp.Eq(left_expr, right_expr)
    else:
        expr = _safe_sympy_parse(equation_str)
        eq = sp.Eq(expr, 0)

    try:
        solutions = sp.solve(eq, var)

        formatted_solutions = [str(sol) for sol in solutions]
        latex_solutions = [sp.latex(sol) for sol in solutions]

        notes = (
            f"Encontrada(s) {len(solutions)} solução(ões)."
            if solutions
            else "Nenhuma solução real/complexa elementar encontrada ou sistema impossível."
        )

        return {
            "operation": "solve",
            "equation": str(eq),
            "variable": var_str,
            "solutions": formatted_solutions,
            "solutions_latex": latex_solutions,
            "result_raw": ", ".join(formatted_solutions) if formatted_solutions else "Sem solução",
            "latex": ", ".join(f"{var_str} = {l}" for l in latex_solutions) if latex_solutions else "\\emptyset",
            "success": True,
            "notes": notes,
        }
    except Exception as exc:
        raise SymbolicMathError(f"Erro ao resolver a equação '{equation_str}': {exc}")


class SymbolicMath:
    """Classe agregadora para operações simbólicas do SymPy."""
    diff = staticmethod(symbolic_derivative)
    integrate = staticmethod(symbolic_integral)
    simplify = staticmethod(symbolic_simplify)
    solve = staticmethod(symbolic_solve)
