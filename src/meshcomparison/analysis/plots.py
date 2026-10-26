# Figures of the evaluated metrics: F(tau) curves, per-region summary, per-view perceptual estimates, sampling spread.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REGION_STYLE = {"all": ("Whole surface", "C0"), "visible": ("Visible", "C2"), "hidden": ("Hidden", "C3")}
PERCEPTUAL_LABELS = {"lpips": "LPIPS (lower is better)", "psnr": "PSNR, dB (higher is better)",
                     "ssim": "SSIM (higher is better)"}


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def bootstrap_mean_ci(values, n_boot=2000, level=0.95, seed=0):
    """Mean of the finite ``values`` and its percentile-bootstrap confidence interval (NaN if none are finite)."""
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    alpha = (1.0 - level) / 2.0
    return float(values.mean()), float(np.quantile(means, alpha)), float(np.quantile(means, 1.0 - alpha))


def plot_fscore_curve(curve, path):
    """F-score, precision and recall against the tolerance tau (% of the GT diagonal), one colour per region."""
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for region, group in curve.groupby("region", sort=False):
        label, color = REGION_STYLE.get(region, (region, None))
        tau = 100.0 * group["tau_normalized"]
        ax.plot(tau, group["fscore"], color=color, lw=2, label=f"{label}: F-score")
        ax.plot(tau, group["precision"], color=color, lw=1, ls="--", label=f"{label}: precision")
        ax.plot(tau, group["recall"], color=color, lw=1, ls=":", label=f"{label}: recall")
    ax.set_xlabel("Tolerance τ (% of GT bounding-box diagonal)")
    ax.set_ylabel("Fraction of samples within τ")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    ax.set_title("F(τ) curve")
    return _save(fig, path)


def plot_region_metrics(metrics, path):
    """Distances (GT units) and scores of each region side by side."""
    regions = [r for r in REGION_STYLE if r in set(metrics["region"])]
    rows = metrics.set_index("region").loc[regions]
    panels = (
        ("Distances (GT units, lower is better)", [("chamfer_mean_gt_units", "Chamfer"), ("hd95_gt_units", "HD95")]),
        ("Scores (higher is better)", [("fscore_tau1pct", "F@1%"), ("fscore_tau2pct", "F@2%"),
                                       ("fscore_tau5pct", "F@5%"), ("fscore_auc", "AUC-F"),
                                       ("normal_consistency", "Normal\nconsistency")]),
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [2, 5]})
    width = 0.8 / len(regions)
    for ax, (title, series) in zip(axes, panels):
        x = np.arange(len(series))
        for i, region in enumerate(regions):
            label, color = REGION_STYLE[region]
            if region != "all":
                label = f"{label} ({rows.loc[region, 'gt_surface_fraction']:.0%} of GT)"
            ax.bar(x + (i - (len(regions) - 1) / 2) * width, [rows.loc[region, c] for c, _ in series], width,
                   color=color, label=label)
        ax.set_xticks(x, [name for _, name in series])
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    axes[1].set_ylim(0, 1.22)
    axes[1].legend(fontsize=8, ncol=len(regions), loc="upper center")
    return _save(fig, path)


def plot_perceptual_views(per_view, path, metrics=("lpips", "psnr", "ssim"), n_boot=2000, seed=0):
    """Each metric against the view azimuth, with its mean over the views and a 95 % bootstrap interval."""
    metrics = [m for m in metrics if m in per_view.columns]
    fig, axes = plt.subplots(len(metrics), 1, figsize=(7, 2.4 * len(metrics)), sharex=True, squeeze=False)
    for ax, metric in zip(axes[:, 0], metrics):
        mean, low, high = bootstrap_mean_ci(per_view[metric], n_boot=n_boot, seed=seed)
        ax.plot(per_view["azimuth_deg"], per_view[metric], marker="o", ms=3, lw=1, label="per view")
        ax.axhline(mean, color="C1", lw=1.5, label=f"mean {mean:.4g} (95 % CI {low:.4g}–{high:.4g})")
        ax.axhspan(low, high, color="C1", alpha=0.2)
        ax.set_ylabel(PERCEPTUAL_LABELS.get(metric, metric), fontsize=8)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    axes[-1, 0].set_xlabel("View azimuth (degrees)")
    axes[0, 0].set_title("Perceptual metrics per view")
    return _save(fig, path)


def plot_sampling_uncertainty(spread, path):
    """Mean ± standard deviation over seed pairs against the number of samples per mesh (log scale)."""
    series = [("chamfer", "Chamfer (normalized)"), ("hd95", "HD95 (normalized)"),
              ("fscore_tau1pct", "F@1%"), ("normal_consistency", "Normal consistency")]
    series = [(c, label) for c, label in series if c in spread.columns]
    stats = spread.groupby("n_samples")[[c for c, _ in series]].agg(["mean", "std"])
    n = stats.index.to_numpy()
    fig, axes = plt.subplots(1, len(series), figsize=(3.3 * len(series), 3.2), squeeze=False)
    for ax, (column, label) in zip(axes[0], series):
        mean, std = stats[(column, "mean")].to_numpy(), stats[(column, "std")].to_numpy()
        ax.plot(n, mean, marker="o", color="C0")
        ax.fill_between(n, mean - std, mean + std, color="C0", alpha=0.25)
        ax.set_xscale("log")
        ax.set_title(label, fontsize=9)
        ax.set_xlabel("Samples per mesh")
        ax.grid(alpha=0.3)
    fig.suptitle(f"Sampling spread: mean ± std over {spread['seed_pair'].nunique()} seed pairs", fontsize=10)
    return _save(fig, path)
