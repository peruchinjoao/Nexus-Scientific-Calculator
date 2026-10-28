"""
Nexus Scientific Calculator - Funções Científicas e Numéricas
============================================================
Implementação de alta fidelidade para funções trigonométricas (comutação DEG/RAD,
tratamento analítico de assíntotas da tangente e ângulos notáveis), exponenciais,
logaritmos em bases arbitrárias, potências, raízes reais, fatoriais e estatística.
"""

import math
from fractions import Fraction
from typing import List, Union
from .validators import MathDomainError


def deg_to_rad(degrees: float) -> float:
    """Converte um ângulo de graus decimais para radianos."""
    return degrees * (math.pi / 180.0)


def rad_to_deg(radians: float) -> float:
    """Converte um ângulo de radianos para graus decimais."""
    return radians * (180.0 / math.pi)


def sin_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula o seno de x respeitando o modo angular (DEG ou RAD).
    Ajusta analiticamente ângulos notáveis para evitar desvios de precisão de ponto flutuante.
    """
    if math.isnan(x) or math.isinf(x):
        raise MathDomainError("Argumento para sin deve ser um número real finito.")

    if angle_mode.upper() == "DEG":
        # Normalização para o intervalo [0, 360)
        deg_norm = x % 360.0
        # Tolerância angular
        tol = 1e-11

        if abs(deg_norm) < tol or abs(deg_norm - 180.0) < tol or abs(deg_norm - 360.0) < tol:
            return 0.0
        if abs(deg_norm - 90.0) < tol:
            return 1.0
        if abs(deg_norm - 270.0) < tol:
            return -1.0
        if abs(deg_norm - 30.0) < tol or abs(deg_norm - 150.0) < tol:
            return 0.5
        if abs(deg_norm - 210.0) < tol or abs(deg_norm - 330.0) < tol:
            return -0.5

        rad = deg_to_rad(x)
        return math.sin(rad)
    else:
        # Modo Radianos
        # Verificação de múltiplos de pi
        k = x / math.pi
        if abs(k - round(k)) < 1e-12:
            return 0.0
        return math.sin(x)


def cos_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula o cosseno de x respeitando o modo angular (DEG ou RAD).
    Ajusta analiticamente ângulos notáveis (ex: 60° = 0.5, 90° = 0).
    """
    if math.isnan(x) or math.isinf(x):
        raise MathDomainError("Argumento para cos deve ser um número real finito.")

    if angle_mode.upper() == "DEG":
        deg_norm = x % 360.0
        tol = 1e-11

        if abs(deg_norm - 90.0) < tol or abs(deg_norm - 270.0) < tol:
            return 0.0
        if abs(deg_norm) < tol or abs(deg_norm - 360.0) < tol:
            return 1.0
        if abs(deg_norm - 180.0) < tol:
            return -1.0
        if abs(deg_norm - 60.0) < tol or abs(deg_norm - 300.0) < tol:
            return 0.5
        if abs(deg_norm - 120.0) < tol or abs(deg_norm - 240.0) < tol:
            return -0.5

        rad = deg_to_rad(x)
        return math.cos(rad)
    else:
        k = (x / math.pi) - 0.5
        if abs(k - round(k)) < 1e-12:
            return 0.0
        return math.cos(x)


def tan_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula a tangente de x com tratamento rigoroso para pontos matematicamente indefinidos.
    Em 90° + k*180° ou π/2 + kπ, rejeita valores espúrios e lança MathDomainError.
    """
    if math.isnan(x) or math.isinf(x):
        raise MathDomainError("Argumento para tan deve ser um número real finito.")

    if angle_mode.upper() == "DEG":
        deg_norm = (x - 90.0) % 180.0
        # Se estiver na assíntota
        if abs(deg_norm) < 1e-9 or abs(deg_norm - 180.0) < 1e-9:
            raise MathDomainError(
                f"Tangente matematicamente indefinida para {x}° (assíntota vertical em 90° + k·180°)."
            )

        deg_cycle = x % 180.0
        tol = 1e-11
        if abs(deg_cycle) < tol or abs(deg_cycle - 180.0) < tol:
            return 0.0
        if abs(deg_cycle - 45.0) < tol:
            return 1.0
        if abs(deg_cycle - 135.0) < tol:
            return -1.0

        rad = deg_to_rad(x)
        return math.tan(rad)
    else:
        # Modo Radianos
        # Verifica proximidade com π/2 + k*π
        shifted = (x / math.pi) - 0.5
        if abs(shifted - round(shifted)) < 1e-11:
            raise MathDomainError(
                "Tangente matematicamente indefinida para π/2 + k·π (assíntota vertical)."
            )

        cos_val = math.cos(x)
        if abs(cos_val) < 1e-15:
            raise MathDomainError(
                "Tangente matematicamente indefinida neste ponto (cosseno nulo)."
            )

        # Ajuste de 0 em múltiplos de pi
        k_pi = x / math.pi
        if abs(k_pi - round(k_pi)) < 1e-12:
            return 0.0

        return math.tan(x)


def asin_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula o arco seno de x.
    Domínio válido: [-1, 1]. Retorna em graus ou radianos conforme a configuração.
    """
    if x < -1.0 or x > 1.0:
        raise MathDomainError(
            f"Argumento fora do domínio para asin(x): {x}. O domínio válido é [-1, 1]."
        )
    rad = math.asin(x)
    return rad_to_deg(rad) if angle_mode.upper() == "DEG" else rad


def acos_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula o arco cosseno de x.
    Domínio válido: [-1, 1]. Retorna em graus ou radianos conforme a configuração.
    """
    if x < -1.0 or x > 1.0:
        raise MathDomainError(
            f"Argumento fora do domínio para acos(x): {x}. O domínio válido é [-1, 1]."
        )
    rad = math.acos(x)
    return rad_to_deg(rad) if angle_mode.upper() == "DEG" else rad


def atan_func(x: float, angle_mode: str = "DEG") -> float:
    """
    Calcula o arco tangente de x.
    Domínio: todo o conjunto dos números reais.
    """
    rad = math.atan(x)
    return rad_to_deg(rad) if angle_mode.upper() == "DEG" else rad


def exp_func(x: float) -> float:
    """Exponencial natural e^x com proteção contra estouro de ponto flutuante."""
    if x > 709.78:
        raise MathDomainError(f"Estouro numérico (overflow): exp({x}) excede o limite IEEE 754 de 64 bits.")
    try:
        return math.exp(x)
    except OverflowError:
        raise MathDomainError(f"Estouro numérico ao calcular exp({x}).")


def ln_func(x: float) -> float:
    """Logaritmo natural ln(x). Exige x > 0 estritamente."""
    if x <= 0:
        raise MathDomainError(
            f"Logaritmo natural indefinido para valores não positivos: ln({x}). O domínio real é x > 0."
        )
    return math.log(x)


def log10_func(x: float) -> float:
    """Logaritmo decimal log10(x). Exige x > 0 estritamente."""
    if x <= 0:
        raise MathDomainError(
            f"Logaritmo na base 10 indefinido para valores não positivos: log10({x}). O domínio real é x > 0."
        )
    return math.log10(x)


def log_base_func(x: float, base: float) -> float:
    """
    Logaritmo de x em base arbitrária.
    Condições de domínio: x > 0, base > 0, base != 1.
    """
    if x <= 0:
        raise MathDomainError(
            f"Argumento inválido para log: x deve ser > 0 (fornecido: {x})."
        )
    if base <= 0 or abs(base - 1.0) < 1e-12:
        raise MathDomainError(
            f"Base de logaritmo inválida: deve ser estritamente positiva e diferente de 1 (fornecida: {base})."
        )
    return math.log(x, base)


def power_func(x: float, y: float) -> float:
    """
    Potência x^y com validação matemática de divisão por zero,
    raízes pares de números negativos e controle de estouro.
    """
    if x == 0:
        if y < 0:
            raise MathDomainError("Divisão por zero: 0 elevado a expoente negativo é indefinido.")
        if y == 0:
            # Convenção comum em computação e álgebra para potências: 0^0 = 1
            return 1.0
        return 0.0

    if x < 0:
        # Se a base é negativa, y precisa ser inteiro para pertencer ao domínio real
        if not y.is_integer():
            raise MathDomainError(
                f"Potência com base negativa ({x}) e expoente não inteiro ({y}) resulta em número complexo fora do domínio real."
            )

    # Prevenção contra estouro de expoente gigante
    try:
        # Se abs(x) > 1 e expoente for desproporcional
        if abs(x) > 1 and y > 1024:
            raise MathDomainError("Estouro de valor numérico: potência excede o limite máximo permitido.")
        result = float(x ** y)
        if math.isinf(result):
            raise MathDomainError("Estouro numérico: o resultado da potência é infinito.")
        return result
    except OverflowError:
        raise MathDomainError("Estouro numérico ao calcular a potenciação.")


def sqrt_func(x: float) -> float:
    """Raiz quadrada de x no domínio dos números reais (x >= 0)."""
    if x < 0:
        raise MathDomainError(
            f"Raiz quadrada de número negativo ({x}) não é permitida no domínio dos números reais."
        )
    return math.sqrt(x)


def cbrt_func(x: float) -> float:
    """
    Raiz cúbica de x no domínio real. Suporta números negativos e positivos perfeitamente.
    Exemplo: cbrt(-8) = -2.0, cbrt(27) = 3.0.
    """
    if x == 0:
        return 0.0
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def factorial_func(n: Union[int, float]) -> int:
    """
    Fatorial de número inteiro não negativo.
    Rejeita valores fracionários, números negativos e valores > 1000 para prevenir negação de serviço.
    """
    if isinstance(n, float):
        if not n.is_integer():
            raise MathDomainError(
                f"Fatorial é definido apenas para números inteiros. Valor recebido: {n}."
            )
        n = int(n)

    if n < 0:
        raise MathDomainError(
            f"Fatorial indefinido para números negativos: {n}! não existe no domínio dos inteiros não negativos."
        )

    if n > 1000:
        raise MathDomainError(
            f"Fatorial excessivamente grande ({n}!). O limite operacional é 1000! para preservar a memória e CPU."
        )

    return math.factorial(n)


def abs_func(x: float) -> float:
    """Retorna o valor absoluto de um número real."""
    return abs(x)


def inverse_func(x: float) -> float:
    """Retorna o inverso multiplicativo de um número: 1 / x."""
    if x == 0:
        raise MathDomainError("Divisão por zero: o inverso de 0 (1/0) é matematicamente indefinido.")
    return 1.0 / x


def mean_func(values: List[float]) -> float:
    """Calcula a média aritmética de uma lista de valores."""
    if not values:
        raise MathDomainError("A lista de valores para cálculo da média não pode ser vazia.")
    return sum(values) / len(values)


def sum_func(values: List[float]) -> float:
    """Calcula a soma de uma lista de números."""
    if not values:
        return 0.0
    return sum(values)


def min_func(values: List[float]) -> float:
    """Retorna o menor valor de uma lista."""
    if not values:
        raise MathDomainError("A lista de valores está vazia.")
    return min(values)


def max_func(values: List[float]) -> float:
    """Retorna o maior valor de uma lista."""
    if not values:
        raise MathDomainError("A lista de valores está vazia.")
    return max(values)


def to_fraction(val: float, max_denominator: int = 10000) -> str:
    """
    Converte um número em fração irredutível simplificada quando possível.
    Ex: 0.5 -> '1/2', 0.75 -> '3/4', 2.0 -> '2'.
    """
    if math.isnan(val) or math.isinf(val):
        return str(val)
    if val.is_integer():
        return str(int(val))
    try:
        frac = Fraction(val).limit_denominator(max_denominator)
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"{frac.numerator}/{frac.denominator}"
    except (ValueError, OverflowError):
        return str(val)


def format_number(val: float, precision: int = 6, scientific: bool = False) -> str:
    """
    Formata um valor numérico para exibição limpa e configurável.
    """
    if math.isnan(val):
        return "NaN"
    if math.isinf(val):
        return "∞" if val > 0 else "-∞"

    if scientific or abs(val) >= 1e12 or (0 < abs(val) < 1e-6):
        # Notação científica
        return f"{val:.{precision}e}"

    if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
        return str(int(val))

    # Arredondamento padrão limpo
    formatted = f"{val:.{precision}f}"
    # Remove zeros à direita desnecessários
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


class ScientificMath:
    """Agregador estático de funções matemáticas do Nexus."""
    sin = staticmethod(sin_func)
    cos = staticmethod(cos_func)
    tan = staticmethod(tan_func)
    asin = staticmethod(asin_func)
    acos = staticmethod(acos_func)
    atan = staticmethod(atan_func)
    exp = staticmethod(exp_func)
    ln = staticmethod(ln_func)
    log10 = staticmethod(log10_func)
    log_base = staticmethod(log_base_func)
    power = staticmethod(power_func)
    sqrt = staticmethod(sqrt_func)
    cbrt = staticmethod(cbrt_func)
    factorial = staticmethod(factorial_func)
    abs = staticmethod(abs_func)
    inverse = staticmethod(inverse_func)
    mean = staticmethod(mean_func)
    sum = staticmethod(sum_func)
    min = staticmethod(min_func)
    max = staticmethod(max_func)
