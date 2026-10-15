# 09 — Relatórios e protocolo experimental

## Saídas reais
| Saída | Origem | Conteúdo |
|---|---|---|
| `output/metrics/mesh_metrics.csv` | geométrico | MSE pré/pós, Chamfer, Hausdorff, RMSE, limiar, matriz e câmera |
| `output/metrics/per_view_metrics.csv` | perceptual | índice, azimute, elevação, LPIPS, PSNR, SSIM, recorte e enquadramento |
| `output/metrics/metric_summary.csv` | perceptual | min, max, p25, p75, mediana e média por métrica |
| `output/metrics/run_metadata.csv` | perceptual | caminhos, alinhamento, vistas e transformação |
| `output/aligned/rm_aligned.ply` | ambos | RM alinhada e reescalada às unidades GT |

## Leitura dos resultados
- **Geométricas** (`mean_chamfer`, `symmetric_hausdorff`, `symmetric_rmse`): **menor indica maior proximidade**.
- **MSE**: comparar pré versus pós-ICP e observar se houve melhora; MSE está em unidades de comprimento ao quadrado.
- **LPIPS**: menor indica maior semelhança perceptual; **PSNR/SSIM**: maior indica maior semelhança.
- **Médias perceptuais**: resumem vistas, mas podem ocultar algumas orientações com erro grande; olhar também mínimo, máximo, quartis e mediana.

## Experimentos reproduzíveis — proposta
1. Congelar versões de Python, dependências, GPU/driver e opções CLI.
2. Registrar hash SHA-256 dos arquivos GT e RM, unidades, contagem de faces/vértices e condição de alinhamento.
3. Executar um experimento por diretório para evitar sobrescrita entre rodadas.
4. Comparar o mesmo par sob pelo menos duas configurações de vista/alinhamento.
5. Registrar resultados de teste em tabela com `case_id`, `metric`, `value`, `units`, `aligned`, `seed`, `timestamp`.
6. Não interpretar um único escore como qualidade geral: checar efeitos de densidade de vértices, topologia, escala e visual.

## Testes de sanidade sugeridos
- Comparar a malha com ela mesma: erros geométricos próximos de zero.
- Transladar uma malha e conferir antes e depois do ICP.
- Adicionar uma ponta ou componente distante: verificar aumento da Hausdorff.
- Duplicar/refinar malhas com geometria próxima: observar sensibilidade à distribuição de vértices.
- Renderizar vistas idênticas: SSIM próximo de 1, LPIPS próximo de 0 e PSNR infinito conforme a definição do código.

**Atenção:** os arquivos dentro de `output/` presentes no repositório são resultados de execuções anteriores. Não são valores de referência universalmente válidos.
