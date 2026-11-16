// Turns a recording from the reference recorder into a "How to sign" animation. Pure data code
// (no DOM) so it can be tested directly. Coordinates match the existing references: shoulder
// widths relative to the shoulder midpoint, x right and y down in the unmirrored camera image,
// the signing hand first. Only landmark numbers leave this module; no pixels are kept.

export const REFERENCE_FRAMES = 48;

export interface RecordedLandmark { x: number; y: number; z: number; visibility?: number }
export interface RecordedFrame {
  timestampMs: number;
  hands: Array<{ label: "left" | "right"; landmarks: RecordedLandmark[]; score: number }>;
  pose: RecordedLandmark[] | null;
}
export interface Take {
  frames: number[][];
  otherFrames: number[][] | null;
  stats: { trimmedFrames: number; durationMs: number; dominantLabel: "left" | "right"; reflected: boolean; dominantRate: number; otherRate: number };
}

const SHOULDERS = [11, 12] as const;
const MINIMUM_SHOULDER_FRAMES = 5;
const MINIMUM_OTHER_HAND_RATE = 0.4;

function median(values: number[]): number {
  const sorted = values.slice().sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

/** Median shoulder midpoint and width in pixels over the take; stable against pose update cadence. */
function shoulderReference(frames: RecordedFrame[], width: number, height: number): { midX: number; midY: number; scale: number } {
  const mids: Array<[number, number]> = [];
  const widths: number[] = [];
  for (const frame of frames) {
    const [left, right] = SHOULDERS.map((index) => frame.pose?.[index]);
    if (!left || !right || (left.visibility ?? 1) < 0.35 || (right.visibility ?? 1) < 0.35) continue;
    mids.push([((left.x + right.x) / 2) * width, ((left.y + right.y) / 2) * height]);
    widths.push(Math.hypot((left.x - right.x) * width, (left.y - right.y) * height));
  }
  if (mids.length < MINIMUM_SHOULDER_FRAMES) throw new Error("Both shoulders were not visible long enough. Step back so your shoulders and hands are in view.");
  return { midX: median(mids.map(([x]) => x)), midY: median(mids.map(([, y]) => y)), scale: median(widths) };
}

function holdNearest(points: Array<number[] | null>): number[][] {
  const present = points.flatMap((value, index) => (value ? [index] : []));
  return points.map((value, index) => value ?? points[present.reduce((best, candidate) => (Math.abs(candidate - index) < Math.abs(best - index) ? candidate : best))]!);
}

/** `trim` is [first, last] frame indexes, inclusive, chosen by the signer. */
export function buildTake(frames: RecordedFrame[], width: number, height: number, trim: [number, number]): Take {
  const reference = shoulderReference(frames, width, height);
  const kept = frames.slice(trim[0], trim[1] + 1);
  if (kept.length < 8) throw new Error("The trimmed take is too short.");
  const best = (frame: RecordedFrame, label: "left" | "right") =>
    frame.hands.filter((hand) => hand.label === label).sort((a, b) => b.score - a.score)[0];
  const counts = { left: kept.filter((frame) => best(frame, "left")).length, right: kept.filter((frame) => best(frame, "right")).length };
  // Same rule as the model contract: the hand tracked in more frames signs; ties keep the right hand.
  const dominantLabel: "left" | "right" = counts.left > counts.right ? "left" : "right";
  const otherLabel = dominantLabel === "left" ? "right" : "left";
  const reflected = dominantLabel === "left"; // canonical coordinates are right-dominant
  const toPoints = (frame: RecordedFrame, label: "left" | "right"): number[] | null => {
    const hand = best(frame, label);
    if (!hand || hand.landmarks.length !== 21) return null;
    return hand.landmarks.flatMap((point) => {
      const x = (point.x * width - reference.midX) / reference.scale;
      return [reflected ? -x : x, (point.y * height - reference.midY) / reference.scale];
    });
  };
  const dominantRate = counts[dominantLabel] / kept.length;
  const otherRate = counts[otherLabel] / kept.length;
  if (dominantRate < 0.5) throw new Error("The signing hand was tracked in too few frames. Keep it clearly in view.");
  const resample = (series: number[][]): number[][] => {
    const first = kept[0].timestampMs;
    const span = kept[kept.length - 1].timestampMs - first;
    return Array.from({ length: REFERENCE_FRAMES }, (_, index) => {
      const target = first + (span * index) / (REFERENCE_FRAMES - 1);
      let nearest = 0;
      kept.forEach((frame, at) => { if (Math.abs(frame.timestampMs - target) < Math.abs(kept[nearest].timestampMs - target)) nearest = at; });
      return series[nearest].map((value) => Math.round(value * 1000) / 1000);
    });
  };
  const dominant = resample(holdNearest(kept.map((frame) => toPoints(frame, dominantLabel))));
  const other = otherRate >= MINIMUM_OTHER_HAND_RATE ? resample(holdNearest(kept.map((frame) => toPoints(frame, otherLabel)))) : null;
  return {
    frames: dominant,
    otherFrames: other,
    stats: { trimmedFrames: kept.length, durationMs: kept[kept.length - 1].timestampMs - kept[0].timestampMs, dominantLabel, reflected, dominantRate, otherRate },
  };
}
