# IJCNN 2027 — Plano de pesquisa e submissão

> **Status:** proposta de pesquisa; estudo comparativo ainda não executado. **Última revisão:** 2026-10-24.  
> **Conferência:** International Joint Conference on Neural Networks (IJCNN 2027), Cape Town, 14–18 junho 2027.  
> **Referências oficiais:** https://ijcnn.org/2027/authors/call-for-papers e https://ijcnn.org/2027/authors/initial-author-instructions.

## 1. Enquadramento e título

**Título de trabalho:** *Evaluating Geometric and Perceptual Fidelity in AI-Based Single-View 3D Reconstruction*.

**Área primária:** Representation Learning and Generative AI. Áreas complementares: Multimodal Learning e Neural Network Applications / Computer Graphics. O trabalho deve discutir os **modelos generativos neurais avaliados e o que revelam os experimentos**, não apenas descrever a interface de software.

**Problema:** uma reconstrução gerada a partir de uma única imagem pode parecer visualmente convincente, mas divergir geometricamente do objeto de referência, sobretudo em regiões não visíveis na entrada.

**Questão de pesquisa (RQ1):** qual a relação entre fidelidade geométrica e similaridade perceptual nas reconstruções single-view produzidas por distintos modelos generativos?
**RQ2:** como essa relação muda entre regiões visíveis e ocultas na imagem de origem?
**RQ3:** quanto os protocolos de alinhamento, escala e densidade de vértices alteram as conclusões?

**Hipótese H1 (a testar):** métricas geométricas e perceptuais apresentam discordâncias relevantes; uma avaliação conjunta evidencia falhas que medidas isoladas não detectam. Não antecipar confirmação nem estabelecer ranking sem validação.

## 2. Contribuição científica pretendida

1. Protocolo pareado e reproduzível para avaliar reconstruções 3D geradas por diferentes sistemas a partir da mesma imagem de entrada.
2. Análise quantitativa e qualitativa de concordância e discordância entre métricas geométricas e perceptuais.
3. Estudo de sensibilidade do protocolo: alinhamento com/sem escala, amostragem da superfície vs. vértices e ângulos de câmera.
4. Conjunto documentado de casos, parâmetros, resultados e limitações. **Não alegar nova rede neural ou nova métrica se não forem desenvolvidas.**

**Critério de novidade:** revisar trabalhos de avaliação de reconstrução single-view / image-to-3D e formular contribuição além de combinar métricas existentes. Se a novidade for insuficiente, restringir a pergunta a uma avaliação controlada de falhas de métodos neurais em geometrias ocluídas.

## 3. Estado atual do repositório (main, em 2026-10-24)

- Aplicativo desktop (PySide6/PyVistaQt) recebe malha GT e RM; não reconstrói malha a partir de imagem.
- Pipeline geométrico inclui ICP condicional, Chamfer médio, Hausdorff, RMSE e heatmap.
- Pipeline perceptual inclui renders multivista pareados e LPIPS, PSNR, SSIM; configuração da GUI usa 100 vistas.
- Os contratos científicos documentam **distâncias de vértice ao vértice mais próximo**, não distância contínua superfície–superfície.
- ICP de similaridade permite escala uniforme; valores pós-ICP isolados podem mascarar erro de escala.
- A avaliação automatizada em lote e o benchmark de diferentes geradores são **propostas**, não resultados existentes.
- Reutilizar docs/harness/CONTRATOS-CIENTIFICOS.md; mudanças metodológicas exigem versão, revisão e testes. Preservar a procedência do projeto original ThiagoFigueiroRibeiro/MeshComparison e diferenciar contribuição prévia de contribuição nova.

## 4. Desenho experimental

### 4.1 Corpus de referência
- Piloto: 5 objetos GT variados, incluindo formas com superfícies ocultas, cavidades, estruturas finas e topologias distintas; esta amostra é apenas para depuração do protocolo.
- Estudo principal: **meta proposta de 20–30 GT** com procedência e licenciamento documentados, idealmente mais se recursos permitirem.
- Para cada GT: renderizar **uma imagem 2D de entrada** com câmera, luz, fundo, resolução e semente controlados. Usar exatamente a mesma imagem para cada gerador.
- Registrar escala/unidades, contagem de vértices/faces, watertightness, orientações e transformações.
- Evitar uso de uma única xícara como base de generalização; estratificar por classe e dificuldade de ocultação.

### 4.2 Reconstrutores candidatos (verificar versões, licença e acesso)
- Tripo AI, Meshy e um baseline neural aberto/reproduzível, por exemplo TRELLIS ou Hunyuan3D, conforme elegibilidade e capacidade computacional.
- Registar versão/checkpoint, endpoint ou configuração, seed quando disponível, data, pós-processamento, custo e tentativas/falhas. Não atribuir diferenças apenas à arquitetura se os serviços não oferecem controle comparável.
- Recomenda-se **3 repetições por GT/modelo**, quando o serviço permitir. Para 20 GT, 3 geradores e 3 repetições: 180 reconstruções. Ajustar orçamento e potência estatística antes de executar.

### 4.3 Protocolo de avaliação
1. Congelar GT e imagem de entrada, registrar hashes, versões de software e modelos.
2. Converter exportações a formato comum sem alterar geometria indevidamente; registrar cada conversão.
3. Executar um cenário **sem alinhamento que permita escala** e um cenário **com ICP condicional atual**, reportando também erro de escala e pré/pós-alinhamento. Separar comparação de forma da avaliação de dimensão.
4. Calcular métricas legadas da aplicação (vertex-to-vertex Chamfer, Hausdorff, RMSE) e, como **análise adicional versionada**, métricas baseadas em amostragem de superfície com densidade comum. Não renomear métricas antigas silenciosamente.
5. Renderizar GT e RM sob câmeras compartilhadas, com luz, resolução, orientação, máscara e enquadramento fixos; calcular LPIPS, PSNR e SSIM. Conferir impacto das máscaras e do fundo.
6. Medir desempenho sob vistas não usadas como entrada e, se possível, separar vistas/regiões ocluídas versus observadas. Definir visibilidade de maneira geométrica e verificável.
7. Documentar malhas inválidas, ausentes, vazias ou falhas de geração; não excluí-las sem informar taxas e critérios.
8. Salvar CSVs, hashes, parâmetros e capturas por amostra/modelo/repetição, identificando qual versão do pipeline produziu cada resultado.

### 4.4 Validação estatística
- Unidade de análise: **GT**, preservando estrutura pareada; repetições do mesmo objeto não são amostras independentes.
- Descrever mediana, IQR, média e intervalos de confiança por modelo e métrica; ICs por bootstrap agrupado por GT, se adequado.
- Calcular Spearman para concordância entre métricas e analisar casos discordantes por objeto.
- Comparações entre modelos com testes pareados adequados ou modelo de efeitos mistos, correção para múltiplas comparações e tamanhos de efeito; especificar análise antes dos resultados.
- Não inventar resultados, significância, rankings ou números de desempenho.

## 5. Figuras e tabelas planejadas (6 páginas padrão IEEE)

- Figura 1: fluxo GT -> única imagem -> reconstruções de redes neurais -> avaliação pareada.
- Tabela 1: classes de GT e configuração dos geradores.
- Tabela 2: métricas e dispersão por modelo (incluindo falhas).
- Figura 2: correlação geométrica × LPIPS/SSIM e casos de discordância.
- Figura 3: GT, reconstruções, mapa de erro e vistas não observadas.
- Ablação curta: pré/pós-ICP e sensibilidade à amostragem.

**Esqueleto:** Abstract (150–200 palavras, somente após experimentos), Introduction (~0,75 pág.), Related Work (~0,75), Methodology (~1,5), Experiments & Results (~1,5), Discussion & Limitations (~0,75), Conclusion e References (~0,75). Redistribuir de acordo com formato real e sem comprimir ilegivelmente.

## 6. Cronograma de execução

| Período | Entrega | Gate |
|---|---|---|
| 24 out–08 nov 2026 | RQ/Hipóteses, trabalhos relacionados, matriz de novidade, escolha e licenças de GT | Proposta justificável |
| 09–22 nov | 5 casos piloto, pré/pós-alinhamento, teste de sensibilidade, manifest de runs | Protocolo executável |
| 23 nov–13 dez | Benchmark principal, inspeção de falhas, logs e agregação | Dataset íntegro |
| 14–31 dez | Estatística, robustez, figuras, tabelas e limitações | Evidências suficientes |
| 01–17 jan 2027 | Redação IEEE completa, citações, anonimização | Rascunho de 6 páginas |
| 18–27 jan | Revisão por orientador/coautores, verificações finais, PDF | Pronto para submeter |
| 28–31 jan | Envio ao Microsoft CMT antes de 31/01/2027 | Comprovante de submissão |

**Datas oficiais:** abertura em 01/12/2026; submissão regular até 31/01/2027; notificação 15/03/2027; camera-ready e registro 12/04/2027; evento 14–18/06/2027. Conferir alterações no site da organização.

## 7. Estrutura sugerida, sem implementação nesta etapa

```text
docs/research/ijcnn-2027/
  README.md              # este plano
  literature-matrix.md    # ainda a criar
  protocol.md             # ainda a criar
  dataset-manifest.csv    # ainda a criar
  results-plan.md         # ainda a criar
  paper/                  # template IEEE e manuscrito posteriormente
```

Manter dados de avaliação em `experiments/ijcnn2027/` ou área equivalente, referenciando artefatos grandes externamente com checksums; não versionar outputs pesados sem necessidade. Integrar execução em lote apenas após teste com pares individuais e autorização explícita de mudança metodológica.

## 8. Checklist de submissão

- [ ] Estudos anteriores e diferencial científico avaliados por orientador/coautores
- [ ] Dataset, direitos, versões, seeds, hashes e protocolo congelados
- [ ] Testes controlados e ablações passam sem regressões não explicadas
- [ ] Resultados executados e reproduzíveis; tabelas coerentes com CSVs
- [ ] Citar código-fonte original e artigos de métricas / reconstrução
- [ ] Declaração de conflitos, financiamento, licenças e uso de IA conforme IEEE
- [ ] PDF no template IEEE, **double-blind**, sem autores/identificadores, e referências anonimizadas adequadamente
- [ ] Meta de até **6 páginas** incluindo figuras e referências; páginas extras têm custo oficial
- [ ] Manuscrito original, não submetido simultaneamente a outro evento
- [ ] Submissão CMT e confirmação até 31/01/2027

**Nota:** IJCNN orienta divulgar texto gerado por IA no artigo (acknowledgements) e citar seções correspondentes; verificar como conciliar esta obrigação com anonimização double-blind. A submissão requer revisão humana de todo texto e de todas as citações.

## Fontes
- https://ijcnn.org/2027/
- https://ijcnn.org/2027/authors/call-for-papers
- https://ijcnn.org/2027/authors/initial-author-instructions
- https://github.com/lianeheidemann/mesh-comparison/blob/main/README.md
- https://github.com/lianeheidemann/mesh-comparison/blob/main/docs/harness/CONTRATOS-CIENTIFICOS.md
- https://github.com/lianeheidemann/mesh-comparison/tree/main/docs/REFERENCES
