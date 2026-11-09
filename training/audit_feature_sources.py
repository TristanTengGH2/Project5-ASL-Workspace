#!/usr/bin/env python3
"""Compare contract-v1 feature distributions across extraction sources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_SOURCES = (
    "google=training-artifacts/google-five-sign-extraction/extraction-manifest.json",
    "popsign-swap=training-artifacts/phase2-five-sign-extraction-dominance/extraction-manifest.json",
    "popsign-keep=training-artifacts/phase2-five-sign-extraction-keep/extraction-manifest.json",
)
DEFAULT_OUTPUT = Path("training-artifacts/phase2-source-audit")
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
)
BODY_CONNECTIONS = (
    (1, 2), (3, 4), (5, 6), (7, 8), (7, 9), (8, 10),
    (7, 11), (8, 12), (11, 12),
)
GROUPS = {
    "dominantLocal": slice(0, 63),
    "dominantWrist": slice(63, 66),
    "dominantPresenceConfidence": slice(66, 68),
    "nonDominantLocal": slice(68, 131),
    "nonDominantWrist": slice(131, 134),
    "nonDominantPresenceConfidence": slice(134, 136),
    "body": slice(136, 188),
}


def parse_source(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"Source must use name=manifest-path: {value}")
    name, path = value.split("=", 1)
    return name, Path(path)


def split_label(item: dict) -> str:
    if "label" in item:
        return item["label"]
    parts = Path(item["video"]).parts
    for index, part in enumerate(parts):
        if part in {"train", "val", "test"} and index + 1 < len(parts):
            return parts[index + 1]
    raise ValueError(f"Cannot derive label from {item['video']}")


def load_source(name: str, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    examples = []
    for item in manifest["videos"]:
        with np.load(item["tensor"]) as archive:
            features = archive["features"].astype(np.float32)
        examples.append(
            {
                "label": split_label(item),
                "features": features,
                "handCoverage": item["handDetectionRate"],
                "decodedFrames": item["decodedFrames"],
                "dominanceMirrored": item.get("dominanceMirrored", False),
                "source": item.get("source", item.get("video")),
            }
        )
    return {
        "name": name,
        "manifest": str(manifest_path),
        "manifestData": manifest,
        "examples": examples,
        "features": np.stack([item["features"] for item in examples]),
    }


def percentiles(values: np.ndarray) -> dict[str, float]:
    return {
        "p10": float(np.percentile(values, 10)),
        "median": float(np.median(values)),
        "p90": float(np.percentile(values, 90)),
        "max": float(np.max(values)),
    }


def summarize(source: dict) -> dict:
    features = source["features"]
    dominant = features[:, :, :68]
    non_dominant = features[:, :, 68:136]
    body = features[:, :, 136:].reshape(*features.shape[:2], 13, 4)
    dominant_present = dominant[:, :, 66] > 0
    non_dominant_present = non_dominant[:, :, 66] > 0
    decoded = np.array([item["decodedFrames"] for item in source["examples"]])
    local = dominant[:, :, :63].reshape(*features.shape[:2], 21, 3)
    wrists = dominant[:, :, 63:66]
    summary = {
        "manifest": source["manifest"],
        "examples": len(source["examples"]),
        "labels": sorted({item["label"] for item in source["examples"]}),
        "decodedFrames": percentiles(decoded),
        "dominantPresenceRate": float(dominant_present.mean()),
        "nonDominantPresenceRate": float(non_dominant_present.mean()),
        "bothHandsPresenceRate": float((dominant_present & non_dominant_present).mean()),
        "bodyAnchorPresenceRate": float((body[:, :, :, 3] > 0).mean()),
        "dominanceMirroredRate": float(
            np.mean([item["dominanceMirrored"] for item in source["examples"]])
        ),
        "dominantWristMeanXyz": [
            float(wrists[:, :, axis][dominant_present].mean()) for axis in range(3)
        ],
        "dominantWristStdXyz": [
            float(wrists[:, :, axis][dominant_present].std()) for axis in range(3)
        ],
        "dominantLocalStdXyz": [
            float(local[:, :, :, axis][dominant_present].std()) for axis in range(3)
        ],
        "featureGroups": {},
    }
    for group, feature_slice in GROUPS.items():
        values = features[:, :, feature_slice]
        summary["featureGroups"][group] = {
            "absoluteMean": float(np.abs(values).mean()),
            "std": float(values.std()),
        }
    return summary


def pairwise(reference: dict, candidate: dict, summaries: dict) -> dict:
    reference_summary = summaries[reference["name"]]
    candidate_summary = summaries[candidate["name"]]
    reference_features = reference["features"]
    candidate_features = candidate["features"]
    reference_mean = reference_features.mean(axis=(0, 1))
    candidate_mean = candidate_features.mean(axis=(0, 1))
    reference_scale = reference_features.std(axis=(0, 1))
    candidate_scale = candidate_features.std(axis=(0, 1))
    pooled_scale = np.maximum(
        np.sqrt((np.square(reference_scale) + np.square(candidate_scale)) / 2),
        1e-4,
    )
    standardized_shift = np.abs(candidate_mean - reference_mean) / pooled_scale
    group_shift = {
        group: float(standardized_shift[feature_slice].mean())
        for group, feature_slice in GROUPS.items()
    }
    reference_x = reference_summary["dominantWristMeanXyz"][0]
    candidate_x = candidate_summary["dominantWristMeanXyz"][0]
    duration_ratio = (
        candidate_summary["decodedFrames"]["median"]
        / reference_summary["decodedFrames"]["median"]
    )
    return {
        "reference": reference["name"],
        "candidate": candidate["name"],
        "canonicalWristXSignMatches": bool(np.sign(reference_x) == np.sign(candidate_x)),
        "canonicalWristMeanXDelta": float(candidate_x - reference_x),
        "medianDecodedFrameRatio": float(duration_ratio),
        "meanAbsoluteStandardizedShiftByGroup": group_shift,
    }


def representative_examples(source: dict) -> dict[str, dict]:
    output = {}
    for label in sorted({item["label"] for item in source["examples"]}):
        candidates = [item for item in source["examples"] if item["label"] == label]
        median = float(np.median([item["handCoverage"] for item in candidates]))
        output[label] = min(candidates, key=lambda item: abs(item["handCoverage"] - median))
    return output


def draw_sequence(axis: plt.Axes, example: dict) -> None:
    features = example["features"]
    sampled = np.linspace(0, len(features) - 1, 8).round().astype(int)
    body = features[:, 136:].reshape(len(features), 13, 4)
    visible = body[:, :, 3] > 0
    mean_body = np.zeros((13, 2), dtype=np.float32)
    for index in range(13):
        if visible[:, index].any():
            mean_body[index] = body[visible[:, index], index, :2].mean(axis=0)
    for start, end in BODY_CONNECTIONS:
        axis.plot(
            [mean_body[start, 0], mean_body[end, 0]],
            [mean_body[start, 1], mean_body[end, 1]],
            color="#9aa7b5",
            linewidth=0.8,
            zorder=1,
        )
    axis.scatter(mean_body[:, 0], mean_body[:, 1], s=5, color="#9aa7b5", zorder=2)
    wrists = features[:, 63:65]
    presence = features[:, 66] > 0
    axis.plot(
        np.where(presence, wrists[:, 0], np.nan),
        np.where(presence, wrists[:, 1], np.nan),
        color="#f5a623",
        linewidth=1.4,
        alpha=0.8,
        zorder=3,
    )
    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(sampled)))
    for color, frame_index in zip(colors, sampled):
        frame = features[frame_index]
        if frame[66] <= 0:
            continue
        local = frame[:63].reshape(21, 3)[:, :2]
        wrist = frame[63:65]
        display_hand = wrist + local * 0.12
        for start, end in HAND_CONNECTIONS:
            axis.plot(
                display_hand[[start, end], 0],
                display_hand[[start, end], 1],
                color=color,
                linewidth=0.55,
                alpha=0.7,
                zorder=4,
            )
    axis.axvline(0, color="#d7dee7", linewidth=0.6, linestyle="--")
    axis.set_xlim(-1.6, 1.6)
    axis.set_ylim(2.0, -2.0)
    axis.set_aspect("equal")
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_title(
        f"{example['label']} · {example['decodedFrames']} frames · "
        f"{example['handCoverage']:.0%} hand",
        fontsize=8,
    )


def render_skeletons(sources: list[dict], output_path: Path) -> None:
    labels = sorted({item["label"] for source in sources for item in source["examples"]})
    figure, axes = plt.subplots(
        len(sources), len(labels), figsize=(3.0 * len(labels), 2.8 * len(sources)), squeeze=False
    )
    for row, source in enumerate(sources):
        representatives = representative_examples(source)
        for column, label in enumerate(labels):
            draw_sequence(axes[row, column], representatives[label])
            if column == 0:
                axes[row, column].set_ylabel(source["name"], fontsize=10)
    figure.suptitle(
        "Contract-v1 source comparison · orange = wrist path · colored = sampled hand shape\n"
        "Hand shape is scaled for display; axes are shoulder-normalized body coordinates.",
        fontsize=11,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source_values = args.source or list(DEFAULT_SOURCES)
    sources = [load_source(*parse_source(value)) for value in source_values]
    if len(sources) < 2:
        parser.error("At least two sources are required")
    summaries = {source["name"]: summarize(source) for source in sources}
    comparisons = [pairwise(sources[0], source, summaries) for source in sources[1:]]
    report = {"sources": summaries, "comparisonsToFirstSource": comparisons}
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "feature-audit.json"
    image_path = args.output / "skeleton-source-comparison.png"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    render_skeletons(sources, image_path)
    for source in sources:
        summary = summaries[source["name"]]
        print(
            f"{source['name']}: wrist x {summary['dominantWristMeanXyz'][0]:.3f}; "
            f"median frames {summary['decodedFrames']['median']:.1f}; "
            f"dominant hand {summary['dominantPresenceRate']:.1%}"
        )
    for comparison in comparisons:
        print(
            f"{comparison['candidate']} vs {comparison['reference']}: "
            f"wrist sign match {comparison['canonicalWristXSignMatches']}; "
            f"median-frame ratio {comparison['medianDecodedFrameRatio']:.2f}"
        )
    print(f"Report: {report_path}")
    print(f"Skeleton comparison: {image_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
