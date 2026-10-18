import argparse

from .pipeline import run_pipeline


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="GT/RM STL mesh evaluation pipeline")
    parser.add_argument("--gt", required=True, help="Path to ground-truth STL")
    parser.add_argument("--rm", required=True, help="Path to reconstructed-model STL")
    parser.add_argument("--out", default="output", help="Output directory")

    parser.add_argument("--mse-threshold", type=float, default=1e-4,
                        help="Normalized symmetric MSE threshold to trigger similarity ICP")
    parser.add_argument("--azimuth", type=float, default=-135.0,
                        help="Orthographic camera azimuth in degrees")
    parser.add_argument("--elevation", type=float, default=25.264,
                        help="Orthographic camera elevation in degrees")
    parser.add_argument("--width", type=int, default=1600, help="Render width")
    parser.add_argument("--height", type=int, default=1200, help="Render height")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    run_pipeline(
        gt_path=args.gt,
        rm_path=args.rm,
        out_dir=args.out,
        mse_threshold_normalized=args.mse_threshold,
        azimuth_deg=args.azimuth,
        elevation_deg=args.elevation,
        width=args.width,
        height=args.height
    )


if __name__ == "__main__":
    main()
