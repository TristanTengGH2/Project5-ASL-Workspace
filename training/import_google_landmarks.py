#!/usr/bin/env python3
"""Download a five-sign Kaggle subset and adapt it to landmark contract v1.

The Google Isolated Sign Language Recognition corpus contains MediaPipe
landmarks rather than videos. This importer keeps its participant groups
separate, downloads only selected parquet files, and writes a manifest that the
existing temporal trainer can consume.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import numpy as np
import requests


COMPETITION = "asl-signs"
CONTRACT_PATH = Path("training/landmark-contract.v1.json")
DEFAULT_DATASET_ROOT = Path("datasets/google-isolated-signs")
DEFAULT_OUTPUT = Path("training-artifacts/google-five-sign-extraction")
DEFAULT_SIGNS = ("after", "hear", "man", "pen", "puppy")
DEFAULT_TOKEN_PATH = Path.home() / ".kaggle" / "access_token"
DOWNLOAD_URL = "https://www.kaggle.com/api/v1/competitions/data/download"
SPLIT_PARTICIPANT_COUNTS = {"train": 13, "val": 4, "test": 4}
BODY_PAIRS = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination not in target.parents and target != destination:
                raise RuntimeError(f"Unsafe archive member: {member.filename}")
        archive.extractall(destination)


def read_access_token(token_path: Path) -> str:
    try:
        token = token_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise RuntimeError(
            f"Kaggle access token not found at {token_path}. Generate a personal API "
            "token and save it there with owner-only permissions."
        ) from error
    if not token.startswith("KGAT_") or len(token) < 20:
        raise RuntimeError(f"Kaggle access token at {token_path} is not valid")
    return token


def kaggle_download(remote_path: str, dataset_root: Path, token: str) -> Path:
    expected = dataset_root / remote_path
    if expected.exists():
        return expected
    dataset_root.mkdir(parents=True, exist_ok=True)
    # Kaggle expects a nested competition filename as one encoded path segment.
    encoded_path = quote(remote_path, safe="")
    url = f"{DOWNLOAD_URL}/{COMPETITION}/{encoded_path}"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=(15, 120),
    )
    if response.status_code in (401, 403):
        raise RuntimeError(
            f"Kaggle denied access to {remote_path} (HTTP {response.status_code}). "
            "Confirm the token is active and the competition rules are accepted."
        )
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raise RuntimeError(
            f"Kaggle download failed for {remote_path} (HTTP {response.status_code})"
        ) from error
    temporary = dataset_root / ".download-in-progress"
    with temporary.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
    if zipfile.is_zipfile(temporary):
        safe_extract(temporary, dataset_root)
        temporary.unlink()
        if expected.exists():
            return expected
        extracted = dataset_root / Path(remote_path).name
        if extracted.exists():
            expected.parent.mkdir(parents=True, exist_ok=True)
            extracted.replace(expected)
            return expected
        raise RuntimeError(f"Kaggle archive did not contain {remote_path}")
    expected.parent.mkdir(parents=True, exist_ok=True)
    temporary.replace(expected)
    return expected


def read_metadata(path: Path, signs: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = [row for row in csv.DictReader(file) if row["sign"] in signs]
    present = {row["sign"] for row in rows}
    missing = sorted(signs - present)
    if missing:
        raise RuntimeError(f"Requested signs are absent from train.csv: {', '.join(missing)}")
    return rows


def participant_splits(rows: list[dict[str, str]], seed: int) -> dict[str, set[str]]:
    participants = sorted({row["participant_id"] for row in rows})
    required = sum(SPLIT_PARTICIPANT_COUNTS.values())
    if len(participants) < required:
        raise RuntimeError(f"Need {required} participants; metadata contains {len(participants)}")
    random.Random(seed).shuffle(participants)
    output: dict[str, set[str]] = {}
    offset = 0
    for split, count in SPLIT_PARTICIPANT_COUNTS.items():
        output[split] = set(participants[offset : offset + count])
        offset += count
    return output


def select_examples(
    rows: list[dict[str, str]],
    splits: dict[str, set[str]],
    limits: dict[str, int],
    seed: int,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    signs = sorted({row["sign"] for row in rows})
    for split, participant_ids in splits.items():
        for sign in signs:
            candidates = [
                row
                for row in rows
                if row["sign"] == sign and row["participant_id"] in participant_ids
            ]
            random.Random(f"{seed}:{split}:{sign}").shuffle(candidates)
            if len(candidates) < limits[split]:
                raise RuntimeError(
                    f"Only {len(candidates)} {sign!r} examples are available in {split}; "
                    f"need {limits[split]}"
                )
            for row in candidates[: limits[split]]:
                selected.append({**row, "split": split})
    return selected


def read_parquet(path: Path) -> dict[str, list]:
    try:
        import pyarrow.parquet as parquet
    except ImportError as error:
        raise RuntimeError(
            "pyarrow is not installed. Install training/requirements.txt in .venv first."
        ) from error
    columns = ["frame", "type", "landmark_index", "x", "y", "z"]
    return parquet.read_table(path, columns=columns).to_pydict()


def frame_landmarks(columns: dict[str, list]) -> list[tuple[int, dict[str, np.ndarray]]]:
    frames: dict[int, dict[str, np.ndarray]] = defaultdict(dict)
    expected_counts = {"left_hand": 21, "right_hand": 21, "pose": 33}
    for row_index, frame_value in enumerate(columns["frame"]):
        kind = columns["type"][row_index]
        if kind not in expected_counts:
            continue
        if kind not in frames[int(frame_value)]:
            frames[int(frame_value)][kind] = np.full(
                (expected_counts[kind], 3), np.nan, dtype=np.float32
            )
        landmark_index = int(columns["landmark_index"][row_index])
        if landmark_index >= expected_counts[kind]:
            continue
        frames[int(frame_value)][kind][landmark_index] = (
            columns["x"][row_index],
            columns["y"][row_index],
            columns["z"][row_index],
        )
    return sorted(frames.items())


def usable(points: np.ndarray | None, count: int) -> bool:
    return points is not None and points.shape == (count, 3) and bool(np.isfinite(points).all())


def body_features(
    pose: np.ndarray | None, anchor_indexes: list[int]
) -> tuple[np.ndarray, np.ndarray | None, float | None, bool]:
    output = np.zeros(len(anchor_indexes) * 4, dtype=np.float32)
    if not usable(pose, 33):
        return output, None, None, False
    assert pose is not None
    origin = (pose[11] + pose[12]) / 2
    scale = float(np.linalg.norm(pose[11] - pose[12]))
    if scale <= 1e-6:
        return output, None, None, False
    for output_index, pose_index in enumerate(anchor_indexes):
        start = output_index * 4
        output[start : start + 3] = (pose[pose_index] - origin) / scale
        output[start + 3] = 1.0
    return output, origin, scale, True


def hand_features(
    hand: np.ndarray | None,
    shoulder_origin: np.ndarray | None,
    shoulder_scale: float | None,
) -> np.ndarray:
    output = np.zeros(68, dtype=np.float32)
    if not usable(hand, 21):
        return output
    assert hand is not None
    wrist = hand[0]
    palm_scale = float(np.mean([np.linalg.norm(hand[index] - wrist) for index in (5, 9, 17)]))
    if palm_scale <= 1e-6:
        return output
    output[:63] = ((hand - wrist) / palm_scale).reshape(-1)
    if shoulder_origin is not None and shoulder_scale is not None:
        output[63:66] = (wrist - shoulder_origin) / shoulder_scale
    output[66:] = (1.0, 1.0)
    return output


def mirror_hand(block: np.ndarray) -> np.ndarray:
    mirrored = block.copy()
    mirrored[:63].reshape(21, 3)[:, 0] *= -1
    mirrored[63] *= -1
    return mirrored


def canonicalize_dominance(features: np.ndarray) -> tuple[np.ndarray, str, bool]:
    left_count = int(np.count_nonzero(features[:, 66]))
    right_count = int(np.count_nonzero(features[:, 68 + 66]))
    dominant = "left" if left_count > right_count else "right"
    canonical = features.copy()
    if dominant == "left":
        for frame_index in range(len(canonical)):
            left = canonical[frame_index, :68].copy()
            right = canonical[frame_index, 68:136].copy()
            body = canonical[frame_index, 136:].reshape(13, 4).copy()
            body[:, 0] *= -1
            for left_index, right_index in BODY_PAIRS:
                body[[left_index, right_index]] = body[[right_index, left_index]]
            canonical[frame_index] = np.concatenate(
                [mirror_hand(left), mirror_hand(right), body.reshape(-1)]
            )
    else:
        canonical[:, :68], canonical[:, 68:136] = (
            features[:, 68:136].copy(),
            features[:, :68].copy(),
        )
    return canonical, dominant, dominant == "left"


def nearest_resample(features: np.ndarray, source_frames: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray]:
    targets = np.linspace(float(source_frames[0]), float(source_frames[-1]), count)
    right = np.searchsorted(source_frames, targets, side="left")
    right = np.clip(right, 0, len(source_frames) - 1)
    left = np.clip(right - 1, 0, len(source_frames) - 1)
    indexes = np.where(
        np.abs(targets - source_frames[left]) <= np.abs(source_frames[right] - targets),
        left,
        right,
    )
    return features[indexes].astype(np.float32), indexes.astype(np.int32)


def convert_sequence(path: Path, contract: dict, tensor_path: Path) -> dict:
    anchors = [item["index"] for item in contract["body"]["anchorOrder"]]
    frames = frame_landmarks(read_parquet(path))
    if not frames:
        raise RuntimeError(f"No usable landmark rows in {path}")
    feature_rows = []
    hand_frames = 0
    body_frames = 0
    for _, landmarks in frames:
        body, origin, scale, body_available = body_features(landmarks.get("pose"), anchors)
        left = hand_features(landmarks.get("left_hand"), origin, scale)
        right = hand_features(landmarks.get("right_hand"), origin, scale)
        feature_rows.append(np.concatenate([left, right, body]))
        hand_frames += int(bool(left[66] or right[66]))
        body_frames += int(body_available)
    raw_features = np.stack(feature_rows).astype(np.float32)
    canonical, dominant, mirrored = canonicalize_dominance(raw_features)
    source_frames = np.array([frame for frame, _ in frames], dtype=np.int32)
    tensor, selected_indexes = nearest_resample(
        canonical, source_frames, contract["sequence"]["normalizedFrameCount"]
    )
    expected_shape = tuple(contract["sequence"]["tensorShape"])
    if tensor.shape != expected_shape or not np.isfinite(tensor).all():
        raise RuntimeError(f"Invalid tensor shape or values for {path}: {tensor.shape}")
    tensor_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        tensor_path,
        features=tensor,
        source_frame_indexes=source_frames[selected_indexes],
    )
    return {
        "source": str(path),
        "sourceSha256": sha256(path),
        "decodedFrames": len(frames),
        "handDetectionFrames": hand_frames,
        "handDetectionRate": hand_frames / len(frames),
        "bodyAnchorFrames": body_frames,
        "bodyAnchorRate": body_frames / len(frames),
        "detectedDominantHand": dominant,
        "dominanceMirrored": mirrored,
        "tensor": str(tensor_path),
        "tensorShape": list(tensor.shape),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--token-path", type=Path, default=DEFAULT_TOKEN_PATH)
    parser.add_argument("--signs", nargs="+", default=list(DEFAULT_SIGNS))
    parser.add_argument("--train", type=int, default=20)
    parser.add_argument("--val", type=int, default=5)
    parser.add_argument("--test", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261109)
    args = parser.parse_args()
    if min(args.train, args.val, args.test) < 1:
        parser.error("All split limits must be positive")

    token = read_access_token(args.token_path)
    metadata = kaggle_download("train.csv", args.dataset_root, token)
    rows = read_metadata(metadata, set(args.signs))
    splits = participant_splits(rows, args.seed)
    limits = {"train": args.train, "val": args.val, "test": args.test}
    selected = select_examples(rows, splits, limits, args.seed)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    reports = []
    for index, item in enumerate(selected, start=1):
        remote_path = item["path"]
        print(f"[{index}/{len(selected)}] {item['split']} {item['sign']}: {remote_path}", flush=True)
        source_path = kaggle_download(remote_path, args.dataset_root, token)
        tensor_path = args.output / "tensors" / item["split"] / item["sign"] / f"{item['sequence_id']}.npz"
        report = convert_sequence(source_path, contract, tensor_path)
        report.update(
            {
                "video": str(
                    args.dataset_root
                    / "selected"
                    / item["split"]
                    / item["sign"]
                    / f"{item['participant_id']}-{item['sequence_id']}.parquet"
                ),
                "split": item["split"],
                "label": item["sign"],
                "participantId": item["participant_id"],
                "sequenceId": item["sequence_id"],
            }
        )
        reports.append(report)

    split_counts = {
        split: dict(Counter(item["label"] for item in reports if item["split"] == split))
        for split in ("train", "val", "test")
    }
    manifest = {
        "contractVersion": contract["contractVersion"],
        "contractSha256": sha256(CONTRACT_PATH),
        "sourceDataset": {
            "name": "Google Isolated Sign Language Recognition Corpus",
            "competition": COMPETITION,
            "license": "CC-BY-4.0 subject to Kaggle competition rules",
            "format": "MediaPipe Holistic landmark parquet",
        },
        "adapter": {
            "name": "google-isolated-signs-to-contract-v1",
            "timing": "Source frame indexes are used as a uniform-time proxy because timestamps are unavailable.",
            "handedness": "Published left_hand/right_hand type labels are used, then dominant-hand canonicalization is applied.",
            "confidence": "The corpus has coordinates but no confidence values; finite detections use confidence/visibility 1.0.",
            "limitations": "This bridge is suitable for pipeline validation, not a directly comparable PopSign video benchmark.",
        },
        "seed": args.seed,
        "participantSplits": {split: sorted(values) for split, values in splits.items()},
        "splitCounts": split_counts,
        "videos": reports,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output / "extraction-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    print(f"Counts: {split_counts}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
