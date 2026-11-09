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

### Nov 9 — Larger temporal-model checkpoint blocked by source TLS

- The Developer approved expanding to 20 training and five validation/test clips per sign, then evaluating one compact temporal model against a 70% held-out top-1 target.
- The official PopSign archive host rejected verified TLS connections. Its certificate is issued to `signdata.cc.gatech.edu` by the InCommon intermediate CA, has SHA-256 fingerprint `43:F9:B6:62:06:F6:49:40:20:BA:F7:BD:4A:EE:26:78:E4:16:AA:9D:82:46:C3:37:A4:12:C7:DA:6B:2F:F0:DE`, and expired Nov 8, 2026 at 19:54:03 UTC. The certificate contains no alternate hostname. Certificate verification was not disabled.
- A discovered [Hugging Face derivative](https://huggingface.co/datasets/sign/popsign-images) was rejected for this checkpoint: it is a third-party 90.8 GB image-frame release sampled at 5 FPS, so it would change provenance, input timing, and the shared browser/offline preprocessing contract. The separate [Kaggle landmark competition release](https://www.kaggle.com/competitions/asl-signs/data) is about 40 GB and also uses a different extraction contract.
- PyTorch 2.8.0 and a deterministic one-layer bidirectional GRU training pipeline were added locally. It uses validation-only early stopping, evaluates test once after restoring the best validation checkpoint, records confusion and synthetic negative behavior, and permits browser export only if both accuracy and unknown-rejection gates pass.
- A tooling smoke test on the existing 25 training clips ran for 50 epochs, restored epoch 15, reached 20.0% validation top-1 and 6.7% test top-1, and did not export. This is not the approved larger experiment and confirms that the small sample is insufficient; it must not be presented as the temporal-model decision result.
- Decision: wait for verified TLS on the official archive host, then resume the documented 150-clip download, extraction, and single-GRU run. Do not bypass certificate verification, substitute derivative data silently, add a second architecture, or begin Phase 3.

### Nov 9 — Cross-source feature audit

- The approved Google-landmark bridge produced 150 balanced examples across five signs and signer-disjoint `100 train / 25 validation / 25 test` splits. The one approved GRU scored 60.0% validation and 48.0% test top-1, below the 70% gate.
- The frozen Google-trained model initially scored 18.2% across the 55 existing PopSign clips and predicted `pen` for 41/55 examples. No PopSign example was used to refit the model or choose a threshold.
- Contract-v1 distribution comparison exposed an inverted canonical wrist side. Google dominant wrists averaged `x = -0.529` relative to the shoulder midpoint, while PopSign extracted with `--handedness-mode swap` averaged `x = +0.568`. Re-extracting the same clips with `keep` changed PopSign to `x = -0.568`, matching Google and the intended canonical-right image side.
- The frozen model's PopSign accuracy improved from 18.2% to 25.5% with corrected handedness, confirming that the old source correction was wrong. Accuracy remained inadequate and 45/55 examples were still predicted as `pen`, so handedness is not the only mismatch.
- Google sequences contain a median 26.5 source frames versus 64 for PopSign, a 2.42x frame-count difference before both are stretched or compressed to 64 model frames. PopSign includes a 755-frame outlier. This supports the existing requirement to isolate a reviewed signing interval; the current extractor instead resamples each entire clip.
- Optional body channels leak source/tracker identity. The Google adapter treats finite hip coordinates as present in every frame because the release has no visibility values; PopSign's tracker reports the two hips in under 1% of frames at the current visibility threshold. Facial/body `z` positions and continuous visibility values also shift across MediaPipe versions.
- A de-identified landmark-only sheet confirms the handedness reflection and shows substantial interval/motion differences without copying source-video pixels. It is stored locally under the ignored source-audit artifacts and indexed in `evidence/image-history.md`.
- **Recommendation pending Developer approval:** replace contract v1 with one source-neutral contract v2 before retraining. Apply explicit per-source handedness, trim a shared hand-presence/motion interval before resampling, remove optional hips, and retain only body/location coordinates and binary masks that both sources can supply comparably. Evaluate whether body/wrist `z` should be removed because the source tracker versions do not agree. Do not mix sources under contract v1 or add a second model architecture.

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
| Kaggle Google ISLR (asl-signs) | https://www.kaggle.com/competitions/asl-signs | CC BY 4.0 plus accepted Kaggle competition rules; landmark data must not be used for identification | Cite Chow et al., "Google - Isolated Sign Language Recognition," Kaggle 2023 | In use as a Phase 2 landmark-pipeline benchmark; 150 selected sequences remain local and are not redistributed |
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
