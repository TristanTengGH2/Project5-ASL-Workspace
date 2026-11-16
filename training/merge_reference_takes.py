#!/usr/bin/env python3
"""Merge reference takes saved by the app's recorder (app/record-reference.html) into the catalog.

A take holds landmark numbers only. Merging replaces that sign's PopSign-derived animation with
the recorded one (signing hand plus, when tracked, the other hand) and marks its provenance, so
rebuilding the PopSign references later keeps it.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FRAMES = 48
POINTS = 21
RECORDED_ATTRIBUTION = (
    "Recorded for this app by a fluent signer with the app's own hand tracker; only hand landmark "
    "coordinates are kept, with no video or face."
)


def check_motion(name: str, motion: list) -> None:
    if len(motion) != FRAMES or any(len(frame) != POINTS * 2 for frame in motion):
        raise ValueError(f"{name}: expected {FRAMES} frames of {POINTS * 2} numbers")
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for frame in motion for value in frame):
        raise ValueError(f"{name}: contains non-finite values")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("takes", nargs="+", type=Path, help="reference-take-*.json files from the recorder")
    parser.add_argument("--catalog", type=Path, default=Path("catalog/sign-catalog.json"))
    parser.add_argument("--references", type=Path, default=Path("catalog/sign-references.json"))
    parser.add_argument("--facts", type=Path, default=Path("catalog/sign-facts.json"))
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    supported = {sign["id"] for sign in catalog["signs"] if sign["status"] == "supported"}
    facts = json.loads(args.facts.read_text(encoding="utf-8"))["signs"]
    references = json.loads(args.references.read_text(encoding="utf-8"))

    for path in args.takes:
        take = json.loads(path.read_text(encoding="utf-8"))
        if take.get("schemaVersion") != 1:
            raise ValueError(f"{path}: unsupported take schema")
        sign_id = take["signId"]
        if sign_id not in supported:
            raise ValueError(f"{path}: {sign_id} is not a supported catalog sign")
        check_motion(f"{path} frames", take["frames"])
        if take["otherFrames"] is not None:
            check_motion(f"{path} otherFrames", take["otherFrames"])
        if take["stats"]["dominantRate"] < 0.5:
            raise ValueError(f"{path}: signing hand tracked in too few frames")
        two_handed = facts.get(sign_id, {}).get("hands") == "two"
        if two_handed and take["otherFrames"] is None:
            raise ValueError(f"{path}: {take['gloss']} uses two hands (ASL-LEX) but the take has no second hand")
        entry = {
            "gloss": take["gloss"],
            "provenance": "recorded",
            "trackedFrameRate": take["stats"]["dominantRate"],
            "frames": take["frames"],
        }
        if take["otherFrames"] is not None:
            entry["otherFrames"] = take["otherFrames"]
        references["signs"][sign_id] = entry
        print(f"{take['gloss']:9s} recorded, second hand: {'yes' if take['otherFrames'] else 'no'}")

    references["recordedAttribution"] = RECORDED_ATTRIBUTION
    args.references.write_text(json.dumps(references, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {args.references}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
