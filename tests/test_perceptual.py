import numpy as np
import pytest

pytest.importorskip("skimage")

from meshcomparison.perceptual.image_metrics import (  # noqa: E402
    crop_to_union_mask,
    masked_psnr,
    rgba_to_rgb_mask,
    summarize_stats,
)


def test_masked_psnr_identical_images_is_inf():
    img = np.random.default_rng(0).random((8, 8, 3)).astype(np.float32)
    mask = np.ones((8, 8), dtype=bool)
    assert masked_psnr(img, img.copy(), mask) == np.inf


def test_masked_psnr_empty_mask_is_nan():
    img = np.zeros((4, 4, 3), dtype=np.float32)
    assert np.isnan(masked_psnr(img, img, np.zeros((4, 4), dtype=bool)))


def test_masked_psnr_known_error_uses_the_mean_over_channels():
    # one masked pixel with error 0.1 in every channel: MSE = 0.01 over the 3 values, PSNR = 20 dB
    gt = np.zeros((2, 2, 3), dtype=np.float32)
    rm = gt.copy()
    rm[0, 0] = 0.1
    mask = np.zeros((2, 2), dtype=bool)
    mask[0, 0] = True
    assert masked_psnr(gt, rm, mask) == pytest.approx(20.0, rel=1e-5)


def test_masked_psnr_ignores_pixels_outside_the_mask():
    gt = np.zeros((2, 2, 3), dtype=np.float32)
    rm = gt.copy()
    rm[0, 0] = 0.1
    rm[1, 1] = 1.0  # large error, but outside the mask
    mask = np.zeros((2, 2), dtype=bool)
    mask[0, 0] = mask[0, 1] = True  # error 0.1 on one of the two masked pixels: MSE = 0.005
    assert masked_psnr(gt, rm, mask) == pytest.approx(10 * np.log10(1 / 0.005), rel=1e-5)


def test_rgba_to_rgb_mask_zeroes_background():
    rgba = np.zeros((2, 2, 4), dtype=np.uint8)
    rgba[0, 0] = [255, 0, 0, 255]
    rgb, alpha, mask = rgba_to_rgb_mask(rgba)
    assert mask.tolist() == [[True, False], [False, False]]
    assert rgb[0, 0].tolist() == [1.0, 0.0, 0.0]


def test_crop_to_union_mask_pads_and_clips():
    img = np.zeros((20, 20, 3), dtype=np.float32)
    m1 = np.zeros((20, 20), dtype=bool)
    m1[5:8, 5:8] = True
    *_, union_c = crop_to_union_mask(img, img, m1, m1, pad=2)
    assert union_c.shape == (7, 7)


def test_summarize_stats_ignores_non_finite():
    stats = summarize_stats([1.0, 3.0, np.inf, np.nan])
    assert stats["min"] == 1.0 and stats["max"] == 3.0 and stats["mean"] == 2.0
