/**
 * Nexus Scientific Calculator - Full-Stack Express Server & Python Bridge
 */

import express, { Request, Response } from 'express';
import { createServer as createViteServer } from 'vite';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const PROJECT_DIR = path.resolve(__dirname, 'nexus-scientific-calculator');

app.use(express.json());

// API: Executa o motor de cálculo Python seguro via AST
app.post('/api/calculate', (req: Request, res: Response) => {
  const { expression, angle_mode = 'DEG', precision = 6, scientific = false, last_ans = 0 } = req.body;

  if (!expression || typeof expression !== 'string') {
    return res.status(400).json({ success: false, error: 'Expressão matemática não fornecida.' });
  }

  // Prepara script Python inline chamando o pacote calculator
  const pyCode = `
import sys, json
sys.path.insert(0, '${PROJECT_DIR}')
from calculator.engine import CalculationEngine
from calculator.validators import CalculationError

try:
    engine = CalculationEngine(angle_mode='${angle_mode}', precision=${precision})
    engine.last_answer = ${Number(last_ans) || 0}
    result = engine.evaluate("""${expression.replace(/"/g, '\\"')}""", scientific_notation=${scientific ? 'True' : 'False'})
    print(json.dumps({
        "success": True,
        "value": result.value,
        "formatted": result.formatted,
        "fraction": result.fraction,
        "mode": result.angle_mode,
        "cleaned": result.cleaned_expression
    }))
except CalculationError as ce:
    print(json.dumps({
        "success": False,
        "error_type": ce.__class__.__name__,
        "error": ce.message
    }))
except Exception as exc:
    print(json.dumps({
        "success": False,
        "error_type": "UnexpectedError",
        "error": str(exc)
    }))
`;

  exec(`python3 -c "${pyCode.replace(/"/g, '\\"')}"`, { cwd: PROJECT_DIR }, (error, stdout, stderr) => {
    try {
      const output = JSON.parse(stdout.trim());
      return res.json(output);
    } catch {
      return res.status(500).json({
        success: false,
        error: stderr || stdout || 'Falha ao processar cálculo no motor Python.',
      });
    }
  });
});

// API: Executa operações algébricas simbólicas com SymPy
app.post('/api/symbolic', (req: Request, res: Response) => {
  const { operation, expression, variable = 'x' } = req.body;

  if (!expression) {
    return res.status(400).json({ success: false, error: 'Expressão simbólica não fornecida.' });
  }

  const pyCode = `
import sys, json
sys.path.insert(0, '${PROJECT_DIR}')
from calculator.symbolic_operations import (
    symbolic_derivative, symbolic_integral, symbolic_simplify, symbolic_solve, SymbolicMathError
)
from calculator.validators import CalculationError

op = '${operation}'
expr = """${expression.replace(/"/g, '\\"')}"""
var = '${variable}'

try:
    if op == 'derivative':
        data = symbolic_derivative(expr, var)
    elif op == 'integral':
        data = symbolic_integral(expr, var)
    elif op == 'simplify':
        data = symbolic_simplify(expr)
    elif op == 'solve':
        data = symbolic_solve(expr, var)
    else:
        raise ValueError(f"Operação desconhecida: {op}")

    print(json.dumps({"success": True, "data": data}))
except CalculationError as ce:
    print(json.dumps({"success": False, "error": ce.message}))
except Exception as exc:
    print(json.dumps({"success": False, "error": str(exc)}))
`;

  exec(`python3 -c "${pyCode.replace(/"/g, '\\"')}"`, { cwd: PROJECT_DIR }, (error, stdout, stderr) => {
    try {
      const output = JSON.parse(stdout.trim());
      return res.json(output);
    } catch {
      return res.status(500).json({
        success: false,
        error: stderr || stdout || 'Falha na computação simbólica.',
      });
    }
  });
});

// API: Executa estatísticas de lista
app.post('/api/stats', (req: Request, res: Response) => {
  const { numbers } = req.body;
  if (!Array.isArray(numbers) || numbers.length === 0) {
    return res.status(400).json({ success: false, error: 'Lista de números vazia ou inválida.' });
  }

  const pyCode = `
import sys, json
sys.path.insert(0, '${PROJECT_DIR}')
from calculator.scientific_functions import mean_func, sum_func, min_func, max_func, to_fraction

nums = ${JSON.stringify(numbers)}
try:
    m = mean_func(nums)
    s = sum_func(nums)
    min_v = min_func(nums)
    max_v = max_func(nums)
    frac = to_fraction(m)
    print(json.dumps({
        "success": True,
        "mean": m,
        "sum": s,
        "min": min_v,
        "max": max_v,
        "fraction": frac,
        "count": len(nums)
    }))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
`;

  exec(`python3 -c "${pyCode.replace(/"/g, '\\"')}"`, { cwd: PROJECT_DIR }, (error, stdout, stderr) => {
    try {
      const output = JSON.parse(stdout.trim());
      return res.json(output);
    } catch {
      return res.status(500).json({
        success: false,
        error: stderr || stdout || 'Falha ao processar estatísticas.',
      });
    }
  });
});

// API: Executa a suíte de testes pytest em tempo real
app.get('/api/run-tests', (req: Request, res: Response) => {
  exec('PYTHONPATH=. pytest tests -v --no-header', { cwd: PROJECT_DIR }, (error, stdout, stderr) => {
    const output = stdout || stderr;
    const passedMatch = output.match(/(\d+)\s+passed/);
    const failedMatch = output.match(/(\d+)\s+failed/);
    const passed = passedMatch ? parseInt(passedMatch[1], 10) : 0;
    const failed = failedMatch ? parseInt(failedMatch[1], 10) : 0;

    return res.json({
      success: !error || failed === 0,
      output,
      passed,
      failed,
      total: passed + failed,
    });
  });
});

// API: Lê arquivos do projeto para o Code Explorer
app.get('/api/file-content', (req: Request, res: Response) => {
  const filePath = req.query.path as string;
  if (!filePath) {
    return res.status(400).json({ error: 'Caminho do arquivo não fornecido.' });
  }

  const resolved = path.resolve(PROJECT_DIR, filePath);
  if (!resolved.startsWith(PROJECT_DIR)) {
    return res.status(403).json({ error: 'Acesso negado fora do repositório.' });
  }

  if (!fs.existsSync(resolved)) {
    return res.status(404).json({ error: 'Arquivo não encontrado.' });
  }

  const content = fs.readFileSync(resolved, 'utf-8');
  return res.json({ path: filePath, content });
});

async function startServer() {
  // Inicializa o Vite como middleware para o frontend React
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });

  app.use(vite.middlewares);

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Nexus Scientific Calculator server rodando na porta ${PORT}`);
  });
}

startServer();
