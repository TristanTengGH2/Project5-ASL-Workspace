#!/usr/bin/env python3
"""Compare browser video-replay rankings with the offline Python evaluation of the same clips."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path, help="Output of app/scripts/replay-videos.mjs")
    parser.add_argument("evaluation", type=Path, help="evaluation.json from train_temporal_model.py")
    args = parser.parse_args()

    replay = json.loads(args.replay.read_text(encoding="utf-8"))
    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    offline = {item["video"]: item for item in evaluation["test"]["predictions"]}

    rows = []
    for item in replay["results"]:
        reference = offline.get(item["video"])
        ranking = [entry["label"] for entry in item.get("ranking") or []]
        rows.append(
            {
                "video": item["video"],
                "label": item["label"],
                "error": item.get("error"),
                "browser": ranking[0] if ranking else None,
                "browserTop3": ranking[:3],
                "offline": reference["predicted"] if reference else None,
                "trackedFrames": item.get("trackedFrames"),
                "dominantRate": (item.get("diagnostics") or {}).get("dominantHandPresenceRate"),
                "nonDominantRate": (item.get("diagnostics") or {}).get("nonDominantHandPresenceRate"),
                "activeFrames": (item.get("diagnostics") or {}).get("activeFrameCount"),
            }
        )
    total = len(rows)
    errors = [row for row in rows if row["error"]]
    scored = [row for row in rows if row["browser"]]
    top1 = sum(row["browser"] == row["label"] for row in scored)
    top3 = sum(row["label"] in row["browserTop3"] for row in scored)
    offline_top1 = sum(row["offline"] == row["label"] for row in rows if row["offline"])
    agree = sum(row["browser"] == row["offline"] for row in scored)
    print(f"clips {total}; browser errors {len(errors)}; scored {len(scored)}")
    print(f"browser top-1 {top1}/{total} = {top1 / total:.1%}; top-3 {top3}/{total} = {top3 / total:.1%}")
    print(f"offline Python top-1 {offline_top1}/{total} = {offline_top1 / total:.1%} (same clips)")
    print(f"browser and offline agree on top-1 for {agree}/{len(scored)} clips")
    per_sign = {}
    for label in sorted({row["label"] for row in rows}):
        group = [row for row in rows if row["label"] == label]
        per_sign[label] = (
            sum(row["browser"] == label for row in group),
            sum(row["offline"] == label for row in group),
            len(group),
        )
    print("per sign (browser / offline / clips):", {k: f"{b}/{o}/{n}" for k, (b, o, n) in per_sign.items()})
    wrong = Counter((row["label"], row["browser"]) for row in scored if row["browser"] != row["label"])
    print("most common browser mistakes:", wrong.most_common(6))
    for row in errors:
        print("error:", row["video"], row["error"])
    dominant = sorted(row["dominantRate"] for row in scored if row["dominantRate"] is not None)
    if dominant:
        print(f"dominant-hand presence in kept interval: median {dominant[len(dominant) // 2]:.2f}, min {dominant[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
