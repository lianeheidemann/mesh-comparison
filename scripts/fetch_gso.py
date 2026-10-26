# Downloads the selected Google Scanned Objects (data/gso/selection.csv) from Gazebo Fuel and writes their manifest.
"""
Usage (from the repository root; needs access to fuel.gazebosim.org):

    python scripts/fetch_gso.py [--selection data/gso/selection.csv] [--out gt/gso] [--count 20]

Takes the ``primary`` objects of the selection in rank order; an object that cannot be found or downloaded is
replaced by the next ``alternate`` and the replacement is recorded. Each object is extracted to
``<out>/<name>/`` (GT mesh: ``meshes/model.obj``), and ``<out>/manifest.csv`` is written with the source, URL,
author and license read from Fuel. Then check the meshes:

    python scripts/check_gt.py --manifest gt/gso/manifest.csv --out gt/gso/gt_report.csv
"""
import argparse
import io
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import pandas as pd

API = "https://fuel.gazebosim.org/1.0"
OWNER = "GoogleResearch"
MANIFEST_COLUMNS = ("object_id", "file", "source", "url", "author", "license", "published_date", "category",
                    "selection_reason", "cleanup_notes", "input_azimuth_deg", "input_elevation_deg")
DATE_KEYS = ("upload_date", "createdAt", "created_at", "modify_date", "updatedAt")


def _get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def model_url(name):
    return f"{API}/{OWNER}/models/{urllib.parse.quote(name)}"


def zip_urls(name):
    """Download URLs to try in order (latest version first)."""
    quoted = urllib.parse.quote(name)
    return [f"{model_url(name)}.zip", f"{model_url(name)}/tip/{quoted}.zip", f"{model_url(name)}/1/{quoted}.zip"]


def metadata(name, get=None):
    """Fuel metadata of the model, or ``None`` if Fuel answers 404; other errors (no network) propagate."""
    try:
        return json.loads((get or _get)(model_url(name)))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def fix_texture_paths(model_dir):
    """Copy each texture an ``.mtl`` names but cannot find next to it (GSO keeps them in materials/textures/)."""
    copied = []
    for root, _, names in os.walk(model_dir):
        for mtl in (n for n in names if n.lower().endswith(".mtl")):
            with open(os.path.join(root, mtl), encoding="utf-8", errors="replace") as f:
                maps = [line.split()[-1] for line in f if line.strip().lower().startswith("map_")]
            for texture in maps:
                target = os.path.join(root, texture)
                if os.path.isfile(target):
                    continue
                for src_root, _, src_names in os.walk(model_dir):
                    if os.path.basename(texture) in src_names:
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        shutil.copy(os.path.join(src_root, os.path.basename(texture)), target)
                        copied.append(target)
                        break
    return copied


def download(name, out_dir, get=None):
    """Extract the model into ``out_dir/name``; returns the path of its OBJ mesh (raises if none works)."""
    errors = []
    for url in zip_urls(name):
        try:
            data = (get or _get)(url)
            archive = zipfile.ZipFile(io.BytesIO(data))
            break
        except Exception as exc:  # try the next URL form
            errors.append(f"{url}: {exc}")
    else:
        raise RuntimeError("; ".join(errors))
    model_dir = os.path.join(out_dir, name)
    root = os.path.realpath(model_dir)
    for member in archive.namelist():  # refuse paths that would leave the model folder
        if not os.path.realpath(os.path.join(model_dir, member)).startswith(root + os.sep):
            raise RuntimeError(f"unsafe path in archive: {member}")
    archive.extractall(model_dir)
    fix_texture_paths(model_dir)
    objs = sorted(os.path.join(r, n) for r, _, ns in os.walk(model_dir) for n in ns if n.lower().endswith(".obj"))
    if not objs:
        raise RuntimeError("no .obj mesh in the archive")
    return objs[0]


def manifest_row(row, meta, mesh_path, manifest_dir, note=""):
    """One manifest row; license, author and date come from Fuel and stay empty when Fuel does not give them."""
    date = next((str(meta[k])[:10] for k in DATE_KEYS if meta.get(k)), "")
    return {
        "object_id": f"gso_{row['gso_name']}",
        "file": os.path.relpath(mesh_path, manifest_dir).replace(os.sep, "/"),
        "source": "Google Scanned Objects",
        "url": f"https://app.gazebosim.org/{OWNER}/fuel/models/{urllib.parse.quote(row['gso_name'])}",
        "author": meta.get("owner", OWNER),
        "license": meta.get("license_name") or meta.get("license") or "",
        "published_date": date,
        "category": row["category"],
        "selection_reason": row["selection_reason"] + (f" ({note})" if note else ""),
        "cleanup_notes": "",
        "input_azimuth_deg": "",
        "input_elevation_deg": "",
    }


def fetch(selection, out_dir, count, get=None):
    """Download up to ``count`` objects (primaries, then alternates); returns ``(manifest rows, skipped)``."""
    selection = selection.sort_values("rank")
    queue = pd.concat([selection[selection["role"] == "primary"], selection[selection["role"] == "alternate"]])
    rows, skipped, to_replace = [], [], []
    for _, row in queue.iterrows():
        if len(rows) == count:
            break
        name = row["gso_name"]
        meta = metadata(name, get)
        reason = "not found on Fuel" if meta is None else ""
        if not reason:
            try:
                mesh = download(name, out_dir, get)
            except Exception as exc:
                reason = f"download failed: {exc}"
        if reason:
            skipped.append((name, reason))
            if row["role"] == "primary":
                to_replace.append(name)
            continue
        note = f"replaces {to_replace.pop(0)}" if row["role"] == "alternate" and to_replace else ""
        rows.append(manifest_row(row, meta, mesh, out_dir, note))
        print(f"ok    {name}")
    return rows, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selection", default=os.path.join("data", "gso", "selection.csv"))
    parser.add_argument("--out", default=os.path.join("gt", "gso"))
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    try:
        rows, skipped = fetch(pd.read_csv(args.selection), args.out, args.count)
    except (urllib.error.URLError, OSError) as exc:
        print(f"Cannot reach {API}: {exc}", file=sys.stderr)
        return 2
    for name, reason in skipped:
        print(f"skip  {name}: {reason}")
    manifest = os.path.join(args.out, "manifest.csv")
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(manifest, index=False)
    print(f"\n{len(rows)}/{args.count} objects -> {manifest}")
    return 0 if len(rows) == args.count else 1


if __name__ == "__main__":
    sys.exit(main())
