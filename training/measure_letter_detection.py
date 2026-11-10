#!/usr/bin/env python3
"""Measure how often MediaPipe finds a hand in a sample of a letter-image archive.

Reads images straight from the zip (nothing is extracted or executed) and runs the same
Hand Landmarker model file the browser uses, in image mode. Reports, per letter, the share
of sampled images with one or two hands found. This is a feasibility check on whether the
archive can produce landmark training data; it does not train or evaluate a classifier.
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision
from PIL import Image

HAND_MODEL = Path("app/public/models/hand_landmarker.task")


def letter_of(path: str) -> str | None:
    for segment in reversed(path.split("/")[:-1]):
        if re.fullmatch(r"[A-Za-z]", segment):
            return segment.upper()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prefix", default="", help="Only use members under this folder, e.g. Train/")
    parser.add_argument("--per-letter", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    zf = zipfile.ZipFile(args.archive)
    by_letter: dict[str, list[str]] = defaultdict(list)
    for info in zf.infolist():
        name = info.filename
        if info.is_dir() or name.startswith("__MACOSX") or not name.lower().endswith(".jpg"):
            continue
        if ".." in name.split("/") or name.startswith("/") or not name.startswith(args.prefix):
            continue
        letter = letter_of(name)
        if letter:
            by_letter[letter].append(name)

    options = vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(HAND_MODEL)),
        running_mode=vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.4,
        min_hand_presence_confidence=0.4,
    )
    rng = random.Random(args.seed)
    report: dict[str, dict] = {}
    with vision.HandLandmarker.create_from_options(options) as landmarker:
        for letter in sorted(by_letter):
            pool = by_letter[letter]
            sample = rng.sample(pool, min(args.per_letter, len(pool)))
            counts = {"images": len(sample), "oneHand": 0, "twoHands": 0, "none": 0}
            for name in sample:
                rgb = np.asarray(Image.open(io.BytesIO(zf.read(name))).convert("RGB"))
                result = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
                found = len(result.hand_landmarks)
                counts["none" if found == 0 else "oneHand" if found == 1 else "twoHands"] += 1
            counts["detectionRate"] = 1 - counts["none"] / counts["images"]
            report[letter] = counts
            print(f"{letter}: {counts['detectionRate']:.0%} of {counts['images']}", flush=True)

    total = sum(c["images"] for c in report.values())
    found = sum(c["images"] - c["none"] for c in report.values())
    summary = {
        "archive": str(args.archive),
        "prefix": args.prefix,
        "sampledImages": total,
        "overallDetectionRate": found / total,
        "perLetter": report,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    weakest = sorted(report.items(), key=lambda item: item[1]["detectionRate"])[:5]
    print(f"overall {found / total:.1%} of {total} images; weakest:", [(k, round(v["detectionRate"], 2)) for k, v in weakest])
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
