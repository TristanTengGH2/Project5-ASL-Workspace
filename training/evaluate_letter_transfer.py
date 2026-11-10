#!/usr/bin/env python3
"""Cross-dataset feasibility check for letter-by-letter fingerspelling.

Trains one small landmark classifier on one dataset and tests it on a different dataset,
so the test people and settings are not in the training data. Settings are fixed in advance:
no early stopping (neither dataset has signer-separated validation data), a fixed epoch
count, and mirrored copies of the training data so the classifier does not depend on hand
chirality or on handedness labels that may disagree across datasets. Test data is never
mirrored. Results are feasibility evidence, not a claim about general accuracy.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

LETTERS = "ABCDEFGHIKLMNOPQRSTUVWXY"
EPOCHS = 30
HIDDEN = 128
DROPOUT = 0.2
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
BATCH = 128
SEED = 20261109

EXPERIMENTS = (
    ("cabana-train", "signalphaset", "Train Cabana, test SignAlphaSet (different people and setting)"),
    ("signalphaset", "cabana-test", "Train SignAlphaSet, test Cabana Test (different people and setting)"),
    ("cabana-train", "cabana-test", "Train Cabana, test Cabana Test (signers may overlap: NOT signer-separated)"),
)


def load(directory: Path, name: str) -> dict:
    archive = np.load(directory / f"{name}.npz")
    labels = np.array([LETTERS.index(l) for l in archive["labels"]], dtype=np.int64)
    return {
        "features": archive["features"].astype(np.float32),
        "labels": labels,
        "sampled": int(archive["sampled_per_letter"].sum()),
    }


def mirror(features: np.ndarray) -> np.ndarray:
    flipped = features.reshape(-1, 21, 3).copy()
    flipped[:, :, 0] *= -1
    return flipped.reshape(-1, 63)


def train(features: np.ndarray, labels: np.ndarray) -> tuple[nn.Module, np.ndarray, np.ndarray]:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    features = np.concatenate([features, mirror(features)])
    labels = np.concatenate([labels, labels])
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale[scale < 1e-5] = 1.0
    data = TensorDataset(torch.from_numpy((features - mean) / scale), torch.from_numpy(labels))
    loader = DataLoader(data, batch_size=BATCH, shuffle=True, generator=torch.Generator().manual_seed(SEED))
    model = nn.Sequential(
        nn.Linear(63, HIDDEN), nn.ReLU(), nn.Dropout(DROPOUT), nn.Linear(HIDDEN, len(LETTERS))
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    loss_function = nn.CrossEntropyLoss()
    for _ in range(EPOCHS):
        model.train()
        for batch_features, batch_labels in loader:
            optimizer.zero_grad()
            loss_function(model(batch_features), batch_labels).backward()
            optimizer.step()
    model.eval()
    return model, mean, scale


def evaluate(model: nn.Module, mean: np.ndarray, scale: np.ndarray, test: dict) -> dict:
    with torch.no_grad():
        probabilities = torch.softmax(model(torch.from_numpy((test["features"] - mean) / scale)), dim=1).numpy()
    ranking = np.argsort(-probabilities, axis=1)
    labels = test["labels"]
    top1 = ranking[:, 0] == labels
    top3 = (ranking[:, :3] == labels[:, None]).any(axis=1)
    per_letter = {
        LETTERS[i]: {"images": int((labels == i).sum()), "top1": float(top1[labels == i].mean()) if (labels == i).any() else None}
        for i in range(len(LETTERS))
    }
    confusion = {}
    for true, predicted in zip(labels[~top1], ranking[~top1, 0]):
        key = f"{LETTERS[true]}->{LETTERS[predicted]}"
        confusion[key] = confusion.get(key, 0) + 1
    return {
        "testImages": int(len(labels)),
        "detectionRateOfSampled": float(len(labels) / test["sampled"]),
        "top1": float(top1.mean()),
        "top3": float(top3.mean()),
        "chanceTop1": 1 / len(LETTERS),
        "perLetterTop1": per_letter,
        "mostCommonMistakes": dict(sorted(confusion.items(), key=lambda kv: -kv[1])[:10]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("training-artifacts/letters"))
    parser.add_argument("--output", type=Path, default=Path("training-artifacts/letters/transfer-results.json"))
    args = parser.parse_args()

    results = []
    for source, target, description in EXPERIMENTS:
        training, testing = load(args.data, source), load(args.data, target)
        model, mean, scale = train(training["features"], training["labels"])
        outcome = evaluate(model, mean, scale, testing)
        outcome.update({"train": source, "test": target, "description": description, "trainImages": int(len(training["labels"]))})
        results.append(outcome)
        worst = sorted(((v["top1"], k) for k, v in outcome["perLetterTop1"].items() if v["top1"] is not None))[:5]
        print(
            f"{description}\n  train {outcome['trainImages']} images; test {outcome['testImages']} images "
            f"(hand found in {outcome['detectionRateOfSampled']:.0%} of sampled)\n"
            f"  top-1 {outcome['top1']:.1%} | top-3 {outcome['top3']:.1%} | chance {outcome['chanceTop1']:.1%}\n"
            f"  weakest letters: {[(k, round(v, 2)) for v, k in worst]}\n"
            f"  most common mistakes: {outcome['mostCommonMistakes']}"
        )
    args.output.write_text(json.dumps({"settings": {"epochs": EPOCHS, "hidden": HIDDEN, "dropout": DROPOUT, "learningRate": LEARNING_RATE, "weightDecay": WEIGHT_DECAY, "seed": SEED, "mirroredTrainingCopies": True}, "experiments": results}, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
