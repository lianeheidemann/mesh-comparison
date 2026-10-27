# Agent Harness — guia de implementação desde o início

> **Objetivo:** manual reutilizável para criar **novos projetos já preparados para desenvolvimento com agentes LLM**, com exemplos reais do **Mesh Comparison**. O mesmo roteiro serve para atualizar projetos existentes **sem reimplementar o que já funciona**.
>
> **Inventário Mesh Comparison:** auditoria inicial da `main` e adequação aos arquivos da branch `harness-documentation-and-new-interface` em 18/10/2026. Os status refletem **arquivos/configuração observados**, não execução atual comprovada, cobertura completa nem garantia de segurança.
>
> **Atualização 27/10/2026:** instruções de agentes (`AGENTS.md`/`CLAUDE.md`) já versionadas; testes de aceitação T-01–T-07 e T-10 dos [contratos científicos](../CONTRATOS-CIENTIFICOS.md) implementados em [`tests/test_scientific_contracts.py`](../../../tests/test_scientific_contracts.py) e executados localmente (ver [etapa 03](03-testes-e-regressoes.md#evidência-de-execução-27102026)).

## Como usar

**Projeto novo (greenfield):** seguir **00 → 06 desde o primeiro commit**; utilizar 07 como checklist e modelo para outros repositórios. Implemente uma pequena funcionalidade vertical, com instruções, testes, CI e revisão desde o começo — não crie todo o produto para só então instalar controles.

**Projeto existente (caso Mesh Comparison):** começar pela matriz abaixo, reaproveitar ✅, completar 🟡 e investigar ❓ antes de declarar o harness operacional. Não tratar ausência de evidência como ausência definitiva.

**Legenda:** ✅ recurso existente/verificado em arquivo · 🟡 parcialmente coberto · ❌ ausente no escopo auditado · ❓ não confirmado/depende de execução ou configuração remota. **Status de recurso ≠ conclusão integral de etapa.**

## Mapa das etapas: novo projeto e exemplo real

| Etapa | O que implantar desde o início | O que o Mesh Comparison já possui | Lacunas atuais |
| --- | --- | --- | --- |
| [00 — Planejamento e arquitetura](00-planejamento-e-arquitetura.md) | Escopo, critérios, invariantes, permissões, decisões e fluxo de PR | ✅ Objetivo, pipelines e documentação de domínio | 🟡 Contratos de regressão; ❓ ADRs e políticas de agente |
| [01 — Ambiente e baseline](01-auditoria-e-linha-de-base.md) | Git, dependências/lock, comandos e primeira saída conhecida | ✅ Ambiente Conda declarado, pipelines modulares e resultados exemplares · 🟡 snapshots Windows distintos (lock CPU pré-GUI e pins pip CUDA 12.8 com GUI) | 🟡 Baseline sistemática; ❓ reprodução multiplataforma |
| [02 — Instruções e contexto](02-instrucoes-e-contexto.md) | `AGENTS.md`, arquitetura, ADRs, templates e regras no primeiro dia | ✅ READMEs, documentação técnica, [`AGENTS.md`](../../../AGENTS.md) e [`CLAUDE.md`](../../../CLAUDE.md) | ❓ Aplicação das instruções em tarefa real; ❓ ADRs |
| [03 — Testes e regressões](03-testes-e-regressoes.md) | Testes unitários, integração, smoke e regressão desde a primeira feature | ✅ pytest/ruff, testes unitários de métricas, device e configuração da GUI · verificação de importação no CI · testes de aceitação T-01–T-07 e T-10 | 🟡 T-08 (renderização/LPIPS/SSIM) e T-09 (original × atual) pendentes |
| [04 — CI e proteção](04-ci-e-protecao.md) | Workflow em PR, checks obrigatórios e aprovação humana | ✅ GitHub Actions com Ruff, pytest e smoke tests | ❌ Pipeline completo não roda na CI; ❓ proteção da `main` |
| [05 — Ciclo de agente](05-ciclo-assistido-e-seguranca.md) | Runtime supervisionado, escopo, ferramentas, feedback e handoff | ✅ Pipelines, documentação e CI podem servir como ferramentas/feedback | ❓ Loop de agente, permissões e checkpoints demonstrados |
| [06 — Avaliação e manutenção](06-evidencias-e-aceite.md) | Evidências de PR, avaliações de tarefas e manutenção do processo | ✅ Documentação e métricas de exemplo já registradas | ❓ Evals do agente, integração supervisionada comprovada |
| [07 — Modelo reutilizável](07-modelo-reutilizavel.md) | Estrutura de repositório, contrato de tarefa e checklist para novos projetos | ✅ Este documento pode ser reutilizado | Não é uma funcionalidade implantada automaticamente |

## Recursos já implantados — não repetir do zero

Este checklist registra **a existência de componentes** no Mesh Comparison. Ele não afirma que um harness completo já está funcionando.

- [x] README principal com propósito, instalação, comandos e saídas ([fonte](../../../README.md)).
- [x] Guia técnico de implementação ([docs/implementation](../../implementation/README.md)).
- [x] Ambiente Conda e dependências declaradas ([environment.yml](../../../environments/environment.yml)).
- [x] Snapshot do ambiente Windows anterior à GUI ([environment-lock.yml](../../../environments/environment-lock.yml)) e snapshot pip separado com PySide6/PyVista/PyVistaQt e PyTorch CUDA 12.8 ([requirements-windows-cu128.txt](../../../environments/requirements-windows-cu128.txt)).
- [x] Dois pipelines executáveis de domínio ([geométrico](../../../src/meshcomparison/geometry/pipeline.py), [perceptual](../../../src/meshcomparison/perceptual/pipeline.py)).
- [x] Pipelines `meshcomparison.geometry` / `meshcomparison.perceptual` executados pela GUI PySide6/PyVistaQt (processos filhos via `meshcomparison.gui.worker`) ([pyproject.toml](../../../pyproject.toml)).
- [x] Configuração de `ruff check .` no [GitHub Actions](../../../.github/workflows/ci.yml).
- [x] Configuração de `pytest -q` no [GitHub Actions](../../../.github/workflows/ci.yml) e testes existentes em [`tests/`](../../../tests/), sem validação end-to-end completa.
- [x] Configuração de smoke test de importação (pipelines e worker) no CI.
- [x] Resultados de exemplo e métricas registrados no [README](../../../README.md), como execução histórica.
- [x] GUI PySide6/PyVistaQt ([código](../../../src/meshcomparison/gui/main_window.py)) — execução gráfica em ambiente real ainda não comprovada nesta auditoria.
- [x] Documentação de Agent Harness e [bibliografia](../REFERENCIAS.md), com diagrama de fluxo ([visão geral](../README.md)).
- [x] Instruções para agentes [`AGENTS.md`](../../../AGENTS.md) e [`CLAUDE.md`](../../../CLAUDE.md), remetendo aos [contratos CC-01–CC-13](../CONTRATOS-CIENTIFICOS.md).
- [x] Testes de aceitação T-01–T-07 e T-10 com valores esperados conhecidos ([`tests/test_scientific_contracts.py`](../../../tests/test_scientific_contracts.py)).

## Pontos a implementar, ampliar ou verificar

- [ ] Especificar um contrato de tarefa/invariantes e ADRs para mudanças críticas.
- [ ] Validar `AGENTS.md`/`CLAUDE.md` (já criados) em uma tarefa real, registrando se as regras foram seguidas.
- [ ] Executar e registrar baseline de testes, hashes e métricas em ambiente limpo.
- [x] **Ampliar** os testes unitários para malhas idênticas, transladadas/rotacionadas, escaladas, deformadas, incompletas e com densidades distintas (T-01–T-06), PSNR legado (T-07) e entradas inválidas (T-10).
- [ ] Criar verificações end-to-end para os outputs perceptuais (T-08: câmeras, PNGs, LPIPS/SSIM com tolerâncias CPU/GPU) e comparar original × atual com entradas idênticas (T-09).
- [ ] Testar **na CI** uma falha proposital (localmente, seis mutações deliberadas já foram detectadas pelos novos testes; ver [etapa 03](03-testes-e-regressoes.md#evidência-de-execução-27102026)).
- [ ] **Verificar** se branch protection/rulesets e aprovações estão realmente habilitados no GitHub.
- [ ] Demonstrar ciclo de agente com erro → diagnóstico → correção → revalidação, logs e limites de acesso.
- [ ] Avaliar tarefas de agente com métricas e evidência em PRs.

Os pontos acima misturam **pendências** e **itens não confirmados**. Consulte a coluna de status nas etapas antes de agir; proteções remotas, por exemplo, não podem ser inferidas de arquivos locais.

## Fluxo que um projeto novo deve ter desde o primeiro dia

1. **Definir o problema:** especificação curta e teste de aceite ([00](00-planejamento-e-arquitetura.md)).
2. **Inicializar o repositório:** ambiente, `README.md`, arquivo de instruções e projeto mínimo ([01](01-auditoria-e-linha-de-base.md), [02](02-instrucoes-e-contexto.md)).
3. **Implementar uma feature pequena:** com testes e saída verificável ([03](03-testes-e-regressoes.md)).
4. **Criar PR e executar CI:** estabelecer checks e revisão antes de escalar o desenvolvimento ([04](04-ci-e-protecao.md)).
5. **Operar o agente com controle:** escopo, permissões, checkpoint e feedback real de ferramentas ([05](05-ciclo-assistido-e-seguranca.md)).
6. **Registrar resultado e evoluir:** critérios de aceite, falhas e melhorias do harness ([06](06-evidencias-e-aceite.md)).

### Critério para marcar uma etapa concluída

Uma etapa **não está concluída** só porque o arquivo ou ferramenta existe. A conclusão exige: (a) artefato versionado; (b) comando/uso demonstrado em ambiente controlado; (c) resultados/evidências registrados; (d) limites conhecidos; e (e) revisão humana quando necessária. Não inventar execuções de CI nem declarar regras remotas sem inspeção real.

**Leituras:** [README principal do Harness](../README.md) · [Referências oficiais e complementares](../REFERENCIAS.md) · [Modelo reutilizável](07-modelo-reutilizavel.md).
