#!/usr/bin/env python3
"""Index a remote uncompressed tar and download a few selected video members."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.request
from urllib.parse import urlparse
from pathlib import Path, PurePosixPath
from typing import Iterator, NamedTuple


BLOCK_SIZE = 512
DEFAULT_OUTPUT = Path("datasets/popsign-v1-0/sample")
SAFE_NAME = re.compile(r"^[A-Za-z0-9._/-]+$")


class TarMember(NamedTuple):
    name: str
    size: int
    data_offset: int


def fetch_range(url: str, start: int, end: int) -> bytes:
    last_error: OSError | None = None
    for attempt in range(3):
        request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                content_range = response.headers.get("Content-Range")
                if response.status != 206 or not content_range:
                    raise RuntimeError(f"Server did not honor byte range {start}-{end}.")
                return response.read()
        except OSError as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Range request failed after 3 attempts: {last_error}")


def parse_octal(field: bytes) -> int:
    value = field.rstrip(b"\0 ").lstrip(b" ")
    return int(value or b"0", 8)


def iter_members(url: str) -> Iterator[TarMember]:
    offset = 0
    while True:
        header = fetch_range(url, offset, offset + BLOCK_SIZE - 1)
        if len(header) != BLOCK_SIZE:
            raise RuntimeError(f"Short tar header at byte {offset}.")
        if header == bytes(BLOCK_SIZE):
            return

        name = header[0:100].rstrip(b"\0").decode("utf-8")
        prefix = header[345:500].rstrip(b"\0").decode("utf-8")
        if prefix:
            name = f"{prefix}/{name}"
        size = parse_octal(header[124:136])
        type_flag = header[156:157]
        data_offset = offset + BLOCK_SIZE
        if type_flag in (b"0", b"\0"):
            yield TarMember(name, size, data_offset)
        offset = data_offset + math.ceil(size / BLOCK_SIZE) * BLOCK_SIZE


def safe_destination(root: Path, member_name: str) -> Path:
    pure = PurePosixPath(member_name)
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or not SAFE_NAME.fullmatch(member_name)
        or pure.suffix.lower() != ".mp4"
    ):
        raise ValueError(f"Unsafe or unsupported archive path: {member_name!r}")
    destination = root.joinpath(*pure.parts).resolve()
    resolved_root = root.resolve()
    if resolved_root not in destination.parents:
        raise ValueError(f"Archive path escapes output directory: {member_name!r}")
    return destination


def signer_id(member_name: str) -> str:
    return PurePosixPath(member_name).name.split("-", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Official PopSign .tar URL")
    parser.add_argument("--limit", type=int, default=3, help="Maximum videos to download")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--allow-same-signer",
        action="store_true",
        help="Do not prefer distinct filename signer prefixes",
    )
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    if not args.url.startswith("https://signdata.cc.gatech.edu/data/popsign_v1_0/"):
        parser.error("URL must be an official PopSign v1.0 archive")

    selected: list[TarMember] = []
    seen_signers: set[str] = set()
    for member in iter_members(args.url):
        if not member.name.lower().endswith(".mp4"):
            continue
        signer = signer_id(member.name)
        if not args.allow_same_signer and signer in seen_signers:
            continue
        safe_destination(args.output, member.name)
        selected.append(member)
        seen_signers.add(signer)
        if len(selected) == args.limit:
            break

    if not selected:
        raise RuntimeError("No MP4 members found in the remote tar.")

    manifest = {
        "sourceArchive": args.url,
        "members": [],
    }
    for member in selected:
        destination = safe_destination(args.output, member.name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = fetch_range(
            args.url,
            member.data_offset,
            member.data_offset + member.size - 1,
        )
        if len(payload) != member.size:
            raise RuntimeError(f"Short download for {member.name}.")
        destination.write_bytes(payload)
        manifest["members"].append(
            {
                "archivePath": member.name,
                "signerId": signer_id(member.name),
                "bytes": member.size,
                "localPath": str(destination),
            }
        )
        print(f"Downloaded {member.name} ({member.size / 1_000_000:.1f} MB)")

    args.output.mkdir(parents=True, exist_ok=True)
    url_parts = PurePosixPath(urlparse(args.url).path)
    split = url_parts.parent.name
    sign = url_parts.stem
    manifest_dir = args.output / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"{split}-{sign}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
