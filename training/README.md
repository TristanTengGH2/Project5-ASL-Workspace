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

## Provisional landmark contract v2

`landmark-contract.v2.json` records the approved source-neutral revision without
overwriting v1 evidence. `landmark_contract_v2.py` implements its shared feature
construction, canonical dominance, relative wrist depth, sustained-run active
interval, and candidate resampling rules. The interval selector prefers the
candidate run with the most detected dominant-hand frames and the highest
detection density, uses wrist motion only to break ties, and keeps two source
frames of context on each side. Run `python3 -m unittest test_landmark_contract_v2`
from `training/` to check it.

V2 retains all 21 local hand landmarks in 3D, shoulder-relative wrist x/y,
active-interval-relative wrist depth, and explicit presence. It removes model
confidence, optional hips, and body z; upper-body anchors use x/y plus binary
presence. The resulting frame has 167 features. A browser quality layer may
still use tracker confidence, but recognition may not learn source-specific
confidence values.

The Developer provisionally approved 48 frames. It is the only tested candidate
that passed the motion-retention and hand-presence thresholds after both source
adapters emitted trimmed v2 active intervals. Reproduce the comparison with:

```sh
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/handshape-mpl \
  .venv/bin/python training/evaluate_temporal_fidelity.py
```

The comparison uses each source's variable-length v2 active interval as the
reference. It does not train a model. Review PopSign start/middle/end frames with:

```sh
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/handshape-mpl \
  .venv/bin/python training/render_active_interval_review.py
```

That image contains identifiable dataset participants and must remain in the
Git-ignored `training-artifacts/` directory. Retraining remains a separate
Developer checkpoint after the interval review.

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
  --handedness-mode keep \
  --contract-version 2
```

`keep` is the verified PopSign source rule. A Nov 9 cross-source audit found
that `swap` placed the canonical dominant wrist on the opposite side from the
Google landmarks; `keep` aligned their shoulder-relative x direction. The
option remains required so a source convention is never assumed silently.
Before training, review the ignored overlay images in
`training-artifacts/phase2-extraction/inspection/` and confirm the labels.

The extractor records source, contract, and model hashes; decoded-frame counts;
hand/body detection rates; fixed tensor shapes; and the source-frame indexes
selected during timestamp-based resampling. Source images remain local because
they contain identifiable dataset participants.

Adapt the signer-separated Google landmark subset to the same v2 contract with:

```sh
.venv/bin/python training/import_google_landmarks.py --contract-version 2
```

The token stays outside the repository. Both v2 adapters preserve their raw
trimmed `active_features` beside the fixed `48 x 167` tensor so temporal-fidelity
checks do not compare one already-resampled representation against another.

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
  --handedness-mode keep \
  --output training-artifacts/phase2-five-sign-large-extraction

.venv/bin/python training/train_temporal_model.py
```

`--signs` accepts either catalog IDs or display glosses. Omit it to download
every catalog sign. For example, the Nov 11 source-matched checkpoint excluded
the rejected `puppy` entry with:

```sh
python3 training/download_catalog_sample.py \
  --train 20 --val 5 --test 5 \
  --signs after hear man pen \
  --output datasets/popsign-v1-0/four-sign-20-5-5
```

Generate the pre-training integrity and tracking report with:

```sh
.venv/bin/python training/report_popsign_checkpoint.py \
  datasets/popsign-v1-0/phase2-five-sign-large/sample-manifest.json \
  training-artifacts/phase2-five-sign-large-extraction/extraction-manifest.json \
  --output training-artifacts/phase2-five-sign-large-extraction/quality-report.json
```

For broad screening, use resumable sign batches. The download manifest and
extraction manifest are updated atomically after every video. Failed clips are
recorded as screening evidence instead of silently removed:

```sh
.venv/bin/python training/download_catalog_sample.py \
  --all-popsign-game --train 5 --val 2 --test 2 --batch-signs 10 \
  --output datasets/popsign-v1-0/all-sign-screening-5-2-2

MPLCONFIGDIR=/tmp/handshape-mpl .venv/bin/python training/extract_landmarks.py \
  datasets/popsign-v1-0/all-sign-screening-5-2-2 \
  --contract-version 2 --handedness-mode keep --continue-on-error \
  --output training-artifacts/popsign-all-sign-screening-v2

.venv/bin/python training/report_popsign_checkpoint.py \
  datasets/popsign-v1-0/all-sign-screening-5-2-2/sample-manifest.json \
  training-artifacts/popsign-all-sign-screening-v2/extraction-manifest.json \
  --output training-artifacts/popsign-all-sign-screening-v2/quality-report.json

.venv/bin/python training/rank_popsign_screening.py \
  training-artifacts/popsign-all-sign-screening-v2/extraction-manifest.json \
  --output training-artifacts/popsign-all-sign-screening-v2/ranking.json
```

The ranking uses training and validation tracking quality only. It does not
read test metrics, measure recognition accuracy, or prove that two signs are
visually distinguishable.

The checkpoint target is at least 70% top-1 accuracy on the official held-out
test signers across all five signs. Accuracy alone does not authorize browser
export: unknown-input rejection must also pass. If this single temporal model
misses the target, stop and review the data, preprocessing, and vocabulary
instead of adding another architecture.

The temporal evaluator reports top-1, top-3, top-5, per-example rankings, and
the full confusion matrix. Test evaluation occurs only after the checkpoint
selected by validation loss is restored.

## Temporary Google-landmark bridge

If the official PopSign video server is unavailable, the Google Isolated Sign
Language Recognition corpus can validate the same five-sign temporal pipeline.
It contains MediaPipe Holistic landmark sequences rather than source videos.
The importer keeps participants disjoint across train, validation, and test,
downloads only 150 selected sequences, and adapts them to the `64 x 188` input
shape. This bridge does not replace the final PopSign evaluation.

First accept the `asl-signs` competition rules on Kaggle. Generate a personal
API token and store it at `~/.kaggle/access_token` with owner-only permissions.
Do not put a token or credentials in this repository. Then run:

```sh
.venv/bin/pip install -r training/requirements.txt
.venv/bin/python training/import_google_landmarks.py
.venv/bin/python training/train_temporal_model.py \
  --manifest training-artifacts/google-five-sign-extraction/extraction-manifest.json \
  --output training-artifacts/google-five-sign-gru
```

The adapter records three source limitations in its manifest: timestamps are
not published, landmark confidence values are unavailable, and the source uses
MediaPipe 0.9.0.1 rather than the current browser tracker. Results must be
labeled as a pipeline-validation benchmark. The already verified 55 PopSign
clips remain a separate cross-dataset check; never disable TLS verification to
retrieve additional PopSign files.

After the Google-trained model finishes, evaluate that exact frozen checkpoint
against the existing verified PopSign extraction without refitting it:

```sh
.venv/bin/python training/evaluate_temporal_transfer.py
```

This transfer result is diagnostic only. It must remain separate from the
Google validation/test score and cannot be used to tune the model.

Audit feature distributions and render de-identified skeleton timelines before
changing preprocessing or running another model:

```sh
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/handshape-mpl \
  .venv/bin/python training/audit_feature_sources.py
```

The ignored `training-artifacts/phase2-source-audit/` output compares canonical
wrist side, missing-hand rates, body availability, source-frame ranges, and
standardized feature-group shifts. Its skeleton sheet contains landmarks only,
not source-video frames.
