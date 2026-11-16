import { copyFile, mkdir } from "node:fs/promises";

const sourceUrl = new URL("../../catalog/sign-catalog.json", import.meta.url);
const outputDirectoryUrl = new URL("../public/data/", import.meta.url);
const outputUrl = new URL("sign-catalog.json", outputDirectoryUrl);

const referencesUrl = new URL("../../catalog/sign-references.json", import.meta.url);

await mkdir(outputDirectoryUrl, { recursive: true });
await copyFile(sourceUrl, outputUrl);
await copyFile(referencesUrl, new URL("sign-references.json", outputDirectoryUrl));
await copyFile(new URL("../../catalog/sign-facts.json", import.meta.url), new URL("sign-facts.json", outputDirectoryUrl));

console.log("Prepared sign catalog and sign references for the app.");
