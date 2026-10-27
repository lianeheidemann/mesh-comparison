# 03 — Começar com testes e critérios de aceitação, não adicioná-los no fim

> **Projeto novo:** criar o primeiro teste antes de ampliar a primeira funcionalidade. **Mesh Comparison: 🟡 pytest está na CI e os testes de aceitação T-01–T-07 e T-10 foram implementados; T-08 e T-09 continuam pendentes.**

## Por que é parte essencial do harness?

Um agente que apenas escreve código e recebe mensagens do tipo “ok” não dispõe de feedback confiável. O harness precisa de **oráculos de teste**, exemplos e condições objetivas para detectar implementações erradas ou regressões.

## Do zero — roteiro passo a passo

1. Para cada funcionalidade, especificar entradas, saídas, condições de erro e invariantes **antes da implementação**.
2. Criar testes **unitários** para comportamento determinístico e **de integração** para módulos e dependências. Separar verificações caras ou que dependem de GPU, rede, banco ou janela gráfica.
3. Criar um exemplo mínimo de ponta a ponta que execute sem intervenção humana e deixe claro seu código de saída.
4. Definir tolerâncias, seeds, arredondamento, hardware e ambiente relevantes. Uma métrica científica não deve ser validada por comparação visual subjetiva.
5. Adicionar um caso de falha deliberada para provar que o teste acusa problemas; evitar testes que sempre passam ou capturam/ignoram todas as exceções.
6. Salvar pequenos resultados de referência com **proveniência** (algoritmo, versão, entrada e parâmetros). Evitar snapshots frágeis a SO, driver ou renderização.
7. Quando o modelo encontrar erro, deve reportar causa, alteração realizada, teste repetido e evidência. **Não reduzir tolerâncias nem remover teste para esconder regressão.**
8. Exigir testes + documentação no PR de cada nova feature; depois conectar essas verificações ao CI na etapa 04.

### Conjunto mínimo recomendado para projetos novos

| Nível | Exemplo genérico | Condição de aprovação |
| --- | --- | --- |
| Unitário | Função pura com casos válidos e inválidos | Resultado esperado e falhas previsíveis |
| Integração | Dois componentes trocam dados | Contrato de entrada/saída preservado |
| Smoke | Importar o módulo ou executar um comando mínimo | Exit code e mensagem adequados |
| End-to-end | Entrada pequena → saída final | Saída completa e validável |
| Regressão | Reexecutar caso já resolvido | Alterações só com aceite explícito |

## Exemplo Mesh Comparison — usar o existente como fundação

| Verificação | Estado | Evidência ou ação |
| --- | :---: | --- |
| Ferramenta de testes integrada ao projeto | ✅ | `pytest` no [environment.yml](../../../environments/environment.yml) e [CI](../../../.github/workflows/ci.yml) |
| Execução automatizada de pytest | ✅ | Etapa `pytest -q` do workflow (configurada; não equivale a run comprovadamente verde) |
| Smoke de importação dos pipelines e do worker | ✅ | Uma chamada `python -c "import ..."` no workflow; o worker também é testado em `tests/test_worker.py` |
| Testes de métricas geométricas de pontos | ✅ | [`tests/test_geometry.py`](../../../tests/test_geometry.py) testa nuvens idênticas, Chamfer, Hausdorff e RMSE para deslocamento simples |
| Transformações de bbox, MSE e subsampling | ✅ | [`tests/test_common.py`](../../../tests/test_common.py); não comprova ICP end-to-end |
| Helpers perceptuais (PSNR, máscaras, estatísticas) | ✅ | [`tests/test_perceptual.py`](../../../tests/test_perceptual.py) |
| Device e parâmetros de interface | ✅ | [`tests/test_device.py`](../../../tests/test_device.py) usa simulações; [`tests/test_gui_config.py`](../../../tests/test_gui_config.py) verifica comandos/configuração, **não uma janela real** |
| Cenários de malhas idênticas, rígidas, escaladas, deformadas, incompletas e densidades distintas (T-01–T-06) | ✅ | [`tests/test_scientific_contracts.py`](../../../tests/test_scientific_contracts.py), com valores esperados derivados à mão ou de transformações controladas |
| PSNR legado (T-07) e entradas inválidas (T-10) | ✅ | [`tests/test_scientific_contracts.py`](../../../tests/test_scientific_contracts.py) |
| Comparação original × atual (T-09) | ❌ | Exige executar o [código original](https://github.com/ThiagoFigueiroRibeiro/MeshComparison) com entradas, parâmetros e versões idênticos |
| Regressão do fluxo multivista LPIPS/PSNR/SSIM | ❓ | Testes integrados com renderização e modelos reais ainda precisam ser demonstrados |

### Casos que devem ser acrescentados neste projeto

- [x] **Identidade em malhas reais** GT = RM, distância zero e execução do pipeline geométrico completo (T-01).
- [x] **Translação/rotação e escala** em malhas, com MSE *antes* e *depois* do ICP, gatilho estritamente maior que o limiar e escala recuperada pelo ICP de similaridade (T-02, T-03, CC-04).
- [x] Ordem dos vértices, deformação localizada, região ausente e densidades desiguais → direção da comparação e efeito da amostragem (T-04–T-06).
- [x] PSNR legado com erro conhecido e diferença de `10*log10(3)` dB para a convenção usual (T-07).
- [x] Casos inválidos → FBX, arquivo inexistente, GT degenerada e máscara vazia com erro explícito (T-10).
- [ ] LPIPS e SSIM com renderização real → fixar views, iluminação, máscara, resolução e parâmetros, documentando variações possíveis CPU/GPU (T-08).
- [ ] Saídas do original × atual com entradas, parâmetros e versões idênticos (T-09).

## Critérios de aceite

- [ ] Uma funcionalidade tem teste determinístico antes ou junto com sua implementação.
- [ ] Unitário, integração e smoke test estão diferenciados.
- [x] Teste deliberadamente quebrado produz falha observável (localmente; ainda não demonstrado na CI).
- [x] Entradas, tolerâncias e saídas foram documentadas (cabeçalho de `tests/test_scientific_contracts.py`).
- [ ] Alterações em contrato exigem revisão e atualização explícita do baseline.

## Evidência de execução (27/10/2026)

Execução local, **não** na CI: Linux, Python 3.12, NumPy 2.5.4, SciPy 1.18.1, Trimesh 5.2.0, Open3D 0.20.0, pyrender 0.1.45 com `PYOPENGL_PLATFORM=egl`; sem `torch`/`lpips` instalados.

| Comando | Resultado |
| --- | --- |
| `pytest -q tests/test_scientific_contracts.py` | 17 passaram |
| `pytest -q` (suíte completa) | 56 passaram; 1 falhou por ambiente (`test_perceptual_outputs_match_the_original_schema`: `lpips` ausente) |
| `ruff check .` | sem erros |

**Falha proposital:** cada mutação abaixo foi aplicada temporariamente ao código, os novos testes foram executados e o código foi restaurado. Todas foram detectadas:

| Mutação | Contrato | Testes que falharam |
| --- | --- | --- |
| PSNR dividido por `3N` | CC-09 | 1 |
| Gatilho do ICP `>=` em vez de `>` | CC-04 | 1 |
| Chamfer como média de distâncias quadradas | CC-05 | 1 |
| ICP sem escala uniforme | CC-04 | 1 |
| Normalização de cada malha pela própria diagonal | CC-02 | 4 |
| Saturação do heatmap no P99 | CC-06 | 1 |

Tolerâncias: STL grava coordenadas em `float32`, então o MSE normalizado após o ICP é comparado com `1e-10`, seis ordens de grandeza abaixo do limiar padrão `1e-4`; relações exatas (conversão de unidades, ordem dos vértices) usam `rel=1e-12`. Esses testes caracterizam a implementação **atual**; não comprovam equivalência com o código original (T-09).

**Próxima etapa:** [04 — CI e proteção](04-ci-e-protecao.md).
