# 03 — Começar com testes e critérios de aceitação, não adicioná-los no fim

> **Projeto novo:** criar o primeiro teste antes de ampliar a primeira funcionalidade. **Mesh Comparison: 🟡 pytest está na CI, mas a validação científica abrangente continua pendente.**

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
| Smoke/CLI | Executar `--help` ou comando mínimo | Exit code e mensagem adequados |
| End-to-end | Entrada pequena → saída final | Saída completa e validável |
| Regressão | Reexecutar caso já resolvido | Alterações só com aceite explícito |

## Exemplo Mesh Comparison — usar o existente como fundação

| Verificação | Estado | Evidência ou ação |
| --- | :---: | --- |
| Ferramenta de testes integrada ao projeto | ✅ | `pytest` no [environment.yml](../../../environments/environment.yml) e [CI](../../../.github/workflows/ci.yml) |
| Execução automatizada de pytest | ✅ | Etapa `pytest -q` do workflow (configurada; não equivale a run comprovadamente verde) |
| Smoke tests dos dois CLIs | ✅ | Duas chamadas `--help` no workflow |
| Cobertura de malhas idênticas, transladadas, escaladas, incompletas, densidades distintas | 🟡 | [Plano de validação existente](../../implementation/step-by-step/10-limitacoes-evolucao.md) registra lacunas |
| Regressão controlada de ICP, Chamfer, Hausdorff e RMSE | ❓ | Precisa ser demonstrada por testes com valores esperados |
| Regressão estável de LPIPS, PSNR e SSIM multiângulo | ❓ | Requer referência de câmeras, máscara, renderizador e parâmetros |

### Casos que devem ser acrescentados neste projeto

- Identidade GT = RM → distância aproximadamente zero (dentro de tolerância explícita).
- Translação e escala → testar distâncias *antes* e *depois* do ICP, distinguindo transformações.
- Deformação localizada, buracos e densidades desiguais → verificar direção da comparação e efeito da amostragem.
- LPIPS, PSNR e SSIM → fixar views, iluminação, máscara, resolução e parâmetros, documentando variações possíveis CPU/GPU.
- Casos inválidos → erro explícito, sem sucesso silencioso; hashes e entradas preservados.

## Critérios de aceite

- [ ] Uma funcionalidade tem teste determinístico antes ou junto com sua implementação.
- [ ] Unitário, integração e smoke test estão diferenciados.
- [ ] Teste deliberadamente quebrado produz falha observável.
- [ ] Entradas, tolerâncias e saídas foram documentadas.
- [ ] Alterações em contrato exigem revisão e atualização explícita do baseline.

**Próxima etapa:** [04 — CI e proteção](04-ci-e-protecao.md).
