# Research

> EDITING DIRECTIVE: DEVELOPER AND AGENT EDIT THIS FILE COLLABORATIVELY. THE DEVELOPER MUST REVIEW AND APPROVE ITS CONTENT.

Purpose: Keep the evidence, decisions, and current scope that guide the build.

## Working agreement

Developer: Direct the inquiry toward what the next decision needs, judge sources and options, make the consequential decisions, and keep this file current.

Agent: Read the project documents and inspect the project. Help investigate, compare options, and test assumptions quickly. Verify sources directly.

When you begin this step, start a fresh chat so its transcript stays clean. For example:

`Read the project documents and help me research what I need for the next build decision.`

## Inquiry and decisions

Record what informs your build decisions: the questions you investigated, useful sources and what they support, experiments and their results, and the decisions you made with your reasons. Distinguish evidence from assumptions; an Agent's recommendation alone is not evidence.

### Nov 2 — PopSign catalog source check

- The official download guide supports per-sign tar archives organized by dataset, category, split, and sign. It says website preview assets are altered for preview and should not be reused.
- `https://signdata.cc.gatech.edu/data/popsign_v1_0/game/train/after.tar` returned HTTP 200. The equivalent `popsign_v2_1` route returned HTTP 404, even though the website exposes a v2.1 page. The first catalog is therefore pinned to the verified `popsign_v1_0` download ID.
- Train, validation, and test archive URLs returned HTTP 200 for the five structural samples: `after`, `hear`, `pen`, `man`, and `puppy`.
- These five entries test the catalog structure only. They are not yet the approved model vocabulary and have not been assessed for visual distinction, variation, or suitability.
- Decision: build an open-source Handshape metadata catalog that references PopSign with stable IDs and provenance. Do not copy dataset media or represent the catalog as an authoritative ASL dictionary.

### Nov 5–6 — PopSign preprocessing feasibility

- The official PopSign v1.0 data card reports 250 one-handed smartphone signs, 47 signers, and 1.1 TB of identifiable video. The paper reports official signer-separated splits of 31 train, eight validation, and eight test signers. It also documents a hand-landmark LSTM baseline, left-dominant normalization, and a 60-frame input. Sources: [official data card](https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/index.html) and [NeurIPS 2023 paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/00dada608b8db212ea7d9d92b24c68de-Paper-Datasets_and_Benchmarks.pdf).
- The `after` archives were measured at approximately 2.10 GB train, 0.76 GB validation, and 0.56 GB test. Downloading whole archives for an early feasibility run was rejected as wasteful. The uncompressed tar server supports byte ranges, so the project downloader indexes headers and retrieves selected MP4 members into Git-ignored storage.
- Three train clips from distinct filename signer prefixes produced `64 x 188` contract-v1 tensors. Hand detection covered 100%, 41%, and 62% of decoded frames; compact body anchors were available in 100% of frames. Local, ignored overlay images showed hand and body joints aligned with representative source frames. Missing hand detections during blur must remain explicit model input rather than being silently interpolated or filtered away.
- A bounded five-sign download stopped after two external failures: first a source-server read timeout and then DNS resolution failure. Nineteen clips were retained: `after` had 5 train/3 validation/3 test examples, and `hear` had 5 train/3 validation examples.
- A preliminary two-class held-out validation smoke test used five train clips and three validation clips per class. One-nearest-neighbor and class-centroid baselines each reached 4/6 top-1 (`66.7%`) but produced different confusion patterns. Synthetic idle and degraded inputs were always assigned a known class because no rejection threshold exists. This is not an integration-ready model and does not satisfy the five-sign recognition gate.
- Decision: keep landmark contract v1 and the range-based sample tooling. Do not export the two-class model. Resume the five-sign, signer-separated evaluation only after the official archive server is reachable; then revise or reduce the provisional 25-sign list in `training/vocabulary-candidates.md` using counts, overlay inspection, and confusion evidence.

### Nov 6 — Completed five-sign feasibility run

- The source server recovered and the bounded sample completed: 55 videos and 301.5 MB, with five training, three validation, and three test clips per sign across `after`, `hear`, `man`, `pen`, and `puppy`. Filename signer prefixes are distinct within each sign/split sample; the official archives keep train, validation, and test signers separated.
- All 55 clips produced `64 x 188` tensors. Selected body anchors were available in every decoded frame. Hand coverage varied from 12.2% to 100%. One `pen` training clip was a 755-frame outlier with 14% hand coverage; it remained in the honest first run rather than being removed after seeing results.
- Without dominant-hand normalization, validation top-1 was 40.0% for one-nearest-neighbor and 26.7% for class-centroid. The contract was corrected to canonical dominant/non-dominant slots because anatomical left/right slots unfairly encode signer handedness. With that correction, validation top-1 was 20.0% and 33.3%; test top-1 was 33.3% and 20.0%. The correction is retained as a fairness/input-contract rule even though it did not rescue the distance baselines.
- Re-testing the three low-coverage `after` validation clips with the PopSign paper's 0.5 detection/0.1 tracking setting changed coverage from 17.0/12.2/20.8% to 14.9/8.2/22.6%. This setting was rejected and the earlier 0.4 thresholds retained.
- Validation-only vocabulary reduction selected `hear` plus `puppy` for one-nearest-neighbor; it scored 5/6 on validation and 5/6 on test. This post-reduction two-class result is useful diagnostic evidence, not enough classes or examples for product integration. No model is exported.
- Decision required: either approve a larger per-class sample and one small temporal model, or reduce the first supported vocabulary to a deliberately tiny proof. Phase 3 browser integration remains blocked until the Developer sets the acceptable feasibility target.

## Scope

### Stretch goals

Keep the current stretch goals in priority order, starting from your approved pitch, noting cuts and additions.

### Scope changes

Record consequential changes to the approved scope: what changed, why, and what was added or cut. Update `spec.md` when a change alters the intended behavior.

## Sources and credits

List every external source, code library, asset, and dataset you use, with its link, license or usage terms, and required credit.

### Datasets

| Source | Link | License or terms | Required credit | Status |
|---|---|---|---|---|
| PopSign ASL v1.0 (Georgia Tech, Deaf Professional Arts Network) | https://signdata.cc.gatech.edu/view/datasets/popsign_v1_0/ | CC BY 4.0 per its dataset page and supplemental licensing plan; suitable use: isolated sign recognition; unsuitable: continuous recognition and sign-to-English translation | Attribution to the dataset and its paper (NeurIPS 2023 Datasets and Benchmarks; DOI 10.52202/075280-0011) | Primary catalog/training candidate; v1.0 per-sign routes verified Nov 2; raw dataset is about 1.1 TB, so use sign-level subsets |
| ASL Citizen (Microsoft Research and collaborators) | https://www.microsoft.com/en-us/research/project/asl-citizen/ | [Dataset license](https://www.microsoft.com/en-us/research/project/asl-citizen/dataset-license/): non-commercial research use only; no distribution of the data or modifications; grant-back to Microsoft; silent on trained models | Cite Desai et al. 2023, "ASL Citizen: A Community-Sourced Dataset for Advancing Isolated Sign Language Recognition", arXiv:2304.05934 (BibTeX on the project page) | Not used yet. Permission email to ASL_Citizen@microsoft.com bounced (550 5.4.1) on Nov 2; question about trained models unresolved |
| ASL-LEX 2.0 | https://osf.io/zpha4/ | CC BY 4.0 per OSF project metadata; license of the example videos not checked | Cite Sehyr, Caselli, Cohen-Goldberg & Emmorey (2021), J. Deaf Studies and Deaf Education 26(2), 263-277, doi 10.1093/deafed/enaa038 | Candidate for sign metadata; not used yet |
| Kaggle Google ISLR (asl-signs) | https://www.kaggle.com/competitions/asl-signs | Not verified (page could not be read) | Unknown | Fallback only |
| WLASL | https://github.com/dxli94/WLASL | C-UDA 1.0 | n/a | Not used: labels from video titles, documented gloss inconsistency (Neidle and Ballard, Boston University) |

### Code libraries and models

| Source | Link | License | Credit | Status |
|---|---|---|---|---|
| MediaPipe Tasks Vision (Hand Landmarker) | https://github.com/google/mediapipe | Apache 2.0 (repository license); the downloaded hand_landmarker.task model file's own terms still to confirm | Google MediaPipe | In use in the tracking spike |
| Ajv JSON Schema validator | https://github.com/ajv-validator/ajv | MIT | Ajv | Used at development time to validate the sign catalog |
| Vite, TypeScript | https://vite.dev, https://www.typescriptlang.org | MIT, Apache 2.0 (verify at install time) | n/a | In use |

### Background sources

- Learner lookup research: Towards an AI-Driven Video-Based American Sign Language Dictionary, https://arxiv.org/html/2504.05857v1
- Camera-based lookup prototypes: https://link.springer.com/chapter/10.1007/978-3-030-70650-0_14 and https://arxiv.org/abs/2407.13571v1
- Deaf community perspectives on sign language technology: Northeastern survey (2026), https://news.northeastern.edu/2026/03/19/sign-language-technology-skepticism/

### Assets

- **Logo draft** (`reference/handshape-logo-draft.png`): AI-generated image. Generated by the Developer with ChatGPT (OpenAI) from a prompt written with the Agent; exact model and date: [Developer to fill in]. Usage terms: [Developer to check the tool's terms for generated images]. Not a human-drawn asset; the hand shape is abstract and does not depict a specific ASL sign.
