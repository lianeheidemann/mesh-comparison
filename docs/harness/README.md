# Agent Harness — Mesh Comparison

> **Estado:** documentação e plano de evolução; **não** significa que um harness autônomo completo esteja implementado.
>
> **Escopo:** inventário inicial realizado na `main` em **18/10/2026**, adaptado à branch `harness-documentation-and-new-interface` (pacote `src/meshcomparison/`, pipelines por módulo executados pela GUI PySide6/PyVista). Os status refletem arquivos e configurações; execução de testes e proteção remota precisam ser comprovadas.

## 1. O que é *harness*?

Um **agent harness** é o conjunto de mecanismos ao redor de um modelo de linguagem que lhe permite executar tarefas de desenvolvimento de forma controlada: instruções e contexto, ferramentas e permissões, ambiente reproduzível, critérios de aceitação, execução de testes, revisão, observabilidade e ciclos de feedback. O modelo **não** se confunde com esse ambiente.

**Harness** não é **harmless**. *Harmless* descreve uma propriedade desejável de segurança de IA; *harness* é a estrutura técnica que coordena agentes. Ter boa documentação e CI deixa um repositório **mais preparado para agentes**, mas não prova que ele já execute ciclos autônomos.

Neste projeto, a finalidade proposta não é substituir o pipeline científico por IA: é tornar as modificações no software de comparação de malhas **reprodutíveis, rastreáveis, testáveis e seguras**, inclusive quando feitas com Codex, Claude Code ou outro agente.

### Abrangência do projeto

- **GT (ground truth)** e **RM (reconstructed mesh)** são processadas por `src/meshcomparison/geometry/pipeline.py` e `src/meshcomparison/perceptual/pipeline.py`, com entradas de exemplo em `data/samples/`.
- Open3D auxilia no alinhamento ICP; Trimesh, NumPy e SciPy dão suporte à geometria; `pyrender` gera renderizações; LPIPS, PSNR e SSIM avaliam imagens. A branch de destino também traz uma interface desktop em PySide6/PyVistaQt.
- Métricas e imagens são artefatos reproduzíveis **desde que** entradas, parâmetros, versões, câmera e ambiente sejam controlados.
- **Não alterar silenciosamente a metodologia:** mudanças em ICP, escala, amostragem de vértices/superfícies, câmera, iluminação, máscaras ou métricas exigem avaliação de regressão e atualização da documentação.

## 2. Inventário do que já existe

**Legenda:** ✅ implementado/arquivo verificado · 🟡 presente, mas com limites relevantes · ❌ ausente no escopo verificado · ❓ não demonstrado/verificação insuficiente.

| Elemento | Estado | Para que serve no harness | Evidência / ressalva |
| --- | :---: | --- | --- |
| Documentação técnica estruturada | ✅ | Contexto e mapa do repositório | [README principal](../../README.md) e [documentação](../README.md) |
| Guias de implementação passo a passo | ✅ | Decomposição de tarefas e transferência de conhecimento | [Guias existentes](../implementation/step-by-step/) |
| Ambiente Conda declarado | ✅ | Instalação do projeto e execução de tarefas/testes | [environment.yml](../../environments/environment.yml) inclui GUI, mas deixa dependências sem pin; a validação limpa da branch atual ainda precisa ser registrada |
| Dependências com versões registradas | 🟡 | Ajuda a reproduzir snapshots específicos | [environment-lock.yml](../../environments/environment-lock.yml) é um snapshot Windows CPU anterior à GUI; [requirements-windows-cu128.txt](../../environments/requirements-windows-cu128.txt) registra outro snapshot pip com GUI e PyTorch CUDA 12.8 |
| Testes com pytest | 🟡 | Permitem verificar alterações | [Testes unitários](../../tests/) para métricas de pontos, CPU/CUDA simulado, PSNR/máscaras e configuração Qt-free da GUI; **regressões end-to-end ainda pendentes** |
| Lint com Ruff | ✅ | Verifica padrões de código | Etapa `ruff check .` no [CI](../../.github/workflows/ci.yml) |
| GitHub Actions | ✅ | Automatiza verificações de CI | Push em `main` e pull requests; executa lint, testes e verificação de importação dos pipelines |
| Pipelines de processamento | ✅ | Permitem execução repetível | [Geometria](../../src/meshcomparison/geometry/pipeline.py) e [avaliação perceptual](../../src/meshcomparison/perceptual/pipeline.py) |
| Instruções específicas para agentes | ❌ | Definem regras de atuação, comandos e limites | `AGENTS.md` e `CLAUDE.md` ausentes na raiz da `main` auditada |
| Ciclo autônomo de correção e validação | ❓ | Permite ao agente testar, diagnosticar, corrigir e revalidar | Não demonstrado por arquivos auditados; CI **não** equivale a agente autônomo |
| Testes de regressão científica abrangentes | 🟡 | Protegem a validade das métricas | [Plano de validação](../implementation/step-by-step/10-limitacoes-evolucao.md) separa casos unitários existentes dos cenários de malhas e renderização ainda pendentes |
| Proteção de branch e revisões obrigatórias | ❓ | Impede merge sem critérios e aprovação | Configuração remota do GitHub não auditada |
| Rastro de tarefas/execuções de agente | ❓ | Documenta decisões, evidências e falhas | Não demonstrado no escopo verificado |
| Interface desktop PySide6/PyVistaQt | ✅ | Permite inspecionar modelos e resultados | [Código](../../src/meshcomparison/gui/main_window.py) e [guia de uso](../gui/README.md); teste gráfico real ainda não documentado |

> Os ícones registram **evidência de arquivos/configuração**, não porcentagens de conclusão. Há testes unitários reais no diretório `tests/`, mas eles não asseguram que todos os cenários científicos estejam testados; a execução e o resultado de cada workflow também devem ser conferidos no GitHub Actions.

## 3. Fluxo desejável

O diagrama abaixo representa um **fluxo-alvo**, não uma funcionalidade que já está rodando automaticamente.

<p align="center">
  <img src="assets/fluxo-harness.svg" width="75%" alt="Fluxo desejável do Agent Harness: solicitação, agente, contexto do repositório, implementação e validação, CI, revisão humana e integração autorizada. O fluxo retorna à implementação quando há falhas.">
</p>

Fluxo recomendado: **solicitação com critérios de aceitação → agente com permissões limitadas → leitura do contexto do repositório → alteração em branch isolada → validação local → CI no pull request → revisão humana → merge autorizado**. Quando os testes falharem, registrar a falha e iterar sem ocultar resultados; quando houver ambiguidade científica, pedir decisão humana.

**Base metodológica para agentes:** antes de alterar os algoritmos de comparação de malhas, consultar os [Contratos científicos (GT × RM)](CONTRATOS-CIENTIFICOS.md), derivados da inspeção do [código original de Thiago Figueiro Ribeiro](https://github.com/ThiagoFigueiroRibeiro/MeshComparison). O documento distingue comportamentos herdados, diferenças de parâmetros e verificações que ainda precisam de testes.

## 4. O que falta para um harness mais completo?

Não existe uma certificação universal de “harness completo”. Neste projeto, adotamos a seguinte **definição operacional de pronto**, sem exigir um orquestrador novo:

1. **Instruções versionadas** e breves (`AGENTS.md`; opcionalmente integração Claude Code), com regras, comandos e limites.
2. **Contexto navegável**: mapa de arquitetura, contratos das métricas, documentação de decisões (ADRs) e procedimento de desenvolvimento.
3. **Ambiente verificável**: dependências consistentes, entradas de teste pequenas e execução dos dois pipelines em ambientes suportados.
4. **Critérios objetivos**: testes unitários, integração, propriedades geométricas, regressão de renderização e tolerâncias explícitas.
5. **Gates de CI**: status checks, proteção de branch, revisão de pull requests e logs reproduzíveis.
6. **Ciclo de agente assistido**: receber tarefa, consultar contexto, planejar, alterar, rodar checks, diagnosticar falhas, revalidar e produzir relatório verificável; sem merge automático sem autorização explícita.
7. **Rastreabilidade e segurança**: menor privilégio, isolamento de ambiente, sem segredos em logs, trilha de decisões, aprovações humanas para ações sensíveis.
8. **Avaliação recorrente do processo**: medir taxa de êxito das tarefas, falhas reabertas, regressões, manutenção da documentação e qualidade dos artefatos.

### Arquitetura recomendada

| Camada | Ferramentas / artefatos | Responsabilidade |
| --- | --- | --- |
| Motor de execução do agente | Codex ou Claude Code | Decidir chamadas de ferramentas **sob permissões definidas**; não é parte do pipeline científico |
| Orientação | `AGENTS.md`, documentação e ADRs | Instruções curtas e fonte de verdade |
| Execução | Conda, interface gráfica e API Python | Rodar o aplicativo e produzir artefatos |
| Verificação | Ruff, pytest, cenários de malhas e validações de saída | Detectar erros e regressões |
| Integração | Git, PR, GitHub Actions, regras de branch | Impedir integração de mudanças não verificadas |
| Evidências | Resultados de testes, logs sem segredos e relatório de PR | Sustentar aprovação ou correção |

**Importante:** usar um agente com um harness próprio (Codex/Claude Code) não requer implementar outro motor de agentes. O trabalho prioritário é aumentar a **confiabilidade verificável deste repositório**.

## 5. Guia completo: implantação desde o primeiro commit

O [**guia de implantação do Harness**](step-by-step/README.md) agora atende a **dois cenários**:

- **Projeto novo:** especificar arquitetura, contexto do agente, ambiente, testes, CI, segurança e avaliação desde a primeira versão — sem depender de adaptações posteriores.
- **Projeto existente (Mesh Comparison):** reutilizar os componentes já implantados e executar apenas o que está parcial, ausente ou não comprovado.

**Importante:** a existência de uma ferramenta (como `pytest` ou GitHub Actions) não significa que o harness supervisionado esteja integralmente operacional. A matriz da documentação separa **status das funcionalidades** e **critérios de conclusão das etapas**.

| Ordem | Etapa e uso |
| --- | --- |
| 00 | [Planejamento e arquitetura desde o zero](step-by-step/00-planejamento-e-arquitetura.md) |
| 01 | [Ambiente reproduzível e baseline](step-by-step/01-auditoria-e-linha-de-base.md) |
| 02 | [Instruções e contexto dos agentes](step-by-step/02-instrucoes-e-contexto.md) |
| 03 | [Testes e regressões desde a primeira funcionalidade](step-by-step/03-testes-e-regressoes.md) |
| 04 | [CI, revisão e proteção de branches](step-by-step/04-ci-e-protecao.md) |
| 05 | [Ciclo supervisionado de agentes e segurança](step-by-step/05-ciclo-assistido-e-seguranca.md) |
| 06 | [Avaliação, evidências e manutenção](step-by-step/06-evidencias-e-aceite.md) |
| 07 | [Modelo reutilizável para futuros projetos](step-by-step/07-modelo-reutilizavel.md) |

A documentação informa, em cada etapa, **como construir do zero, o que já existe no Mesh Comparison, o que falta e como verificar a conclusão**.

## 6. Referências e leitura complementar

Todas as referências técnicas utilizadas neste plano foram organizadas no catálogo:

**[Referências sobre Agent Harness — docs/harness/REFERENCIAS.md](REFERENCIAS.md)**

O arquivo reúne materiais da **Anthropic**, **OpenAI**, **VS Code / Microsoft**, **Claude Code** e **GitHub**, incluindo o artigo da OpenAI em português e o material da Anthropic sobre *long-running application development*.

O **CanIRun.ai** está separado como recurso **complementar para IA local**: suas estimativas de hardware podem ser úteis se forem estudados agentes locais, mas não são evidência de implementação de um harness.

As referências apresentam **boas práticas e possibilidades**, não garantem que uma funcionalidade já esteja habilitada no repositório. Reavaliar recomendações em novas versões de agentes, GitHub Actions e bibliotecas.
