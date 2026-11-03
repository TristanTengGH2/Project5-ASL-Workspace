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
