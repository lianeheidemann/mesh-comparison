# ADR 0002 — Normal consistency, curva F(τ) e estudo de robustez

- **Estado:** aceito (26/10/2026); arquivos renomeados pelo [ADR 0003](0003-single-metric-standard.md).

## Contexto

O artigo precisa mostrar **por que** as métricas são confiáveis. Os *priors* de *Geometric Deep Learning* (Bronstein et al., 2021) dão critérios verificáveis: invariância à discretização da superfície, resposta monotônica a distorções controladas e ausência de dependência de uma única tolerância.

## Decisão

1. **Normal consistency:** média de |cos| entre a normal de cada amostra e a da amostra mais próxima na outra superfície, nos dois sentidos. As normais vêm das faces sorteadas; o valor absoluto é usado porque malhas reconstruídas não têm orientação confiável. Varia em [0, 1].
2. **Curva F(τ):** τ = 0,5 %, 1,0 %, …, 10 % (20 pontos). A **AUC-F** é a área pelo trapézio dividida pela faixa de τ.
3. **Estudo de robustez** (`analysis/robustness.py`, `scripts/robustness_study.py`): re-triangulação (permutação e subdivisões), ruído na direção da normal, saliência gaussiana e remoção de área. As comparações são feitas **sem ICP**, com sementes fixas e contra um baseline por vértice.

**Adiado:** métrica 3D aprendida (features de PointNet/DGCNN), que exige pesos e validação humana; e decimação, que depende de um pacote extra.

## Consequências

- **Piso da normal consistency:** é menor que 1 em superfícies com arestas vivas e deve ser relatado.
- **Resultados:** [docs/results/robustness](../results/robustness/README.md).
