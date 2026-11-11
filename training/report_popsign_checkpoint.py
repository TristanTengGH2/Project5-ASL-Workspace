#!/usr/bin/env python3
"""Summarize a bounded PopSign download and its landmark extraction quality."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path, PurePosixPath

import numpy as np


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot summarize an empty list")
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def distribution(values: list[float]) -> dict[str, float]:
    return {
        "minimum": min(values),
        "p10": percentile(values, 0.10),
        "median": statistics.median(values),
        "p90": percentile(values, 0.90),
        "maximum": max(values),
    }


def split_and_sign(video_path: str) -> tuple[str, str]:
    parts = PurePosixPath(video_path).parts
    for split in ("train", "val", "test"):
        if split in parts:
            index = parts.index(split)
            return split, parts[index + 1]
    raise ValueError(f"Could not determine split and sign from {video_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("download_manifest", type=Path)
    parser.add_argument("extraction_manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--weak-active-rate", type=float, default=0.60)
    args = parser.parse_args()

    download = json.loads(args.download_manifest.read_text(encoding="utf-8"))
    extraction = json.loads(args.extraction_manifest.read_text(encoding="utf-8"))
    downloads = download["downloads"]
    videos = extraction["videos"]
    failures = extraction.get("failures", [])

    downloaded_paths = {str(Path(item["localPath"]).resolve()) for item in downloads}
    extracted_paths = {str(Path(item["video"]).resolve()) for item in videos}
    failure_paths = {str(Path(item["video"]).resolve()) for item in failures}
    if extracted_paths & failure_paths:
        raise ValueError("A video cannot be both successfully extracted and failed")
    processed_paths = extracted_paths | failure_paths
    if downloaded_paths != processed_paths:
        missing = sorted(downloaded_paths - processed_paths)
        unexpected = sorted(processed_paths - downloaded_paths)
        raise ValueError(f"Manifest paths differ; missing={missing}, unexpected={unexpected}")

    signer_sets: dict[str, set[str]] = defaultdict(set)
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for item in downloads:
        signer_sets[item["split"]].add(item["signerId"])
        sign = item["signId"].rsplit(":", 1)[-1]
        counts[(item["split"], sign)] += 1

    downloaded_sign_ids = sorted({item["signId"] for item in downloads})
    expected_per_sign = sum(download["limits"].values())
    completed_sign_ids = sorted(
        sign_id
        for sign_id in downloaded_sign_ids
        if sum(item["signId"] == sign_id for item in downloads) == expected_per_sign
    )

    overlaps = {}
    split_names = ("train", "val", "test")
    for index, first in enumerate(split_names):
        for second in split_names[index + 1 :]:
            overlaps[f"{first}-{second}"] = sorted(signer_sets[first] & signer_sets[second])

    tensor_failures = []
    weak_counts: dict[tuple[str, str], int] = defaultdict(int)
    for item in videos:
        tensor_path = Path(item["tensor"])
        with np.load(tensor_path) as payload:
            tensor = payload["features"]
        if tensor.shape != (48, 167) or not np.isfinite(tensor).all():
            tensor_failures.append(item["video"])
        split, sign = split_and_sign(item["video"])
        if item["activeDominantHandDetectionRate"] < args.weak_active_rate:
            weak_counts[(split, sign)] += 1

    report = {
        "source": {
            "dataset": "PopSign ASL v1.0",
            "plannedSignCount": len(download["signIds"]),
            "downloadedSignCount": len(downloaded_sign_ids),
            "completedSignCount": len(completed_sign_ids),
            "completedSignIds": completed_sign_ids,
            "limits": download["limits"],
            "downloadedVideos": len(downloads),
            "downloadedBytes": sum(item["bytes"] for item in downloads),
        },
        "splitIntegrity": {
            "uniqueSigners": {split: len(signer_sets[split]) for split in split_names},
            "crossSplitSignerOverlaps": overlaps,
            "counts": {
                f"{split}/{sign}": count
                for (split, sign), count in sorted(counts.items())
            },
        },
        "extraction": {
            "contractVersion": extraction["contractVersion"],
            "handednessMode": extraction["handednessMode"],
            "successfulVideos": len(videos),
            "failedVideos": len(failures),
            "failuresByReason": dict(
                sorted(
                    (reason, sum(item["error"] == reason for item in failures))
                    for reason in {item["error"] for item in failures}
                )
            ),
            "decodedFrameMismatches": sum(
                item["sourceFramesReported"] != item["decodedFrames"] for item in videos
            ),
            "validFiniteTensors": len(videos) - len(tensor_failures),
            "tensorFailures": tensor_failures,
            "decodedFrames": distribution([float(item["decodedFrames"]) for item in videos]),
            "activeFrames": distribution([float(item["activeFrames"]) for item in videos]),
            "wholeClipHandDetectionRate": distribution(
                [float(item["handDetectionRate"]) for item in videos]
            ),
            "activeDominantHandDetectionRate": distribution(
                [float(item["activeDominantHandDetectionRate"]) for item in videos]
            ),
            "weakActiveRateThreshold": args.weak_active_rate,
            "weakActiveClips": sum(weak_counts.values()),
            "weakActiveClipsBySplitAndSign": {
                f"{split}/{sign}": weak_counts[(split, sign)]
                for (split, sign) in sorted(counts)
            },
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
