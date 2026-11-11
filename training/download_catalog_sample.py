#!/usr/bin/env python3
"""Download a bounded signer-diverse sample for every sign in the catalog."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from download_popsign_sample import fetch_range, iter_members, safe_destination, signer_id


CATALOG_PATH = Path("catalog/sign-catalog.json")
DEFAULT_OUTPUT = Path("datasets/popsign-v1-0/phase2-five-sign")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=int, default=5)
    parser.add_argument("--val", type=int, default=3)
    parser.add_argument("--test", type=int, default=3)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-member-mb", type=float, default=25.0)
    parser.add_argument(
        "--signs",
        nargs="+",
        help="Catalog sign IDs or display glosses to download (default: every catalog sign)",
    )
    args = parser.parse_args()
    limits = {"train": args.train, "val": args.val, "test": args.test}
    if any(value < 1 for value in limits.values()):
        parser.error("Every split limit must be at least 1")

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_signs = {sign["id"]: sign for sign in catalog["signs"]}
    sign_aliases = dict(catalog_signs)
    for sign in catalog["signs"]:
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
    run_manifest = {
        "catalogVersion": catalog["catalogVersion"],
        "signIds": requested_ids,
        "limits": limits,
        "downloads": [],
    }
    maximum_bytes = math.floor(args.max_member_mb * 1_000_000)
    for sign in selected_signs:
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
                print(f"{split:5} {sign['displayGloss']:8} {signer_id(member.name):20} {member.size / 1e6:5.1f} MB", flush=True)

    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output / "sample-manifest.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
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
