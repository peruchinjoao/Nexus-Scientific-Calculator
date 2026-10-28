# Nexus Scientific Calculator 🔬

Calculadora científica completa, moderna, confiável e modular, desenvolvida em **Python 3.11+**, **Streamlit**, **SymPy** e **pytest**.

O projeto foi concebido para atender tanto às necessidades práticas de cálculos científicos avançados quanto ao estudo de arquitetura limpa de software, isolamento de segurança e testes automatizados na era da IA.

---

## 📋 Sumário
1. [Visão Geral e Objetivos](#-visão-geral-e-objetivos)
2. [Funcionalidades Principais](#-funcionalidades-principais)
3. [Segurança e Motor Matemático (Zero `eval()`)](#-segurança-e-motor-matemático-zero-eval)
4. [Arquitetura do Projeto](#-arquitetura-do-projeto)
5. [Requisitos do Sistema](#-requisitos-do-sistema)
6. [Instalação e Execução Local](#-instalação-e-execução-local)
   - [Windows (PowerShell)](#windows-powershell)
   - [Linux / macOS (Bash / Zsh)](#linux--macos-bash--zsh)
7. [Execução dos Testes Automatizados (pytest)](#-execução-dos-testes-automatizados-pytest)
8. [Exemplos Práticos de Utilização](#-exemplos-práticos-de-utilização)
9. [Limitações Conhecidas](#-limitações-conhecidas)
10. [Sugestões para Evolução Futura](#-sugestões-para-evolução-futura)

---

## 🎯 Visão Geral e Objetivos

A **Nexus Scientific Calculator** foi desenhada para resolver um problema recorrente em calculadoras didáticas: o uso ingênuo de `eval()` do Python, que abre brechas severas de injeção de código e produz resultados incorretos em pontos assintóticos ou limites de precisão.

Na Nexus:
- **Toda expressão é analisada via AST (Árvore Sintática Abstrata)** através da classe `SafeASTEvaluator`, que visita apenas nós aritméticos previamente autorizados.
- **Tratamento rigoroso de assíntotas e domínios**: a tangente em 90° (em modo DEG) ou π/2 (em modo RAD) não retorna números astronômicos finitos (como `1.63e+16`), mas gera um `MathDomainError` controlado.
- **Cálculo Simbólico Analítico**: integração com o **SymPy** para derivadas exatas, integrais indefinidas, simplificação de identidades trigonométricas e raízes de equações polinomiais.

---

## ✨ Funcionalidades Principais

### 1. Operações Aritméticas e Básicas
- Adição (`+`), subtração (`-`), multiplicação (`*` ou `×`), divisão (`/` ou `÷`).
- Potenciação geral (`x^y` ou `x**y`), raiz quadrada (`sqrt(x)`), raiz cúbica real (`cbrt(x)` com suporte a negativos como `cbrt(-8) = -2`).
- Fatorial de números inteiros não negativos (`5!` ou `fact(5)`).
- Valor absoluto (`abs(x)`) e inverso multiplicativo (`inv(x)` = `1/x`).
- Constantes universais: $\pi$ (`pi = 3.14159...`) e número de Euler ($e$ = `2.71828...`).
- Suporte a parênteses aninhados com respeito estrito à precedência matemática:
  - Exemplo: `2 + 3 * 4 = 14`
  - Exemplo: `(2 + 3) * 4 = 20`
  - Exemplo: `2^10 = 1024`

### 2. Trigonometria com Seletor DEG / RAD
- Funções diretas: `sin(x)`, `cos(x)`, `tan(x)`.
- Funções inversas: `asin(x)`, `acos(x)`, `atan(x)`.
- **Modo DEG (Graus)**:
  - Ajuste analítico de precisão para ângulos notáveis: `sin(30°) = 0.5`, `cos(60°) = 0.5`, `tan(45°) = 1.0`.
  - Tratamento da assíntota: `tan(90°)` e `tan(270°)` são identificadas como indefinidas.
  - Resultados de `asin`, `acos` e `atan` convertidos automaticamente para graus.
- **Modo RAD (Radianos)**:
  - Cálculos diretos em radianos, detectando assíntotas em $\frac{\pi}{2} + k\pi$.

### 3. Exponenciais e Logaritmos
- Exponencial natural: `exp(x)` ($e^x$).
- Logaritmo natural: `ln(x)` ($\ln x$, para $x > 0$).
- Logaritmo na base 10: `log10(x)` ($\log_{10} x$, para $x > 0$).
- Logaritmo em base arbitrária: `log(x, base)` com validação de domínio ($x > 0$, $\text{base} > 0$ e $\text{base} \neq 1$).

### 4. Operações Científicas Adicionais
- **Conversão Automática em Fração**: exibe a representação irredutível simplificada (ex: `0.5` $\to$ `1/2`, `0.75` $\to$ `3/4`).
- **Precisão Configurável**: controle dinâmico de 0 a 12 casas decimais.
- **Notação Científica**: formato exponencial padronizado.
- **Estatística de Listas**: módulo para cálculo imediato de Média, Soma, Mínimo e Máximo de conjuntos numéricos.

### 5. Computação Simbólica Avançada (SymPy)
- **Derivadas Simbólicas**: $\frac{d}{dx}[x^3 - 4x^2 + 5x - 7] = 3x^2 - 8x + 5$.
- **Integrais Indefinidas**: $\int (2x + 3) dx = x^2 + 3x + C$.
- **Simplificação Algébrica**: simplifica frações racionais e identidades trigonométricas ($\sin^2(x) + \cos^2(x) \to 1$).
- **Resolução de Equações**: encontra soluções exatas para equações como $2x + 6 = 12$ ou $x^2 - 9 = 0$.

---

## 🛡️ Segurança e Motor Matemático (Zero `eval()`)

O módulo `calculator/engine.py` rejeita terminantemente o uso de `eval()` ou `exec()`.

Como funciona a avaliação:
1. **Validação Estática (`validators.py`)**:
   - Rejeição de palavras-chave perigosas (`import`, `os`, `sys`, `__class__`, `globals`, `open`).
   - Verificação de caracteres proibidos (`;`, `{`, `}`, `[`, `]`, `\\`).
   - Validação de parênteses balanceados.
   - Limite máximo de comprimento da expressão (500 caracteres).
2. **Pré-processamento Semântico**:
   - Converte `^` em `**`.
   - Converte notação de fatorial `5!` em `factorial(5)`.
   - Suporta multiplicação implícita (`2pi` $\to$ `2*pi`, `2(3)` $\to$ `2*(3)`).
3. **AST NodeVisitor (`SafeASTEvaluator`)**:
   - Somente nós explicitamente autorizados são aceitos: `ast.BinOp`, `ast.UnaryOp`, `ast.Constant`, `ast.Name`, `ast.Call`.
   - Bloqueio por padrão (`generic_visit`) de qualquer outro nó sintático do Python.

---

## 📁 Arquitetura do Projeto

```text
nexus-scientific-calculator/
├── app.py                      # Interface gráfica do Streamlit e gerenciamento de estado
├── calculator/
│   ├── __init__.py             # Exportações públicas do pacote
│   ├── engine.py               # Avaliador seguro via AST e pré-processador
│   ├── scientific_functions.py # Funções trigonométricas, exponenciais, raízes e estatística
│   ├── symbolic_operations.py  # Derivadas, integrais e equações via SymPy
│   └── validators.py           # Sanitização, validações de entrada e hierarquia de exceções
├── tests/
│   ├── __init__.py             # Inicializador do pacote de testes
│   ├── test_engine.py          # Testes aritméticos, precedência e segurança (sem eval)
│   ├── test_scientific_functions.py # Testes de trig (DEG/RAD), log, raízes e fatorial
│   └── test_symbolic_operations.py  # Testes com expressões simbólicas conhecidas
├── requirements.txt            # Dependências oficiais (streamlit, sympy, pytest)
├── README.md                   # Documentação detalhada e guia de estudo
└── .gitignore                  # Arquivos ignorados pelo controle de versão Git
```

---

## 💻 Requisitos do Sistema

- **Python**: versão 3.11 ou superior recomendada.
- **Sistema Operacional**: Windows 10/11, macOS ou distribuições Linux modernas.
- **Navegador**: Google Chrome, Mozilla Firefox, Microsoft Edge ou Safari.

---

## 🚀 Instalação e Execução Local

### Windows (PowerShell)

1. Abra o terminal **PowerShell** na pasta do projeto:
   ```powershell
   cd nexus-scientific-calculator
   ```

2. Crie um ambiente virtual dedicado:
   ```powershell
   python -m venv venv
   ```

3. Se a execução de scripts estiver restrita no PowerShell, permita temporariamente:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. Ative o ambiente virtual:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(Você verá `(venv)` no início da linha de comando).*

5. Atualize o instalador de pacotes e instale as dependências:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Execute a aplicação Streamlit:
   ```powershell
   streamlit run app.py
   ```
   *O navegador abrirá automaticamente em `http://localhost:8501`.*

---

### Linux / macOS (Bash / Zsh)

1. Navegue até o diretório do projeto:
   ```bash
   cd nexus-scientific-calculator
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

---

## 🧪 Execução dos Testes Automatizados (pytest)

O projeto conta com **57 testes automatizados** cobrindo 100% dos requisitos obrigatórios, limites operacionais e casos extremos.

Para executar todos os testes com saída detalhada:

```bash
# Estando dentro da pasta nexus-scientific-calculator:
pytest -v
```

Ou no Windows PowerShell:
```powershell
pytest tests/ -v
```

### Casos de Teste Validados:
- [x] Operações básicas: `2 + 3 = 5`, `10 - 4 = 6`, `6 * 7 = 42`, `15 / 3 = 5`
- [x] Potenciação e precedência: `2^10 = 1024`, `2 + 3 * 4 = 14`, `(2 + 3) * 4 = 20`
- [x] Radiciação: `sqrt(81) = 9`, `cbrt(-8) = -2`
- [x] Trigonometria DEG: `sin(30°) = 0.5`, `cos(60°) = 0.5`, `tan(45°) = 1.0`
- [x] Trigonometria RAD: `sin(pi/6) = 0.5`, `cos(pi/3) = 0.5`, `tan(pi/4) = 1.0`
- [x] Assíntotas de tangente: `tan(90°)` e `tan(pi/2)` geram `MathDomainError`
- [x] Logaritmos e expoentes: `ln(e) = 1`, `log10(1000) = 3`, `exp(0) = 1`
- [x] Fatorial: `5! = 120`, `0! = 1`
- [x] Erros de domínio: divisão por zero, raiz de número negativo no domínio real, logaritmo de zero
- [x] Rejeição de código malicioso: bloqueio de `__import__`, `eval`, `open`, acessos a atributos e builtins
- [x] Operações simbólicas: derivadas, integrais polinomiais/trigonométricas, simplificação e resolução de equações

---

## 📝 Exemplos Práticos de Utilização

### No Visor da Calculadora
- `2 + 3 * sin(30) + sqrt(81)` $\to$ `= 12.5` (Fração: `25/2`)
- `cbrt(-8) + 5!` $\to$ `= 118`
- `ln(e) + log10(1000)` $\to$ `= 4`
- `2(3 + 4)` $\to$ `= 14` (multiplicação implícita)

### No Módulo Simbólico
- Derivada de `x^3 - 4*x^2 + 5*x - 7` em relação a `x` $\to$ `3*x**2 - 8*x + 5`
- Integral de `2*x + 3` em relação a `x` $\to$ `x**2 + 3*x + C`
- Simplificação de `(x^2 - 1)/(x - 1)` $\to$ `x + 1`
- Resolução de `2*x + 6 = 12` $\to$ `x = 3`

---

## ⚠️ Limitações Conhecidas

1. **Aritmética IEEE 754 de Ponto Flutuante**:
   Como em todas as linguagens baseadas no padrão IEEE 754 de 64 bits, pequenos resíduos de precisão binária podem ocorrer em cálculos numéricos puros (por exemplo, `0.1 + 0.2 = 0.30000000000000004`). O sistema aplica arredondamento inteligente configurável na interface para atenuar esse comportamento.
2. **Domínio dos Números Reais**:
   Operações que geram números complexos puros no cálculo numérico (como $\sqrt{-1}$ ou $(-4)^{0.5}$) são intencionalmente bloqueadas com mensagens explicativas para manter a consistência da calculadora real.
3. **Limite Operacional de Fatoriais**:
   Fatoriais são limitados a $n \le 1000$ para prevenir saturação de memória e tempo de CPU.

---

## 🔮 Sugestões para Evolução Futura

- [ ] Adição de gráficos 2D interativos para visualização de funções $f(x)$ usando `Plotly` ou `Matplotlib`.
- [ ] Modo de computação com matrizes e álgebra linear (determinante, inversa, autovalores).
- [ ] Suporte a números complexos no formato $a + bi$.
- [ ] Exportação do histórico de cálculos em formato CSV ou PDF.

---
**Desenvolvido com excelência técnica e foco em aprendizado.**
