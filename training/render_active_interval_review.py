#!/usr/bin/env python3
"""Render local source-frame evidence for PopSign v2 active intervals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


DEFAULT_MANIFEST = Path(
    "training-artifacts/phase2-five-sign-v2-extraction/extraction-manifest.json"
)
DEFAULT_OUTPUT = Path(
    "training-artifacts/phase2-v2-active-interval-review/popsign-active-intervals.png"
)


def split_label(video_path: str) -> str:
    parts = Path(video_path).parts
    for index, part in enumerate(parts):
        if part in {"train", "val", "test"} and index + 1 < len(parts):
            return parts[index + 1]
    raise ValueError(f"Cannot derive label from {video_path}")


def representatives(videos: list[dict]) -> list[dict]:
    labels = sorted({split_label(item["video"]) for item in videos})
    selected = []
    for label in labels:
        candidates = [item for item in videos if split_label(item["video"]) == label]
        ratios = [item["activeFrames"] / item["decodedFrames"] for item in candidates]
        median = float(np.median(ratios))
        selected.append(
            min(candidates, key=lambda item: abs(item["activeFrames"] / item["decodedFrames"] - median))
        )
    longest = max(videos, key=lambda item: item["decodedFrames"])
    if longest not in selected:
        selected.append(longest)
    return selected


def read_frame(video_path: Path, timestamp_ms: float) -> np.ndarray:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open {video_path}")
    try:
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok:
        raise RuntimeError(f"Could not read {video_path} at {timestamp_ms:.1f} ms")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    selected = representatives(manifest["videos"])
    figure, axes = plt.subplots(len(selected), 3, figsize=(9, 2.2 * len(selected)), squeeze=False)
    for row, item in enumerate(selected):
        start = item["activeStartMs"]
        end = item["activeEndMs"]
        timestamps = (start, (start + end) / 2, end)
        label = split_label(item["video"])
        for column, (stage, timestamp) in enumerate(zip(("start", "middle", "end"), timestamps)):
            axes[row, column].imshow(read_frame(Path(item["video"]), timestamp))
            axes[row, column].axis("off")
            axes[row, column].set_title(f"{label} · {stage} · {timestamp / 1000:.2f}s")
        axes[row, 0].set_ylabel(
            f"{item['decodedFrames']} → {item['activeFrames']} frames",
            fontsize=10,
        )
    figure.suptitle(
        "Local PopSign active-interval review — identifiable source frames, do not commit",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=100)
    plt.close(figure)
    print(f"Review image: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
