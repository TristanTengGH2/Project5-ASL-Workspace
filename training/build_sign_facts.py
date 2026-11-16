#!/usr/bin/env python3
"""Build verified per-sign facts (hands, location, movement, handshape) from ASL-LEX 2.0.

ASL-LEX (Sehyr et al., 2021; CC BY 4.0) codes citation forms of signs. When a gloss has several
entries (variant forms), a field is kept only if every entry agrees; otherwise it is left out,
so the app never states a detail that some forms contradict.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

# ASL-LEX SignType values grouped into hand counts (Battison's sign types).
ONE_HAND = {"OneHanded"}
TWO_HANDS = {"SymmetricalOrAlternating", "AsymmetricalSameHandshape", "AsymmetricalDifferentHandshape"}


def agree(values: list[str | None]) -> str | None:
    return values[0] if values and len(set(values)) == 1 else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("signdata", type=Path, help="ASL-LEX signdata.csv (downloaded from the OSF project zpha4)")
    parser.add_argument("--catalog", type=Path, default=Path("catalog/sign-catalog.json"))
    parser.add_argument("--output", type=Path, default=Path("catalog/sign-facts.json"))
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(args.signdata.open(encoding="latin-1")))
    signs = {}
    for sign in catalog["signs"]:
        if sign["status"] != "supported":
            continue
        gloss = sign["displayGloss"].lower()
        entries = [row for row in rows if row["LemmaID"].lower() == gloss or row["EntryID"].lower() == gloss]
        if not entries:
            print(f"{gloss:9s} not in ASL-LEX; no facts written")
            continue
        types = [row["SignType.2.0"] for row in entries]
        counts = {"one" if t in ONE_HAND else "two" if t in TWO_HANDS else "other" for t in types}
        hands = counts.pop() if len(counts) == 1 else "varies"
        signs[sign["id"]] = {
            "aslLexEntries": len(entries),
            "hands": hands if hands in ("one", "two", "varies") else "varies",
            "signType": agree(types),
            "majorLocation": agree([row["MajorLocation.2.0"] for row in entries]),
            "minorLocation": agree([row["MinorLocation.2.0"] for row in entries]),
            "movement": agree([row["Movement.2.0"] for row in entries]),
            "repeated": agree([row["RepeatedMovement.2.0"] for row in entries]),
            "handshape": agree([row["Handshape.2.0"] for row in entries]),
            "nonDominantHandshape": agree([row["NonDominantHandshape.2.0"] for row in entries]),
        }
        print(f"{gloss:9s} entries {len(entries)}  hands {signs[sign['id']]['hands']}")
    output = {
        "schemaVersion": 1,
        "source": {
            "name": "ASL-LEX 2.0",
            "citation": "Sehyr, Caselli, Cohen-Goldberg & Emmorey (2021), J. Deaf Studies and Deaf Education 26(2), 263-277, doi 10.1093/deafed/enaa038",
            "license": "CC BY 4.0",
            "url": "https://osf.io/zpha4/",
            "note": "Codes describe citation forms; the PopSign example may differ. Fields are omitted when a sign's ASL-LEX forms disagree.",
        },
        "signs": signs,
    }
    args.output.write_text(json.dumps(output, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
