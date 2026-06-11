#!/usr/bin/env python3
"""Launch JupyterLab or Voila for the dstatemachine app."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK = "App.ipynb"


def has_credentials() -> bool:
    return (ROOT / "data/.credentials").exists() and (ROOT / ".salt").exists()


def require_command(command: str, install_hint: str) -> str:
    local_executable = Path(sys.executable).parent / command
    if local_executable.exists():
        return str(local_executable)

    executable = shutil.which(command)
    if executable:
        return executable

    print(f"Missing executable: {command}", file=sys.stderr)
    print(install_hint, file=sys.stderr)
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run dstatemachine through JupyterLab or Voila."
    )
    parser.add_argument(
        "mode",
        choices=("lab", "voila"),
        help="Server type to start.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address. Use 0.0.0.0 only behind trusted network controls.",
    )
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument(
        "--notebook",
        default=DEFAULT_NOTEBOOK,
        help="Notebook to serve in Voila mode.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser automatically.",
    )
    parser.add_argument(
        "--allow-missing-credentials",
        action="store_true",
        help="Start even if data/.credentials and .salt are missing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cache_dir = ROOT / ".cache"
    for path in [
        cache_dir / "matplotlib",
        cache_dir / "jupyter-config",
        cache_dir / "jupyter-data",
        cache_dir / "jupyter-runtime",
        cache_dir / "ipython",
        cache_dir / "xdg",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    if not has_credentials() and not args.allow_missing_credentials:
        print(
            "Missing credentials. Run `.venv/bin/python scripts/init_credentials.py` first.",
            file=sys.stderr,
        )
        return 2

    if args.mode == "lab":
        jupyter = require_command(
            "jupyter",
            "Install dependencies first, for example: `python3 -m pip install -r requirements.txt`.",
        )
        cmd = [jupyter, "lab", "--ip", args.host]
        if args.port is not None:
            cmd += ["--port", str(args.port)]
        if args.no_browser:
            cmd.append("--no-browser")
    else:
        voila = require_command(
            "voila",
            "Install dependencies first, for example: `python3 -m pip install -r requirements.txt`.",
        )
        notebook = ROOT / args.notebook
        if not notebook.exists():
            print(f"Notebook not found: {notebook}", file=sys.stderr)
            return 2
        cmd = [voila, str(notebook), "--Voila.ip", args.host]
        if args.port is not None:
            cmd += ["--port", str(args.port)]
        if args.no_browser:
            cmd.append("--no-browser")

    print("Starting:", " ".join(cmd))
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", str(cache_dir / "matplotlib"))
    env.setdefault("JUPYTER_CONFIG_DIR", str(cache_dir / "jupyter-config"))
    env.setdefault("JUPYTER_DATA_DIR", str(cache_dir / "jupyter-data"))
    env.setdefault("JUPYTER_RUNTIME_DIR", str(cache_dir / "jupyter-runtime"))
    env.setdefault("IPYTHONDIR", str(cache_dir / "ipython"))
    env.setdefault("XDG_CACHE_HOME", str(cache_dir / "xdg"))
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
