#!/usr/bin/env python3
"""Render what the tracker found for one sign's held-out clips, split by right and wrong.

Reads Google landmark parquet sequences (landmarks only, no video) and a trained model's
evaluation report. Writes two Git-ignored images:
  timeline   per source frame, which hands and body points were detected, with the
             trimmed active interval shaded
  skeletons  hands and shoulders/arms at the middle of each active interval

The images contain only landmark points, but they come from real participants, so they stay
in the ignored training-artifacts directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from import_google_landmarks import frame_landmarks, read_parquet  # noqa: E402

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11),
    (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]
ARM_CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]


def collect(manifest: Path, evaluation: Path, sign: str, split: str) -> list[dict]:
    videos = {v["video"]: v for v in json.loads(manifest.read_text())["videos"]}
    report = json.loads(evaluation.read_text())[split]["predictions"]
    clips = []
    for row in report:
        if row["expected"] != sign:
            continue
        entry = videos[row["video"]]
        frames = frame_landmarks(read_parquet(Path(entry["source"])))
        clips.append(
            {
                "correct": row["predicted"] == sign,
                "predicted": row["predicted"],
                "entry": entry,
                "frames": frames,
            }
        )
    return sorted(clips, key=lambda c: (not c["correct"], c["entry"]["activeFrames"]))


def present(landmarks: dict, key: str, count: int) -> bool:
    points = landmarks.get(key)
    return points is not None and points.shape[0] == count and bool(np.isfinite(points).all())


def draw_timeline(clips: list[dict], sign: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 0.34 * len(clips) + 1.5))
    for row, clip in enumerate(clips):
        for frame_index, landmarks in clip["frames"]:
            if present(landmarks, "left_hand", 21):
                ax.plot(frame_index, row + 0.18, "s", color="#1f77b4", ms=3)
            if present(landmarks, "right_hand", 21):
                ax.plot(frame_index, row - 0.18, "s", color="#e8756a", ms=3)
            if present(landmarks, "pose", 33):
                ax.plot(frame_index, row, ".", color="#999999", ms=2)
        start, end = clip["entry"]["activeSourceStart"], clip["entry"]["activeSourceEnd"]
        ax.axvspan(start - 0.5, end + 0.5, ymin=0, ymax=1, color="#cccccc", alpha=0.25, lw=0)
        ax.fill_betweenx([row - 0.45, row + 0.45], start - 0.5, end + 0.5, color="#ffe9a8", alpha=0.7)
    ax.set_yticks(range(len(clips)))
    ax.set_yticklabels(
        [
            f"{'RIGHT' if c['correct'] else 'wrong'} -> {c['predicted']} "
            f"(active {c['entry']['activeFrames']} of {c['entry']['decodedFrames']})"
            for c in clips
        ],
        fontsize=7,
    )
    ax.invert_yaxis()
    ax.set_xlabel("source frame")
    ax.set_title(
        f"'{sign}' held-out clips: blue square = left hand found, coral = right hand found, "
        f"grey dot = body found, yellow = trimmed active interval",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def draw_skeletons(clips: list[dict], sign: str, path: Path) -> None:
    columns = 5
    rows = int(np.ceil(len(clips) / columns))
    fig, axes = plt.subplots(rows, columns, figsize=(2.3 * columns, 2.6 * rows))
    for ax in np.atleast_1d(axes).ravel():
        ax.axis("off")
    for ax, clip in zip(np.atleast_1d(axes).ravel(), clips):
        start, end = clip["entry"]["activeSourceStart"], clip["entry"]["activeSourceEnd"]
        middle = (start + end) / 2
        frame_index, landmarks = min(clip["frames"], key=lambda f: abs(f[0] - middle))
        pose = landmarks.get("pose")
        if pose is not None and pose.shape[0] == 33:
            for a, b in ARM_CONNECTIONS:
                ax.plot(pose[[a, b], 0], pose[[a, b], 1], color="#999999", lw=1.2)
        for key, color in (("left_hand", "#1f77b4"), ("right_hand", "#e8756a")):
            hand = landmarks.get(key)
            if hand is None or hand.shape[0] != 21:
                continue
            for a, b in HAND_CONNECTIONS:
                ax.plot(hand[[a, b], 0], hand[[a, b], 1], color=color, lw=1.2)
        ax.set_xlim(0, 1)
        ax.set_ylim(1.1, -0.1)
        ax.set_aspect("equal")
        ax.axis("on")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(
            f"{'RIGHT' if clip['correct'] else 'wrong'} -> {clip['predicted']}\n"
            f"frame {int(frame_index)}, active {clip['entry']['activeFrames']}",
            fontsize=7,
            color="#1a7a1a" if clip["correct"] else "#b02020",
        )
    fig.suptitle(
        f"'{sign}' held-out clips at the middle of the active interval (blue left hand, coral right hand, grey arms)",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sign", default="puppy")
    parser.add_argument("--split", default="test")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("training-artifacts/google-five-sign-v2c-extraction/extraction-manifest.json"),
    )
    parser.add_argument(
        "--evaluation",
        type=Path,
        default=Path("training-artifacts/google-five-sign-gru-v2c/evaluation.json"),
    )
    parser.add_argument("--output", type=Path, default=Path("training-artifacts/tracked-sequences"))
    args = parser.parse_args()

    clips = collect(args.manifest, args.evaluation, args.sign, args.split)
    args.output.mkdir(parents=True, exist_ok=True)
    timeline = args.output / f"{args.sign}-{args.split}-timeline.png"
    skeletons = args.output / f"{args.sign}-{args.split}-skeletons.png"
    draw_timeline(clips, args.sign, timeline)
    draw_skeletons(clips, args.sign, skeletons)
    print(f"{len(clips)} clips ({sum(c['correct'] for c in clips)} right)")
    print(timeline)
    print(skeletons)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
