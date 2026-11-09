#!/usr/bin/env python3
"""Compare candidate sequence lengths against the 64-frame v1 evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_SOURCES = (
    "google=training-artifacts/google-five-sign-extraction/extraction-manifest.json",
    "popsign=training-artifacts/phase2-five-sign-extraction-keep/extraction-manifest.json",
)
DEFAULT_OUTPUT = Path("training-artifacts/phase2-temporal-fidelity")
CANDIDATES = (16, 24, 32, 48)
REFERENCE_COUNT = 64
THRESHOLDS = {
    "medianMotionRetention": 0.85,
    "p10MotionRetention": 0.65,
    "p90PresenceCoverageError": 0.05,
}


def parse_source(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"Source must use name=manifest-path: {value}")
    name, path = value.split("=", 1)
    return name, Path(path)


def load_sequences(manifest_path: Path) -> list[np.ndarray]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sequences = []
    for item in manifest["videos"]:
        with np.load(item["tensor"]) as archive:
            features = archive["features"].astype(np.float32)
        if features.shape != (REFERENCE_COUNT, 188):
            raise RuntimeError(f"Expected v1 reference shape [64, 188], got {features.shape}")
        sequences.append(features)
    return sequences


def resample(features: np.ndarray, count: int) -> np.ndarray:
    indexes = np.rint(np.linspace(0, len(features) - 1, count)).astype(int)
    return features[indexes]


def motion(features: np.ndarray) -> tuple[float, float, float]:
    present = features[:, 66] > 0
    consecutive = present[:-1] & present[1:]
    if not consecutive.any():
        return 0.0, 0.0, float(present.mean())
    wrist_steps = np.linalg.norm(np.diff(features[:, 63:65], axis=0), axis=1)
    hands = features[:, :63].reshape(len(features), 21, 3)
    hand_steps = np.linalg.norm(np.diff(hands, axis=0), axis=2).mean(axis=1)
    return (
        float(wrist_steps[consecutive].sum()),
        float(hand_steps[consecutive].sum()),
        float(present.mean()),
    )


def ratio(candidate: float, reference: float) -> float:
    return candidate / reference if reference > 1e-6 else 1.0


def summarize_source(sequences: list[np.ndarray], count: int) -> tuple[dict, dict[str, list[float]]]:
    measurements = {"wrist": [], "hand": [], "presenceError": []}
    for reference in sequences:
        reference_motion = motion(reference)
        candidate_motion = motion(resample(reference, count))
        measurements["wrist"].append(ratio(candidate_motion[0], reference_motion[0]))
        measurements["hand"].append(ratio(candidate_motion[1], reference_motion[1]))
        measurements["presenceError"].append(
            abs(candidate_motion[2] - reference_motion[2])
        )
    wrist = np.array(measurements["wrist"])
    hand = np.array(measurements["hand"])
    presence = np.array(measurements["presenceError"])
    summary = {
        "examples": len(sequences),
        "wristMotionRetention": {
            "p10": float(np.percentile(wrist, 10)),
            "median": float(np.median(wrist)),
        },
        "localHandMotionRetention": {
            "p10": float(np.percentile(hand, 10)),
            "median": float(np.median(hand)),
        },
        "presenceCoverageAbsoluteError": {
            "median": float(np.median(presence)),
            "p90": float(np.percentile(presence, 90)),
        },
    }
    summary["passesProvisionalThresholds"] = bool(
        summary["wristMotionRetention"]["median"]
        >= THRESHOLDS["medianMotionRetention"]
        and summary["localHandMotionRetention"]["median"]
        >= THRESHOLDS["medianMotionRetention"]
        and summary["wristMotionRetention"]["p10"]
        >= THRESHOLDS["p10MotionRetention"]
        and summary["localHandMotionRetention"]["p10"]
        >= THRESHOLDS["p10MotionRetention"]
        and summary["presenceCoverageAbsoluteError"]["p90"]
        <= THRESHOLDS["p90PresenceCoverageError"]
    )
    return summary, measurements


def render(measurements: dict, output_path: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    source_names = list(measurements)
    colors = ("#e96b5b", "#304b68")
    for axis, metric, title in zip(
        axes,
        ("wrist", "hand"),
        ("Wrist-path motion retained", "Local hand motion retained"),
    ):
        positions = []
        values = []
        box_colors = []
        labels = []
        position = 1
        for count in CANDIDATES:
            for source_index, source in enumerate(source_names):
                positions.append(position)
                values.append(measurements[source][count][metric])
                box_colors.append(colors[source_index % len(colors)])
                labels.append(f"{count}\n{source}")
                position += 1
            position += 0.5
        boxes = axis.boxplot(values, positions=positions, patch_artist=True, widths=0.7)
        for patch, color in zip(boxes["boxes"], box_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
        axis.axhline(THRESHOLDS["medianMotionRetention"], color="#202a35", linestyle="--")
        axis.set_xticks(positions, labels, fontsize=8)
        axis.set_title(title)
        axis.set_ylim(0, 1.2)
        axis.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Candidate path length / 64-frame reference")
    figure.suptitle(
        "Temporal fidelity of uniform nearest-frame resampling\n"
        "Reference is existing contract-v1 evidence; rerun after v2 active-interval extraction."
    )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source_values = args.source or list(DEFAULT_SOURCES)
    sources = {name: load_sequences(path) for name, path in map(parse_source, source_values)}
    summaries = {source: {} for source in sources}
    measurements = {source: {} for source in sources}
    for source, sequences in sources.items():
        for count in CANDIDATES:
            summary, raw = summarize_source(sequences, count)
            summaries[source][str(count)] = summary
            measurements[source][count] = raw
    passing = [
        count
        for count in CANDIDATES
        if all(summaries[source][str(count)]["passesProvisionalThresholds"] for source in sources)
    ]
    recommendation = min(passing) if passing else None
    report = {
        "status": "provisional-v1-reference",
        "referenceFrameCount": REFERENCE_COUNT,
        "candidateFrameCounts": list(CANDIDATES),
        "thresholds": THRESHOLDS,
        "sources": summaries,
        "recommendedCount": recommendation,
        "limitation": (
            "This test measures fidelity against already normalized contract-v1 sequences. "
            "Repeat it after contract-v2 active-interval extraction before training."
        ),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "temporal-fidelity.json"
    image_path = args.output / "temporal-fidelity.png"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    render(measurements, image_path)
    for count in CANDIDATES:
        details = "; ".join(
            f"{source}: wrist {summaries[source][str(count)]['wristMotionRetention']['median']:.1%}, "
            f"hand {summaries[source][str(count)]['localHandMotionRetention']['median']:.1%}, "
            f"pass {summaries[source][str(count)]['passesProvisionalThresholds']}"
            for source in sources
        )
        print(f"{count} frames — {details}")
    print(f"Provisional recommendation: {recommendation}")
    print(f"Report: {report_path}")
    print(f"Plot: {image_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
