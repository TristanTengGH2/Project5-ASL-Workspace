#!/usr/bin/env python3
"""Evaluate deterministic nearest-neighbor baselines on extracted tensors."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np


DEFAULT_MANIFEST = Path("training-artifacts/phase2-two-sign-extraction/extraction-manifest.json")
DEFAULT_OUTPUT = Path("training-artifacts/phase2-two-sign-baseline")
SPLITS = {"train", "val", "test"}


def split_and_label(video_path: str) -> tuple[str, str]:
    parts = Path(video_path).parts
    for index, part in enumerate(parts):
        if part in SPLITS and index + 1 < len(parts):
            return part, parts[index + 1]
    raise ValueError(f"Could not derive split and label from {video_path}")


def load_examples(manifest: dict) -> list[dict]:
    examples = []
    for item in manifest["videos"]:
        split, label = split_and_label(item["video"])
        with np.load(item["tensor"]) as archive:
            features = archive["features"].astype(np.float32)
        examples.append({"split": split, "label": label, "video": item["video"], "features": features})
    return examples


def standardizer(train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    flattened_frames = train.reshape(-1, train.shape[-1])
    mean = flattened_frames.mean(axis=0)
    scale = flattened_frames.std(axis=0)
    scale[scale < 1e-5] = 1.0
    return mean, scale


def distances(query: np.ndarray, references: np.ndarray) -> np.ndarray:
    return np.mean((references - query[None, ...]) ** 2, axis=(1, 2))


def ranked_labels_nearest(
    query: np.ndarray, train: np.ndarray, train_labels: list[str], labels: list[str]
) -> tuple[list[str], dict[str, float]]:
    all_distances = distances(query, train)
    by_class = {
        label: float(np.min(all_distances[np.array(train_labels) == label])) for label in labels
    }
    return sorted(labels, key=by_class.get), by_class


def ranked_labels_centroid(
    query: np.ndarray, centroids: dict[str, np.ndarray], labels: list[str]
) -> tuple[list[str], dict[str, float]]:
    by_class = {
        label: float(np.mean((centroids[label] - query) ** 2)) for label in labels
    }
    return sorted(labels, key=by_class.get), by_class


def evaluate(name: str, validation: list[dict], ranker) -> dict:
    rows = []
    for example in validation:
        ranking, class_distances = ranker(example["features"])
        rows.append(
            {
                "video": example["video"],
                "expected": example["label"],
                "predicted": ranking[0],
                "ranking": ranking,
                "classDistances": class_distances,
            }
        )
    correct = sum(row["expected"] == row["predicted"] for row in rows)
    labels = sorted({row["expected"] for row in rows})
    confusion = {
        expected: {
            predicted: sum(
                row["expected"] == expected and row["predicted"] == predicted for row in rows
            )
            for predicted in labels
        }
        for expected in labels
    }
    return {
        "name": name,
        "examples": len(rows),
        "top1Accuracy": correct / len(rows),
        "topK": min(5, len(labels)),
        "topKAccuracy": sum(row["expected"] in row["ranking"][:5] for row in rows) / len(rows),
        "confusion": confusion,
        "predictions": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    examples = load_examples(manifest)
    train_examples = [item for item in examples if item["split"] == "train"]
    validation_examples = [item for item in examples if item["split"] == "val"]
    labels = sorted({item["label"] for item in train_examples})
    if len(labels) < 2:
        raise RuntimeError("At least two training labels are required")
    if set(labels) != {item["label"] for item in validation_examples}:
        raise RuntimeError("Training and validation labels do not match")

    train = np.stack([item["features"] for item in train_examples])
    mean, scale = standardizer(train)
    train = (train - mean) / scale
    for item in validation_examples:
        item["features"] = (item["features"] - mean) / scale
    train_labels = [item["label"] for item in train_examples]
    centroids = {
        label: train[np.array(train_labels) == label].mean(axis=0) for label in labels
    }

    nearest = evaluate(
        "one-nearest-neighbor",
        validation_examples,
        lambda query: ranked_labels_nearest(query, train, train_labels, labels),
    )
    centroid = evaluate(
        "class-centroid",
        validation_examples,
        lambda query: ranked_labels_centroid(query, centroids, labels),
    )

    encoded_missing_frame = (np.zeros_like(mean) - mean) / scale
    synthetic_inputs = {
        "all-zero-idle": np.tile(encoded_missing_frame, (train.shape[1], 1)),
        "pose-only-missing-hands": train[0].copy(),
        "alternating-hand-loss": train[0].copy(),
    }
    synthetic_inputs["pose-only-missing-hands"][:, :136] = encoded_missing_frame[:136]
    synthetic_inputs["alternating-hand-loss"][::2, :136] = encoded_missing_frame[:136]
    synthetic_results = {}
    for name, tensor in synthetic_inputs.items():
        ranking, class_distances = ranked_labels_nearest(tensor, train, train_labels, labels)
        synthetic_results[name] = {
            "nearestClass": ranking[0],
            "classDistances": class_distances,
            "rejected": False,
            "note": "No rejection threshold is fitted in this feasibility baseline.",
        }

    report = {
        "status": "preliminary-two-class-smoke-test",
        "warning": "Two classes and five training examples per class cannot establish usable ASL recognition accuracy.",
        "contractVersion": manifest["contractVersion"],
        "tensorShape": list(train.shape[1:]),
        "splitCounts": {
            split: dict(Counter(item["label"] for item in examples if item["split"] == split))
            for split in ("train", "val", "test")
        },
        "evaluations": [nearest, centroid],
        "syntheticNegativeBehavior": synthetic_results,
        "export": {
            "attempted": False,
            "reason": "The five-sign held-out gate is incomplete and this baseline has no unknown-sign rejection.",
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "evaluation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    model_path = args.output / "nearest-neighbor-model.npz"
    np.savez_compressed(
        model_path,
        train=train,
        train_labels=np.array(train_labels),
        mean=mean,
        scale=scale,
    )
    print(f"Train: {report['splitCounts']['train']}")
    print(f"Validation: {report['splitCounts']['val']}")
    for result in report["evaluations"]:
        print(f"{result['name']}: top-1 {result['top1Accuracy']:.1%} ({result['examples']} examples)")
        print(f"  confusion: {result['confusion']}")
    print("Synthetic negatives: not rejected (no threshold fitted)")
    print(f"Report: {report_path}")
    print(f"Model: {model_path} ({model_path.stat().st_size / 1000:.1f} kB)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
