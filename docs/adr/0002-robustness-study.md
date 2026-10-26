# ADR 0002 — Normal consistency, curva F(τ) e estudo de invariância/sensibilidade

- **Estado:** aceito pela pessoa responsável pelo projeto (26/10/2026), como complemento do [ADR 0001](0001-evaluation-v2.md). Ainda não foi validado nos dados reais do benchmark.
- **Contratos:** CC-18 em [CONTRATOS-CIENTIFICOS.md](../harness/CONTRATOS-CIENTIFICOS.md). CC-01 a CC-17 não mudam.

## Contexto

O artigo para a IJCNN 2027 precisa justificar **por que** as métricas são confiáveis. Os *priors* de *Geometric Deep Learning* (Bronstein et al., 2021: invariância, estabilidade e multiescala; malhas como variedades discretizadas) dão um critério verificável: uma métrica de reconstrução deve ser invariante à discretização da superfície, responder de forma monotônica a distorções controladas e não depender de uma única escala de tolerância.

## Decisão

1. **Normal consistency** (CC-18): média de `|cos|` entre a normal de cada amostra e a normal da amostra mais próxima na outra superfície, nos dois sentidos. As normais são as das faces sorteadas pela mesma amostragem de CC-14 (`return_normals=True` não altera os pontos). Usa valor absoluto porque malhas reconstruídas não têm orientação confiável. Fica em [0, 1]; maior é melhor.
2. **Curva F(τ)** com τ = 0,5 %, 1,0 %, …, 10 % da diagonal da GT (20 pontos), e **AUC-F** = área pelo trapézio dividida pela faixa de τ, em [0, 1].
3. **Saídas aditivas:** as colunas `normal_consistency` e `fscore_auc` entram **ao final** de `metrics_geometry_v2.csv`, e o arquivo novo `metrics/fscore_curve_v2.csv` guarda a curva por região. A GUI ganha a linha "Normal consistency" na aba "Geometric summary".
4. **Estudo de robustez:** `meshcomparison/analysis/robustness.py` e `scripts/robustness_study.py`, fora da GUI.
   - Re-triangulação: permutação, subdivisão e subdivisão desigual.
   - Ruído na direção da normal, saliência gaussiana local e remoção de área.
   - Comparação **sem ICP**, para isolar a resposta das métricas; sementes fixas.

## Alternativas consideradas

- **Métrica 3D aprendida** (features de PointNet/DGCNN): adiada, porque exige pesos, validação humana e mais espaço que as 6 páginas do artigo.
- **Normal consistency orientada** (sem valor absoluto): rejeitada, porque penalizaria inversões de orientação que não mudam a geometria.
- **Decimação** para testar a re-triangulação: adiada, porque depende de pacote extra (`fast_simplification`). A subdivisão já preserva a superfície exatamente.

## Consequências

- Os valores v2 anteriores (CD, HD95, F@τ) não mudam: a amostragem é idêntica, o que foi verificado no conjunto de exemplo.
- A normal consistency tem piso menor que 1 em superfícies com arestas vivas, e o F@τ tem piso menor que 1 quando o espaçamento entre amostras se aproxima de τ. Os dois pisos precisam ser relatados.
- Resultados da primeira execução: [docs/results/robustness](../results/robustness/README.md).

## Rollback

Remover as duas colunas finais, `fscore_curve_v2.csv`, o módulo `analysis/` e o script. O legado e as colunas v2 do ADR 0001 não dependem deles.
