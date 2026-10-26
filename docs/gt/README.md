# Escolha e preparação das malhas de referência (GT)

Qualquer malha triangular em STL, OBJ, PLY, OFF ou GLB/GLTF pode ser GT. Os resultados, porém, só valem como benchmark se as GTs forem **novas para os modelos**, **escolhidas por um critério definido antes** e **limpas**. Este guia define o protocolo; o verificador `scripts/check_gt.py` confere a parte técnica.

## Estrutura recomendada

| Conjunto | Origem e papel |
| --- | --- |
| Quantitativo | 30–50 objetos do [Google Scanned Objects](https://arxiv.org/abs/2204.11918v1), por categoria (há bichinhos, brinquedos e bonecos); seleção atual [abaixo](#user-content-seleção-do-gso-deste-repositório). **Números principais**, comparáveis com a literatura |
| Curado | 10–20 objetos escolhidos por você: escaneados, modelados ou publicados depois do treino dos modelos. **Figuras e generalização**, reportado à parte |

### Seleção do GSO deste repositório

[`data/gso/selection.csv`](../../data/gso/selection.csv) lista 20 objetos principais e 4 suplentes (mais 1 objeto excluído, ver abaixo). Foram escolhidos **à mão**, antes de rodar qualquer modelo, com este critério: objetos visualmente atraentes (animais, dinossauros, bonecos, veículos e utensílios), alternando corpos lisos com partes finas (asas, chifres, hélices, alças) e incluindo alguns casos de controle rígidos ou quase simétricos (ônibus, panda). Como a escolha é manual, declare esse critério no artigo.

```bash
python scripts/fetch_gso.py --out data/gso/meshes  # baixa do Gazebo Fuel e escreve data/gso/meshes/manifest.csv
python scripts/check_gt.py --manifest data/gso/meshes/manifest.csv --out data/gso/meshes/gt_report.csv
```

- **Substituição:** um objeto que não exista no Fuel é trocado pelo próximo suplente, e a troca fica registrada em `selection_reason`. Os nomes foram listados sem acesso ao Fuel, então confira o relatório do script.
- **Metadados:** licença, autoria e data vêm do Fuel; campo vazio no manifesto significa que o Fuel não os informou.
- **Limpeza:** objetos com WARN no `check_gt.py` também são trocados pelo próximo suplente, com o motivo registrado.
- **Data de corte:** todos os objetos do GSO foram publicados antes do corte de treino dos modelos atuais, então o `--cutoff` acusaria todos. Para o GSO, confira a contaminação nos artigos dos modelos (seção abaixo) e rode o `check_gt.py` sem `--cutoff`.
- **Arquivos:** as 20 malhas principais (e o `manifest.csv` e o `gt_report.csv`) estão versionadas em `data/gso/meshes/` (cerca de 476 MB), com `.obj`, `.png` e `.jpg` no **Git LFS** (`.gitattributes`). Depois de clonar, rode `git lfs install` e `git lfs pull`. O script só precisa ser rodado para baixar de novo ou para outra seleção. Licença CC-BY: cite a autoria do manifesto. Suas próprias GTs em `gt/` continuam fora do Git.
- **Resultado da checagem:** 20 OK, 0 WARN, 0 falhas. Na primeira checagem (antes de qualquer modelo rodar) o `Transformers_Age_of_Extinction_Mega_1Step_Bumblebee_Figure` (rank 16) deu WARN, com 6,7 % de superfície encerrada, e foi trocado pelo primeiro suplente, `Great_Dinos_Triceratops_Toy` (rank 21). Na `selection.csv` o Bumblebee ficou como `excluded` e o Triceratops como `primary`, ambos com o motivo em `selection_reason`.

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

| Aviso (gatilho) | Por quê → o que fazer |
| --- | --- |
| **Partes separadas** (> 5 % da área fora da maior parte) | Base, cenário ou chão entram no Chamfer e na separação visível/oculta → remover base e cenário; peças do próprio objeto (olhos, botões) podem ficar |
| **Superfície aberta** (> 1 % de arestas de borda) | Buracos mudam a cobertura (recall) e o F-score → fechar os buracos (Blender: *Fill Holes*) ou trocar o objeto |
| **Superfície encerrada** (> 2 % da área) | Faces escondidas (cascas internas, roupas sobre o corpo, olhos dentro da cabeça) recebem amostras que nenhum modelo reconstrói → apagar as faces internas; concavidades profundas também disparam o aviso, então confira visualmente |
| **Arestas não-manifold** (> 0) | Geometria quebrada → limpar (Blender: *Merge by Distance*) |
| **Faces duplicadas** (> 0) ou **degeneradas** (> 1 %) | Geometria quebrada → limpar (Blender: *Merge by Distance*, *Delete Loose*) |
| **Falha de leitura ou formato** | Não é avaliável → converter (FBX → GLB/OBJ) |

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

Quando a cena tem mais de uma malha, o log mostra o nome e a área de cada uma (por exemplo, `Scene model.glb: ground 2 tri 86%, object 12 tri 14%`). O `check_gt.py` repete essa lista no aviso de partes separadas e nas colunas `scene_meshes` e `dropped`; numa avaliação, ela vai para as colunas `gt_scene_meshes`/`rm_scene_meshes` de `metrics_geometry.csv` e aparece como aviso na aba *Geometric summary* da GUI.

Nada é removido automaticamente, porque decidir o que é cenário é uma escolha de quem prepara a GT. Remova os nós extras no Blender (*Outliner* → apagar o nó → exportar GLB) e registre isso em `cleanup_notes` no manifesto.

## Imagem de entrada

Renderize a imagem de entrada a partir da própria GT, com uma **câmera conhecida**. A mesma imagem vai para todos os modelos:

- fundo uniforme, resolução fixa e objeto centralizado;
- elevação de 20–30°;
- azimute e elevação registrados no manifesto (`input_azimuth_deg`, `input_elevation_deg`, com z para cima e azimute medido de +x para +y). São esses valores que a separação visível/oculta usa.
