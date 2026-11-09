#!/usr/bin/env python3
"""Evaluate a frozen temporal checkpoint against a separate extraction source."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

from train_temporal_model import SequenceGRU, evaluate, load_examples


DEFAULT_MODEL = Path("training-artifacts/google-five-sign-gru/gru-model.pt")
DEFAULT_MANIFEST = Path(
    "training-artifacts/phase2-five-sign-extraction-keep/extraction-manifest.json"
)
DEFAULT_OUTPUT = Path("training-artifacts/google-to-popsign-transfer.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_tensors(
    examples: list[dict], split: str, labels: list[str], mean: np.ndarray, scale: np.ndarray
) -> tuple[torch.Tensor, torch.Tensor, list[str]]:
    selected = [example for example in examples if example["split"] == split]
    unknown = sorted({example["label"] for example in selected} - set(labels))
    if unknown:
        raise RuntimeError(f"Transfer source has unknown labels: {', '.join(unknown)}")
    features = np.stack([(example["features"] - mean) / scale for example in selected])
    targets = np.array([labels.index(example["label"]) for example in selected], dtype=np.int64)
    videos = [example["video"] for example in selected]
    return torch.from_numpy(features), torch.from_numpy(targets), videos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    checkpoint = torch.load(args.model, map_location="cpu", weights_only=False)
    labels = checkpoint["labels"]
    mean = checkpoint["mean"].astype(np.float32)
    scale = checkpoint["scale"].astype(np.float32)
    input_shape = checkpoint["inputShape"]
    model = SequenceGRU(input_shape[1], checkpoint["hiddenSize"], len(labels), dropout=0.0)
    model.load_state_dict(checkpoint["stateDict"])
    model.eval()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    examples = load_examples(manifest)
    source_labels = sorted({example["label"] for example in examples})
    if source_labels != sorted(labels):
        raise RuntimeError(
            f"Transfer labels {source_labels} do not match model labels {sorted(labels)}"
        )
    splits = sorted({example["split"] for example in examples})
    loss_function = nn.CrossEntropyLoss()
    tensors = {
        split: split_tensors(examples, split, labels, mean, scale) for split in splits
    }
    evaluations = {
        split: evaluate(model, *tensors[split], labels, loss_function) for split in splits
    }
    all_features = torch.cat([tensors[split][0] for split in splits])
    all_targets = torch.cat([tensors[split][1] for split in splits])
    all_videos = sum([tensors[split][2] for split in splits], [])
    evaluations["all"] = evaluate(
        model, all_features, all_targets, all_videos, labels, loss_function
    )
    report = {
        "status": "diagnostic-only",
        "model": {"path": str(args.model), "sha256": sha256(args.model)},
        "transferManifest": {
            "path": str(args.manifest),
            "sha256": sha256(args.manifest),
        },
        "labels": labels,
        "note": (
            "The model was frozen after Google-landmark training. PopSign examples were "
            "not used for fitting or threshold selection; this is a cross-source diagnostic."
        ),
        "evaluations": evaluations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for split in (*splits, "all"):
        result = evaluations[split]
        print(f"{split}: {result['examples']} examples; top-1 {result['top1Accuracy']:.1%}")
    print(f"All-source confusion: {evaluations['all']['confusion']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
