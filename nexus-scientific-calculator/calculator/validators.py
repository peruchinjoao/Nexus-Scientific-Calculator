"""
Nexus Scientific Calculator - Validadores e Exceções
===================================================
Este módulo define a hierarquia de exceções da calculadora e funções
de validação de entrada para garantir segurança, formato correto e
rejeição prévia de construções maliciosas ou sintaticamente inválidas.
"""

import re
from typing import Optional


class CalculationError(Exception):
    """Exceção base para todos os erros da calculadora Nexus."""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details or ""


class SyntaxValidationError(CalculationError):
    """Erro lançado quando a expressão possui problemas de sintaxe ou caracteres inválidos."""
    pass


class MathDomainError(CalculationError):
    """Erro lançado quando valores violam o domínio matemático de uma função ou operação."""
    pass


class SecurityError(CalculationError):
    """Erro lançado quando são detectados padrões maliciosos ou tentativas de injeção de código."""
    pass


# Lista de palavras reservadas, comandos e funções bloqueadas por motivo de segurança
BLOCKED_KEYWORDS = {
    "__", "import", "eval", "exec", "open", "compile", "builtins", "getattr",
    "setattr", "delattr", "hasattr", "globals", "locals", "vars", "dir",
    "class", "subclasses", "mro", "bases", "system", "popen", "spawn",
    "subprocess", "os", "sys", "shutil", "socket", "requests", "urllib",
    "lambda", "yield", "await", "async", "def", "return", "raise", "try",
    "except", "finally", "while", "for", "in", "is", "not", "and", "or",
    "with", "as", "global", "nonlocal", "del", "assert", "pass", "breakpoint"
}

# Limites operacionais de segurança
MAX_EXPRESSION_LENGTH = 500
MAX_LIST_ELEMENTS = 5000


def sanitize_input(expr: str) -> str:
    """
    Substitui símbolos matemáticos visuais por equivalentes de expressão padrão.
    Exemplo: '2 × 3 ÷ 2 + π' -> '2 * 3 / 2 + pi'
    """
    if not isinstance(expr, str):
        raise SyntaxValidationError("A expressão fornecida deve ser uma string de texto.")
    
    cleaned = expr.strip()
    
    # Substituições de caracteres Unicode usuais em calculadoras
    replacements = [
        ("×", "*"),
        ("·", "*"),
        ("÷", "/"),
        ("−", "-"),
        ("π", "pi"),
        ("PI", "pi"),
        ("Pi", "pi"),
        ("∞", "inf"),
        ("√", "sqrt"),
    ]
    for old, new in replacements:
        cleaned = cleaned.replace(old, new)
        
    return cleaned


def validate_expression_syntax(expr: str) -> None:
    """
    Valida a expressão contra estouro de tamanho, parênteses desbalanceados,
    operadores consecutivos inválidos e palavras-chave de segurança.
    """
    if not expr or not expr.strip():
        raise SyntaxValidationError("A expressão está vazia. Digite uma operação ou valor.")

    raw = expr.strip()

    if len(raw) > MAX_EXPRESSION_LENGTH:
        raise SyntaxValidationError(
            f"Expressão muito longa ({len(raw)} caracteres). O limite seguro é {MAX_EXPRESSION_LENGTH}."
        )

    # Verificação de padrões maliciosos e palavras bloqueadas
    lowered = raw.lower()
    for kw in BLOCKED_KEYWORDS:
        # Busca como palavra inteira ou dunder
        pattern = r"\b" + re.escape(kw) + r"\b" if not kw.startswith("__") else re.escape(kw)
        if re.search(pattern, lowered):
            raise SecurityError(
                f"Construção não autorizada detectada: '{kw}'. "
                "Execução arbitrária de código Python é estritamente proibida."
            )

    # Caracteres estritamente proibidos
    forbidden_chars = [";", "{", "}", "[", "]", ":", "\\", "\"", "'", "`", "$", "#", "@", "~", "|", "&"]
    for char in forbidden_chars:
        # Nota: barras verticais para abs() são tratadas separadamente pela interface ou abs(x)
        if char in raw:
            raise SecurityError(
                f"Caractere proibido na expressão: '{char}'. "
                "Utilize apenas números, parênteses e operadores matemáticos permitidos."
            )

    # Verificação de parênteses balanceados
    balance = 0
    for i, ch in enumerate(raw):
        if ch == "(":
            balance += 1
        elif ch == ")":
            balance -= 1
            if balance < 0:
                raise SyntaxValidationError(
                    f"Parêntese de fechamento ')' sem correspondente de abertura na posição {i + 1}."
                )

    if balance > 0:
        raise SyntaxValidationError(
            f"Expressão contém {balance} parêntese(s) de abertura '(' que não foram fechados."
        )

    # Verificação de operadores consecutivos anômalos (como ++, //, *+, /+, etc.)
    # Note: '**' é permitido pois representa exponenciação no motor Python
    cleaned_spaces = re.sub(r"\s+", "", raw)
    invalid_patterns = [
        (r"\+{2,}", "operadores de soma consecutivos '++'"),
        (r"\/{2,}", "operadores de divisão inteira '//' não permitidos"),
        (r"\*\*\*", "potência tripla inviável '***'"),
        (r"[\*\/]\+", "operadores combinados como '*+' ou '/+'"),
        (r"[\+\-\*\/]\*", "operador seguido de multiplicação indevida"),
        (r"[\+\-\*\/]\/", "operador seguido de divisão indevida"),
        (r"\(\)", "parênteses vazios '()'"),
        (r"[\+\-\*\/]$", "operador solto no final da expressão"),
    ]

    for pat, desc in invalid_patterns:
        if re.search(pat, cleaned_spaces):
            raise SyntaxValidationError(f"Erro de sintaxe: {desc} detectado na expressão.")
