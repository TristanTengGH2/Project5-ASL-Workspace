import { readFile } from "node:fs/promises";
import Ajv2020 from "ajv/dist/2020.js";

const schemaUrl = new URL("../../catalog/sign-catalog.schema.json", import.meta.url);
const catalogUrl = new URL("../../catalog/sign-catalog.json", import.meta.url);

const [schema, catalog] = await Promise.all(
  [schemaUrl, catalogUrl].map(async (url) => JSON.parse(await readFile(url, "utf8"))),
);

const ajv = new Ajv2020({ allErrors: true });
const validate = ajv.compile(schema);

if (!validate(catalog)) {
  for (const error of validate.errors ?? []) {
    console.error(`${error.instancePath || "/"} ${error.message}`);
  }
  process.exitCode = 1;
} else {
  const semanticErrors = [];
  const sources = new Map();

  for (const source of catalog.sources) {
    if (sources.has(source.id)) semanticErrors.push(`Duplicate source id: ${source.id}`);
    sources.set(source.id, source);
  }

  const signIds = new Set();
  for (const sign of catalog.signs) {
    if (signIds.has(sign.id)) semanticErrors.push(`Duplicate sign id: ${sign.id}`);
    signIds.add(sign.id);

    const source = sources.get(sign.source.sourceId);
    if (!source) {
      semanticErrors.push(`${sign.id}: unknown source ${sign.source.sourceId}`);
      continue;
    }

    const expectedId = `${source.id}:${sign.source.category}:${sign.source.slug}`;
    if (sign.id !== expectedId) semanticErrors.push(`${sign.id}: expected id ${expectedId}`);
    if (sign.language !== catalog.language.code) {
      semanticErrors.push(`${sign.id}: language must match catalog language`);
    }
    if (!sign.englishGlosses.includes(sign.displayGloss)) {
      semanticErrors.push(`${sign.id}: displayGloss must appear in englishGlosses`);
    }

    for (const split of ["train", "val", "test"]) {
      const expectedUrl = `https://signdata.cc.gatech.edu/data/${source.downloadId}/${sign.source.category}/${split}/${sign.source.slug}.tar`;
      if (sign.archives[split] !== expectedUrl) {
        semanticErrors.push(`${sign.id}: ${split} archive does not match its source fields`);
      }
    }
  }

  if (semanticErrors.length) {
    for (const error of semanticErrors) console.error(error);
    process.exitCode = 1;
  } else {
    console.log(
      `Catalog valid: ${catalog.signs.length} signs, ${catalog.sources.length} source, schema v${catalog.schemaVersion}.`,
    );
  }
}
