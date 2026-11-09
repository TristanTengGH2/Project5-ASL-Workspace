"""Shared source-neutral feature construction for provisional contract v2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


HAND_FEATURES = 67
BODY_ANCHORS = (0, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14)
BODY_PAIRS = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10))
FRAME_FEATURES = 167
CANDIDATE_COUNTS = (16, 24, 32, 48)


@dataclass(frozen=True)
class PreparedSequence:
    features: np.ndarray
    source_positions: np.ndarray
    active_start: int
    active_end: int
    dominant_hand: str
    dominance_mirrored: bool


def usable(points: np.ndarray | None, count: int) -> bool:
    return points is not None and points.shape == (count, 3) and bool(np.isfinite(points).all())


def pose_shape_valid(pose: np.ndarray | None) -> bool:
    return pose is not None and pose.shape == (33, 3)


def shoulder_reference(
    pose: np.ndarray | None, pose_present: np.ndarray | None
) -> tuple[np.ndarray | None, float | None]:
    if not pose_shape_valid(pose):
        return None, None
    assert pose is not None
    if not np.isfinite(pose[[11, 12]]).all():
        return None, None
    if pose_present is not None and not bool(pose_present[11] and pose_present[12]):
        return None, None
    origin = (pose[11] + pose[12]) / 2
    scale = float(np.linalg.norm(pose[11, :2] - pose[12, :2]))
    if scale <= 1e-6:
        return None, None
    return origin, scale


def hand_features(
    hand: np.ndarray | None,
    shoulder_origin: np.ndarray | None,
    shoulder_scale: float | None,
) -> np.ndarray:
    output = np.zeros(HAND_FEATURES, dtype=np.float32)
    if not usable(hand, 21):
        return output
    assert hand is not None
    wrist = hand[0]
    palm_scale = float(
        np.mean([np.linalg.norm(hand[index, :2] - wrist[:2]) for index in (5, 9, 17)])
    )
    if palm_scale <= 1e-6:
        return output
    output[:63] = ((hand - wrist) / palm_scale).reshape(-1)
    if shoulder_origin is not None and shoulder_scale is not None:
        output[63:66] = (wrist - shoulder_origin) / shoulder_scale
    output[66] = 1.0
    return output


def body_features(
    pose: np.ndarray | None,
    pose_present: np.ndarray | None,
    shoulder_origin: np.ndarray | None,
    shoulder_scale: float | None,
) -> np.ndarray:
    output = np.zeros(len(BODY_ANCHORS) * 3, dtype=np.float32)
    if not pose_shape_valid(pose) or shoulder_origin is None or shoulder_scale is None:
        return output
    assert pose is not None
    for output_index, pose_index in enumerate(BODY_ANCHORS):
        present = (pose_present is None or bool(pose_present[pose_index])) and bool(
            np.isfinite(pose[pose_index]).all()
        )
        if not present:
            continue
        start = output_index * 3
        output[start : start + 2] = (pose[pose_index, :2] - shoulder_origin[:2]) / shoulder_scale
        output[start + 2] = 1.0
    return output


def frame_features(
    left_hand: np.ndarray | None,
    right_hand: np.ndarray | None,
    pose: np.ndarray | None,
    pose_present: np.ndarray | None = None,
) -> np.ndarray:
    origin, scale = shoulder_reference(pose, pose_present)
    output = np.concatenate(
        [
            hand_features(left_hand, origin, scale),
            hand_features(right_hand, origin, scale),
            body_features(pose, pose_present, origin, scale),
        ]
    ).astype(np.float32)
    if output.shape != (FRAME_FEATURES,):
        raise RuntimeError(f"Unexpected contract-v2 frame shape: {output.shape}")
    return output


def mirror_hand(block: np.ndarray) -> np.ndarray:
    mirrored = block.copy()
    mirrored[:63].reshape(21, 3)[:, 0] *= -1
    mirrored[63] *= -1
    return mirrored


def canonicalize_dominance(features: np.ndarray) -> tuple[np.ndarray, str, bool]:
    left_count = int(np.count_nonzero(features[:, 66]))
    right_count = int(np.count_nonzero(features[:, HAND_FEATURES + 66]))
    dominant = "left" if left_count > right_count else "right"
    canonical = features.copy()
    for frame_index in range(len(canonical)):
        left = features[frame_index, :HAND_FEATURES].copy()
        right = features[frame_index, HAND_FEATURES : HAND_FEATURES * 2].copy()
        body = features[frame_index, HAND_FEATURES * 2 :].reshape(len(BODY_ANCHORS), 3).copy()
        if dominant == "left":
            dominant_hand = mirror_hand(left)
            non_dominant_hand = mirror_hand(right)
            body[:, 0] *= -1
            for left_index, right_index in BODY_PAIRS:
                body[[left_index, right_index]] = body[[right_index, left_index]]
        else:
            dominant_hand = right
            non_dominant_hand = left
        canonical[frame_index] = np.concatenate(
            [dominant_hand, non_dominant_hand, body.reshape(-1)]
        )
    return canonical, dominant, dominant == "left"


def active_interval(
    canonical: np.ndarray, bridge_gap: int = 3, context: int = 2
) -> tuple[int, int]:
    present = canonical[:, 66] > 0
    indexes = np.flatnonzero(present)
    if not len(indexes):
        raise ValueError("Sequence has no detected dominant hand")
    bridged = present.copy()
    for left, right in zip(indexes[:-1], indexes[1:]):
        if right - left - 1 <= bridge_gap:
            bridged[left : right + 1] = True
    padded = np.concatenate(([False], bridged, [False])).astype(np.int8)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    candidates = []
    for start, end in zip(starts, ends):
        span = int(end - start)
        detections = int(np.count_nonzero(present[start:end]))
        density = detections / span
        sustained_score = detections * density
        wrist = canonical[start:end, 63:65]
        detected_wrist = wrist[present[start:end]]
        wrist_motion = (
            float(np.linalg.norm(np.diff(detected_wrist, axis=0), axis=1).sum())
            if len(detected_wrist) > 1
            else 0.0
        )
        candidates.append(
            (sustained_score, detections, density, wrist_motion, span, -int(start))
        )
    selected = max(range(len(candidates)), key=candidates.__getitem__)
    start = max(0, int(starts[selected]) - context)
    end = min(len(canonical), int(ends[selected]) + context)
    return start, end


def center_wrist_depth(features: np.ndarray) -> np.ndarray:
    centered = features.copy()
    for offset in (0, HAND_FEATURES):
        present = centered[:, offset + 66] > 0
        if present.any():
            median = float(np.median(centered[present, offset + 65]))
            centered[present, offset + 65] -= median
    return centered


def prepare_sequence(features: np.ndarray, source_positions: np.ndarray) -> PreparedSequence:
    if features.ndim != 2 or features.shape[1] != FRAME_FEATURES:
        raise ValueError(f"Expected [frames, {FRAME_FEATURES}], got {features.shape}")
    if len(features) != len(source_positions) or not len(features):
        raise ValueError("Features and source positions must have equal nonzero length")
    if not np.all(np.diff(source_positions) > 0):
        raise ValueError("Source positions must increase")
    canonical, dominant, mirrored = canonicalize_dominance(features)
    start, end = active_interval(canonical)
    active = center_wrist_depth(canonical[start:end])
    return PreparedSequence(
        features=active,
        source_positions=source_positions[start:end],
        active_start=start,
        active_end=end,
        dominant_hand=dominant,
        dominance_mirrored=mirrored,
    )


def resample_nearest(
    features: np.ndarray, source_positions: np.ndarray, count: int
) -> tuple[np.ndarray, np.ndarray]:
    if count < 2:
        raise ValueError("Resample count must be at least two")
    targets = np.linspace(float(source_positions[0]), float(source_positions[-1]), count)
    right = np.searchsorted(source_positions, targets, side="left")
    right = np.clip(right, 0, len(source_positions) - 1)
    left = np.clip(right - 1, 0, len(source_positions) - 1)
    indexes = np.where(
        np.abs(targets - source_positions[left]) <= np.abs(source_positions[right] - targets),
        left,
        right,
    )
    return features[indexes].astype(np.float32), indexes.astype(np.int32)


def candidate_tensors(sequence: PreparedSequence) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    return {
        count: resample_nearest(sequence.features, sequence.source_positions, count)
        for count in CANDIDATE_COUNTS
    }
