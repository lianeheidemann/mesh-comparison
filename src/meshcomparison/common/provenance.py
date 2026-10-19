import datetime
import platform
import sys
from importlib import metadata


def _version(package):
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "not installed"


def collect_provenance():
    """Software environment of a run, to be stored next to its parameters so results can be reproduced.

    PyTorch is never imported here (the geometric pipeline does not need it); its CUDA version is only
    reported when the running pipeline has already loaded it.
    """
    torch = sys.modules.get("torch")
    cuda = getattr(getattr(torch, "version", None), "cuda", None)
    return {
        "project_version": _version("meshcomparison"),
        "python_version": platform.python_version(),
        "torch_version": _version("torch"),
        "torch_cuda_version": cuda if cuda else ("none" if torch is not None else "not loaded"),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
