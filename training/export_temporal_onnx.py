#!/usr/bin/env python3
"""Export a trained temporal model to ONNX and verify held-out parity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch

from train_temporal_model import SequenceGRU, load_examples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    labels = list(checkpoint["labels"])
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    scale = np.asarray(checkpoint["scale"], dtype=np.float32)
    input_shape = tuple(checkpoint["inputShape"])
    model = SequenceGRU(
        input_size=input_shape[1],
        hidden_size=int(checkpoint["hiddenSize"]),
        class_count=len(labels),
        dropout=0.0,
    )
    model.load_state_dict(checkpoint["stateDict"])
    model.eval()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    example = torch.zeros((1, *input_shape), dtype=torch.float32)
    torch.onnx.export(
        model,
        example,
        args.output,
        input_names=["sequence"],
        output_names=["logits"],
        opset_version=17,
        do_constant_folding=True,
    )
    onnx.checker.check_model(onnx.load(args.output))

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    tests = [item for item in load_examples(manifest) if item["split"] == "test"]
    inputs = np.stack([(item["features"] - mean) / scale for item in tests]).astype(np.float32)
    with torch.no_grad():
        torch_logits = model(torch.from_numpy(inputs)).numpy()
    session = ort.InferenceSession(str(args.output), providers=["CPUExecutionProvider"])
    onnx_logits = np.concatenate(
        [session.run(["logits"], {"sequence": row[None]})[0] for row in inputs], axis=0
    )
    maximum_error = float(np.max(np.abs(torch_logits - onnx_logits)))
    rankings_match = bool(
        np.array_equal(np.argsort(-torch_logits, axis=1), np.argsort(-onnx_logits, axis=1))
    )
    if maximum_error > 1e-4 or not rankings_match:
        raise RuntimeError(
            f"ONNX parity failed: maximum error {maximum_error:.8f}; "
            f"rankings match {rankings_match}"
        )

    metadata = {
        "formatVersion": 1,
        "model": args.output.name,
        "architecture": "one-layer-bidirectional-gru",
        "inputName": "sequence",
        "outputName": "logits",
        "inputShape": [1, *input_shape],
        "labels": labels,
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "contractVersion": manifest["contractVersion"],
        "contractSha256": manifest["contractSha256"],
        "resultPolicy": "not-sure-with-ranked-possible-matches",
        "parity": {
            "heldOutExamples": len(tests),
            "maximumAbsoluteLogitError": maximum_error,
            "allRankingsMatch": rankings_match,
        },
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Model: {args.output} ({args.output.stat().st_size / 1000:.1f} kB)")
    print(f"Metadata: {args.metadata}")
    print(f"Parity: {len(tests)} held-out clips; max error {maximum_error:.8f}; rankings match")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}")
        raise SystemExit(1)
