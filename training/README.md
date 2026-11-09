# Phase 2 training workspace

This directory contains reproducible code and small, reviewable metadata for
the Phase 2 feasibility test. Downloaded videos, extracted landmarks, models,
and evaluation outputs belong in the root `datasets/` and
`training-artifacts/` directories, which Git ignores.

## Landmark contract

`landmark-contract.v1.json` is the shared input contract for offline training
and later browser inference. Version 1 produces a `64 x 188` sequence:

- 68 features for dominant and non-dominant hand slots;
- 13 compact body anchors with `x`, `y`, `z`, and visibility;
- explicit presence values so missing landmarks are not confused with zeros.

The contract preserves hand orientation and broad body-relative location. It
does not yet represent eyebrow, eyelid, or mouth-expression features, so signs
that depend on those distinctions are outside the first model vocabulary.
Left-dominant sequences are reflected into canonical right-dominant coordinates,
including paired body anchors, so handedness is not learned as a sign class.
The exact confidence thresholds and model hashes are written into each
extraction manifest. A comparison with the PopSign paper's 0.5 detection and
0.1 tracking settings reduced average hand coverage in the three difficult
`after` validation clips, so the tested 0.4 defaults remain in use.

## Small PopSign downloads

PopSign's per-sign archives can be several gigabytes. The sample downloader
indexes the remote uncompressed tar and retrieves only selected MP4 byte
ranges. It refuses unsafe archive paths and writes only under `datasets/`.

Example (from the repository root):

```sh
python3 training/download_popsign_sample.py \
  --url https://signdata.cc.gatech.edu/data/popsign_v1_0/game/train/after.tar \
  --limit 3
```

The filename prefix before the first hyphen is retained as the source signer
identifier. Split membership still comes from the official archive path; the
pipeline must never randomly mix clips across the published splits.

## Extract a feasibility sample

Create a local environment and reuse the same model assets as the browser:

```sh
python3 -m venv .venv
.venv/bin/pip install -r training/requirements.txt
cd app && npm run fetch-assets && cd ..
MPLCONFIGDIR=/tmp/handshape-mpl .venv/bin/python training/extract_landmarks.py \
  datasets/popsign-v1-0/sample \
  --handedness-mode swap
```

`swap` corrects MediaPipe's selfie-mirror handedness convention for the
unmirrored source frames. The option is required so a source convention is
never assumed silently. Before training, review the ignored overlay images in
`training-artifacts/phase2-extraction/inspection/` and confirm the labels.

The extractor records source, contract, and model hashes; decoded-frame counts;
hand/body detection rates; fixed tensor shapes; and the source-frame indexes
selected during timestamp-based resampling. Source images remain local because
they contain identifiable dataset participants.

For the bounded five-sign feasibility run, download five training signers and
three held-out signers in each official validation/test split:

```sh
python3 training/download_catalog_sample.py --train 5 --val 3 --test 3
```

This command follows the catalog URLs, caps individual clips at 25 MB, and
retains the official split directory. It is a feasibility sample, not the full
dataset and not enough evidence to claim production accuracy.

Run the deterministic feasibility baseline after extraction:

```sh
MPLCONFIGDIR=/tmp/handshape-mpl .venv/bin/python training/evaluate_baseline.py
```

It compares one-nearest-neighbor and class-centroid sequence distances on the
official validation and test splits. Any vocabulary reduction is selected using
validation only and then reported once on test. Synthetic missing-tracking
inputs document behavior before unknown-sign rejection exists. A two-class or
otherwise incomplete run must remain labeled as a smoke test and must not be
exported to the browser.

## Temporal model checkpoint

The approved larger checkpoint uses 20 training and five validation/test clips
per sign, then trains one compact bidirectional GRU. Validation controls early
stopping; the test split is evaluated only after the best validation checkpoint
is restored.

```sh
python3 training/download_catalog_sample.py \
  --train 20 --val 5 --test 5 \
  --output datasets/popsign-v1-0/phase2-five-sign-large

MPLCONFIGDIR=/tmp/handshape-mpl .venv/bin/python training/extract_landmarks.py \
  datasets/popsign-v1-0/phase2-five-sign-large \
  --handedness-mode swap \
  --output training-artifacts/phase2-five-sign-large-extraction

.venv/bin/python training/train_temporal_model.py
```

The checkpoint target is at least 70% top-1 accuracy on the official held-out
test signers across all five signs. Accuracy alone does not authorize browser
export: unknown-input rejection must also pass. If this single temporal model
misses the target, stop and review the data, preprocessing, and vocabulary
instead of adding another architecture.
