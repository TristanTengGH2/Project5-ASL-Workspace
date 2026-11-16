// Replays local PopSign clips through the real browser pipeline in headless Chrome and writes
// per-clip rankings. Needs the dev server running (npm run dev). Videos are served only to this
// local browser from the git-ignored datasets/ directory and are never copied into the app.
//
// usage: node scripts/replay-videos.mjs <extraction-manifest.json> <output.json> [split=test] [limit]
import { spawn } from "node:child_process";
import { createReadStream, readFileSync, statSync, writeFileSync, mkdtempSync, mkdirSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";

const [manifestPath, outputPath, split = "test", limitArg] = process.argv.slice(2);
if (!manifestPath || !outputPath) throw new Error("usage: replay-videos.mjs <manifest> <output.json> [split] [limit]");
const repoRoot = path.resolve(import.meta.dirname, "../..");
const datasetsRoot = path.join(repoRoot, "datasets");
const chrome = process.env.CHROME_PATH ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const appUrl = process.env.APP_URL ?? "http://localhost:5173";

const manifest = JSON.parse(readFileSync(path.resolve(repoRoot, manifestPath), "utf8"));
const clips = manifest.videos
  .map((item) => ({ video: item.video, fps: item.fps, parts: item.video.split("/") }))
  .filter((item) => item.parts.includes(split))
  .map((item) => ({ video: item.video, fps: item.fps || 30, label: item.parts.at(-2), split }));
const selected = limitArg ? clips.slice(0, Number(limitArg)) : clips;

// Static, read-only video server restricted to datasets/, with range support for <video>.
const server = createServer((request, response) => {
  const relative = decodeURIComponent(new URL(request.url, "http://x").pathname.replace(/^\/v\//, ""));
  const file = path.resolve(repoRoot, relative);
  if (!file.startsWith(datasetsRoot + path.sep) || !file.endsWith(".mp4")) { response.writeHead(403).end(); return; }
  let size;
  try { size = statSync(file).size; } catch { response.writeHead(404).end(); return; }
  const headers = { "Access-Control-Allow-Origin": "*", "Content-Type": "video/mp4", "Accept-Ranges": "bytes" };
  const range = /bytes=(\d*)-(\d*)/.exec(request.headers.range ?? "");
  if (range) {
    const start = range[1] ? Number(range[1]) : 0;
    const end = range[2] ? Number(range[2]) : size - 1;
    response.writeHead(206, { ...headers, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": end - start + 1 });
    createReadStream(file, { start, end }).pipe(response);
  } else {
    response.writeHead(200, { ...headers, "Content-Length": size });
    createReadStream(file).pipe(response);
  }
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const videoBase = `http://127.0.0.1:${server.address().port}/v/`;

const debugPort = 9333;
const profile = mkdtempSync(path.join(tmpdir(), "replay-chrome-"));
const browser = spawn(chrome, [
  "--headless=new", `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`,
  "--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--no-first-run",
], { stdio: "ignore" });
const cleanup = () => { browser.kill(); server.close(); };
process.on("exit", cleanup);

async function debuggerUrl() {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
      const page = targets.find((target) => target.type === "page");
      if (page) return page.webSocketDebuggerUrl;
    } catch { /* Chrome is still starting. */ }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error("Chrome did not start");
}
const socket = new WebSocket(await debuggerUrl());
await new Promise((resolve) => { socket.onopen = resolve; });
let nextId = 0;
const pending = new Map();
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) { pending.get(message.id)(message); pending.delete(message.id); }
};
const send = (method, params = {}) => new Promise((resolve) => {
  const id = ++nextId; pending.set(id, resolve); socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const reply = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (reply.result.exceptionDetails) throw new Error(JSON.stringify(reply.result.exceptionDetails.exception?.description ?? reply.result.exceptionDetails));
  return reply.result.result.value;
};

await send("Page.enable");
await send("Page.navigate", { url: `${appUrl}/video-replay.html` });
for (let attempt = 0; attempt < 150 && !(await evaluate("window.replayReady === true").catch(() => false)); attempt += 1) {
  await new Promise((resolve) => setTimeout(resolve, 200));
}
if (!(await evaluate("window.replayReady === true"))) throw new Error("replay page did not become ready (is the dev server running?)");

mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
const results = [];
for (const [index, clip] of selected.entries()) {
  const url = videoBase + clip.video;
  const result = await evaluate(`window.replayClip(${JSON.stringify(url)}, ${clip.fps})`);
  results.push({ ...result, url: undefined, video: clip.video, label: clip.label, split });
  const top = result.ranking?.[0];
  console.log(`${index + 1}/${selected.length} ${clip.label.padEnd(8)} -> ${top ? `${top.label} ${(top.score * 100).toFixed(0)}%` : `ERROR ${result.error}`}`);
  writeFileSync(path.resolve(outputPath), JSON.stringify({ createdAt: new Date().toISOString(), split, results }, null, 2));
}
cleanup();
process.exit(0);
