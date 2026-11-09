#!/usr/bin/env python3
"""Extract versioned landmark tensors and local inspection overlays from sign videos."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import mediapipe as mp
import numpy as np

import landmark_contract_v2 as v2


CONTRACT_PATHS = {
    1: Path("training/landmark-contract.v1.json"),
    2: Path("training/landmark-contract.v2.json"),
}
DEFAULT_OUTPUTS = {
    1: Path("training-artifacts/phase2-extraction"),
    2: Path("training-artifacts/phase2-v2-extraction"),
}
HAND_MODEL = Path("app/public/models/hand_landmarker.task")
POSE_MODEL = Path("app/public/models/pose_landmarker_lite.task")
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
)
POSE_CONNECTIONS = (
    (2, 5), (7, 8), (9, 10), (11, 12), (11, 13), (12, 14),
    (11, 23), (12, 24), (23, 24),
)


@dataclass
class ExtractedFrame:
    timestamp_ms: float
    features: np.ndarray
    hands_detected: int
    body_available: bool
    overlay: np.ndarray


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resized_for_tracking(frame: np.ndarray, maximum_side: int) -> np.ndarray:
    height, width = frame.shape[:2]
    scale = min(1.0, maximum_side / max(height, width))
    if scale == 1.0:
        return frame
    return cv2.resize(frame, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)


def corrected_label(model_label: str, mode: str) -> str:
    label = model_label.lower()
    if label not in ("left", "right"):
        return "unknown"
    if mode == "swap":
        return "right" if label == "left" else "left"
    return label


def xyz(landmark: object) -> np.ndarray:
    return np.array([landmark.x, landmark.y, landmark.z], dtype=np.float32)


def landmark_array(landmarks: list[object] | None, count: int) -> np.ndarray | None:
    if landmarks is None or len(landmarks) != count:
        return None
    return np.stack([xyz(point) for point in landmarks]).astype(np.float32)


def hand_features(
    landmarks: list[object],
    confidence: float,
    shoulder_origin: np.ndarray | None,
    shoulder_scale: float | None,
) -> np.ndarray:
    wrist = xyz(landmarks[0])
    palm_scale = float(np.mean([np.linalg.norm(xyz(landmarks[i]) - wrist) for i in (5, 9, 17)]))
    if palm_scale <= 1e-6:
        return np.zeros(68, dtype=np.float32)
    local = np.concatenate([(xyz(point) - wrist) / palm_scale for point in landmarks])
    body_wrist = np.zeros(3, dtype=np.float32)
    if shoulder_origin is not None and shoulder_scale is not None:
        body_wrist = (wrist - shoulder_origin) / shoulder_scale
    return np.concatenate(
        [local, body_wrist, np.array([1.0, confidence], dtype=np.float32)]
    ).astype(np.float32)


def body_features(
    landmarks: list[object] | None,
    anchor_indexes: list[int],
    minimum_visibility: float,
) -> tuple[np.ndarray, np.ndarray | None, float | None, bool]:
    output = np.zeros(len(anchor_indexes) * 4, dtype=np.float32)
    if not landmarks:
        return output, None, None, False
    left_shoulder, right_shoulder = landmarks[11], landmarks[12]
    if min(left_shoulder.visibility, right_shoulder.visibility) < minimum_visibility:
        return output, None, None, False
    left_xyz, right_xyz = xyz(left_shoulder), xyz(right_shoulder)
    origin = (left_xyz + right_xyz) / 2
    scale = float(np.linalg.norm(left_xyz - right_xyz))
    if scale <= 1e-6:
        return output, None, None, False
    for output_index, pose_index in enumerate(anchor_indexes):
        point = landmarks[pose_index]
        visibility = float(point.visibility)
        if visibility < minimum_visibility:
            continue
        start = output_index * 4
        output[start : start + 3] = (xyz(point) - origin) / scale
        output[start + 3] = visibility
    return output, origin, scale, True


def point_xy(point: object, frame: np.ndarray) -> tuple[int, int]:
    height, width = frame.shape[:2]
    return round(point.x * width), round(point.y * height)


def draw_overlay(
    frame: np.ndarray,
    hand_landmarks: list[list[object]],
    hand_labels: list[str],
    pose_landmarks: list[object] | None,
    anchor_indexes: list[int],
) -> np.ndarray:
    overlay = resized_for_tracking(frame, 900).copy()
    for landmarks, label in zip(hand_landmarks, hand_labels):
        for start, end in HAND_CONNECTIONS:
            cv2.line(overlay, point_xy(landmarks[start], overlay), point_xy(landmarks[end], overlay), (0, 220, 255), 2)
        for point in landmarks:
            cv2.circle(overlay, point_xy(point, overlay), 3, (30, 80, 255), -1)
        wrist_x, wrist_y = point_xy(landmarks[0], overlay)
        cv2.putText(overlay, label, (wrist_x + 8, wrist_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    if pose_landmarks:
        allowed = set(anchor_indexes)
        for start, end in POSE_CONNECTIONS:
            if start in allowed and end in allowed:
                cv2.line(overlay, point_xy(pose_landmarks[start], overlay), point_xy(pose_landmarks[end], overlay), (90, 255, 90), 2)
        for index in anchor_indexes:
            point = pose_landmarks[index]
            if point.visibility >= 0.35:
                cv2.circle(overlay, point_xy(point, overlay), 4, (90, 255, 90), -1)
    return overlay


def nearest_resample(frames: list[ExtractedFrame], count: int) -> tuple[np.ndarray, np.ndarray]:
    timestamps = np.array([frame.timestamp_ms for frame in frames], dtype=np.float64)
    targets = np.linspace(timestamps[0], timestamps[-1], count)
    right = np.searchsorted(timestamps, targets, side="left")
    right = np.clip(right, 0, len(timestamps) - 1)
    left = np.clip(right - 1, 0, len(timestamps) - 1)
    choose_left = np.abs(targets - timestamps[left]) <= np.abs(timestamps[right] - targets)
    indexes = np.where(choose_left, left, right)
    tensor = np.stack([frames[index].features for index in indexes]).astype(np.float32)
    return tensor, indexes.astype(np.int32)


def mirror_hand_block(block: np.ndarray) -> np.ndarray:
    mirrored = block.copy()
    mirrored[:63].reshape(21, 3)[:, 0] *= -1
    mirrored[63] *= -1
    return mirrored


def canonicalize_dominance(frames: list[ExtractedFrame]) -> tuple[str, bool]:
    left_count = sum(frame.features[66] > 0 for frame in frames)
    right_count = sum(frame.features[68 + 66] > 0 for frame in frames)
    dominant = "left" if left_count > right_count else "right"
    body_pairs = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12))
    for frame in frames:
        left = frame.features[:68].copy()
        right = frame.features[68:136].copy()
        body = frame.features[136:].reshape(13, 4).copy()
        if dominant == "left":
            dominant_hand = mirror_hand_block(left)
            non_dominant_hand = mirror_hand_block(right)
            body[:, 0] *= -1
            for left_index, right_index in body_pairs:
                body[[left_index, right_index]] = body[[right_index, left_index]]
        else:
            dominant_hand = right
            non_dominant_hand = left
        frame.features = np.concatenate(
            [dominant_hand, non_dominant_hand, body.reshape(-1)]
        ).astype(np.float32)
    return dominant, dominant == "left"


def extract_video(
    video_path: Path,
    hand_landmarker: object,
    pose_landmarker: object,
    contract: dict,
    output_root: Path,
    handedness_mode: str,
    maximum_side: int,
) -> dict:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open {video_path}")
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        raise RuntimeError(f"Invalid FPS for {video_path}")
    source_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    anchor_indexes = [item["index"] for item in contract["body"]["anchorOrder"]]
    frames: list[ExtractedFrame] = []
    frame_index = 0
    try:
        while True:
            ok, bgr = capture.read()
            if not ok:
                break
            timestamp_ms = frame_index * 1000.0 / fps
            tracked = resized_for_tracking(bgr, maximum_side)
            rgb = cv2.cvtColor(tracked, cv2.COLOR_BGR2RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_integer = round(timestamp_ms)
            hands_result = hand_landmarker.detect_for_video(image, timestamp_integer)
            pose_result = pose_landmarker.detect_for_video(image, timestamp_integer)
            pose = pose_result.pose_landmarks[0] if pose_result.pose_landmarks else None
            body, shoulder_origin, shoulder_scale, body_available = body_features(pose, anchor_indexes, 0.35)

            slots: dict[str, tuple[list[object], float]] = {}
            labels: list[str] = []
            for landmarks, categories in zip(hands_result.hand_landmarks, hands_result.handedness):
                category = categories[0]
                label = corrected_label(category.category_name, handedness_mode)
                labels.append(label)
                prior = slots.get(label)
                if label in ("left", "right") and (prior is None or category.score > prior[1]):
                    slots[label] = (landmarks, float(category.score))
            hand_parts = []
            for label in ("left", "right"):
                detection = slots.get(label)
                hand_parts.append(
                    hand_features(detection[0], detection[1], shoulder_origin, shoulder_scale)
                    if detection
                    else np.zeros(68, dtype=np.float32)
                )
            features = np.concatenate([*hand_parts, body]).astype(np.float32)
            if features.shape != (contract["sequence"]["frameFeatureCount"],):
                raise RuntimeError(f"Unexpected feature shape {features.shape}")
            overlay = draw_overlay(bgr, hands_result.hand_landmarks, labels, pose, anchor_indexes)
            frames.append(ExtractedFrame(timestamp_ms, features, len(hands_result.hand_landmarks), body_available, overlay))
            frame_index += 1
    finally:
        capture.release()
    if not frames:
        raise RuntimeError(f"No decoded frames in {video_path}")

    dominant_hand, dominance_mirrored = canonicalize_dominance(frames)
    tensor, selected_indexes = nearest_resample(frames, contract["sequence"]["normalizedFrameCount"])
    stem = video_path.stem
    tensor_dir = output_root / "tensors"
    inspection_dir = output_root / "inspection" / stem
    tensor_dir.mkdir(parents=True, exist_ok=True)
    inspection_dir.mkdir(parents=True, exist_ok=True)
    tensor_path = tensor_dir / f"{stem}.npz"
    np.savez_compressed(
        tensor_path,
        features=tensor,
        source_frame_indexes=selected_indexes,
        source_timestamps_ms=np.array([frame.timestamp_ms for frame in frames], dtype=np.float64),
    )

    detected_indexes = [index for index, frame in enumerate(frames) if frame.hands_detected]
    inspection_indexes = []
    if detected_indexes:
        inspection_indexes = sorted({
            detected_indexes[0],
            detected_indexes[len(detected_indexes) // 2],
            detected_indexes[-1],
        })
    for index in inspection_indexes:
        cv2.imwrite(str(inspection_dir / f"frame-{index:04d}.jpg"), frames[index].overlay)

    hand_frames = sum(frame.hands_detected > 0 for frame in frames)
    body_frames = sum(frame.body_available for frame in frames)
    return {
        "video": str(video_path),
        "videoSha256": sha256(video_path),
        "sourceFramesReported": source_frame_count,
        "decodedFrames": len(frames),
        "fps": fps,
        "handDetectionFrames": hand_frames,
        "handDetectionRate": hand_frames / len(frames),
        "bodyAnchorFrames": body_frames,
        "bodyAnchorRate": body_frames / len(frames),
        "detectedDominantHand": dominant_hand,
        "dominanceMirrored": dominance_mirrored,
        "tensor": str(tensor_path),
        "tensorShape": list(tensor.shape),
        "inspectionFrames": inspection_indexes,
    }


def extract_video_v2(
    video_path: Path,
    hand_landmarker: object,
    pose_landmarker: object,
    contract: dict,
    output_root: Path,
    handedness_mode: str,
    maximum_side: int,
) -> dict:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open {video_path}")
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        raise RuntimeError(f"Invalid FPS for {video_path}")
    source_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    anchor_indexes = [item["index"] for item in contract["body"]["anchorOrder"]]
    frames: list[ExtractedFrame] = []
    frame_index = 0
    try:
        while True:
            ok, bgr = capture.read()
            if not ok:
                break
            timestamp_ms = frame_index * 1000.0 / fps
            tracked = resized_for_tracking(bgr, maximum_side)
            rgb = cv2.cvtColor(tracked, cv2.COLOR_BGR2RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_integer = round(timestamp_ms)
            hands_result = hand_landmarker.detect_for_video(image, timestamp_integer)
            pose_result = pose_landmarker.detect_for_video(image, timestamp_integer)
            pose_landmarks = pose_result.pose_landmarks[0] if pose_result.pose_landmarks else None
            pose = landmark_array(pose_landmarks, 33)
            pose_present = (
                np.array([point.visibility >= 0.35 for point in pose_landmarks], dtype=bool)
                if pose_landmarks
                else np.zeros(33, dtype=bool)
            )

            slots: dict[str, tuple[list[object], float]] = {}
            labels: list[str] = []
            for landmarks, categories in zip(hands_result.hand_landmarks, hands_result.handedness):
                category = categories[0]
                label = corrected_label(category.category_name, handedness_mode)
                labels.append(label)
                prior = slots.get(label)
                if label in ("left", "right") and (prior is None or category.score > prior[1]):
                    slots[label] = (landmarks, float(category.score))
            left = landmark_array(slots["left"][0], 21) if "left" in slots else None
            right = landmark_array(slots["right"][0], 21) if "right" in slots else None
            features = v2.frame_features(left, right, pose, pose_present)
            _, shoulder_scale = v2.shoulder_reference(pose, pose_present)
            overlay = draw_overlay(
                bgr, hands_result.hand_landmarks, labels, pose_landmarks, anchor_indexes
            )
            frames.append(
                ExtractedFrame(
                    timestamp_ms,
                    features,
                    len(hands_result.hand_landmarks),
                    shoulder_scale is not None,
                    overlay,
                )
            )
            frame_index += 1
    finally:
        capture.release()
    if not frames:
        raise RuntimeError(f"No decoded frames in {video_path}")

    raw_features = np.stack([frame.features for frame in frames])
    source_positions = np.array([frame.timestamp_ms for frame in frames], dtype=np.float64)
    prepared = v2.prepare_sequence(raw_features, source_positions)
    count = contract["sequence"]["normalizedFrameCount"]
    tensor, selected_indexes = v2.resample_nearest(
        prepared.features, prepared.source_positions, count
    )
    expected_shape = tuple(contract["sequence"]["tensorShape"])
    if tensor.shape != expected_shape or not np.isfinite(tensor).all():
        raise RuntimeError(f"Invalid v2 tensor shape or values for {video_path}: {tensor.shape}")

    stem = video_path.stem
    tensor_dir = output_root / "tensors"
    inspection_dir = output_root / "inspection" / stem
    tensor_dir.mkdir(parents=True, exist_ok=True)
    inspection_dir.mkdir(parents=True, exist_ok=True)
    tensor_path = tensor_dir / f"{stem}.npz"
    np.savez_compressed(
        tensor_path,
        features=tensor,
        active_features=prepared.features,
        active_source_positions=prepared.source_positions,
        source_timestamps_ms=prepared.source_positions[selected_indexes],
    )

    detected_indexes = [index for index, frame in enumerate(frames) if frame.hands_detected]
    inspection_indexes = []
    if detected_indexes:
        inspection_indexes = sorted(
            {
                detected_indexes[0],
                detected_indexes[len(detected_indexes) // 2],
                detected_indexes[-1],
            }
        )
    for index in inspection_indexes:
        cv2.imwrite(str(inspection_dir / f"frame-{index:04d}.jpg"), frames[index].overlay)

    hand_frames = sum(frame.hands_detected > 0 for frame in frames)
    body_frames = sum(frame.body_available for frame in frames)
    return {
        "video": str(video_path),
        "videoSha256": sha256(video_path),
        "sourceFramesReported": source_frame_count,
        "decodedFrames": len(frames),
        "activeFrames": len(prepared.features),
        "activeStartMs": float(prepared.source_positions[0]),
        "activeEndMs": float(prepared.source_positions[-1]),
        "activeDominantHandDetectionRate": float(np.mean(prepared.features[:, 66] > 0)),
        "fps": fps,
        "handDetectionFrames": hand_frames,
        "handDetectionRate": hand_frames / len(frames),
        "bodyAnchorFrames": body_frames,
        "bodyAnchorRate": body_frames / len(frames),
        "detectedDominantHand": prepared.dominant_hand,
        "dominanceMirrored": prepared.dominance_mirrored,
        "tensor": str(tensor_path),
        "tensorShape": list(tensor.shape),
        "inspectionFrames": inspection_indexes,
    }


def videos_from_inputs(inputs: Iterable[str]) -> list[Path]:
    videos: list[Path] = []
    for value in inputs:
        path = Path(value)
        if path.is_dir():
            videos.extend(path.rglob("*.mp4"))
        elif path.suffix.lower() == ".mp4":
            videos.append(path)
        else:
            raise ValueError(f"Expected an MP4 or directory: {path}")
    return sorted(set(videos))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="MP4 files or directories")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--contract-version", type=int, choices=(1, 2), default=1)
    parser.add_argument("--handedness-mode", choices=("keep", "swap"), required=True)
    parser.add_argument("--maximum-side", type=int, default=960)
    parser.add_argument("--hand-detection-confidence", type=float, default=0.4)
    parser.add_argument("--hand-presence-confidence", type=float, default=0.4)
    parser.add_argument("--hand-tracking-confidence", type=float, default=0.4)
    args = parser.parse_args()
    output = args.output or DEFAULT_OUTPUTS[args.contract_version]
    contract_path = CONTRACT_PATHS[args.contract_version]
    videos = videos_from_inputs(args.inputs)
    if not videos:
        parser.error("No MP4 videos found")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for model in (HAND_MODEL, POSE_MODEL):
        if not model.exists():
            parser.error(f"Missing {model}; run npm run fetch-assets from app/")

    vision = mp.tasks.vision
    hand_options = vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(HAND_MODEL)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=args.hand_detection_confidence,
        min_hand_presence_confidence=args.hand_presence_confidence,
        min_tracking_confidence=args.hand_tracking_confidence,
    )
    pose_options = vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(POSE_MODEL)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.4,
        min_pose_presence_confidence=0.4,
        min_tracking_confidence=0.4,
    )
    reports = []
    for video in videos:
        print(f"Extracting {video}", flush=True)
        # VIDEO mode requires increasing timestamps and carries tracking state.
        # A fresh pair per clip prevents state from crossing signer boundaries.
        with vision.HandLandmarker.create_from_options(hand_options) as hands:
            with vision.PoseLandmarker.create_from_options(pose_options) as pose:
                extractor = extract_video_v2 if args.contract_version == 2 else extract_video
                report = extractor(
                    video, hands, pose, contract, output, args.handedness_mode, args.maximum_side
                )
        reports.append(report)
        print(
            f"  {report['decodedFrames']} frames; "
            f"hands {report['handDetectionRate']:.1%}; body {report['bodyAnchorRate']:.1%}",
            flush=True,
        )

    manifest = {
        "contractVersion": contract["contractVersion"],
        "contractSha256": sha256(contract_path),
        "handModelSha256": sha256(HAND_MODEL),
        "poseModelSha256": sha256(POSE_MODEL),
        "handednessMode": args.handedness_mode,
        "maximumTrackingSide": args.maximum_side,
        "handConfidenceThresholds": {
            "detection": args.hand_detection_confidence,
            "presence": args.hand_presence_confidence,
            "tracking": args.hand_tracking_confidence,
        },
        "videos": reports,
    }
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "extraction-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
