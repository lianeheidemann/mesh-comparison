# 01 — Construir ambiente reproduzível e primeira linha de base

> **Projeto novo:** implementar antes da primeira funcionalidade relevante. **Mesh Comparison: ✅ infraestrutura presente; 🟡 baseline científica e validação multiplataforma ainda incompletas.**

## Finalidade

Um agente deve poder instalar, executar, testar e reproduzir o projeto sem depender de informações que só estejam em um chat ou na máquina de quem o iniciou.

## Do zero — roteiro reutilizável

1. Criar repositório Git e decidir branches, política de PR e convenções de commits; nunca editar a branch protegida diretamente por padrão.
2. Selecionar um sistema de dependências adequado: `pyproject.toml`/uv/pip/Conda (Python), `package.json` com lock (Node), ou equivalente. Definir versão de linguagem, ferramenta de execução, plataformas suportadas e regras de atualização.
3. Criar um comando **único e documentado** para instalar e pelo menos um para executar teste rápido. Se houver configuração de GPU, torná-la opcional e detectável.
4. Criar `README.md` com objetivo, requisitos, instalação, exemplos mínimos, entradas, saídas, limitações e comandos exatos.
5. Versionar **pequena entrada de teste** e saída esperada (ou gerador determinístico). Registrar seed, parâmetros, unidade de medida, versão de algoritmo e formatos utilizados.
6. Incluir `.gitignore` para ambientes virtuais, credenciais, cache, arquivos grandes e artefatos descartáveis; fornecer `.env.example` sem segredo se necessário.
7. Executar um *smoke test* (ex.: `--help` ou teste trivial) **antes** da primeira grande implementação; documentar diferenças entre desenvolvimento local e runner de CI.
8. Criar registro de baseline com commit, comando, SO, runtime, dependências e resultado observado; atualizar apenas mediante mudança intencional de contrato.

### Exemplo concreto em Python/Conda (não genérico a outras stacks)

```bash
conda env create -f environments/environment.yml
conda activate meshEval
python -m pip install -e . --no-deps
python -m meshcomparison.geometry --help
python -m meshcomparison.perceptual --help
ruff check .
pytest -q
```

Para um **novo** repositório, substitua nomes e comandos pelo seu próprio ambiente e entrypoint. O `environments/environment-lock.yml` foi obtido em Windows **antes de PySide6/PyVista/PyVistaQt serem incluídos** e não deve ser tratado como lock universal de Linux/macOS ou garantia de execução da GUI.

## O que já está implantado no Mesh Comparison

| Item | Estado | Referência |
| --- | :---: | --- |
| Gerenciamento de ambiente Conda | ✅ | [environment.yml](../../../environments/environment.yml) |
| Dependências com versões registradas | 🟡 | [environment-lock.yml](../../../environments/environment-lock.yml) registra versões antigas do Windows, **sem a GUI** |
| Entradas e scripts executáveis documentados | ✅ | [README](../../../README.md), `data/samples/gt.stl`, `data/samples/mod.stl` e pipelines |
| Saídas de avaliação e métricas de exemplo | ✅ | [README principal](../../../README.md) e [`examples/output/`](../../../examples/output/); `output/` é pasta local ignorada pelo Git |
| Baseline sistemática com hashes e comparação de cenários | 🟡 | Exemplos existem; validação ampla documentada como pendente |
| Reprodutibilidade de toda a renderização entre plataformas | ❓ | Não comprovada; requer validação específica |
| Interface gráfica PySide6/PyVistaQt | ✅ | [Código](../../../src/meshcomparison/gui/) e [guia desktop](../../gui/README.md); funcionamento precisa ser testado em SO real |

### Verificação prática deste projeto

Em branch isolada, rodar os comandos acima. Em seguida:

```bash
python -m meshcomparison.geometry --gt data/samples/gt.stl --rm data/samples/mod.stl --out output/harness-baseline-geometry
python -m meshcomparison.perceptual --gt data/samples/gt.stl --rm data/samples/mod.stl --out output/harness-baseline-perceptual --num-views 10 --save-views 1 5 10
```

Separar essas saídas das anteriores. Não comparar a mediana de 10 vistas com resultados anteriores de 100 vistas como se os experimentos fossem equivalentes. Executar e registrar resultados reais antes de afirmar que tudo passou.

## Critérios de aceite

- [ ] Uma instalação limpa reproduz os comandos documentados.
- [ ] Pelo menos um teste automatizado e um smoke test têm resultado registrado.
- [ ] Inputs, parâmetros e outputs de referência estão identificados.
- [ ] Ambientes suportados e limitações (GPU, renderização, SO) estão descritos.
- [ ] Artefatos temporários e segredos não entram em commits.

**Próxima etapa:** [02 — Instruções e arquitetura](02-instrucoes-e-contexto.md).
