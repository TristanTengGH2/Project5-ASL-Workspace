# Handshape sign catalog

This directory contains the versioned metadata contract for signs that Handshape may evaluate and support. It is a project catalog, not an authoritative ASL dictionary. The current five entries are structural samples only; none is approved model vocabulary yet.

## Files

- `sign-catalog.json`: single source of truth for sign and source metadata.
- `sign-catalog.schema.json`: JSON Schema for the catalog structure.

The app generates `app/public/data/sign-catalog.json` from the root source. Do not edit or commit the generated copy.

## Validate and prepare

From `app/`:

```sh
npm run validate:catalog
npm run prepare:catalog
```

`npm run dev` and `npm run build` prepare the catalog automatically. Validation checks the JSON Schema plus unique IDs, source references, language consistency, display glosses, and versioned archive URL structure.

## Entry statuses

- `sample`: exercises the catalog structure; not reviewed for vocabulary use.
- `candidate`: under review for data coverage, visual distinction, variants, and project fit.
- `supported`: included in a tested released model and visible as supported in the app.
- `rejected`: reviewed but excluded, with the reason recorded in `notes`.

Changing a status to `supported` requires a corresponding model version and evaluation evidence. A sign request begins outside the catalog and does not create or verify an ASL sign.

## Source and license

The current source is PopSign ASL v1.0 from the Georgia Institute of Technology and Deaf Professional Arts Network, licensed CC BY 4.0. Cite the dataset and its NeurIPS 2023 Datasets and Benchmarks paper as recorded in `sign-catalog.json` and `research.md`.

The official download guide says the website preview media is altered for preview and should not be reused. Catalog entries therefore reference verified original archive URLs. The repository does not redistribute PopSign videos or extracted landmarks.

## Contribution rules

1. Use a stable source-scoped ID; never use an editable English gloss as the ID.
2. Keep the ASL language code `ase` and separate English glosses from sign identity.
3. Record the exact dataset version, license, attribution, and source URLs.
4. Do not add a requested or regional sign without a verified source and appropriate ASL review.
5. Do not commit videos, extracted landmarks, model training data, or website preview assets. Downloaded data belongs in the root git-ignored `datasets/` directory.
6. Run catalog validation and the production build before committing changes.

If another project later consumes the catalog or it develops independent releases and governance, it can be split into a separate repository. Until then, it remains a self-contained module in the Handshape repository.
