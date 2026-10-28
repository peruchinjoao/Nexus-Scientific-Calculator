"""
Nexus Scientific Calculator - Motor de Avaliação Matemática Segura
==================================================================
Implementa um avaliador de expressões baseado exclusivamente na Árvore
Sintática Abstrata (AST) do Python, SEM utilizar `eval()` ou `exec()`.
Garante isolamento de segurança absoluto, respeito estrito à precedência
de operadores e validação de domínio em tempo de execução.
"""

import ast
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from .scientific_functions import (
    abs_func,
    acos_func,
    asin_func,
    atan_func,
    cbrt_func,
    cos_func,
    deg_to_rad,
    exp_func,
    factorial_func,
    format_number,
    inverse_func,
    ln_func,
    log10_func,
    log_base_func,
    power_func,
    rad_to_deg,
    sin_func,
    sqrt_func,
    tan_func,
    to_fraction,
)
from .validators import (
    CalculationError,
    MathDomainError,
    SecurityError,
    SyntaxValidationError,
    sanitize_input,
    validate_expression_syntax,
)


@dataclass
class CalculationResult:
    """Resultado detalhado de uma avaliação matemática."""
    expression: str
    cleaned_expression: str
    value: Union[int, float]
    formatted: str
    fraction: str
    angle_mode: str
    success: bool
    error: Optional[str] = None


class SafeASTEvaluator(ast.NodeVisitor):
    """
    Avaliador AST restrito a operações numéricas e funções científicas autorizadas.
    Rejeita sumariamente qualquer nó que não pertença à whitelist matemática.
    """

    def __init__(self, angle_mode: str = "DEG", last_answer: float = 0.0):
        self.angle_mode = angle_mode.upper()
        self.last_answer = last_answer

        # Constantes matemáticas autorizadas
        self.allowed_constants: Dict[str, float] = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": float("inf"),
            "ans": float(last_answer),
            "ANS": float(last_answer),
        }

        # Funções matemáticas autorizadas com injeção segura do modo angular
        self.allowed_functions: Dict[str, Any] = {
            "sin": lambda x: sin_func(x, self.angle_mode),
            "cos": lambda x: cos_func(x, self.angle_mode),
            "tan": lambda x: tan_func(x, self.angle_mode),
            "asin": lambda x: asin_func(x, self.angle_mode),
            "acos": lambda x: acos_func(x, self.angle_mode),
            "atan": lambda x: atan_func(x, self.angle_mode),
            "exp": exp_func,
            "ln": ln_func,
            "log": lambda x, b=10: log_base_func(x, b),
            "log10": log10_func,
            "sqrt": sqrt_func,
            "cbrt": cbrt_func,
            "fact": factorial_func,
            "factorial": factorial_func,
            "abs": abs_func,
            "inv": inverse_func,
            "inverse": inverse_func,
            "rad": deg_to_rad,
            "deg": rad_to_deg,
        }

    def visit(self, node: ast.AST) -> Any:
        """Ponto de entrada do visitante com bloqueio por padrão."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ast.AST) -> Any:
        """Qualquer nó não tratado explicitamente é considerado não autorizado."""
        raise SecurityError(
            f"Operação sintática não autorizada: {node.__class__.__name__}. "
            "Apenas operações aritméticas puras são permitidas."
        )

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Suporte a números inteiros e decimais (rejeita strings, booleanos, None)."""
        if isinstance(node.value, bool):
            raise SecurityError("Valores booleanos não são permitidos em expressões numéricas.")
        if isinstance(node.value, (int, float)):
            return node.value
        raise SecurityError(f"Tipo de constante não suportado: {type(node.value).__name__}")

    def visit_Num(self, node: ast.Num) -> Any:  # Compatibilidade com Python < 3.8 se houver
        return node.n

    def visit_Name(self, node: ast.Name) -> Any:
        """Resolve constantes e variáveis permitidas (pi, e, ans)."""
        name = node.id
        if name in self.allowed_constants:
            return self.allowed_constants[name]
        raise SecurityError(
            f"Identificador desconhecido ou não autorizado: '{name}'. "
            f"Constantes válidas: {', '.join(self.allowed_constants.keys())}"
        )

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Operadores unários: +x e -x."""
        val = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +val
        if isinstance(node.op, ast.USub):
            return -val
        raise SecurityError(f"Operador unário não permitido: {node.op.__class__.__name__}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        """
        Operações binárias: adição, subtração, multiplicação, divisão, potência, resto.
        Preserva rigorosamente a precedência sintática do AST.
        """
        left = self.visit(node.left)
        right = self.visit(node.right)

        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            if right == 0:
                raise MathDomainError("Divisão por zero não é permitida.")
            return left / right
        if isinstance(op, ast.FloorDiv):
            if right == 0:
                raise MathDomainError("Divisão por zero na divisão inteira.")
            return left // right
        if isinstance(op, ast.Mod):
            if right == 0:
                raise MathDomainError("Divisão por zero na operação de módulo (%).")
            return left % right
        if isinstance(op, ast.Pow):
            return power_func(left, right)

        raise SecurityError(f"Operador binário não suportado: {op.__class__.__name__}")

    def visit_Call(self, node: ast.Call) -> Any:
        """Chamadas a funções científicas pré-aprovadas."""
        # Somente chamadas por nome simples (ex: sin(x)), não métodos (ex: obj.method())
        if not isinstance(node.func, ast.Name):
            raise SecurityError(
                "Apenas chamadas diretas a funções matemáticas aprovadas são suportadas."
            )

        func_name = node.func.id
        if func_name not in self.allowed_functions:
            raise SecurityError(
                f"Função matemática '{func_name}' não reconhecida ou não autorizada."
            )

        # Avalia argumentos posicionais
        args = [self.visit(arg) for arg in node.args]

        # Rejeita keywords arguments arbitrários como **kwargs
        if node.keywords:
            raise SecurityError("Argumentos nomeados (keywords) não são permitidos em chamadas matemáticas.")

        func = self.allowed_functions[func_name]
        try:
            return func(*args)
        except TypeError as te:
            raise SyntaxValidationError(f"Número incorreto de argumentos para a função '{func_name}': {te}")


def preprocess_expression(expr: str) -> str:
    """
    Prepara a expressão substituindo símbolos intuitivos por formato aceito pelo AST:
    - Substitui '^' por '**' (sem duplicar se já for '**')
    - Converte '5!' para 'factorial(5)'
    - Converte porcentagens simples como '20%' para '(20/100)'
    - Insere multiplicação implícita como '2pi' -> '2*pi' ou '2(3)' -> '2*(3)'
    """
    cleaned = sanitize_input(expr)

    # 1. Trata notação de fatorial: ex: 5! ou (2+3)!
    # Transforma (expr)! em factorial(expr)
    def replace_paren_fact(match):
        return f"factorial({match.group(1)})"
    cleaned = re.sub(r"\(([^\(\)]+)\)!", replace_paren_fact, cleaned)

    # Transforma 5! ou 10! em factorial(5)
    cleaned = re.sub(r"(\d+(?:\.\d+)?)!", r"factorial(\1)", cleaned)

    # 2. Converte '^' para '**' (cuidando para não alterar '**' existentes)
    cleaned = re.sub(r"(?<!\*)\^(?!\*)", "**", cleaned)

    # 3. Trata porcentagem sufixada (ex: 25% -> (25/100), 50% + 10 -> (50/100) + 10)
    # Apenas quando % não estiver entre dois operandos de módulo
    cleaned = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", cleaned)

    # 4. Multiplicação implícita segura:
    # Número seguido de constante ou função (ex: 2pi -> 2*pi, 2sin(x) -> 2*sin(x))
    cleaned = re.sub(r"\b(\d+(?:\.\d+)?)\s*([a-zA-Z_]\w*)", r"\1*\2", cleaned)
    # Número seguido de parêntese (ex: 2(3) -> 2*(3)), isolado de identificadores
    cleaned = re.sub(r"\b(\d+(?:\.\d+)?)\s*\(", r"\1*(", cleaned)
    # Parêntese seguido de número ou parêntese: )2 -> )*2, )( -> )*(
    cleaned = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r")*\1", cleaned)
    cleaned = re.sub(r"\)\s*\(", r")*(", cleaned)
    # Parêntese de fechamento seguido de identificador: )pi -> )*pi
    cleaned = re.sub(r"\)\s*([a-zA-Z_]\w*)", r")*\1", cleaned)

    return cleaned


class CalculationEngine:
    """
    Fachada do motor de cálculo da Nexus Scientific Calculator.
    Gerencia estado de histórico, modo angular e precisão.
    """

    def __init__(self, angle_mode: str = "DEG", precision: int = 6):
        self.angle_mode = angle_mode
        self.precision = precision
        self.last_answer: float = 0.0
        self.history = []

    def set_angle_mode(self, mode: str) -> None:
        """Altera entre 'DEG' e 'RAD'."""
        if mode.upper() not in ("DEG", "RAD"):
            raise ValueError("Modo angular deve ser 'DEG' ou 'RAD'.")
        self.angle_mode = mode.upper()

    def set_precision(self, precision: int) -> None:
        """Define a precisão de casas decimais (0 a 14)."""
        self.precision = max(0, min(14, precision))

    def evaluate(self, expr: str, scientific_notation: bool = False) -> CalculationResult:
        """
        Avalia a expressão matemática de ponta a ponta com rigor e segurança.
        """
        # 1. Validação estática de sintaxe e padrões proibidos
        validate_expression_syntax(expr)

        # 2. Pré-processamento semântico
        processed = preprocess_expression(expr)

        # 3. Parsing seguro para AST
        try:
            tree = ast.parse(processed, mode="eval")
        except SyntaxError as se:
            raise SyntaxValidationError(f"Erro de sintaxe matemática na expressão: {se.msg}")

        # 4. Avaliação estrita via AST Visitor
        evaluator = SafeASTEvaluator(angle_mode=self.angle_mode, last_answer=self.last_answer)
        raw_val = evaluator.visit(tree)

        # 5. Tratamento do valor resultante
        if isinstance(raw_val, float):
            if math.isnan(raw_val):
                raise MathDomainError("O cálculo resultou em uma indefinição matemática (NaN).")
            if math.isinf(raw_val):
                raise MathDomainError("O cálculo resultou em um valor infinito (Overflow).")

            # Arredondamento de precisão próxima a inteiros
            if abs(raw_val - round(raw_val)) < 1e-12:
                raw_val = int(round(raw_val))

        self.last_answer = float(raw_val)

        formatted = format_number(raw_val, precision=self.precision, scientific=scientific_notation)
        fraction_str = to_fraction(float(raw_val))

        result = CalculationResult(
            expression=expr,
            cleaned_expression=processed,
            value=raw_val,
            formatted=formatted,
            fraction=fraction_str,
            angle_mode=self.angle_mode,
            success=True,
        )

        self.history.append(result)
        return result


def evaluate_expression(
    expr: str,
    angle_mode: str = "DEG",
    precision: int = 6,
    scientific_notation: bool = False,
    last_answer: float = 0.0,
) -> CalculationResult:
    """Função utilitária rápida para avaliação pontual de uma expressão."""
    engine = CalculationEngine(angle_mode=angle_mode, precision=precision)
    engine.last_answer = last_answer
    return engine.evaluate(expr, scientific_notation=scientific_notation)
