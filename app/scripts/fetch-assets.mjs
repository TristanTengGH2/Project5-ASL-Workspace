// Downloads the MediaPipe model files and copies the WASM runtime so the app
// serves everything itself (no third-party CDN at runtime).
import { mkdir, writeFile, cp } from "node:fs/promises";

const MODELS = {
  "hand_landmarker.task":
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
  "pose_landmarker_lite.task":
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
};

await mkdir("public/models", { recursive: true });
for (const [name, url] of Object.entries(MODELS)) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${name}: HTTP ${res.status}`);
  const bytes = Buffer.from(await res.arrayBuffer());
  await writeFile(`public/models/${name}`, bytes);
  console.log(`${name}: ${(bytes.length / 1e6).toFixed(1)} MB`);
}
await cp("node_modules/@mediapipe/tasks-vision/wasm", "public/wasm", { recursive: true });
console.log("wasm runtime copied");
