# Implementação — validação sistemática e plano de evolução

Este documento reúne o que já está testado no pacote `src/meshcomparison/`, o que ainda precisa ser validado e as evoluções previstas. A estrutura dos módulos está resumida na [visão geral da documentação](../README.md#user-content-entrada-rápida-para-a-versão-atual).

## 1. O que já está testado

Os testes abaixo **existem no repositório**; isso não equivale a afirmar que foram executados nesta revisão nem que têm cobertura completa.

| Componente | Evidência existente | Limite |
| --- | --- | --- |
| Erros geométricos entre pontos | [`tests/test_geometry.py`](../../tests/test_geometry.py): nuvens idênticas e deslocamento de um ponto | Não exercita pipeline de malhas completo nem superfície contínua |
| MSE, amostragem e transformação de caixa | [`tests/test_common.py`](../../tests/test_common.py) | Não comprova convergência robusta de ICP em todas as situações |
| Device CPU/CUDA e avisos | [`tests/test_device.py`](../../tests/test_device.py) com simulações (*mocks*) | Não confirma GPU real nem execução de LPIPS em CUDA |
| PSNR e máscaras | [`tests/test_perceptual.py`](../../tests/test_perceptual.py) | Não confirma renderização/LPIPS/SSIM em cenário multivista completo |
| Preparo comum e exportação alinhada | [`tests/test_prepare.py`](../../tests/test_prepare.py) | Não cobre todas as condições geométricas nem a convergência robusta de ICP |
| Configuração e worker da GUI | [`tests/test_gui_config.py`](../../tests/test_gui_config.py), [`tests/test_worker.py`](../../tests/test_worker.py) | Worker exercitado em subprocesso para geometria; não abre janela nem valida Qt/PyVistaQt |
| Leitura de resultados para o viewer | [`tests/test_outputs.py`](../../tests/test_outputs.py) | Não valida a interação real com o viewer 3D |
| Escala do heatmap (percentil 95) | [`tests/test_heatmap.py`](../../tests/test_heatmap.py) | Não valida a imagem renderizada do heatmap |
| Reuso do renderer offscreen | [`tests/test_rendering.py`](../../tests/test_rendering.py): renderer reutilizado igual a renders avulsos | Ignorado (*skip*) sem OpenGL offscreen; não compara com o renderer do código original |
| Galeria de imagens da GUI | [`tests/test_gallery.py`](../../tests/test_gallery.py): pareamento GT/RM por vista e ordenação | Lógica sem Qt; não abre a janela |
| Métricas `evaluation-v2` (CC-14 a CC-17) | [`tests/test_metrics_v2.py`](../../tests/test_metrics_v2.py): amostragem reprodutível e proporcional à área, deslocamento paralelo conhecido (CD = HD95 = δ; F-score em degrau), HD95 robusto a *outliers*, precisão/cobertura, regiões, escala do ICP, visibilidade de um cubo; PSNR padrão em [`tests/test_perceptual.py`](../../tests/test_perceptual.py) | Casos sintéticos; não valida em malhas reais de TripoSR/SF3D/InstantMesh nem a convenção de eixos de cada conjunto de dados |
| Normal consistency, curva F(τ) e estudo de robustez (CC-18) | [`tests/test_robustness.py`](../../tests/test_robustness.py): normais amostradas, NC = cos θ para planos inclinados, F(τ) monotônica e AUC em [0,1], permutação sem efeito, re-triangulação que altera o legado e não o v2, perturbações monotônicas, remoção que reduz a cobertura | Uma GT sintética por teste; os números do estudo em [`docs/results/robustness`](../results/robustness/README.md) usam uma única GT e não incluem LPIPS |
| Schema dos CSVs | [`tests/test_output_schema.py`](../../tests/test_output_schema.py): executa os pipelines em subprocesso e compara colunas com `examples/output/metrics/` | Verifica estrutura, não valores científicos |

O [workflow de CI](../../.github/workflows/ci.yml) chama Ruff, pytest e uma verificação de importação dos pipelines e do worker. Pelo pytest, `test_output_schema.py` e `test_worker.py` executam os pipelines em subprocesso com configuração reduzida (320 × 240 px; 2 vistas perceptuais em CPU) para verificar a estrutura das saídas; o CI **não** valida valores científicos, não roda a configuração padrão (100 vistas, 1600 × 1200 px), não usa CUDA e não faz teste gráfico da GUI.

## 2. O que ainda precisa ser implementado e comprovado

| Caso de teste | Resultado esperado / objetivo | Prioridade |
| --- | --- | --- |
| Malhas 3D idênticas | Métricas geométricas próximas de zero, sem alinhamento desnecessário (v2: valor igual ao piso de amostragem, já medido no [estudo de robustez](../results/robustness/README.md)) | Alta |
| Translação e rotação controladas | MSE pré/pós-ICP e transformação coerentes | Alta |
| Escala uniforme | Distinguibilidade entre diferenças dimensionais e alinhamento com escala (`icp_scale` já é registrado no CSV v2) | Alta |
| Diferenças de densidade de vértices | **Parcial:** viés das métricas por vértice mostrado com re-triangulação em casos sintéticos e numa GT de exemplo; falta repetir nas malhas do benchmark | Alta |
| Buracos e superfícies incompletas | **Parcial:** remoção controlada de área (cobertura/F-score) em casos sintéticos e numa GT; falta caso com ICP e malhas reais | Alta |
| Deformação localizada | **Parcial:** saliência gaussiana no estudo de robustez; falta verificar o heatmap | Alta |
| Regiões visível/oculta | Conferir a convenção de eixos (z para cima) e a câmera de entrada de cada conjunto de dados; comparar câmera ortográfica × perspectiva | Alta |
| Variação entre sementes de amostragem | Medir o desvio de CD, HD95, F@τ e normal consistency nas malhas reais (CV < 1 % na peça de exemplo) | Alta |
| Renderização offscreen | Gerar PNGs consistentes com câmeras e parâmetros documentados | Alta |
| LPIPS/PSNR/SSIM em múltiplas vistas | Validar contratos, máscaras, valores-limite e estabilidade; rodar o estudo de robustez com `--lpips` (os pesos da AlexNet precisam estar acessíveis) | Alta |
| Abertura, execução e cancelamento via GUI | Teste manual documentado ou teste Qt automatizado em ambiente compatível | Média |
| CUDA disponível vs CPU-only | Verificar device real, avisos, metadados e equivalência metodológica | Média |

Separe testes unitários rápidos dos testes de integração pesados. Controle SO, resolução, driver/renderizador, tolerâncias numéricas, parâmetros de câmera e versões de modelo. Um teste sintético que passa **não** demonstra equivalência de resultados entre GPU/CPU ou entre sistemas operacionais.

## 3. Exemplo reproduzível já possível

O código seguinte usa a **função real** `compute_metrics` do pacote, após instalação editável:

```python
# Verifica que nuvens de pontos idênticas têm distância geométrica nula
import numpy as np
from meshcomparison.geometry.metrics import compute_metrics

points = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
result = compute_metrics(points, points.copy())

assert np.isclose(result["chamfer_mean"], 0.0)
assert np.isclose(result["hausdorff"], 0.0)
assert np.isclose(result["rmse"], 0.0)
```

Isso verifica uma propriedade básica de **distâncias entre vértices**; não valida ICP nem avaliação de malhas tridimensionais inteiras.

## 4. Melhoria de arquitetura: fazer depois de proteger as métricas

Potenciais evoluções: amostragem uniforme de superfície, análise topológica, escolha de ICP com/sem escala, PSNR RGB convencional e validação de renderização. A **separação em módulos já foi implementada** em `src/meshcomparison/`, portanto não deve continuar como uma tarefa pendente genérica. Alterações nas definições científicas exigem testes de regressão e documentação (ADR) antes de comparar novos CSVs com o histórico.

## 5. Ajustes recentes da implementação

O preparo compartilhado dos pipelines agora está em [`common/prepare.py`](../../src/meshcomparison/common/prepare.py); a camada GUI foi separada em painéis, supervisor, worker de processo filho e carregador de saídas. A mensagem de progresso do pipeline perceptual também usa agora o número real de vistas (`num_views`). Esses testes cobrem partes isoladas do contrato; não substituem a validação end-to-end e a inspeção da janela em um ambiente gráfico real.

## Critérios de conclusão

- [ ] Casos geométricos controlados (identidade, transformação, deformação, incompletude e densidade) automatizados.
- [ ] Teste integrado de pelo menos uma execução completa dos pipelines com saídas verificadas.
- [ ] GPU/GUI, se declaradas suportadas, testadas em ambiente real e documentadas.
- [ ] Metodologia, parâmetros, tolerâncias e comandos de reprodução registrados.
- [ ] Resultados comparáveis e exceções conhecidos sem mascarar falhas.

Retorne à [visão geral da documentação](../README.md), ao [guia de Harness](../harness/README.md) ou ao [README principal](../../README.md).
