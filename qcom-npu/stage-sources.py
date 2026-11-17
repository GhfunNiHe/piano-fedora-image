#!/usr/bin/env python3
"""Stage the hash-locked source inputs for the QCOM NPU RPM build."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def valid(path: Path, row: dict) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == row["bytes"]
        and sha256(path) == row["sha256"]
    )


def download(row: dict, output: Path) -> None:
    target = output / row["filename"]
    if valid(target, row):
        print(f"cached {target.name}")
        return

    partial = target.with_name(target.name + ".partial")
    partial.unlink(missing_ok=True)
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(row["url"], timeout=120) as response:
                with partial.open("wb") as stream:
                    while chunk := response.read(1024 * 1024):
                        stream.write(chunk)
            if not valid(partial, row):
                raise RuntimeError(f"size or SHA256 mismatch for {target.name}")
            os.replace(partial, target)
            print(f"downloaded {target.name}")
            return
        except Exception:
            partial.unlink(missing_ok=True)
            if attempt == 5:
                raise
            time.sleep(attempt * 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    lock = json.loads(args.lock.read_text())
    inputs = lock["inputs"]
    rows = [
        row
        for row in [*inputs.values(), *inputs.get("build-dependencies", [])]
        if isinstance(row, dict)
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    for row in rows:
        download(row, args.output)


if __name__ == "__main__":
    main()
