// Run with: npm run test:reference
import { buildTake, type RecordedFrame } from "../src/reference-take.ts";
const W = 1280, H = 720;
const pose = Array.from({ length: 33 }, () => ({ x: 0.5, y: 0.5, z: 0, visibility: 1 }));
pose[11] = { x: 480 / W, y: 400 / H, z: 0, visibility: 1 };  // shoulders 320 px apart, midpoint (640, 400)
pose[12] = { x: 800 / W, y: 400 / H, z: 0, visibility: 1 };
const hand = (px: number, py: number) => Array.from({ length: 21 }, (_, i) => ({ x: (px + i) / W, y: py / H, z: 0 }));
// Signer's right hand (label "right") appears on the image LEFT at (480,300); left hand at (800,300).
const make = (n: number, rightOnly: boolean, leftOnly = false): RecordedFrame[] => Array.from({ length: n }, (_, i) => ({
  timestampMs: i * 33, pose,
  hands: [
    ...(!leftOnly ? [{ label: "right" as const, score: 0.9, landmarks: hand(480, 300) }] : []),
    ...(!rightOnly ? [{ label: "left" as const, score: 0.9, landmarks: hand(800, 300) }] : []),
  ],
}));
const near = (a: number, b: number) => Math.abs(a - b) < 1e-3;
let failures = 0; const check = (name: string, ok: boolean) => { console.log(`${ok ? "PASS" : "FAIL"} ${name}`); if (!ok) failures++; };

const two = buildTake(make(60, false), W, H, [0, 59]);
check("48 frames of 42 numbers", two.frames.length === 48 && two.frames.every((f) => f.length === 42));
check("signing right hand wrist x = -0.5 shoulder widths, y = -0.3125", near(two.frames[0][0], -0.5) && near(two.frames[0][1], -0.3125));
check("other hand present with mirrored x = +0.5", two.otherFrames !== null && near(two.otherFrames[0][0], 0.5));
check("dominant right, not reflected", two.stats.dominantLabel === "right" && !two.stats.reflected);

const leftSolo = buildTake(make(60, false, true), W, H, [0, 59]);
check("left-hand solo is reflected into right-dominant coordinates (x = -0.5)", leftSolo.stats.reflected && near(leftSolo.frames[0][0], -0.5) && leftSolo.otherFrames === null);

const one = buildTake(make(60, true), W, H, [0, 59]);
check("one-handed take has no second hand", one.otherFrames === null && near(one.stats.otherRate, 0));

const trimmed = buildTake(make(60, false), W, H, [10, 40]);
check("trim keeps 31 frames", trimmed.stats.trimmedFrames === 31 && Math.round(trimmed.stats.durationMs) === 990);

const gaps = make(60, false).map((f, i) => (i % 5 === 0 ? { ...f, hands: f.hands.filter((h) => h.label === "right") } : f));
const filled = buildTake(gaps, W, H, [0, 59]);
check("gaps in the second hand are filled (all 48 frames finite)", filled.otherFrames !== null && filled.otherFrames.every((f) => f.every(Number.isFinite)));

let threw = false; try { buildTake(make(60, false).map((f) => ({ ...f, pose: null })), W, H, [0, 59]); } catch { threw = true; }
check("throws when shoulders were never visible", threw);
threw = false; try { buildTake(make(60, false), W, H, [0, 3]); } catch { threw = true; }
check("throws on a trim that is too short", threw);
process.exit(failures ? 1 : 0);
