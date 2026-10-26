# ADR 0005 — Inicialização global do ICP

- **Estado:** aceito (26/10/2026). Altera só o alinhamento; as métricas e as saídas não mudam.

## Contexto

O [estudo do ICP](../results/icp/README.md) mostrou que o ICP de similaridade, iniciado só pelos centroides e pela razão das diagonais, converge apenas até cerca de 45°–60° de rotação. Acima disso, cai num mínimo local que deixa um Chamfer de 2,5–3,1 % da diagonal, valor que parece uma reconstrução ruim e não um erro de alinhamento. Modelos de imagem única usam convenções de eixo diferentes (por exemplo, y para cima × z para cima, uma rotação de 90°), então essa falha seria comum no benchmark.

## Decisão

`common/alignment.py:similarity_icp_align` passa a escolher o ponto de partida entre **28 candidatos**:

- as 24 rotações que levam os eixos coordenados uns nos outros (cobrem exatamente as mudanças de convenção de eixos);
- as 4 rotações que alinham os eixos principais (PCA) da RM aos da GT.

Para cada candidato:

- a escala inicial é a razão dos raios RMS em torno dos centroides, que não depende da orientação (antes, era a razão das diagonais das caixas, que muda com a rotação);
- roda-se um ICP grosso curto (30 iterações, 5 000 amostras).

Fica a partida com a menor distância média simétrica ao vizinho mais próximo. A partir dela, rodam o ICP grosso e o fino de antes (50 000 amostras, limiares 0,25 e 0,05, até 100 iterações). O gatilho (MSE ponto-superfície > 10⁻⁴) não muda.

## Consequências

Varredura de 0° a 180° em torno dos eixos z e [1, 1, 1], com escala 1,3 (26 casos):

| Resultado | Antes | Depois |
| --- | ---: | ---: |
| Casos recuperados¹ | 9 | 26 |
| Erro máximo de rotação | 175° | 0,05° |
| Erro máximo de escala | 10 % | 0,008 % |
| Chamfer máximo pós-alinhamento | 3,1 × 10⁻² | 6,3 × 10⁻⁵ |

¹ Chamfer < 1 % da diagonal da GT.

- **Custo:** cerca de 2 s a mais por alinhamento, e só quando o ICP é acionado. No par de exemplo o ICP não é acionado, e as métricas são idênticas.
- **Objetos simétricos:** podem ser alinhados em qualquer orientação equivalente. Isso não altera as métricas, mas o erro de rotação deixa de ser único.
- **Formas diferentes:** com uma reconstrução muito distante da GT, a partida escolhida é a que **minimiza a distância**. Esse é o comportamento esperado para avaliação, mas pode esconder uma orientação errada do modelo; inspecione `icp_scale` e o heatmap.
- **Testes:** `tests/test_icp.py` (rotações de 90°, 120°, 135° e 180° numa forma sem simetria) e `tests/test_common.py` (rotações dos eixos, PCA e inicialização).
