#!/usr/bin/env python3
"""Build the app's "How to sign" landmark animations from extracted PopSign tensors.

For each supported sign, pick the training clip whose standardized features sit closest to
the class mean (a medoid) among clips with dense dominant-hand tracking, and store its
48-frame dominant-hand skeleton. Only landmark coordinates are written: no video, no
signer identifier, no file name.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from train_temporal_model import drop_body_anchors, drop_v3_head_offsets, load_examples

# Palm length in shoulder widths. Contract tensors store hand shape in palm units and the
# wrist in shoulder units, so absolute hand size is not recoverable; this is a schematic
# proportion (adult palm about a quarter of the shoulder width).
PALM_IN_SHOULDER_WIDTHS = 0.25
MINIMUM_DOMINANT_RATE = 0.85
FRAMES = 48


def hand_points(frame: np.ndarray) -> np.ndarray:
    """Dominant-hand skeleton for one 134-wide frame, in shoulder widths (x right, y down)."""
    local = frame[:63].reshape(21, 3)[:, :2] * PALM_IN_SHOULDER_WIDTHS
    wrist = frame[63:65]
    return local + wrist


def fill_gaps(points: np.ndarray, present: np.ndarray) -> np.ndarray:
    """Hold the nearest tracked pose across frames where the hand was lost."""
    filled = points.copy()
    indexes = np.flatnonzero(present)
    for frame in range(len(filled)):
        if not present[frame]:
            nearest = indexes[np.argmin(np.abs(indexes - frame))]
            filled[frame] = points[nearest]
    return filled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="+", type=Path, help="Contract-v3 extraction manifests")
    parser.add_argument("--catalog", type=Path, default=Path("catalog/sign-catalog.json"))
    parser.add_argument("--output", type=Path, default=Path("catalog/sign-references.json"))
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    supported = {
        sign["displayGloss"]: sign["id"] for sign in catalog["signs"] if sign["status"] == "supported"
    }
    examples = []
    rates = {}
    for manifest_path in args.manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if int(manifest["contractVersion"]) != 3:
            raise ValueError(f"{manifest_path}: contract v3 manifest required")
        rates.update({item["video"]: item["activeDominantHandDetectionRate"] for item in manifest["videos"]})
        for example in load_examples(manifest):
            example["features"] = drop_body_anchors(drop_v3_head_offsets(example["features"]))
            examples.append(example)
    train = [e for e in examples if e["split"] == "train" and e["label"] in supported]
    stack = np.stack([e["features"] for e in train])
    frames = stack.reshape(-1, stack.shape[-1])
    mean = frames.mean(axis=0)
    scale = frames.std(axis=0)
    scale[scale < 1e-6] = 1.0

    # Recorded two-hand references (see merge_reference_takes.py) must survive a PopSign rebuild.
    kept = {}
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        kept = {key: value for key, value in previous["signs"].items() if value.get("provenance") == "recorded"}
    recorded_attribution = json.loads(args.output.read_text(encoding="utf-8")).get("recordedAttribution") if kept else None

    references = {}
    for label, sign_id in sorted(supported.items()):
        if sign_id in kept:
            references[sign_id] = kept[sign_id]
            print(f"{label:9s} keeping recorded reference")
            continue
        group = [e for e in train if e["label"] == label and rates.get(e["video"], 0) >= MINIMUM_DOMINANT_RATE]
        if not group:
            raise ValueError(f"No dense dominant-hand training clip for {label}")
        standardized = np.stack([(e["features"] - mean) / scale for e in group])
        centre = standardized.mean(axis=0)
        distances = np.sqrt(((standardized - centre) ** 2).mean(axis=(1, 2)))
        chosen = group[int(np.argmin(distances))]
        features = chosen["features"]
        present = features[:, 66] > 0
        points = np.stack([hand_points(frame) for frame in features])
        points = fill_gaps(points, present)
        references[sign_id] = {
            "gloss": label,
            "provenance": "popsign",
            "clipsConsidered": len(group),
            "trackedFrameRate": round(float(present.mean()), 2),
            "frames": np.round(points.astype(np.float64).reshape(FRAMES, 42), 3).tolist(),
        }
        print(f"{label:9s} medoid of {len(group):2d} clips, tracked {present.mean():.0%}")

    output = {
        "schemaVersion": 1,
        "frames": FRAMES,
        "points": 21,
        "units": "shoulder widths; x right and y down in the unmirrored camera image, dominant hand in right-hand coordinates",
        "palmInShoulderWidths": PALM_IN_SHOULDER_WIDTHS,
        "attribution": "Hand landmarks derived from PopSign ASL v1.0 (Georgia Institute of Technology and Deaf Professional Arts Network; Starner et al., NeurIPS 2023), CC BY 4.0.",
        "signs": references,
    }
    if recorded_attribution:
        output["recordedAttribution"] = recorded_attribution
    args.output.write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size / 1000:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
