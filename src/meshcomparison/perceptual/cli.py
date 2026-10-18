import argparse

from .pipeline import run_pipeline


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="GT/RM STL perceptual evaluation pipeline")
    parser.add_argument("--gt", required=True, help="Path to ground-truth STL")
    parser.add_argument("--rm", required=True, help="Path to reconstructed-model STL")
    parser.add_argument("--out", default="output", help="Output directory")

    parser.add_argument("--mse-threshold", type=float, default=1e-4,
                        help="Normalized symmetric MSE threshold to trigger similarity ICP")
    parser.add_argument("--elevation", type=float, default=25.264,
                        help="Fixed elevation in degrees")
    parser.add_argument("--width", type=int, default=1600, help="Render width")
    parser.add_argument("--height", type=int, default=1200, help="Render height")
    parser.add_argument("--num-views", type=int, default=100, help="Number of azimuth views")
    parser.add_argument("--save-views", nargs="+", type=int, default=[1, 33, 66],
                        help="1-based view indices to save as images")

    parser.add_argument("--camera-margin", type=float, default=1.05,
                        help="Margin for orthographic framing; smaller values make object larger")
    parser.add_argument("--radius-factor", type=float, default=1.45,
                        help="Camera distance as a multiple of bbox diagonal")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    run_pipeline(
        gt_path=args.gt,
        rm_path=args.rm,
        out_dir=args.out,
        mse_threshold_normalized=args.mse_threshold,
        elevation_deg=args.elevation,
        width=args.width,
        height=args.height,
        num_views=args.num_views,
        save_views=args.save_views,
        camera_margin=args.camera_margin,
        radius_factor=args.radius_factor
    )


if __name__ == "__main__":
    main()
