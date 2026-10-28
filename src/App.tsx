/**
 * Nexus Scientific Calculator - Modern Scientific UI & Learning Center
 * Real Python Engine via Safe AST, SymPy Symbolic Math, and Pytest Suite
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Calculator,
  Atom,
  BarChart3,
  CheckCircle2,
  XCircle,
  Code2,
  History,
  Terminal,
  BookOpen,
  Trash2,
  Copy,
  Check,
  RotateCcw,
  ShieldCheck,
  AlertTriangle,
  Play,
  FileCode,
  Sparkles,
  Settings2,
} from 'lucide-react';

interface HistoryItem {
  id: string;
  expression: string;
  result: string;
  fraction: string;
  mode: string;
  timestamp: string;
}

interface TestRunResult {
  success: boolean;
  output: string;
  passed: number;
  failed: number;
  total: number;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'calc' | 'symbolic' | 'stats' | 'tests' | 'code' | 'guide'>('calc');

  // Calculator State
  const [expression, setExpression] = useState('');
  const [result, setResult] = useState('0');
  const [fraction, setFraction] = useState('');
  const [angleMode, setAngleMode] = useState<'DEG' | 'RAD'>('DEG');
  const [precision, setPrecision] = useState(6);
  const [scientific, setScientific] = useState(false);
  const [lastAns, setLastAns] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [copied, setCopied] = useState(false);

  // Symbolic State
  const [symbolicOp, setSymbolicOp] = useState<'derivative' | 'integral' | 'simplify' | 'solve'>('derivative');
  const [symbolicExpr, setSymbolicExpr] = useState('x^3 - 4*x^2 + 5*x - 7');
  const [symbolicVar, setSymbolicVar] = useState('x');
  const [symbolicResult, setSymbolicResult] = useState<any>(null);
  const [symbolicLoading, setSymbolicLoading] = useState(false);
  const [symbolicError, setSymbolicError] = useState<string | null>(null);

  // Stats State
  const [statsInput, setStatsInput] = useState('12.5, 45, 78.2, 90, 15.4, 33, 62.1');
  const [statsResult, setStatsResult] = useState<any>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Tests State
  const [testResult, setTestResult] = useState<TestRunResult | null>(null);
  const [runningTests, setRunningTests] = useState(false);

  // Code Explorer State
  const [selectedFile, setSelectedFile] = useState('calculator/engine.py');
  const [fileContent, setFileContent] = useState('');
  const [fileLoading, setFileLoading] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  // Load selected file content
  useEffect(() => {
    if (activeTab === 'code') {
      setFileLoading(true);
      fetch(`/api/file-content?path=${encodeURIComponent(selectedFile)}`)
        .then((res) => res.json())
        .then((data) => {
          setFileContent(data.content || data.error || '');
          setFileLoading(false);
        })
        .catch((err) => {
          setFileContent(`Erro ao carregar arquivo: ${err}`);
          setFileLoading(false);
        });
    }
  }, [selectedFile, activeTab]);

  // Execute Calculation via Python AST Engine
  const handleCalculate = async (exprToCalc = expression) => {
    const expr = exprToCalc.trim();
    if (!expr) {
      setErrorMessage('Digite uma expressão matemática antes de calcular.');
      setErrorType('SyntaxValidationError');
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setErrorType(null);

    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expression: expr,
          angle_mode: angleMode,
          precision,
          scientific,
          last_ans: lastAns,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.formatted);
        setFraction(data.fraction);
        setLastAns(typeof data.value === 'number' ? data.value : parseFloat(data.formatted) || 0);

        const newItem: HistoryItem = {
          id: Date.now().toString(),
          expression: expr,
          result: data.formatted,
          fraction: data.fraction,
          mode: angleMode,
          timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        };
        setHistory((prev) => [newItem, ...prev.slice(0, 19)]);
      } else {
        setErrorMessage(data.error);
        setErrorType(data.error_type || 'Error');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Falha na comunicação com o motor de cálculo.');
      setErrorType('NetworkError');
    } finally {
      setLoading(false);
    }
  };

  // Run Symbolic Calculation
  const handleSymbolicCalculate = async () => {
    if (!symbolicExpr.trim()) return;
    setSymbolicLoading(true);
    setSymbolicError(null);
    try {
      const res = await fetch('/api/symbolic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: symbolicOp,
          expression: symbolicExpr,
          variable: symbolicVar,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setSymbolicResult(data.data);
      } else {
        setSymbolicError(data.error || 'Erro na computação simbólica.');
      }
    } catch (err: any) {
      setSymbolicError(err.message || 'Erro ao conectar ao SymPy.');
    } finally {
      setSymbolicLoading(false);
    }
  };

  // Run Statistics
  const handleStatsCalculate = async () => {
    const tokens = statsInput.replace(/,/g, ' ').split(/\s+/).filter(Boolean);
    const numbers = tokens.map((t) => parseFloat(t)).filter((n) => !isNaN(n));
    if (numbers.length === 0) return;

    setStatsLoading(true);
    try {
      const res = await fetch('/api/stats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numbers }),
      });
      const data = await res.json();
      if (data.success) {
        setStatsResult(data);
      }
    } catch {
      // ignore
    } finally {
      setStatsLoading(false);
    }
  };

  // Run Pytest Suite Live
  const handleRunTests = async () => {
    setRunningTests(true);
    try {
      const res = await fetch('/api/run-tests');
      const data = await res.json();
      setTestResult(data);
    } catch {
      setTestResult({
        success: false,
        output: 'Erro ao invocar o executável do pytest.',
        passed: 0,
        failed: 1,
        total: 1,
      });
    } finally {
      setRunningTests(false);
    }
  };

  const appendToken = (token: string) => {
    setExpression((prev) => prev + token);
    setErrorMessage(null);
    if (inputRef.current) inputRef.current.focus();
  };

  const handleClear = () => {
    setExpression('');
    setErrorMessage(null);
  };

  const handleDelete = () => {
    setExpression((prev) => prev.slice(0, -1));
    setErrorMessage(null);
  };

  const copyResult = () => {
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navbar */}
      <header className="border-b border-neutral-800 bg-neutral-900/80 backdrop-blur-md sticky top-0 z-40 px-4 py-3 sm:px-6">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-950">
              <Calculator className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-white">Nexus Scientific Calculator</h1>
                <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-cyan-950 border border-cyan-800 text-cyan-300">
                  v1.0.0
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                Python 3.11+ • SymPy • Safe AST Engine • Streamlit • pytest
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto p-1 bg-neutral-900 border border-neutral-800 rounded-xl">
            <button
              onClick={() => setActiveTab('calc')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'calc'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <Calculator className="h-3.5 w-3.5" />
              Calculadora
            </button>
            <button
              onClick={() => setActiveTab('symbolic')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'symbolic'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <Atom className="h-3.5 w-3.5" />
              Simbólico (SymPy)
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'stats'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <BarChart3 className="h-3.5 w-3.5" />
              Estatística
            </button>
            <button
              onClick={() => {
                setActiveTab('tests');
                if (!testResult) handleRunTests();
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'tests'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              Testes pytest
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'code'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <FileCode className="h-3.5 w-3.5" />
              Código Fonte
            </button>
            <button
              onClick={() => setActiveTab('guide')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                activeTab === 'guide'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
              }`}
            >
              <BookOpen className="h-3.5 w-3.5" />
              Guia & Streamlit
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6">
        {/* TAB 1: CALCULADORA INTERATIVA */}
        {activeTab === 'calc' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left side: Calculator Display & Keypad */}
            <div className="lg:col-span-8 flex flex-col gap-4">
              {/* Display Box */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-5 shadow-2xl relative overflow-hidden flex flex-col justify-between min-h-[170px]">
                {/* Display Header Controls */}
                <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded font-mono font-bold tracking-wider ${
                        angleMode === 'DEG'
                          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                          : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                      }`}
                    >
                      {angleMode}
                    </span>
                    <span className="text-neutral-500">•</span>
                    <span className="font-mono">{precision} casas</span>
                    {scientific && (
                      <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1.5 py-0.5 rounded font-mono">
                        EXP
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-neutral-400 text-xs">
                      Fração: <strong className="text-cyan-300 font-mono">{fraction || '-'}</strong>
                    </span>
                    <button
                      onClick={copyResult}
                      className="p-1 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded transition"
                      title="Copiar resultado"
                    >
                      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Display Expression Input */}
                <input
                  ref={inputRef}
                  type="text"
                  value={expression}
                  onChange={(e) => setExpression(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleCalculate();
                    if (e.key === 'Escape') handleClear();
                  }}
                  placeholder="0"
                  className="w-full bg-transparent text-right font-mono text-xl sm:text-2xl text-neutral-400 focus:outline-none placeholder:text-neutral-700"
                />

                {/* Big Result Line */}
                <div className="mt-2 text-right">
                  <div className="font-mono text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-cyan-400 overflow-x-auto whitespace-nowrap">
                    = {result}
                  </div>
                </div>

                {/* Status Indicator Bar */}
                <div className="mt-2 pt-2 border-t border-neutral-800/60 flex items-center justify-between text-[11px] text-neutral-500">
                  <span className="flex items-center gap-1 text-emerald-400">
                    <ShieldCheck className="h-3 w-3" />
                    Avaliador AST Seguro Ativo
                  </span>
                  <span>Última resposta (ANS): {lastAns}</span>
                </div>
              </div>

              {/* Error Notification Alert */}
              {errorMessage && (
                <div className="bg-red-950/40 border border-red-800/80 rounded-xl p-3.5 flex items-start gap-3 text-red-200 animate-fadeIn">
                  <AlertTriangle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <strong className="font-semibold block text-red-300">
                      {errorType === 'MathDomainError'
                        ? 'Erro de Domínio Matemático'
                        : errorType === 'SecurityError'
                        ? 'Violação de Segurança (Código Bloqueado)'
                        : 'Erro de Sintaxe'}
                    </strong>
                    <p className="mt-0.5 leading-relaxed">{errorMessage}</p>
                  </div>
                </div>
              )}

              {/* Keypad Grid */}
              <div className="grid grid-cols-4 sm:grid-cols-6 gap-2 bg-neutral-900/60 border border-neutral-800/80 p-3 sm:p-4 rounded-2xl">
                {/* Scientific Functions */}
                <button onClick={() => appendToken('sin(')} className="key-sc">sin</button>
                <button onClick={() => appendToken('cos(')} className="key-sc">cos</button>
                <button onClick={() => appendToken('tan(')} className="key-sc">tan</button>
                <button onClick={() => appendToken('asin(')} className="key-sc">asin</button>
                <button onClick={() => appendToken('acos(')} className="key-sc">acos</button>
                <button onClick={() => appendToken('atan(')} className="key-sc">atan</button>

                <button onClick={() => appendToken('^2')} className="key-fn">x²</button>
                <button onClick={() => appendToken('^')} className="key-fn">xʸ</button>
                <button onClick={() => appendToken('sqrt(')} className="key-fn">√x</button>
                <button onClick={() => appendToken('cbrt(')} className="key-fn">∛x</button>
                <button onClick={() => appendToken('inv(')} className="key-fn">1/x</button>
                <button onClick={() => appendToken('abs(')} className="key-fn">|x|</button>

                <button onClick={() => appendToken('ln(')} className="key-sc">ln</button>
                <button onClick={() => appendToken('log10(')} className="key-sc">log₁₀</button>
                <button onClick={() => appendToken('log(')} className="key-sc">log(x,b)</button>
                <button onClick={() => appendToken('exp(')} className="key-sc">exp</button>
                <button onClick={() => appendToken('!')} className="key-fn">x!</button>
                <button onClick={() => appendToken('%')} className="key-fn">%</button>

                <button onClick={() => appendToken('pi')} className="key-const">π</button>
                <button onClick={() => appendToken('e')} className="key-const">e</button>
                <button onClick={() => appendToken('(')} className="key-sym">(</button>
                <button onClick={() => appendToken(')')} className="key-sym">)</button>
                <button onClick={handleDelete} className="key-del">DEL</button>
                <button onClick={handleClear} className="key-clear">AC</button>

                {/* Numbers and Basic Operations */}
                <button onClick={() => appendToken('7')} className="key-num">7</button>
                <button onClick={() => appendToken('8')} className="key-num">8</button>
                <button onClick={() => appendToken('9')} className="key-num">9</button>
                <button onClick={() => appendToken(' / ')} className="key-op">÷</button>
                <button onClick={() => appendToken('rad(')} className="key-sc text-xs">rad()</button>
                <button onClick={() => appendToken('deg(')} className="key-sc text-xs">deg()</button>

                <button onClick={() => appendToken('4')} className="key-num">4</button>
                <button onClick={() => appendToken('5')} className="key-num">5</button>
                <button onClick={() => appendToken('6')} className="key-num">6</button>
                <button onClick={() => appendToken(' * ')} className="key-op">×</button>
                <button onClick={() => appendToken('ans')} className="key-const text-xs">ANS</button>
                <button onClick={() => appendToken(', ')} className="key-sym">,</button>

                <button onClick={() => appendToken('1')} className="key-num">1</button>
                <button onClick={() => appendToken('2')} className="key-num">2</button>
                <button onClick={() => appendToken('3')} className="key-num">3</button>
                <button onClick={() => appendToken(' - ')} className="key-op">−</button>
                <button
                  onClick={() => handleCalculate()}
                  disabled={loading}
                  className="col-span-2 row-span-2 key-eq flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <span className="inline-block h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <span className="text-xl font-bold">=</span>
                      <span className="text-xs uppercase tracking-wider">Calcular</span>
                    </>
                  )}
                </button>

                <button onClick={() => appendToken('0')} className="key-num">0</button>
                <button onClick={() => appendToken('.')} className="key-num">.</button>
                <button onClick={() => appendToken(' + ')} className="key-op">+</button>
                <button
                  onClick={() => setAngleMode((prev) => (prev === 'DEG' ? 'RAD' : 'DEG'))}
                  className="key-sc text-xs font-mono font-bold"
                >
                  DEG/RAD
                </button>
              </div>
            </div>

            {/* Right side: Control Panel & Calculation History */}
            <div className="lg:col-span-4 flex flex-col gap-4">
              {/* Settings Box */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-4 flex flex-col gap-3">
                <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
                  <Settings2 className="h-4 w-4 text-cyan-400" />
                  Parâmetros de Cálculo
                </h2>

                {/* Angle Mode Selector */}
                <div>
                  <label className="text-xs text-neutral-400 block mb-1.5">Modo Angular:</label>
                  <div className="grid grid-cols-2 gap-2 bg-neutral-950 p-1 rounded-xl border border-neutral-800">
                    <button
                      onClick={() => setAngleMode('DEG')}
                      className={`py-1.5 text-xs font-semibold rounded-lg transition ${
                        angleMode === 'DEG'
                          ? 'bg-cyan-600 text-white shadow'
                          : 'text-neutral-400 hover:text-white'
                      }`}
                    >
                      DEG (Graus 360°)
                    </button>
                    <button
                      onClick={() => setAngleMode('RAD')}
                      className={`py-1.5 text-xs font-semibold rounded-lg transition ${
                        angleMode === 'RAD'
                          ? 'bg-cyan-600 text-white shadow'
                          : 'text-neutral-400 hover:text-white'
                      }`}
                    >
                      RAD (Radianos 2π)
                    </button>
                  </div>
                </div>

                {/* Precision Slider */}
                <div>
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-neutral-400">Precisão Decimal:</span>
                    <span className="font-mono font-bold text-cyan-400">{precision} casas</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="12"
                    value={precision}
                    onChange={(e) => setPrecision(parseInt(e.target.value, 10))}
                    className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-neutral-800 rounded-lg"
                  />
                </div>

                {/* Scientific Notation Checkbox */}
                <label className="flex items-center gap-2 text-xs text-neutral-300 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={scientific}
                    onChange={(e) => setScientific(e.target.checked)}
                    className="accent-cyan-500 rounded"
                  />
                  Forçar Notação Científica Exponencial
                </label>
              </div>

              {/* History Box */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-4 flex-1 flex flex-col min-h-[300px]">
                <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
                  <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
                    <History className="h-4 w-4 text-cyan-400" />
                    Histórico ({history.length})
                  </h2>
                  {history.length > 0 && (
                    <button
                      onClick={() => setHistory([])}
                      className="text-xs text-neutral-400 hover:text-red-400 flex items-center gap-1 transition"
                      title="Limpar histórico"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Limpar
                    </button>
                  )}
                </div>

                <div className="flex-1 overflow-y-auto space-y-2.5 mt-3 pr-1 max-h-[360px]">
                  {history.length === 0 ? (
                    <div className="h-40 flex flex-col items-center justify-center text-center text-neutral-500 text-xs">
                      <Calculator className="h-8 w-8 mb-2 opacity-30" />
                      Nenhum cálculo registrado ainda.
                    </div>
                  ) : (
                    history.map((item) => (
                      <div
                        key={item.id}
                        onClick={() => {
                          setExpression(item.expression);
                          setResult(item.result);
                          setFraction(item.fraction);
                        }}
                        className="p-2.5 bg-neutral-950/70 hover:bg-neutral-800/50 border border-neutral-800/80 rounded-xl transition cursor-pointer group"
                      >
                        <div className="flex justify-between items-center text-[10px] text-neutral-500 mb-1">
                          <span className="font-mono">[{item.mode}] {item.timestamp}</span>
                          <span className="opacity-0 group-hover:opacity-100 text-cyan-400 flex items-center gap-1">
                            <RotateCcw className="h-3 w-3" /> Reutilizar
                          </span>
                        </div>
                        <div className="font-mono text-xs text-neutral-300 truncate">{item.expression}</div>
                        <div className="flex justify-between items-baseline mt-1">
                          <span className="font-mono text-sm font-bold text-cyan-400">= {item.result}</span>
                          {item.fraction && item.fraction !== item.result && (
                            <span className="text-[11px] text-neutral-400 font-mono">({item.fraction})</span>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CÁLCULO SIMBÓLICO (SYMPY) */}
        {activeTab === 'symbolic' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-2">
                <Atom className="h-6 w-6 text-cyan-400" />
                <h2 className="text-xl font-bold text-white">Computação Algébrica Simbólica (SymPy)</h2>
              </div>
              <p className="text-sm text-neutral-400">
                Calcule derivadas exatas, integrais indefinidas analíticas, resolva equações polinomiais
                e simplifique identidades matemáticas diretamente no motor simbólico Python.
              </p>

              {/* Selector */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-6">
                {[
                  { id: 'derivative', label: 'Derivada d/dx', icon: 'd/dx' },
                  { id: 'integral', label: 'Integral ∫ dx', icon: '∫' },
                  { id: 'simplify', label: 'Simplificação', icon: '≈' },
                  { id: 'solve', label: 'Resolver Equação', icon: 'x =' },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      setSymbolicOp(item.id as any);
                      if (item.id === 'derivative') setSymbolicExpr('x^3 - 4*x^2 + 5*x - 7');
                      if (item.id === 'integral') setSymbolicExpr('2*x + 3');
                      if (item.id === 'simplify') setSymbolicExpr('(x^2 - 1)/(x - 1)');
                      if (item.id === 'solve') setSymbolicExpr('2*x + 6 = 12');
                      setSymbolicResult(null);
                    }}
                    className={`p-3 rounded-xl border text-center transition font-semibold text-xs flex flex-col items-center gap-1 ${
                      symbolicOp === item.id
                        ? 'bg-cyan-600/20 border-cyan-500 text-cyan-300 shadow-md'
                        : 'bg-neutral-950 border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800/40'
                    }`}
                  >
                    <span className="font-mono text-base font-bold text-cyan-400">{item.icon}</span>
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>

              {/* Expression inputs */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 mt-5">
                <div className="sm:col-span-9">
                  <label className="text-xs text-neutral-400 block mb-1.5">Expressão Matemática:</label>
                  <input
                    type="text"
                    value={symbolicExpr}
                    onChange={(e) => setSymbolicExpr(e.target.value)}
                    placeholder="Ex: x^2 + 2*x + 1 ou sin(x)^2 + cos(x)^2"
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-2.5 text-sm font-mono text-neutral-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div className="sm:col-span-3">
                  <label className="text-xs text-neutral-400 block mb-1.5">Variável:</label>
                  <input
                    type="text"
                    value={symbolicVar}
                    onChange={(e) => setSymbolicVar(e.target.value)}
                    placeholder="x"
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-2.5 text-sm font-mono text-neutral-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <button
                onClick={handleSymbolicCalculate}
                disabled={symbolicLoading}
                className="mt-4 w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2 shadow-lg shadow-cyan-950"
              >
                {symbolicLoading ? (
                  <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Processar com SymPy
                  </>
                )}
              </button>
            </div>

            {/* Symbolic Output Box */}
            {symbolicError && (
              <div className="bg-red-950/40 border border-red-800 rounded-2xl p-4 text-red-200 text-xs flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-400 shrink-0" />
                <div>
                  <strong className="block text-red-300 font-semibold mb-1">Erro de Computação Simbólica</strong>
                  {symbolicError}
                </div>
              </div>
            )}

            {symbolicResult && (
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
                  <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                    Resultado Analítico Exato
                  </span>
                  <span className="text-xs text-neutral-400 font-mono">{symbolicResult.notes}</span>
                </div>

                <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 text-center">
                  <span className="text-xs text-neutral-500 block mb-1">Fórmula Simbólica:</span>
                  <div className="font-mono text-2xl font-bold text-cyan-300">
                    {symbolicResult.result_raw}
                  </div>
                </div>

                {symbolicResult.expanded && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-neutral-950 rounded-lg border border-neutral-800/80">
                      <span className="text-neutral-500 block mb-1">Forma Expandida:</span>
                      <span className="font-mono text-neutral-200 font-bold">{symbolicResult.expanded}</span>
                    </div>
                    <div className="p-3 bg-neutral-950 rounded-lg border border-neutral-800/80">
                      <span className="text-neutral-500 block mb-1">Forma Fatorada:</span>
                      <span className="font-mono text-neutral-200 font-bold">{symbolicResult.factored}</span>
                    </div>
                  </div>
                )}

                {symbolicResult.solutions && (
                  <div className="p-3 bg-neutral-950 rounded-lg border border-neutral-800 text-xs">
                    <span className="text-neutral-500 block mb-1">Conjunto de Soluções:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {symbolicResult.solutions.map((sol: string, idx: number) => (
                        <span key={idx} className="px-2.5 py-1 bg-cyan-950 border border-cyan-800 text-cyan-300 rounded font-mono font-bold">
                          {symbolicVar} = {sol}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: LISTAS & ESTATÍSTICA */}
        {activeTab === 'stats' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-6 w-6 text-cyan-400" />
                <h2 className="text-xl font-bold text-white">Análise Estatística de Listas</h2>
              </div>
              <p className="text-sm text-neutral-400">
                Insira uma sequência de valores numéricos para cálculo automático de média aritmética,
                somatório total, valores extremos (mín/máx) e conversão da média em fração.
              </p>

              <div className="mt-5">
                <label className="text-xs text-neutral-400 block mb-1.5">
                  Valores (separados por vírgula, espaço ou quebra de linha):
                </label>
                <textarea
                  rows={3}
                  value={statsInput}
                  onChange={(e) => setStatsInput(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-xl p-3 text-sm font-mono text-neutral-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                onClick={handleStatsCalculate}
                disabled={statsLoading}
                className="mt-4 px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2"
              >
                {statsLoading ? 'Processando...' : 'Calcular Estatísticas'}
              </button>
            </div>

            {statsResult && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 animate-fadeIn">
                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl text-center">
                  <span className="text-xs text-neutral-400 block mb-1">Média Aritmética</span>
                  <div className="text-2xl font-bold font-mono text-cyan-400">
                    {statsResult.mean.toFixed(4)}
                  </div>
                  <span className="text-[11px] text-cyan-300 font-mono mt-1 block">
                    Fração: {statsResult.fraction}
                  </span>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl text-center">
                  <span className="text-xs text-neutral-400 block mb-1">Soma Total (Σ)</span>
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    {statsResult.sum.toFixed(4)}
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-1 block">
                    {statsResult.count} elementos
                  </span>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl text-center">
                  <span className="text-xs text-neutral-400 block mb-1">Menor Valor (Mín)</span>
                  <div className="text-2xl font-bold font-mono text-amber-400">
                    {statsResult.min}
                  </div>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl text-center">
                  <span className="text-xs text-neutral-400 block mb-1">Maior Valor (Máx)</span>
                  <div className="text-2xl font-bold font-mono text-purple-400">
                    {statsResult.max}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SUÍTE DE TESTES (PYTEST) */}
        {activeTab === 'tests' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
                <div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-6 w-6 text-emerald-400" />
                    <h2 className="text-xl font-bold text-white">Bateria Automatizada pytest</h2>
                  </div>
                  <p className="text-xs text-neutral-400 mt-1">
                    57 testes automatizados cobrindo os 23 casos obrigatórios, isolamento de segurança, limites e exceções.
                  </p>
                </div>

                <button
                  onClick={handleRunTests}
                  disabled={runningTests}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2 shrink-0 shadow-lg shadow-emerald-950"
                >
                  {runningTests ? (
                    <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <Play className="h-3.5 w-3.5 fill-white" />
                      Reexecutar Testes Agora
                    </>
                  )}
                </button>
              </div>

              {/* Status summary */}
              {testResult && (
                <div className="grid grid-cols-3 gap-3 my-5">
                  <div className="p-3 bg-neutral-950 border border-neutral-800 rounded-xl text-center">
                    <span className="text-[11px] text-neutral-400 block">Total de Testes</span>
                    <span className="text-2xl font-bold font-mono text-white">{testResult.total}</span>
                  </div>
                  <div className="p-3 bg-emerald-950/40 border border-emerald-800/80 rounded-xl text-center">
                    <span className="text-[11px] text-emerald-400 block">Aprovados</span>
                    <span className="text-2xl font-bold font-mono text-emerald-400">{testResult.passed}</span>
                  </div>
                  <div className="p-3 bg-red-950/30 border border-red-800/60 rounded-xl text-center">
                    <span className="text-[11px] text-red-400 block">Falhas</span>
                    <span className="text-2xl font-bold font-mono text-red-400">{testResult.failed}</span>
                  </div>
                </div>
              )}

              {/* Terminal Logs Output */}
              <div>
                <div className="flex items-center gap-2 text-xs text-neutral-400 mb-2">
                  <Terminal className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Terminal de Saída do Pytest (Python 3.11):</span>
                </div>
                <pre className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 font-mono text-xs text-neutral-300 overflow-x-auto max-h-96 leading-relaxed select-text">
                  {testResult ? testResult.output : 'Executando testes pytest...'}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: EXPLORADOR DE CÓDIGO FONTE */}
        {activeTab === 'code' && (
          <div className="max-w-5xl mx-auto space-y-6">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
                <div>
                  <div className="flex items-center gap-2">
                    <Code2 className="h-6 w-6 text-cyan-400" />
                    <h2 className="text-xl font-bold text-white">Explorador de Código Fonte (Python)</h2>
                  </div>
                  <p className="text-xs text-neutral-400 mt-1">
                    Estrutura modular limpa projetada para estudo de engenharia de software e práticas modernas.
                  </p>
                </div>

                {/* File picker */}
                <select
                  value={selectedFile}
                  onChange={(e) => setSelectedFile(e.target.value)}
                  className="bg-neutral-950 border border-neutral-700 text-xs text-cyan-300 rounded-xl px-3 py-2 font-mono focus:outline-none"
                >
                  <option value="calculator/engine.py">calculator/engine.py (Avaliador AST Seguro)</option>
                  <option value="calculator/scientific_functions.py">calculator/scientific_functions.py (Trig & Funções)</option>
                  <option value="calculator/symbolic_operations.py">calculator/symbolic_operations.py (SymPy)</option>
                  <option value="calculator/validators.py">calculator/validators.py (Sanitização & Erros)</option>
                  <option value="app.py">app.py (Interface Streamlit)</option>
                  <option value="tests/test_engine.py">tests/test_engine.py (Testes Aritméticos)</option>
                  <option value="tests/test_scientific_functions.py">tests/test_scientific_functions.py (Testes Trig)</option>
                  <option value="tests/test_symbolic_operations.py">tests/test_symbolic_operations.py (Testes SymPy)</option>
                  <option value="requirements.txt">requirements.txt (Dependências)</option>
                  <option value="README.md">README.md (Documentação Completa)</option>
                </select>
              </div>

              {/* Code display */}
              <div className="mt-4">
                <div className="flex justify-between items-center text-xs text-neutral-400 mb-2">
                  <span className="font-mono text-cyan-400">{selectedFile}</span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(fileContent);
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    }}
                    className="flex items-center gap-1 hover:text-white transition"
                  >
                    {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                    {copied ? 'Copiado!' : 'Copiar Código'}
                  </button>
                </div>

                <pre className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 font-mono text-xs text-neutral-200 overflow-x-auto max-h-[550px] leading-relaxed select-text">
                  {fileLoading ? 'Carregando arquivo...' : fileContent}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: GUIA & STREAMLIT */}
        {activeTab === 'guide' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-6">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-cyan-400" />
                  Guia de Execução Local no Windows & Streamlit
                </h2>
                <p className="text-sm text-neutral-400 mt-1">
                  Instruções passo a passo para rodar o projeto localmente com PowerShell e Streamlit.
                </p>
              </div>

              {/* PowerShell snippet */}
              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider block mb-2">
                  Comandos no Windows PowerShell:
                </span>
                <pre className="font-mono text-xs text-neutral-300 overflow-x-auto space-y-1">
                  <code># 1. Navegue até a pasta do projeto</code><br />
                  <code className="text-cyan-300 font-bold">cd nexus-scientific-calculator</code><br /><br />
                  <code># 2. Crie o ambiente virtual Python</code><br />
                  <code className="text-cyan-300 font-bold">python -m venv venv</code><br /><br />
                  <code># 3. Habilite execução de scripts (se necessário) e ative o venv</code><br />
                  <code className="text-neutral-400">Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</code><br />
                  <code className="text-cyan-300 font-bold">.\venv\Scripts\Activate.ps1</code><br /><br />
                  <code># 4. Instale as dependências</code><br />
                  <code className="text-cyan-300 font-bold">pip install -r requirements.txt</code><br /><br />
                  <code># 5. Inicie a interface Streamlit no seu navegador</code><br />
                  <code className="text-cyan-300 font-bold">streamlit run app.py</code><br /><br />
                  <code># 6. Execute a bateria completa de 57 testes pytest</code><br />
                  <code className="text-emerald-400 font-bold">pytest -v</code>
                </pre>
              </div>

              {/* Architecture highlights */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-white">Por que o avaliador AST é superior ao `eval()`?</h3>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  Em muitas implementações didáticas, programadores iniciantes utilizam <code>eval(expressao)</code> para
                  calcular expressões. Isso é extremamente perigoso: qualquer usuário pode digitar comandos maliciosos como{' '}
                  <code>__import__('os').system('rm -rf /')</code> ou ler arquivos confidenciais do servidor.
                </p>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  No <strong>Nexus Scientific Calculator</strong>, a classe <code>SafeASTEvaluator</code> inspeciona cada nó
                  da árvore de sintaxe do Python. Somente operações aritméticas e chamadas a funções cadastradas em uma
                  lista segura são avaliadas. Qualquer comando não autorizado é bloqueado imediatamente com uma exceção{' '}
                  <code>SecurityError</code> antes de qualquer execução de código.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-900 bg-neutral-950 px-4 py-3 text-center text-xs text-neutral-500">
        Nexus Scientific Calculator • Desenvolvida para excelência acadêmica e profissional • 100% Python, Streamlit, SymPy & Pytest
      </footer>
    </div>
  );
}
