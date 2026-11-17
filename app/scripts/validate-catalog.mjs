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

  // Every supported sign needs a well-formed "How to sign" animation, and none may be orphaned.
  const references = JSON.parse(await readFile(new URL("../../catalog/sign-references.json", import.meta.url), "utf8"));
  const supported = new Set(catalog.signs.filter((sign) => sign.status === "supported").map((sign) => sign.id));
  for (const id of supported) if (!references.signs[id]) semanticErrors.push(`${id}: missing sign reference`);
  for (const [id, reference] of Object.entries(references.signs)) {
    if (!supported.has(id)) semanticErrors.push(`${id}: reference does not belong to a supported catalog sign`);
    const valid = Array.isArray(reference.frames) && reference.frames.length === references.frames
      && reference.frames.every((frame) => frame.length === references.points * 2 && frame.every(Number.isFinite));
    if (!valid) semanticErrors.push(`${id}: reference must be ${references.frames} frames of ${references.points} finite points`);
    if (reference.otherFrames !== undefined) {
      const otherValid = Array.isArray(reference.otherFrames) && reference.otherFrames.length === references.frames
        && reference.otherFrames.every((frame) => frame.length === references.points * 2 && frame.every(Number.isFinite));
      if (!otherValid) semanticErrors.push(`${id}: otherFrames must match the frame shape`);
    }
    if (!["popsign", "recorded"].includes(reference.provenance)) semanticErrors.push(`${id}: reference needs a provenance of popsign or recorded`);
  }

  const facts = JSON.parse(await readFile(new URL("../../catalog/sign-facts.json", import.meta.url), "utf8"));
  for (const id of supported) {
    if (!facts.signs[id]) semanticErrors.push(`${id}: missing sign facts`);
    else if (!["one", "two", "varies", "unknown"].includes(facts.signs[id].hands)) semanticErrors.push(`${id}: facts need a hands value`);
  }
  for (const id of Object.keys(facts.signs)) if (!supported.has(id)) semanticErrors.push(`${id}: facts do not belong to a supported catalog sign`);

  const missingSecondHand = [...supported].filter((id) => facts.signs[id]?.hands === "two" && !references.signs[id]?.otherFrames);
  if (missingSecondHand.length) console.log(`Note: ${missingSecondHand.length} two-handed sign(s) still lack a recorded second hand: ${missingSecondHand.map((id) => id.split(":").pop()).join(", ")}`);

  if (semanticErrors.length) {
    for (const error of semanticErrors) console.error(error);
    process.exitCode = 1;
  } else {
    console.log(
      `Catalog valid: ${catalog.signs.length} signs, ${Object.keys(references.signs).length} references, ${Object.keys(facts.signs).length} fact sets, ${catalog.sources.length} source, schema v${catalog.schemaVersion}.`,
    );
  }
}
