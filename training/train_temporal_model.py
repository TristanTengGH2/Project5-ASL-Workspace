#!/usr/bin/env python3
"""Train one compact GRU feasibility model on contract-v1 landmark sequences."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


DEFAULT_MANIFEST = Path(
    "training-artifacts/phase2-five-sign-large-extraction/extraction-manifest.json"
)
DEFAULT_OUTPUT = Path("training-artifacts/phase2-five-sign-gru")
CONTRACT_PATH = Path("training/landmark-contract.v1.json")
SPLITS = {"train", "val", "test"}


class SequenceGRU(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, class_count: int, dropout: float):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            batch_first=True,
            bidirectional=True,
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, class_count),
        )

    def forward(self, sequence: torch.Tensor) -> torch.Tensor:
        _, hidden = self.gru(sequence)
        summary = torch.cat((hidden[-2], hidden[-1]), dim=1)
        return self.classifier(summary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        examples.append(
            {
                "split": split,
                "label": label,
                "video": item["video"],
                "features": features,
            }
        )
    return examples


def standardizer(train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    frames = train.reshape(-1, train.shape[-1])
    mean = frames.mean(axis=0).astype(np.float32)
    scale = frames.std(axis=0).astype(np.float32)
    scale[scale < 1e-5] = 1.0
    return mean, scale


def tensors_for_split(
    examples: list[dict], split: str, labels: list[str], mean: np.ndarray, scale: np.ndarray
) -> tuple[torch.Tensor, torch.Tensor, list[str]]:
    selected = [example for example in examples if example["split"] == split]
    features = np.stack([(example["features"] - mean) / scale for example in selected])
    targets = np.array([labels.index(example["label"]) for example in selected], dtype=np.int64)
    return torch.from_numpy(features), torch.from_numpy(targets), [item["video"] for item in selected]


def evaluate(
    model: nn.Module,
    features: torch.Tensor,
    targets: torch.Tensor,
    videos: list[str],
    labels: list[str],
    loss_function: nn.Module,
) -> dict:
    model.eval()
    with torch.no_grad():
        logits = model(features)
        loss = float(loss_function(logits, targets).item())
        probabilities = torch.softmax(logits, dim=1)
        rankings = torch.argsort(probabilities, dim=1, descending=True)
    predictions = rankings[:, 0]
    correct = int((predictions == targets).sum().item())
    rows = []
    for index, video in enumerate(videos):
        ranking = [labels[value] for value in rankings[index].tolist()]
        rows.append(
            {
                "video": video,
                "expected": labels[int(targets[index])],
                "predicted": labels[int(predictions[index])],
                "ranking": ranking,
                "probabilities": {
                    label: float(probabilities[index, label_index])
                    for label_index, label in enumerate(labels)
                },
            }
        )
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
        "loss": loss,
        "examples": len(rows),
        "top1Accuracy": correct / len(rows),
        "top5Accuracy": sum(row["expected"] in row["ranking"][:5] for row in rows) / len(rows),
        "top5Note": "Top-5 is non-discriminating when the vocabulary contains exactly five classes.",
        "confusion": confusion,
        "predictions": rows,
    }


def synthetic_negative_results(
    model: nn.Module, mean: np.ndarray, scale: np.ndarray, reference: np.ndarray, labels: list[str]
) -> dict:
    missing_frame = (np.zeros_like(mean) - mean) / scale
    inputs = {
        "all-zero-idle": np.tile(missing_frame, (reference.shape[0], 1)),
        "pose-only-missing-hands": reference.copy(),
        "alternating-hand-loss": reference.copy(),
    }
    inputs["pose-only-missing-hands"][:, :136] = missing_frame[:136]
    inputs["alternating-hand-loss"][::2, :136] = missing_frame[:136]
    batch = torch.from_numpy(np.stack(list(inputs.values())).astype(np.float32))
    model.eval()
    with torch.no_grad():
        probabilities = torch.softmax(model(batch), dim=1)
    results = {}
    for index, name in enumerate(inputs):
        best = int(torch.argmax(probabilities[index]).item())
        results[name] = {
            "predicted": labels[best],
            "confidence": float(probabilities[index, best]),
            "rejected": False,
            "note": "No unknown-sign rejection threshold is fitted in Phase 2.",
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--hidden-size", type=int, default=48)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--weight-decay", type=float, default=0.0001)
    parser.add_argument("--max-epochs", type=int, default=300)
    parser.add_argument("--patience", type=int, default=35)
    parser.add_argument("--target-accuracy", type=float, default=0.70)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    current_contract_hash = sha256(CONTRACT_PATH)
    if manifest["contractSha256"] != current_contract_hash:
        raise RuntimeError("Extraction manifest does not match the current landmark contract")
    examples = load_examples(manifest)
    labels = sorted({example["label"] for example in examples if example["split"] == "train"})
    if len(labels) < 2:
        raise RuntimeError("At least two classes are required")
    for split in SPLITS:
        split_labels = {example["label"] for example in examples if example["split"] == split}
        if split_labels != set(labels):
            raise RuntimeError(f"{split} labels do not match training labels")

    raw_train = np.stack(
        [example["features"] for example in examples if example["split"] == "train"]
    )
    mean, scale = standardizer(raw_train)
    split_tensors = {
        split: tensors_for_split(examples, split, labels, mean, scale)
        for split in ("train", "val", "test")
    }
    train_features, train_targets, _ = split_tensors["train"]
    train_loader = DataLoader(
        TensorDataset(train_features, train_targets),
        batch_size=args.batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
    )

    model = SequenceGRU(train_features.shape[2], args.hidden_size, len(labels), args.dropout)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    loss_function = nn.CrossEntropyLoss()
    best_state = None
    best_epoch = 0
    best_validation_loss = float("inf")
    epochs_without_improvement = 0
    history = []
    for epoch in range(1, args.max_epochs + 1):
        model.train()
        epoch_loss = 0.0
        for batch_features, batch_targets in train_loader:
            optimizer.zero_grad()
            loss = loss_function(model(batch_features), batch_targets)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_loss += float(loss.item()) * len(batch_targets)
        epoch_loss /= len(train_features)
        validation = evaluate(
            model,
            *split_tensors["val"],
            labels,
            loss_function,
        )
        history.append(
            {
                "epoch": epoch,
                "trainLoss": epoch_loss,
                "validationLoss": validation["loss"],
                "validationTop1": validation["top1Accuracy"],
            }
        )
        if validation["loss"] < best_validation_loss - 1e-5:
            best_validation_loss = validation["loss"]
            best_epoch = epoch
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epoch == 1 or epoch % 20 == 0:
            print(
                f"epoch {epoch:3}: train loss {epoch_loss:.4f}; "
                f"val loss {validation['loss']:.4f}; val top-1 {validation['top1Accuracy']:.1%}",
                flush=True,
            )
        if epochs_without_improvement >= args.patience:
            break
    if best_state is None:
        raise RuntimeError("Training did not produce a model state")
    model.load_state_dict(best_state)

    validation = evaluate(model, *split_tensors["val"], labels, loss_function)
    test = evaluate(model, *split_tensors["test"], labels, loss_function)
    reference = ((raw_train[0] - mean) / scale).astype(np.float32)
    negatives = synthetic_negative_results(model, mean, scale, reference, labels)
    target_passed = test["top1Accuracy"] >= args.target_accuracy
    negative_rejection_passed = all(item["rejected"] for item in negatives.values())
    export_ready = target_passed and negative_rejection_passed

    args.output.mkdir(parents=True, exist_ok=True)
    model_path = args.output / "gru-model.pt"
    torch.save(
        {
            "stateDict": model.state_dict(),
            "labels": labels,
            "mean": mean,
            "scale": scale,
            "inputShape": list(train_features.shape[1:]),
            "hiddenSize": args.hidden_size,
        },
        model_path,
    )
    split_counts = {
        split: dict(Counter(example["label"] for example in examples if example["split"] == split))
        for split in ("train", "val", "test")
    }
    report = {
        "status": "pass" if export_ready else "not-ready",
        "architecture": "one-layer-bidirectional-gru",
        "seed": args.seed,
        "contractVersion": manifest["contractVersion"],
        "contractSha256": manifest["contractSha256"],
        "splitCounts": split_counts,
        "configuration": {
            "hiddenSize": args.hidden_size,
            "dropout": args.dropout,
            "batchSize": args.batch_size,
            "learningRate": args.learning_rate,
            "weightDecay": args.weight_decay,
            "maxEpochs": args.max_epochs,
            "patience": args.patience,
        },
        "bestEpoch": best_epoch,
        "epochsRun": len(history),
        "history": history,
        "validation": validation,
        "test": test,
        "syntheticNegativeBehavior": negatives,
        "gate": {
            "targetTop1Accuracy": args.target_accuracy,
            "accuracyPassed": target_passed,
            "negativeRejectionPassed": negative_rejection_passed,
            "exportReady": export_ready,
        },
        "model": {
            "path": str(model_path),
            "bytes": model_path.stat().st_size,
            "browserExportAttempted": False,
            "reason": None if export_ready else "Accuracy and unknown-rejection gates must both pass.",
        },
    }
    report_path = args.output / "evaluation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Best epoch: {best_epoch}; epochs run: {len(history)}")
    print(f"Validation top-1: {validation['top1Accuracy']:.1%}")
    print(f"Test top-1: {test['top1Accuracy']:.1%}")
    print(f"Test confusion: {test['confusion']}")
    print(f"Accuracy gate ({args.target_accuracy:.0%}): {'pass' if target_passed else 'fail'}")
    print("Unknown rejection: fail (not implemented in Phase 2)")
    print(f"Browser export: {'ready' if export_ready else 'not attempted'}")
    print(f"Report: {report_path}")
    print(f"Model: {model_path} ({model_path.stat().st_size / 1000:.1f} kB)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
