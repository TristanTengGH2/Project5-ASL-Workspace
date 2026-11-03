import { copyFile, mkdir } from "node:fs/promises";

const sourceUrl = new URL("../../catalog/sign-catalog.json", import.meta.url);
const outputDirectoryUrl = new URL("../public/data/", import.meta.url);
const outputUrl = new URL("sign-catalog.json", outputDirectoryUrl);

await mkdir(outputDirectoryUrl, { recursive: true });
await copyFile(sourceUrl, outputUrl);

console.log("Prepared sign catalog for the app.");
