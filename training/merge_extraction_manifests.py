#!/usr/bin/env python3
"""Combine extraction manifests (same contract, different signs) into one training manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifests = [json.loads(path.read_text(encoding="utf-8")) for path in args.manifests]
    for key in ("contractVersion", "contractSha256"):
        if len({manifest[key] for manifest in manifests}) != 1:
            raise ValueError(f"Manifests disagree on {key}; they cannot be combined")
    videos = [video for manifest in manifests for video in manifest["videos"]]
    names = [video["video"] for video in videos]
    if len(set(names)) != len(names):
        raise ValueError("A video appears in more than one manifest")
    combined = {key: value for key, value in manifests[0].items() if key not in ("videos", "failures")}
    combined["videos"] = videos
    combined["failures"] = [failure for manifest in manifests for failure in manifest.get("failures", [])]
    combined["combinedFrom"] = [str(path) for path in args.manifests]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")
    print(f"{len(videos)} videos, {len(combined['failures'])} recorded failures -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
