#!/usr/bin/env python3
"""Extract hand-landmark features for fingerspelling letters from a zip of JPG images.

Images are read directly from the archive (nothing is extracted or executed). The feature
vector is the 21 hand landmarks of the first detected hand, converted to pixel units so image
shape does not distort proportions, translated to the wrist, and divided by palm size. Images
with no detected hand are counted and skipped. The same recipe must be used in the browser.
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
# Letters present in both candidate datasets; J and Z need motion and are excluded.
LETTERS = "ABCDEFGHIKLMNOPQRSTUVWXY"


def letter_of(path: str) -> str | None:
    for segment in reversed(path.split("/")[:-1]):
        if re.fullmatch(r"[A-Za-z]", segment):
            return segment.upper()
    return None


def hand_features(hand: np.ndarray) -> np.ndarray | None:
    """hand: (21, 3) in pixel units. Returns 63 wrist-relative, palm-scaled values."""
    wrist = hand[0]
    palm = float(np.mean([np.linalg.norm(hand[i, :2] - wrist[:2]) for i in (5, 9, 17)]))
    if palm <= 1e-6 or not np.isfinite(hand).all():
        return None
    return ((hand - wrist) / palm).reshape(-1).astype(np.float32)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--per-letter", type=int, required=True)
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
        if letter in LETTERS:
            by_letter[letter].append(name)

    options = vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(HAND_MODEL)),
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.4,
        min_hand_presence_confidence=0.4,
    )
    rng = random.Random(args.seed)
    features, labels, names, handedness = [], [], [], []
    missed = defaultdict(int)
    sampled = defaultdict(int)
    with vision.HandLandmarker.create_from_options(options) as landmarker:
        for letter in LETTERS:
            pool = sorted(by_letter[letter])
            for name in rng.sample(pool, min(args.per_letter, len(pool))):
                sampled[letter] += 1
                image = Image.open(io.BytesIO(zf.read(name))).convert("RGB")
                width, height = image.size
                result = landmarker.detect(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(image))
                )
                if not result.hand_landmarks:
                    missed[letter] += 1
                    continue
                hand = np.array([[p.x * width, p.y * height, p.z * width] for p in result.hand_landmarks[0]])
                vector = hand_features(hand)
                if vector is None:
                    missed[letter] += 1
                    continue
                features.append(vector)
                labels.append(letter)
                names.append(name)
                handedness.append(result.handedness[0][0].category_name)
            print(f"{letter}: kept {sampled[letter] - missed[letter]} of {sampled[letter]}", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        features=np.stack(features),
        labels=np.array(labels),
        names=np.array(names),
        handedness=np.array(handedness),
        sampled_per_letter=np.array([sampled[l] for l in LETTERS]),
        missed_per_letter=np.array([missed[l] for l in LETTERS]),
    )
    meta = {
        "archive": str(args.archive),
        "prefix": args.prefix,
        "seed": args.seed,
        "letters": LETTERS,
        "sampled": int(sum(sampled.values())),
        "kept": len(labels),
        "handednessCounts": {h: handedness.count(h) for h in sorted(set(handedness))},
    }
    args.output.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
