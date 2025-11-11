from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from shutil import which


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate frontend documentation with Compodoc."
    )
    parser.add_argument(
        "--project",
        default="merkaz-frontend/tsconfig.app.json",
        help="Path to the Angular tsconfig file (default: merkaz-frontend/tsconfig.app.json).",
    )
    parser.add_argument(
        "--output-dir",
        default="documentation/autogen/merkaz-frontend",
        help="Directory where Compodoc should place the generated files.",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Do not remove the output directory before generation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_path = Path(args.project)
    output_dir = Path(args.output_dir)

    if not args.skip_clean:
        shutil.rmtree(output_dir, ignore_errors=True)

    output_dir.mkdir(parents=True, exist_ok=True)

    npx_executable = which("npx")
    if not npx_executable:
        raise RuntimeError(
            "Unable to locate 'npx'. Ensure Node.js is installed and available on PATH."
        )

    cmd = [
        npx_executable,
        "compodoc",
        "-p",
        str(project_path),
        "-d",
        str(output_dir),
        "--disableCoverage",
        "--minimal",
        "--silent",
    ]

    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

