#!/usr/bin/env python3
"""Evaluate a confidence-threshold rule for rejecting unknown input.

A scan is accepted when its confidence score is at least the threshold. Scores:
  top      the model's top softmax probability
  margin   top probability minus the second-highest probability
  entropy  1 minus the normalized entropy of the softmax distribution
Two stages keep the held-out test participants untouched until a threshold is chosen:

  validation  Sweep thresholds using validation participants only (real signs from the
              supported vocabulary plus unsupported-sign negatives). Writes a curve.
  test        Evaluate one Developer-chosen threshold once on the test participants.

Softmax scores are not calibrated probabilities; the threshold is an empirical cutoff.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from train_temporal_model import CONTRACTS, SequenceGRU, load_examples, synthetic_negative_results

DEFAULT_MODEL = Path("training-artifacts/google-five-sign-gru-v2c/gru-model.pt")
DEFAULT_KNOWN = Path("training-artifacts/google-five-sign-v2c-extraction/extraction-manifest.json")
DEFAULT_UNSUPPORTED = Path(
    "training-artifacts/google-unsupported-v2-extraction/extraction-manifest.json"
)
DEFAULT_OUTPUT = Path("training-artifacts/google-v2c-unknown-rejection")
SWEEP = np.round(np.arange(0.0, 1.0, 0.01), 2)
REPORT_THRESHOLDS = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95)
UNKNOWN_REJECTION_TARGETS = (0.50, 0.80, 0.90)
SCORE_KINDS = ("top", "margin", "entropy")


def load_model(path: Path):
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    labels = checkpoint["labels"]
    model = SequenceGRU(
        checkpoint["inputShape"][1], checkpoint["hiddenSize"], len(labels), dropout=0.0
    )
    model.load_state_dict(checkpoint["stateDict"])
    model.eval()
    return model, labels, checkpoint["mean"].astype(np.float32), checkpoint["scale"].astype(np.float32)


def confidence(probabilities: np.ndarray, kind: str) -> np.ndarray:
    """Per-row confidence score in [0, 1] computed from softmax probabilities."""
    ordered = np.sort(probabilities, axis=1)
    if kind == "top":
        return ordered[:, -1]
    if kind == "margin":
        return ordered[:, -1] - ordered[:, -2]
    entropy = -(probabilities * np.log(np.clip(probabilities, 1e-12, 1.0))).sum(axis=1)
    return 1.0 - entropy / np.log(probabilities.shape[1])


def scores(
    model, examples: list[dict], mean: np.ndarray, scale: np.ndarray, labels: list[str], kind: str
):
    """Return confidence score, predicted label and true label for each example."""
    batch = torch.from_numpy(np.stack([(e["features"] - mean) / scale for e in examples]))
    with torch.no_grad():
        probabilities = torch.softmax(model(batch), dim=1).numpy()
    predicted = [labels[i] for i in probabilities.argmax(axis=1)]
    return confidence(probabilities, kind), predicted, [e["label"] for e in examples]


def load_split(manifest_path: Path, split: str) -> list[dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [e for e in load_examples(manifest) if e["split"] == split]


def auroc(known: np.ndarray, unknown: np.ndarray) -> float:
    """Probability that a random known scan scores higher than a random unknown scan."""
    wins = (known[:, None] > unknown[None, :]).sum() + 0.5 * (known[:, None] == unknown[None, :]).sum()
    return float(wins / (len(known) * len(unknown)))


def operating_point(threshold, known_top, known_correct, unknown_top) -> dict:
    accepted = known_top >= threshold
    return {
        "threshold": float(threshold),
        "knownAcceptedRate": float(accepted.mean()),
        "knownFalseRejectRate": float(1 - accepted.mean()),
        "accuracyAmongAcceptedKnown": (
            float(known_correct[accepted].mean()) if accepted.any() else None
        ),
        "knownCorrectAndAcceptedRate": float((accepted & known_correct).mean()),
        "unknownAcceptedRate": float((unknown_top >= threshold).mean()),
        "unknownRejectedRate": float((unknown_top < threshold).mean()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("validation", "test"), required=True)
    parser.add_argument("--threshold", type=float, help="Required for the test stage.")
    parser.add_argument("--score", choices=SCORE_KINDS, default="top")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--known", type=Path, default=DEFAULT_KNOWN)
    parser.add_argument("--unsupported", type=Path, default=DEFAULT_UNSUPPORTED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.stage == "test" and args.threshold is None:
        parser.error("--threshold is required for the test stage (choose it from the validation curve)")
    if args.stage == "validation" and args.threshold is not None:
        parser.error("the validation stage sweeps thresholds; do not pass --threshold")

    model, labels, mean, scale = load_model(args.model)
    split = "val" if args.stage == "validation" else "test"
    known_examples = load_split(args.known, split)
    unknown_examples = load_split(args.unsupported, split)
    known_top, known_pred, known_true = scores(
        model, known_examples, mean, scale, labels, args.score
    )
    unknown_top, unknown_pred, unknown_true = scores(
        model, unknown_examples, mean, scale, labels, args.score
    )
    known_correct = np.array([p == t for p, t in zip(known_pred, known_true)])

    # Synthetic idle / missing-hand inputs use the same reference sequence as training.
    known_manifest = json.loads(args.known.read_text(encoding="utf-8"))
    train_first = next(e for e in load_examples(known_manifest) if e["split"] == "train")
    reference = ((train_first["features"] - mean) / scale).astype(np.float32)
    hand_width = CONTRACTS[int(known_manifest["contractVersion"])]["hand_width"]
    synthetic = synthetic_negative_results(model, mean, scale, reference, labels, hand_width)

    report = {
        "stage": args.stage,
        "split": split,
        "model": str(args.model),
        "score": args.score,
        "rule": f"accept when the {args.score} score >= threshold",
        "knownExamples": len(known_examples),
        "unsupportedExamples": len(unknown_examples),
        "unsupportedSigns": sorted(set(unknown_true)),
        "knownTop1Accuracy": float(known_correct.mean()),
        "separationAuroc": auroc(known_top, unknown_top),
        "knownScore": {"median": float(np.median(known_top))},
        "unknownScore": {"median": float(np.median(unknown_top))},
        "unsupportedPredictedAs": {
            label: int(sum(p == label for p in unknown_pred)) for label in labels
        },
        "syntheticNegatives": {
            name: {
                "predicted": item["predicted"],
                "score": float(confidence(np.array([item["probabilities"]]), args.score)[0]),
            }
            for name, item in synthetic.items()
        },
    }
    if args.stage == "validation":
        report["curve"] = [operating_point(t, known_top, known_correct, unknown_top) for t in SWEEP]
        report["selected"] = [
            operating_point(t, known_top, known_correct, unknown_top) for t in REPORT_THRESHOLDS
        ]
        # Comparable across scores: the lowest threshold that rejects each share of unknowns.
        report["atUnknownRejectionTargets"] = [
            next(p for p in report["curve"] if p["unknownRejectedRate"] >= target)
            for target in UNKNOWN_REJECTION_TARGETS
            if report["curve"][-1]["unknownRejectedRate"] >= target
        ]
    else:
        point = operating_point(args.threshold, known_top, known_correct, unknown_top)
        point["syntheticRejected"] = {
            name: float(confidence(np.array([item["probabilities"]]), args.score)[0]) < args.threshold
            for name, item in synthetic.items()
        }
        report["result"] = point

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / f"{args.stage}-{args.score}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"{args.stage}: {len(known_examples)} known, {len(unknown_examples)} unsupported; "
        f"known top-1 {known_correct.mean():.1%}; score {args.score}; "
        f"separation AUROC {report['separationAuroc']:.3f}"
    )
    rows = report["atUnknownRejectionTargets"] if args.stage == "validation" else [report["result"]]
    print("threshold | known kept | acc of kept | unknown let through | unknown rejected")
    for r in rows:
        acc = "n/a" if r["accuracyAmongAcceptedKnown"] is None else f"{r['accuracyAmongAcceptedKnown']:.1%}"
        print(
            f"   {r['threshold']:.2f}   |   {r['knownAcceptedRate']:.1%}   |   {acc}   |"
            f"   {r['unknownAcceptedRate']:.1%}   |   {r['unknownRejectedRate']:.1%}"
        )
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
