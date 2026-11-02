# Métricas recentes adotadas

Este guia explica as métricas incorporadas ao protocolo atual e diferencia métricas novas das que já existiam no código antigo, mas tiveram sua definição alterada. As decisões técnicas e os estudos estão nos [ADRs 0001–0004](adr/).

## O que foi acrescentado

| Métrica | O que mede | Como interpretar |
| --- | --- | --- |
| **HD95** | O maior entre os percentis 95 das distâncias nos dois sentidos (GT→RM e RM→GT). | Menor é melhor. Resume discrepâncias grandes sem deixar que um único ponto extremo determine o resultado, como acontece com o Hausdorff máximo. |
| **Precisão** | Fração das amostras da RM que ficam a menos de uma tolerância τ da superfície GT. | Maior é melhor. Indica quanto da reconstrução está próximo da referência. |
| **Recall (cobertura)** | Fração das amostras GT que ficam a menos de τ da superfície RM. | Maior é melhor. Indica quanto da referência foi coberto pela reconstrução. |
| **F-score @τ** | Média harmônica entre precisão e recall para τ de 1%, 2% e 5% da diagonal da caixa delimitadora da GT. | Maior é melhor. Combina proximidade da reconstrução com cobertura da referência. |
| **Curva F(τ) e AUC-F** | Calcula o F-score em 20 tolerâncias, de 0,5% a 10% da diagonal da GT; AUC-F resume a área sob essa curva, normalizada pela faixa de tolerâncias. | Maior é melhor. Mostra o comportamento em várias tolerâncias, em vez de depender de um único τ. |
| **Consistência de normais (NC)** | Média, nos dois sentidos, do valor absoluto do cosseno entre a normal de uma amostra e a normal da superfície correspondente mais próxima. | Varia de 0 a 1; maior é melhor. Compara a orientação local das superfícies sem depender da orientação global das faces. |

As métricas geométricas podem ser calculadas para a superfície inteira e, quando a câmera da imagem de entrada é fornecida, separadamente para as regiões **visível** e **oculta** da GT. Essa separação é um recorte de análise; não é uma métrica independente.

## Métricas herdadas com definição revisada

**Chamfer** usa um nome que já existia, mas a versão atual não é o Chamfer vértice a vértice do código antigo. Agora compara amostras uniformes por área e distâncias até os triângulos da outra malha. A fórmula é metade da média GT→RM somada à média RM→GT. Menor é melhor. Essa definição reduz a dependência da densidade e da triangulação.

**PSNR** continua sendo uma métrica de imagem. A implementação atual calcula o erro quadrático médio sobre os três canais RGB dos pixels na união das máscaras (3N valores) e então aplica PSNR. Maior é melhor; um erro zero resulta em infinito. Isso corrige o denominador da versão anterior, que usava N.

**Chamfer, HD95, F-score, curva F(τ), AUC-F e NC** agora usam distâncias ponto-superfície: cada amostra é comparada com o ponto mais próximo nos triângulos da outra malha. Essa revisão, registrada no [ADR 0004](adr/0004-point-to-surface.md), remove o piso de erro causado pela distância entre duas amostragens discretas. É uma mudança de método, não uma métrica adicional.

## Diferenças em relação ao conjunto antigo

O protocolo atual deixa de usar as distâncias **vértice a vértice** do conjunto anterior: Chamfer e RMSE calculados entre vértices, além do Hausdorff máximo. O Chamfer atual tem definição por superfície; o HD95 é a medida robusta de discrepâncias altas. Precisão, recall, F-score, AUC-F e NC fazem parte do conjunto adotado nos ADRs 0001 e 0002. O PSNR também mudou para o cálculo padrão sobre os 3N valores RGB. Por isso, os resultados antigos não devem ser comparados diretamente com os atuais.

## Métricas perceptuais

**SSIM** estima semelhança estrutural entre imagens renderizadas, e **LPIPS** compara características perceptuais extraídas por uma rede neural. São calculadas em vistas compartilhadas da GT e da RM, com o fundo fora da união das máscaras zerado. **SSIM é melhor quanto maior; LPIPS é melhor quanto menor.** O projeto agrega os resultados das vistas por estatísticas como mediana e média. Os ADRs sobre o conjunto geométrico não apresentam SSIM e LPIPS como métricas recém-adotadas; elas compõem a avaliação perceptual por imagens.

## O que não deve ser confundido com métrica de qualidade

- **MSE simétrico** é usado como critério para decidir se o alinhamento ICP deve rodar e como diagnóstico da execução; não é apresentado como pontuação principal.
- **Escala do ICP** registra o fator de escala uniforme aplicado no alinhamento; serve para inspecionar o ajuste.
- **Heatmap** visualiza as distâncias da GT alinhada à RM. O limite de cor usa o percentil 95 para reduzir a influência de valores extremos.

As distâncias geométricas são normalizadas pela diagonal da caixa delimitadora da GT; as colunas em unidades da GT são obtidas multiplicando esse valor pela diagonal original. Os resultados são estimativas sobre 100 000 amostras por malha, com sementes fixas.

## Onde ficam no código

- Métricas geométricas e curva: [`geometry/metrics.py`](../src/meshcomparison/geometry/metrics.py)
- Pipeline e CSV geométrico: [`geometry/pipeline.py`](../src/meshcomparison/geometry/pipeline.py)
- PSNR, SSIM e LPIPS: [`perceptual/image_metrics.py`](../src/meshcomparison/perceptual/image_metrics.py)
- Renderização e agregação multivista: [`perceptual/pipeline.py`](../src/meshcomparison/perceptual/pipeline.py)
