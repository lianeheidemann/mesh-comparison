# 10 — Limitações metodológicas e próximos passos

## Distinção entre qualidade geométrica e qualidade de malha
O projeto **mede proximidade geométrica por vértices** e **semelhança visual de renderizações**. Atualmente isso **não equivale** a auditar topologia, variedade (*manifold*), faces degeneradas, normais invertidas, interseções, número de componentes conectados, UVs, materiais nem custo de renderização.

## Pontos de atenção verificados no código
1. **Densidade de vértices:** distâncias são `vertex-to-vertex`, não `point-to-triangle` ou amostragem uniforme da superfície.
2. **Escala no alinhamento:** ICP permite escala uniforme, o que pode esconder variações dimensionais importantes.
3. **Critério de alinhamento:** um MSE inicial abaixo do limiar impede ICP, mesmo que haja diferenças de orientação relevantes; um ICP executado não é rejeitado automaticamente quando piora o MSE.
4. **Perceptual:** PSNR tem denominador não usual para RGB; SSIM e LPIPS usam fundo zerado e não máscara espacial ponderada; LPIPS depende da rede AlexNet e configurações de entrada.
5. **Comparação entre experimentos:** escolha da câmera, iluminação, proporção de recorte, distância de correspondência e percentil de heatmap precisam ser controlados.
6. **Exportação:** ambos os programas escrevem o mesmo `output/aligned/rm_aligned.ply` e podem sobrescrever resultados.

## Evolução priorizada (ainda não implementada)
- **P1 — Qualidade e testes:** testes unitários para fórmulas, proteção contra NaN e arrays vazios, documentação de unidades e versões congeladas.
- **P2 — Distâncias contínuas:** comparar pontos amostrados uniformemente por área, usar ponto-superfície para reduzir viés de triangulação e relatar método/amostragem.
- **P3 — Registro controlado:** oferecer ICP rígido (sem escala), inspeção visual do resultado e rejeição opcional por piora no MSE.
- **P4 — Métricas de malha:** faces degeneradas, buracos, orientabilidade, componentes conectados, manifold e auto-interseção.
- **P5 — Resultados estatísticos:** executar múltiplas seeds, descrever intervalos de confiança e produzir gráficos de distribuição por vista.
- **P6 — Engenharia:** criar configuração YAML/JSON, CI, testes de regressão e versão de saída sem sobrescrita.

## Critérios científicos
Antes de afirmar que um método é “melhor”, declarar: tipo de entrada, unidade de medida, protocolo de alinhamento, definição precisa da métrica, estratégia de amostragem, hardware, versão de bibliotecas e número de repetições. Uma avaliação robusta combina métricas geométricas, inspeção visual e validação das propriedades topológicas pertinentes ao uso final.
