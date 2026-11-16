#!/usr/bin/env python3
"""Replay a browser landmark tensor and compare it with PopSign references."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from train_temporal_model import SequenceGRU, drop_body_anchors, drop_v3_head_offsets, load_examples


BODY_ANCHORS = 11


def tensor_metrics(tensor: np.ndarray, hand_features: int) -> dict:
    presence_index = hand_features - 1
    body_offset = hand_features * 2
    dominant = tensor[:, presence_index] > 0
    non_dominant = tensor[:, hand_features + presence_index] > 0
    detected = tensor[dominant]
    wrist_path = (
        float(np.linalg.norm(np.diff(detected[:, 63:65], axis=0), axis=1).sum())
        if len(detected) > 1
        else 0.0
    )
    body_presence = tensor[:, body_offset + 2 :: 3] if tensor.shape[1] > body_offset else np.zeros((1, 1))
    return {
        "dominantPresenceRate": float(dominant.mean()),
        "nonDominantPresenceRate": float(non_dominant.mean()),
        "twoHandPresenceRate": float((dominant & non_dominant).mean()),
        "bodyAnchorPresenceRate": float(body_presence.mean()),
        "dominantWristPath": wrist_path,
        "dominantWristMedianX": float(np.median(detected[:, 63])) if len(detected) else None,
        "dominantWristMedianY": float(np.median(detected[:, 64])) if len(detected) else None,
    }


def summarize(values: list[float]) -> dict:
    data = np.asarray(values, dtype=np.float64)
    return {
        "minimum": float(data.min()),
        "median": float(np.median(data)),
        "maximum": float(data.max()),
    }


def summarize_class(examples: list[dict], hand_features: int) -> dict:
    rows = [tensor_metrics(item["features"], hand_features) for item in examples]
    return {
        key: summarize([row[key] for row in rows if row[key] is not None])
        for key in rows[0]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--expected", required=True)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("training-artifacts/popsign-ten-sign-gru-v3-hands-only/gru-model.pt"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(
            "training-artifacts/popsign-ten-sign-v3-extraction/extraction-manifest.json"
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    contract_version = int(capture["contractVersion"])
    # Aspect-only captures are v3 geometry without head offsets (67 values per hand).
    hands_only = capture.get("variant") == "hands-only-134"
    aspect_only = hands_only or capture.get("variant") == "aspect-only-167"
    hand_features = 67 if aspect_only else {2: 67, 3: 69}.get(contract_version)
    if hand_features is None:
        raise ValueError(f"Unsupported capture contract v{contract_version}")
    shape = tuple(capture["tensorShape"])
    tensor = np.asarray(capture["tensor"], dtype=np.float32).reshape(shape)
    expected_width = hand_features * 2 + (0 if hands_only else BODY_ANCHORS * 3)
    if shape != (48, expected_width) or not np.isfinite(tensor).all():
        raise ValueError(f"Unexpected or non-finite tensor shape: {shape}")

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    labels = list(checkpoint["labels"])
    if args.expected not in labels:
        raise ValueError(f"Expected label is not in this model: {args.expected}")
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    scale = np.asarray(checkpoint["scale"], dtype=np.float32)
    standardized = ((tensor - mean) / scale).astype(np.float32)
    model = SequenceGRU(shape[1], int(checkpoint["hiddenSize"]), len(labels), 0.0)
    model.load_state_dict(checkpoint["stateDict"])
    model.eval()
    with torch.no_grad():
        probabilities = torch.softmax(model(torch.from_numpy(standardized[None])), dim=1)[0].numpy()
    order = np.argsort(-probabilities)
    python_ranking = [
        {"label": labels[index], "score": float(probabilities[index])} for index in order
    ]
    browser_ranking = capture["browserRanking"]
    browser_scores = {item["label"]: float(item["score"]) for item in browser_ranking}

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    examples = [item for item in load_examples(manifest) if item["split"] == "train"]
    if aspect_only and int(manifest["contractVersion"]) == 3:
        for item in examples:
            item["features"] = drop_v3_head_offsets(item["features"])
            if hands_only:
                item["features"] = drop_body_anchors(item["features"])
    standardized_examples = [
        (item, ((item["features"] - mean) / scale).astype(np.float32)) for item in examples
    ]
    nearest = sorted(
        (
            {
                "label": item["label"],
                "video": item["video"],
                "standardizedRmse": float(np.sqrt(np.mean((features - standardized) ** 2))),
            }
            for item, features in standardized_examples
        ),
        key=lambda item: item["standardizedRmse"],
    )[:10]
    centroids = {
        label: np.mean(
            [features for item, features in standardized_examples if item["label"] == label],
            axis=0,
        )
        for label in labels
    }
    centroid_ranking = sorted(
        (
            {
                "label": label,
                "standardizedRmse": float(np.sqrt(np.mean((centroid - standardized) ** 2))),
            }
            for label, centroid in centroids.items()
        ),
        key=lambda item: item["standardizedRmse"],
    )
    relevant_labels = list(
        dict.fromkeys([args.expected, *(item["label"] for item in python_ranking[:3])])
    )
    report = {
        "capture": str(args.capture),
        "expected": args.expected,
        "browserDiagnostics": capture["diagnostics"],
        "normalizedCaptureMetrics": tensor_metrics(tensor, hand_features),
        "inferenceParity": {
            "rankingLabelsMatch": [item["label"] for item in browser_ranking]
            == [item["label"] for item in python_ranking],
            "maximumProbabilityDifference": max(
                abs(float(probabilities[labels.index(label)]) - browser_scores[label])
                for label in labels
            ),
            "pythonRanking": python_ranking,
            "browserRanking": browser_ranking,
        },
        "nearestTrainingExamples": nearest,
        "centroidRanking": centroid_ranking,
        "trainingReferenceMetrics": {
            label: summarize_class(
                [item for item in examples if item["label"] == label], hand_features
            )
            for label in relevant_labels
        },
        "interpretationLimits": [
            "Distance to a training example or centroid is diagnostic, not recognition accuracy.",
            "The capture contains landmarks only; it cannot verify whether the performed ASL form matches PopSign video content.",
        ],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Report: {args.output}")
    print(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"error: {error}")
        raise SystemExit(1)
