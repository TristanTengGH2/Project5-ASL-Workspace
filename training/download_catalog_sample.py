#!/usr/bin/env python3
"""Download a bounded signer-diverse sample for every sign in the catalog."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

from download_popsign_sample import fetch_range, iter_members, safe_destination, signer_id


CATALOG_PATH = Path("catalog/sign-catalog.json")
DEFAULT_OUTPUT = Path("datasets/popsign-v1-0/phase2-five-sign")
POPSIGN_INDEX_URL = "https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/index.html"
POPSIGN_GAME_LINK = re.compile(
    rb"/view/datasets/popsign_v1_0/game/([a-z0-9]+)/index\.html"
)


def official_game_signs() -> list[dict]:
    with urllib.request.urlopen(POPSIGN_INDEX_URL, timeout=30) as response:
        page = response.read()
    slugs = sorted({match.decode("ascii") for match in POPSIGN_GAME_LINK.findall(page)})
    if len(slugs) != 250:
        raise RuntimeError(f"Expected 250 PopSign v1.0 game signs, found {len(slugs)}")
    return [
        {
            "id": f"popsign-v1-0:game:{slug}",
            "displayGloss": slug,
            "archives": {
                split: (
                    "https://signdata.cc.gatech.edu/data/"
                    f"popsign_v1_0/game/{split}/{slug}.tar"
                )
                for split in ("train", "val", "test")
            },
        }
        for slug in slugs
    ]


def write_manifest(path: Path, manifest: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=int, default=5)
    parser.add_argument("--val", type=int, default=3)
    parser.add_argument("--test", type=int, default=3)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-member-mb", type=float, default=25.0)
    parser.add_argument(
        "--all-popsign-game",
        action="store_true",
        help="Use all 250 signs indexed by the official PopSign v1.0 game page",
    )
    parser.add_argument(
        "--batch-signs",
        type=int,
        help="Process at most this many incomplete signs, for resumable batch runs",
    )
    parser.add_argument(
        "--signs",
        nargs="+",
        help="Catalog sign IDs or display glosses to download (default: every catalog sign)",
    )
    args = parser.parse_args()
    limits = {"train": args.train, "val": args.val, "test": args.test}
    if any(value < 1 for value in limits.values()):
        parser.error("Every split limit must be at least 1")
    if args.batch_signs is not None and args.batch_signs < 1:
        parser.error("--batch-signs must be at least 1")

    if args.all_popsign_game:
        available_signs = official_game_signs()
        catalog_version = None
        source_index = POPSIGN_INDEX_URL
    else:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        available_signs = catalog["signs"]
        catalog_version = catalog["catalogVersion"]
        source_index = str(CATALOG_PATH)

    catalog_signs = {sign["id"]: sign for sign in available_signs}
    sign_aliases = dict(catalog_signs)
    for sign in available_signs:
        gloss = sign["displayGloss"]
        if gloss in sign_aliases:
            parser.error(f"Ambiguous catalog sign selector: {gloss}")
        sign_aliases[gloss] = sign

    requested = args.signs or list(catalog_signs)
    unknown = sorted(set(requested) - set(sign_aliases))
    if unknown:
        parser.error(f"Unknown catalog signs: {', '.join(unknown)}")
    requested_ids = [sign_aliases[selector]["id"] for selector in requested]
    if len(requested_ids) != len(set(requested_ids)):
        parser.error("--signs must not contain duplicates")

    selected_signs = [catalog_signs[sign_id] for sign_id in requested_ids]
    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output / "sample-manifest.json"
    if manifest_path.exists():
        run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "sourceIndex" not in run_manifest:
            run_manifest["sourceIndex"] = source_index
            write_manifest(manifest_path, run_manifest)
        expected = {
            "sourceIndex": source_index,
            "signIds": requested_ids,
            "limits": limits,
        }
        actual = {key: run_manifest.get(key) for key in expected}
        if actual != expected:
            raise RuntimeError(
                "Existing manifest does not match this run; choose a different output directory"
            )
    else:
        run_manifest = {
            "catalogVersion": catalog_version,
            "sourceIndex": source_index,
            "signIds": requested_ids,
            "limits": limits,
            "downloads": [],
        }
        write_manifest(manifest_path, run_manifest)

    recorded = {
        (item["signId"], item["split"], item["archivePath"])
        for item in run_manifest["downloads"]
    }
    maximum_bytes = math.floor(args.max_member_mb * 1_000_000)
    expected_per_sign = sum(limits.values())
    processed_signs = 0
    for sign in selected_signs:
        recorded_for_sign = sum(item["signId"] == sign["id"] for item in run_manifest["downloads"])
        if recorded_for_sign >= expected_per_sign:
            continue
        if args.batch_signs is not None and processed_signs >= args.batch_signs:
            break
        processed_signs += 1
        for split, limit in limits.items():
            url = sign["archives"][split]
            selected = []
            seen_signers = set()
            for member in iter_members(url):
                if not member.name.lower().endswith(".mp4") or member.size > maximum_bytes:
                    continue
                signer = signer_id(member.name)
                if signer in seen_signers:
                    continue
                selected.append(member)
                seen_signers.add(signer)
                if len(selected) == limit:
                    break
            if len(selected) < limit:
                raise RuntimeError(f"Only found {len(selected)} usable members for {sign['id']} {split}")

            for member in selected:
                destination = safe_destination(args.output / split, member.name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists() or destination.stat().st_size != member.size:
                    payload = fetch_range(url, member.data_offset, member.data_offset + member.size - 1)
                    if len(payload) != member.size:
                        raise RuntimeError(f"Short download for {member.name}")
                    destination.write_bytes(payload)
                key = (sign["id"], split, member.name)
                if key not in recorded:
                    run_manifest["downloads"].append(
                        {
                            "signId": sign["id"],
                            "split": split,
                            "signerId": signer_id(member.name),
                            "archive": url,
                            "archivePath": member.name,
                            "bytes": member.size,
                            "localPath": str(destination),
                        }
                    )
                    recorded.add(key)
                    write_manifest(manifest_path, run_manifest)
                print(f"{split:5} {sign['displayGloss']:8} {signer_id(member.name):20} {member.size / 1e6:5.1f} MB", flush=True)

    total_bytes = sum(item["bytes"] for item in run_manifest["downloads"])
    print(f"Downloaded {len(run_manifest['downloads'])} videos ({total_bytes / 1e6:.1f} MB)")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
