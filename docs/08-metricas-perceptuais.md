# 08 — LPIPS, PSNR e SSIM

![Esquema de avaliação multivista](images/multiview.svg)

## Pipeline implementado
O script `percept_eval_pipeline.py` alinha as malhas como o geométrico e usa **100 azimutes uniformemente distribuídos** por padrão, de 0° até menos de 360°, com elevação fixa em 25,264°. Para cada câmera ortográfica, renderiza GT/RM com a **mesma pose e enquadramento**, calcula máscaras alfa, recorta a união das silhuetas (12 pixels de margem), zera o fundo e calcula três métricas.

Por padrão, apenas as vistas **1, 33 e 66** são exportadas como PNG, embora todas as 100 participem das métricas.

## PSNR (Peak Signal-to-Noise Ratio)
\[
PSNR=10\log_{10}\left(\frac{MAX^2}{MSE_{pixels}}\right)
\]

`masked_psnr` calcula erro RGB ao quadrado para pixels na **máscara da união** das silhuetas; imagens são normalizadas para [0,1] e `MAX=1`. Erro nulo retorna infinito. **Maior é melhor**, em dB.

**Observação de código:** o denominador atual conta os pixels da máscara **uma vez**, mas soma erros em 3 canais RGB: isso gera uma convenção de agregação diferente do MSE RGB usual que divide por 3 também. Ao confrontar com outros PSNRs, padronizar o denominador.

## SSIM (Structural Similarity Index)
SSIM combina luminância, contraste e estrutura local:

\[
SSIM(x,y)=\frac{(2\mu_x\mu_y+C_1)(2\sigma_{xy}+C_2)}{(\mu_x^2+\mu_y^2+C_1)(\sigma_x^2+\sigma_y^2+C_2)}
\]

`masked_ssim` usa `skimage.metrics.structural_similarity` sobre a imagem RGB **recortada com fundo zerado**. Não usa diretamente um SSIM verdadeiramente ponderado por máscara; pixels de fundo dentro do recorte ainda participam. **Maior é melhor**, com 1 indicando correspondência estrutural máxima para a convenção.

## LPIPS (Learned Perceptual Image Patch Similarity)
`masked_lpips` converte H×W×3 para lote de tensores 1×3×H×W, transforma intensidades de [0,1] para [−1,1] e aplica `lpips.LPIPS(net="alex")` em `torch.no_grad()`. LPIPS compara características de camadas de uma rede neural pré-treinada; **menor geralmente é melhor**. Não é distância geométrica, nem medida direta da qualidade da topologia.

O termo *masked* no nome da função não significa que a rede aplique uma máscara de pesos em cada posição: a implementação zera o fundo antes de inferir.

## Implementar com cuidado
1. Garantir iluminação e câmera idênticas no par de uma mesma vista.
2. Preservar diferenças de silhueta na máscara de união.
3. Conferir `crop_h` e `crop_w`; recortes minúsculos podem invalidar a janela SSIM ou reduzir a robustez do LPIPS.
4. Instalar `torch`, `torchvision`, `lpips` e `scikit-image`.
5. Exportar valores por vista e estatísticas agregadas. **Não comparar LPIPS de resoluções/crops distintos sem controlar o protocolo.**
