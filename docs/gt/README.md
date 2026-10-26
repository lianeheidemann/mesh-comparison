# Escolha e preparação das malhas de referência (GT)

Qualquer malha triangular em STL, OBJ, PLY, OFF ou GLB/GLTF pode ser GT. Os resultados, porém, só valem como benchmark se as GTs forem **novas para os modelos**, **escolhidas por um critério definido antes** e **limpas**. Este guia define o protocolo; o verificador `scripts/check_gt.py` confere a parte técnica.

## Estrutura recomendada

| Conjunto | Origem | Papel no artigo |
| --- | --- | --- |
| **Quantitativo** | 30–50 objetos do [Google Scanned Objects](https://arxiv.org/abs/2204.11918v1), escolhidos por categoria (bichinhos, brinquedos e bonecos também existem ali) | Números principais, comparáveis com a literatura |
| **Curado** | 10–20 objetos escolhidos por você: escaneados, modelados ou publicados depois do treino dos modelos | Figuras e teste de generalização, reportado **separadamente** |

## Contaminação do treino

- **Fontes de treino:** a maioria dos modelos de imagem para 3D treina no Objaverse, montado a partir do Sketchfab. O Objaverse-XL acrescenta Thingiverse, GitHub e outros acervos públicos.
- **Risco:** um modelo "fofo" baixado dessas fontes pode ter sido visto no treino, e a reconstrução fica boa por memorização.
- **GTs seguras:**
  - **feitas por você:** fotogrametria com o celular ou modelagem própria;
  - **publicadas depois** da data de corte do treino de **todos** os modelos avaliados (use a data mais recente entre eles como `--cutoff`);
  - **do GSO:** costuma ficar fora do treino, mas confira no artigo de cada modelo se ele declara ter treinado com GSO.

## Protocolo de seleção

1. **Critério antes de rodar:** escreva o critério antes de executar qualquer modelo. Por exemplo: "N objetos; metade orgânicos, metade rígidos; com e sem partes finas; com e sem textura".
2. **Registro no manifesto:** registre cada objeto no manifesto ([modelo](manifest_template.csv)), com origem, URL, autoria, licença, data de publicação, categoria, motivo da escolha, limpeza aplicada e a câmera da imagem de entrada.
3. **Licença:** use só licenças que permitam publicação (CC0, CC-BY) e cite a autoria no artigo ou no material suplementar.
4. **Sem trocas depois dos resultados:** não troque objetos depois de ver os resultados. Se precisar trocar, registre o motivo.

## Requisitos técnicos e o que fazer em cada aviso

```bash
python scripts/check_gt.py gt/ --manifest gt/manifest.csv --cutoff AAAA-MM-DD --out gt_report.csv
```

| Aviso | Limite | Por que importa | O que fazer |
| --- | --- | --- | --- |
| Partes separadas | > 5 % da área fora da maior parte | Uma base, cenário ou chão entra no Chamfer e na separação visível/oculta | Remover a base e o cenário; peças pequenas do próprio objeto (olhos, botões) podem ficar |
| Superfície aberta | > 1 % de arestas de borda | Buracos mudam a cobertura (recall) e o F-score | Fechar os buracos (no Blender, *Fill Holes*) ou trocar o objeto |
| Superfície encerrada | > 2 % da área | Faces escondidas (cascas internas, roupas sobre o corpo, olhos dentro da cabeça) recebem amostras que nenhum modelo reconstrói | Apagar as faces internas; concavidades profundas também disparam o aviso, então confira visualmente |
| Arestas não-manifold, faces duplicadas ou degeneradas | > 0, > 0, > 1 % | Indicam geometria quebrada | Limpar (no Blender: *Merge by Distance*, *Delete Loose*) |
| Falha de leitura ou formato | — | Não é avaliável | Converter (FBX → GLB/OBJ) |

A textura (`has_texture`) não gera aviso, mas afeta as métricas perceptuais: use objetos todos com textura ou todos sem.

**Exemplo:** a GT de exemplo (`data/samples/gt.stl`) recebe WARN. Ela tem 3 partes separadas (6 % da área fora da maior), 2,9 % de arestas de borda e 3,7 % de superfície encerrada. Serve para testar o software, mas não seria uma GT de benchmark sem limpeza.

## GLB/GLTF com cena

Um GLB/GLTF guarda uma **cena**, não só uma malha. O carregador (`common/io.py:load_mesh`) trata cada elemento assim:

| Elemento | Tratamento |
| --- | --- |
| Câmeras, luzes | Ignoradas: não são geometria |
| Linhas e pontos (auxiliares, *gizmos*) | Descartados e listados no log |
| Esqueleto, animação, *morph targets* | Não aplicados: a malha entra na **pose de repouso** |
| **Todas as malhas triangulares da cena** | **Entram juntas**, com as transformações da cena (inclusive chão, cenário e outros objetos) |

Quando a cena tem mais de uma malha, o log mostra o nome e a área de cada uma (por exemplo, `Scene model.glb: ground 2 tri 86%, object 12 tri 14%`). O `check_gt.py` repete essa lista no aviso de partes separadas e nas colunas `scene_meshes` e `dropped`.

Nada é removido automaticamente, porque decidir o que é cenário é uma escolha de quem prepara a GT. Remova os nós extras no Blender (*Outliner* → apagar o nó → exportar GLB) e registre isso em `cleanup_notes` no manifesto.

## Imagem de entrada

Renderize a imagem de entrada a partir da própria GT, com uma **câmera conhecida**. A mesma imagem vai para todos os modelos:

- fundo uniforme, resolução fixa e objeto centralizado;
- elevação de 20–30°;
- azimute e elevação registrados no manifesto (`input_azimuth_deg`, `input_elevation_deg`, com z para cima e azimute medido de +x para +y). São esses valores que a separação visível/oculta usa.
