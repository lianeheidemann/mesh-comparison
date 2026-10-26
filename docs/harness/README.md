# Agent Harness

Conjunto de instruções, testes, CI e regras de revisão que tornam as alterações feitas com Codex, Claude Code ou outros agentes **reprodutíveis, verificáveis e rastreáveis**. Não é um agente autônomo: os ciclos continuam supervisionados.

## Estado

✅ implementado · 🟡 parcial · ❓ não demonstrado

| Elemento | Estado | Evidência / limite |
| --- | :---: | --- |
| Instruções para agentes | ✅ | [AGENTS.md](../../AGENTS.md): planejamento, testes, relato honesto de resultados e proveniência de IA nos commits |
| Definições das métricas | ✅ | [ADRs](../adr/) 0001–0003 |
| Testes (pytest) e lint (Ruff) | 🟡 | Casos sintéticos e integração por subprocesso ([inventário](../implementation/README.md)); faltam as malhas do benchmark |
| CI (GitHub Actions) | ✅ | Lint, testes e import dos pipelines em push para `main` e em PRs; não valida valores, CUDA nem a janela da GUI |
| Ambiente reproduzível | 🟡 | [environment.yml](../../environments/environment.yml) sem versões fixas; snapshots em [environment-lock.yml](../../environments/environment-lock.yml) e [requirements-windows-cu128.txt](../../environments/requirements-windows-cu128.txt) |
| Proveniência de IA | ✅ | Hook `.githooks/commit-msg` e trailer `AI-Agent` |
| Proteção de branch e revisão obrigatória | ❓ | Configuração remota não auditada |
| Ciclo supervisionado registrado (tarefa → testes → relatório) | ❓ | Ainda não documentado |

## Fluxo

<p align="center">
  <img src="assets/fluxo-harness.svg" width="75%" alt="Fluxo do Agent Harness: solicitação, agente, contexto do repositório, implementação e validação, CI, revisão humana e integração autorizada">
</p>

Solicitação com critérios de aceite → agente com permissões limitadas → leitura do contexto → alteração em branch isolada → testes locais → CI no PR → revisão humana → merge autorizado. Falhas são registradas e corrigidas sem ocultar resultados. Mudanças nas definições das métricas exigem um ADR, testes determinísticos e a comparação dos resultados antes e depois.

## Próximas ações

1. Registrar uma baseline da versão atual nas malhas do benchmark: commits, hashes, parâmetros, dependências e resultados.
2. Estender os testes para malhas reais (identidade, transformação e escala conhecidas, deformação, incompletude, densidade).
3. Rodar o [estudo de robustez](../results/robustness/README.md) nas GTs do benchmark, com LPIPS.
4. Ativar a proteção de branch com status checks e revisão obrigatória.
5. Registrar um ciclo supervisionado completo de agente, com logs, testes e relatório.

## Referências

- Anthropic — [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026): separação entre planejamento, implementação e avaliação; critérios de aceite explícitos.
- OpenAI — [Harness engineering](https://openai.com/index/harness-engineering/) (2026): documentação como fonte de verdade e legibilidade do repositório para agentes.
- Microsoft — [Understand agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses): distinção entre o modelo e o ambiente de contexto, ferramentas e execução.
- OpenAI Cookbook — [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans): planejamento rastreável de tarefas longas.
- Claude Code — [Memory](https://code.claude.com/docs/en/memory) e [Hooks](https://code.claude.com/docs/en/hooks): instruções persistentes e verificações automáticas.
- GitHub Docs — [Workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows) e [Branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule).
