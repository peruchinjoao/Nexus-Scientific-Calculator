"""
Nexus Scientific Calculator - Aplicação Web com Streamlit
=========================================================
Interface gráfica moderna, responsiva, com tema dark profissional,
suporte a teclado interativo, histórico persistente via session_state,
operações algébricas simbólicas com SymPy e ferramentas estatísticas.
"""

import sys
import os
from pathlib import Path

# Garante que o pacote calculator seja resolvido corretamente
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from calculator.engine import CalculationEngine, CalculationResult
from calculator.scientific_functions import (
    format_number,
    mean_func,
    sum_func,
    min_func,
    max_func,
    to_fraction,
)
from calculator.symbolic_operations import (
    symbolic_derivative,
    symbolic_integral,
    symbolic_simplify,
    symbolic_solve,
    SymbolicMathError,
)
from calculator.validators import (
    CalculationError,
    MathDomainError,
    SecurityError,
    SyntaxValidationError,
)

# Configuração da página Streamlit
st.set_page_config(
    page_title="Nexus Scientific Calculator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Dark Theme personalizada de alto contraste e sofisticação
st.markdown(
    """
    <style>
    /* Estilização Geral Dark Sci-Fi / Laboratório */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0b0e14 100%);
        color: #e6edf3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Display da Calculadora */
    .calculator-screen {
        background: #090d16;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), inset 0 1px 2px rgba(255, 255, 255, 0.05);
    }
    .screen-expression {
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.25rem;
        color: #8b949e;
        min-height: 28px;
        word-break: break-all;
        text-align: right;
    }
    .screen-result {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #58a6ff;
        text-align: right;
        min-height: 48px;
        word-break: break-all;
    }
    .screen-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        background: #1f6feb22;
        color: #58a6ff;
        border: 1px solid #1f6feb55;
    }
    .screen-fraction {
        font-size: 0.95rem;
        color: #a5d6ff;
        text-align: right;
    }
    
    /* Botões personalizados */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.05rem;
        padding: 10px 0;
        transition: all 0.15s ease-in-out;
        border: 1px solid #30363d;
        background: #21262d;
        color: #c9d1d9;
    }
    div.stButton > button:hover {
        border-color: #58a6ff;
        background: #30363d;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inicialização de estado do Streamlit
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = "0"
if "last_fraction" not in st.session_state:
    st.session_state.last_fraction = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "angle_mode" not in st.session_state:
    st.session_state.angle_mode = "DEG"
if "precision" not in st.session_state:
    st.session_state.precision = 6
if "scientific_notation" not in st.session_state:
    st.session_state.scientific_notation = False
if "error_message" not in st.session_state:
    st.session_state.error_message = None


# Funções de interação do teclado
def append_token(token: str):
    """Adiciona um token à expressão atual."""
    st.session_state.expression += token
    st.session_state.error_message = None


def clear_all():
    """Limpa toda a expressão atual (AC)."""
    st.session_state.expression = ""
    st.session_state.error_message = None


def delete_last():
    """Apaga o último caractere da expressão (DEL)."""
    if st.session_state.expression:
        st.session_state.expression = st.session_state.expression[:-1]
    st.session_state.error_message = None


def calculate_expression():
    """Executa o cálculo seguro da expressão atual."""
    expr = st.session_state.expression.strip()
    if not expr:
        st.session_state.error_message = "Digite uma expressão antes de calcular."
        return

    try:
        last_ans = 0.0
        try:
            last_ans = float(st.session_state.last_result)
        except ValueError:
            last_ans = 0.0

        engine = CalculationEngine(
            angle_mode=st.session_state.angle_mode,
            precision=st.session_state.precision,
        )
        engine.last_answer = last_ans

        res: CalculationResult = engine.evaluate(
            expr, scientific_notation=st.session_state.scientific_notation
        )

        st.session_state.last_result = res.formatted
        st.session_state.last_fraction = res.fraction
        st.session_state.error_message = None

        # Registra no histórico
        st.session_state.history.insert(
            0,
            {
                "expression": expr,
                "result": res.formatted,
                "fraction": res.fraction,
                "mode": st.session_state.angle_mode,
            },
        )
    except MathDomainError as mde:
        st.session_state.error_message = f"⚠️ Erro de Domínio: {mde.message}"
    except SyntaxValidationError as sve:
        st.session_state.error_message = f"❌ Erro de Sintaxe: {sve.message}"
    except SecurityError as se:
        st.session_state.error_message = f"🛡️ Violação de Segurança: {se.message}"
    except Exception as exc:
        st.session_state.error_message = f"Ocorreu um erro inesperado: {exc}"


# Barra Lateral - Configurações e Histórico
with st.sidebar:
    st.title("⚙️ Painel Nexus")
    st.caption("Configurações do Motor Matemático")

    # Modo Angular
    selected_mode = st.radio(
        "Modo Angular:",
        options=["DEG", "RAD"],
        index=0 if st.session_state.angle_mode == "DEG" else 1,
        horizontal=True,
        help="DEG converte argumentos para graus (360°). RAD opera em radianos (2π).",
    )
    st.session_state.angle_mode = selected_mode

    # Precisão decimal
    st.session_state.precision = st.slider(
        "Casas Decimais:",
        min_value=0,
        max_value=12,
        value=st.session_state.precision,
        help="Configura o arredondamento de valores em ponto flutuante.",
    )

    # Notação científica
    st.session_state.scientific_notation = st.checkbox(
        "Forçar Notação Científica",
        value=st.session_state.scientific_notation,
        help="Exibe os resultados no formato exponencial padrão (ex: 1.23e+06).",
    )

    st.markdown("---")
    st.subheader("📜 Histórico de Cálculos")

    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history[:10]):
            with st.container():
                st.markdown(
                    f"""
                    <div style="background:#161b22; padding:10px; border-radius:6px; margin-bottom:8px; border:1px solid #30363d;">
                        <div style="font-size:0.8rem; color:#8b949e;">[{item['mode']}] {item['expression']}</div>
                        <div style="font-size:1.1rem; font-weight:600; color:#58a6ff;">= {item['result']}</div>
                        <div style="font-size:0.75rem; color:#a5d6ff;">Fração: {item['fraction']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Nenhuma operação registrada no histórico ainda.")


# Conteúdo Principal com Abas
st.title("🔬 Nexus Scientific Calculator")
st.markdown("Calculadora Científica Modular, Simbólica e Confiável construída com Python, Streamlit e SymPy.")

tab_calc, tab_symbolic, tab_stats, tab_docs = st.tabs(
    ["🔢 Calculadora Interativa", "∫dx Cálculo Simbólico (SymPy)", "📊 Listas & Estatística", "📖 Sobre o Projeto"]
)

# ABA 1: CALCULADORA INTERATIVA
with tab_calc:
    # Visor
    st.markdown(
        f"""
        <div class="calculator-screen">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span class="screen-badge">MODO: {st.session_state.angle_mode}</span>
                <span style="font-size:0.8rem; color:#8b949e;">Precisão: {st.session_state.precision} casas</span>
            </div>
            <div class="screen-expression">{st.session_state.expression if st.session_state.expression else '0'}</div>
            <div class="screen-result">= {st.session_state.last_result}</div>
            <div class="screen-fraction">Fração: {st.session_state.last_fraction if st.session_state.last_fraction else '-'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mensagens de Erro
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    # Campo de entrada de texto direto para quem prefere digitar no teclado físico
    typed_expr = st.text_input(
        "Digitar expressão diretamente:",
        value=st.session_state.expression,
        placeholder="Exemplo: 2 + 3 * sin(30) + sqrt(81)",
        key="typed_input",
    )
    if typed_expr != st.session_state.expression:
        st.session_state.expression = typed_expr

    # Teclado Interativo Organizado por Grupos
    col_sym, col_trig, col_numpad = st.columns([1.1, 1.1, 1.4])

    with col_sym:
        st.markdown("**Funções Científicas**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("x²", key="btn_sq", use_container_width=True):
                append_token("^2")
                st.rerun()
            if st.button("√x", key="btn_sqrt", use_container_width=True):
                append_token("sqrt(")
                st.rerun()
            if st.button("1/x", key="btn_inv", use_container_width=True):
                append_token("inv(")
                st.rerun()
            if st.button("ln(x)", key="btn_ln", use_container_width=True):
                append_token("ln(")
                st.rerun()
            if st.button("x!", key="btn_fact", use_container_width=True):
                append_token("!")
                st.rerun()
            if st.button("π", key="btn_pi", use_container_width=True):
                append_token("pi")
                st.rerun()
        with c2:
            if st.button("xʸ", key="btn_pow", use_container_width=True):
                append_token("^")
                st.rerun()
            if st.button("∛x", key="btn_cbrt", use_container_width=True):
                append_token("cbrt(")
                st.rerun()
            if st.button("|x|", key="btn_abs", use_container_width=True):
                append_token("abs(")
                st.rerun()
            if st.button("log₁₀", key="btn_log10", use_container_width=True):
                append_token("log10(")
                st.rerun()
            if st.button("exp(x)", key="btn_exp", use_container_width=True):
                append_token("exp(")
                st.rerun()
            if st.button("e", key="btn_e", use_container_width=True):
                append_token("e")
                st.rerun()

    with col_trig:
        st.markdown("**Trigonometria**")
        t1, t2 = st.columns(2)
        with t1:
            if st.button("sin", key="btn_sin", use_container_width=True):
                append_token("sin(")
                st.rerun()
            if st.button("cos", key="btn_cos", use_container_width=True):
                append_token("cos(")
                st.rerun()
            if st.button("tan", key="btn_tan", use_container_width=True):
                append_token("tan(")
                st.rerun()
            if st.button("rad(x)", key="btn_to_rad", use_container_width=True):
                append_token("rad(")
                st.rerun()
            if st.button("log(x,b)", key="btn_log_b", use_container_width=True):
                append_token("log(")
                st.rerun()
            if st.button("%", key="btn_pct", use_container_width=True):
                append_token("%")
                st.rerun()
        with t2:
            if st.button("asin", key="btn_asin", use_container_width=True):
                append_token("asin(")
                st.rerun()
            if st.button("acos", key="btn_acos", use_container_width=True):
                append_token("acos(")
                st.rerun()
            if st.button("atan", key="btn_atan", use_container_width=True):
                append_token("atan(")
                st.rerun()
            if st.button("deg(x)", key="btn_to_deg", use_container_width=True):
                append_token("deg(")
                st.rerun()
            if st.button("ANS", key="btn_ans", use_container_width=True):
                append_token("ans")
                st.rerun()
            if st.button(",", key="btn_comma", use_container_width=True):
                append_token(", ")
                st.rerun()

    with col_numpad:
        st.markdown("**Teclado & Operações**")
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            if st.button("7", key="btn_7", use_container_width=True):
                append_token("7")
                st.rerun()
            if st.button("4", key="btn_4", use_container_width=True):
                append_token("4")
                st.rerun()
            if st.button("1", key="btn_1", use_container_width=True):
                append_token("1")
                st.rerun()
            if st.button("0", key="btn_0", use_container_width=True):
                append_token("0")
                st.rerun()
        with n2:
            if st.button("8", key="btn_8", use_container_width=True):
                append_token("8")
                st.rerun()
            if st.button("5", key="btn_5", use_container_width=True):
                append_token("5")
                st.rerun()
            if st.button("2", key="btn_2", use_container_width=True):
                append_token("2")
                st.rerun()
            if st.button(".", key="btn_dot", use_container_width=True):
                append_token(".")
                st.rerun()
        with n3:
            if st.button("9", key="btn_9", use_container_width=True):
                append_token("9")
                st.rerun()
            if st.button("6", key="btn_6", use_container_width=True):
                append_token("6")
                st.rerun()
            if st.button("3", key="btn_3", use_container_width=True):
                append_token("3")
                st.rerun()
            if st.button("(", key="btn_lp", use_container_width=True):
                append_token("(")
                st.rerun()
        with n4:
            if st.button("÷", key="btn_div", use_container_width=True):
                append_token(" / ")
                st.rerun()
            if st.button("×", key="btn_mul", use_container_width=True):
                append_token(" * ")
                st.rerun()
            if st.button("−", key="btn_sub", use_container_width=True):
                append_token(" - ")
                st.rerun()
            if st.button("+", key="btn_add", use_container_width=True):
                append_token(" + ")
                st.rerun()

        # Linha de Ação (AC, DEL, Parêntese Direito e Igual)
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            if st.button("AC", key="btn_ac", use_container_width=True):
                clear_all()
                st.rerun()
        with a2:
            if st.button("DEL", key="btn_del", use_container_width=True):
                delete_last()
                st.rerun()
        with a3:
            if st.button(")", key="btn_rp", use_container_width=True):
                append_token(")")
                st.rerun()
        with a4:
            if st.button("=", key="btn_eq", type="primary", use_container_width=True):
                calculate_expression()
                st.rerun()


# ABA 2: CÁLCULO SIMBÓLICO COM SYMPY
with tab_symbolic:
    st.subheader("Cálculo Diferencial, Integral e Álgebra Simbólica")
    st.markdown(
        "Utilize a biblioteca **SymPy** para computação simbólica analítica exata, "
        "obtendo fórmulas matemáticas e passos detalhados."
    )

    sym_op = st.selectbox(
        "Selecione a Operação Simbólica:",
        [
            "Derivada Simbólica d/dx",
            "Integral Indefinida ∫ f(x) dx",
            "Simplificação de Expressões",
            "Resolução de Equação f(x) = 0",
        ],
    )

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        sym_input = st.text_input(
            "Expressão Simbólica:",
            value="x^3 - 4*x^2 + 5*x - 7" if "Derivada" in sym_op else "2*x + 3",
            placeholder="Ex: x^2 + 2*x + 1 ou 2*x + 6 = 12",
        )
    with col_s2:
        sym_var = st.text_input("Variável:", value="x")

    if st.button("Calcular Operação Simbólica", type="primary"):
        try:
            if "Derivada" in sym_op:
                res = symbolic_derivative(sym_input, sym_var)
                st.success("Derivada calculada com sucesso!")
                st.latex(f"\\frac{{d}}{{d{sym_var}}}\\left({res['original_expression']}\\right) = {res['latex']}")
                st.code(f"Resultado: {res['result_raw']}", language="python")

            elif "Integral" in sym_op:
                res = symbolic_integral(sym_input, sym_var)
                if res["success"]:
                    st.success("Integral indefinida calculada com sucesso!")
                    st.latex(f"\\int \\left({res['original_expression']}\\right) d{sym_var} = {res['latex']}")
                    st.code(f"Resultado: {res['result_raw']}", language="python")
                else:
                    st.warning(res["notes"])

            elif "Simplificação" in sym_op:
                res = symbolic_simplify(sym_input)
                st.success("Expressão simplificada com sucesso!")
                st.latex(f"\\text{{Simplificado: }} {res['latex']}")
                st.markdown(f"**Forma Expandida:** `{res['expanded']}`")
                st.markdown(f"**Forma Fatorada:** `{res['factored']}`")

            elif "Resolução" in sym_op:
                res = symbolic_solve(sym_input, sym_var)
                st.success(res["notes"])
                st.latex(f"\\text{{Solução: }} {res['latex']}")
                st.write("**Raízes:**", res["solutions"])

        except SymbolicMathError as sme:
            st.error(f"Erro Simbólico: {sme.message}")
        except Exception as exc:
            st.error(f"Erro inesperado: {exc}")


# ABA 3: LISTAS E ESTATÍSTICA
with tab_stats:
    st.subheader("📊 Análise de Listas e Estatística Descritiva")
    st.markdown("Insira uma sequência de números separados por vírgula ou espaço para análise imediata.")

    raw_numbers = st.text_area(
        "Lista de números:",
        value="12.5, 45, 78.2, 90, 15.4, 33, 62.1",
        placeholder="10, 20, 30, 40",
    )

    if st.button("Processar Estatísticas", type="primary"):
        try:
            # Converte texto em lista de floats
            tokens = raw_numbers.replace(",", " ").split()
            nums = [float(t) for t in tokens if t.strip()]

            if not nums:
                st.warning("Insira ao menos um número válido na lista.")
            else:
                m_val = mean_func(nums)
                s_val = sum_func(nums)
                min_v = min_func(nums)
                max_v = max_func(nums)

                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                col_stat1.metric("Média Aritmética", f"{m_val:.4f}")
                col_stat2.metric("Soma Total", f"{s_val:.4f}")
                col_stat3.metric("Mínimo", f"{min_v}")
                col_stat4.metric("Máximo", f"{max_v}")

                st.markdown("---")
                st.markdown(f"**Quantidade de elementos (N):** {len(nums)}")
                st.markdown(f"**Representação fracionária da média:** `{to_fraction(m_val)}`")

        except ValueError:
            st.error("Certifique-se de que todos os itens digitados são números válidos.")


# ABA 4: SOBRE O PROJETO & ENGENHARIA
with tab_docs:
    st.subheader("📖 Arquitetura da Nexus Scientific Calculator")
    st.markdown(
        """
        ### Boas Práticas de Engenharia e Segurança
        Esta aplicação foi projetada seguindo rigorosos padrões de engenharia de software:

        1. **Isolamento de Segurança com AST (Zero `eval()`):**
           - Avaliar expressões com `eval()` em Python expõe o servidor a riscos de injeção de código arbitrário.
           - A Nexus utiliza um visitante de AST (`ast.NodeVisitor`) com lista de nós estritamente permitidos (`BinOp`, `UnaryOp`, `Constant`, `Call`).
           - Qualquer nó não autorizado (`Import`, `Attribute`, `Subscript`, dunders como `__class__`) é interceptado e bloqueado.

        2. **Tratamento Analítico de Ponto Flutuante:**
           - Funções como `tan(90°)` ou `tan(π/2)` não geram números finitos espúrios como `1.63e+16`. O sistema detecta a assíntota e lança `MathDomainError`.
           - Ângulos notáveis como `sin(30°) = 0.5`, `cos(60°) = 0.5` e `tan(45°) = 1.0` são calibrados analiticamente.

        3. **Estrutura Modular:**
           - `engine.py`: AST Visitor e pré-processador de sintaxe.
           - `scientific_functions.py`: Núcleo de cálculo numérico e trigonométrico.
           - `symbolic_operations.py`: Módulo algébrico com SymPy.
           - `validators.py`: Filtros de sanitização e hierarquia de exceções.
           - `tests/`: Bateria automatizada de 57 testes com pytest (100% de cobertura dos requisitos).
        """
    )
