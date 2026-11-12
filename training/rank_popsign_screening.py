#!/usr/bin/env python3
"""Rank screened PopSign signs by train/validation tracking quality only."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path, PurePosixPath


def split_and_sign(video_path: str) -> tuple[str, str]:
    parts = PurePosixPath(video_path).parts
    for split in ("train", "val", "test"):
        if split in parts:
            index = parts.index(split)
            return split, parts[index + 1]
    raise ValueError(f"Could not determine split and sign from {video_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extraction_manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--weak-active-rate", type=float, default=0.60)
    args = parser.parse_args()

    extraction = json.loads(args.extraction_manifest.read_text(encoding="utf-8"))
    successes: dict[str, list[dict]] = defaultdict(list)
    failures: dict[str, list[dict]] = defaultdict(list)

    for item in extraction["videos"]:
        split, sign = split_and_sign(item["video"])
        if split in {"train", "val"}:
            successes[sign].append(item)
    for item in extraction.get("failures", []):
        split, sign = split_and_sign(item["video"])
        if split in {"train", "val"}:
            failures[sign].append(item)

    rankings = []
    for sign in sorted(set(successes) | set(failures)):
        items = successes[sign]
        rates = [float(item["activeDominantHandDetectionRate"]) for item in items]
        active_frames = [int(item["activeFrames"]) for item in items]
        ranking = {
            "sign": sign,
            "successfulClips": len(items),
            "failedClips": len(failures[sign]),
            "weakClips": sum(rate < args.weak_active_rate for rate in rates),
            "minimumActiveHandRate": min(rates) if rates else 0.0,
            "medianActiveHandRate": statistics.median(rates) if rates else 0.0,
            "medianActiveFrames": statistics.median(active_frames) if active_frames else 0.0,
        }
        rankings.append(ranking)

    rankings.sort(
        key=lambda item: (
            item["failedClips"],
            item["weakClips"],
            -item["minimumActiveHandRate"],
            -item["medianActiveHandRate"],
            item["sign"],
        )
    )
    report = {
        "selectionSplits": ["train", "val"],
        "testSplitUsed": False,
        "weakActiveRateThreshold": args.weak_active_rate,
        "rankings": rankings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
