# Validação do alinhamento (ICP de similaridade)

**Método.** A RM é construída aplicando à GT normalizada (`data/samples/gt.stl`) uma similaridade conhecida: rotação de 0° a 180° em passos de 15°, em torno do eixo z e do eixo oblíquo [1, 1, 1], com escala 1,3 e translação de 0,2 da diagonal. O alinhamento é o mesmo do pipeline: MSE ponto-superfície sobre 10⁵ amostras, limiar 10⁻⁴ e `similarity_icp_align` (inicialização por centroides e diagonais, ICP grosso e depois fino). O erro de rotação é o ângulo da matriz residual (ICP ∘ transformação aplicada), e o ideal é 0.

**Execução:** `python scripts/icp_study.py --gt data/samples/gt.stl --out <pasta>`. Dados em [icp_recovery.csv](icp_recovery.csv).

![Recuperação de rotações conhecidas](icp_recovery.png)

| Rotação aplicada | Eixo z | Eixo [1, 1, 1] |
| --- | --- | --- |
| 0°–30° | recuperada (erro ≤ 0,05°, Chamfer ≤ 6 × 10⁻⁵) | recuperada (erro ≤ 0,06°) |
| 45° | parcial (erro 1,7°, Chamfer 1,8 × 10⁻³) | recuperada (erro 0,05°) |
| 60° | **falha** (erro 54°) | parcial (erro 2,3°) |
| ≥ 75° | **falha** | **falha** |

Em todos os casos recuperados, a escala ficou com erro < 0,1 % e a translação com erro < 10⁻³ da diagonal.

## Conclusões

- O ICP é **local**: com esta GT, converge até cerca de 45°–60° de rotação inicial. Acima disso, cai num mínimo local.
- **Falha difícil de perceber:** em uma falha, o Chamfer pós-alinhamento fica em 2,5–3,1 % da diagonal (F@1 % entre 0,28 e 0,37), valores que parecem uma reconstrução ruim, e não um erro de alinhamento.
- **Implicação para o benchmark:** modelos de imagem única usam convenções de eixo diferentes (por exemplo, y para cima × z para cima, que é uma rotação de 90°). Antes de avaliar, coloque a saída de cada modelo no referencial da GT com uma rotação conhecida, ou adicione uma inicialização global (por exemplo, eixos principais ou várias rotações iniciais escolhendo o menor MSE). Inspecione sempre `icp_scale` e o heatmap.
- **Cobertura de testes:** `tests/test_icp.py` verifica a recuperação de 15° com escala 1,3 e translação, a identidade sem ICP e o caminho completo do pipeline (10°, escala 0,8).
