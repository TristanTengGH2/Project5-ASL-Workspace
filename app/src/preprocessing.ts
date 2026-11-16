import type { NormalizedLandmark } from "@mediapipe/tasks-vision";
import type { TrackingFrame } from "./tracker";

export const FRAME_FEATURES = 167;
export const NORMALIZED_FRAMES = 48;
const HAND_FEATURES = 67;
const BODY_ANCHORS = [0, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14] as const;
const BODY_PAIRS = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]] as const;

export interface FeatureFrame {
  timestampMs: number;
  features: Float32Array;
}

export interface SequenceDiagnostics {
  rawFrameCount: number;
  captureDurationMs: number;
  activeStartFrame: number;
  activeEndFrame: number;
  activeFrameCount: number;
  activeDurationMs: number;
  detectedDominantHand: "left" | "right";
  dominanceMirrored: boolean;
  dominantHandPresenceRate: number;
  nonDominantHandPresenceRate: number;
  twoHandPresenceRate: number;
  bodyAnchorPresenceRate: number;
  dominantWristPath: number;
}

export interface PreparedBrowserSequence {
  tensor: Float32Array;
  diagnostics: SequenceDiagnostics;
}

function distance2d(a: NormalizedLandmark, b: NormalizedLandmark): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function finitePoint(point: NormalizedLandmark | undefined): point is NormalizedLandmark {
  return Boolean(point && Number.isFinite(point.x) && Number.isFinite(point.y) && Number.isFinite(point.z));
}

function visiblePosePoint(point: NormalizedLandmark | undefined): point is NormalizedLandmark {
  return finitePoint(point) && (point.visibility ?? 1) >= 0.35;
}

export function shouldersReady(pose: NormalizedLandmark[] | null): boolean {
  return Boolean(pose && visiblePosePoint(pose[11]) && visiblePosePoint(pose[12]) && distance2d(pose[11], pose[12]) > 1e-6);
}

function handBlock(hand: NormalizedLandmark[] | null, pose: NormalizedLandmark[] | null): Float32Array {
  const output = new Float32Array(HAND_FEATURES);
  if (!hand || hand.length !== 21 || !hand.every((point) => finitePoint(point))) return output;
  const wrist = hand[0];
  const palmScale = ([5, 9, 17] as const).reduce((sum, index) => sum + distance2d(hand[index], wrist), 0) / 3;
  if (palmScale <= 1e-6) return output;
  hand.forEach((point, index) => {
    output[index * 3] = (point.x - wrist.x) / palmScale;
    output[index * 3 + 1] = (point.y - wrist.y) / palmScale;
    output[index * 3 + 2] = (point.z - wrist.z) / palmScale;
  });
  if (pose && shouldersReady(pose)) {
    const left = pose[11];
    const right = pose[12];
    const scale = distance2d(left, right);
    output[63] = (wrist.x - (left.x + right.x) / 2) / scale;
    output[64] = (wrist.y - (left.y + right.y) / 2) / scale;
    output[65] = (wrist.z - (left.z + right.z) / 2) / scale;
  }
  output[66] = 1;
  return output;
}

function bodyBlock(pose: NormalizedLandmark[] | null): Float32Array {
  const output = new Float32Array(BODY_ANCHORS.length * 3);
  if (!pose || !shouldersReady(pose)) return output;
  const left = pose[11];
  const right = pose[12];
  const originX = (left.x + right.x) / 2;
  const originY = (left.y + right.y) / 2;
  const scale = distance2d(left, right);
  BODY_ANCHORS.forEach((poseIndex, outputIndex) => {
    const point = pose[poseIndex];
    if (!visiblePosePoint(point)) return;
    output[outputIndex * 3] = (point.x - originX) / scale;
    output[outputIndex * 3 + 1] = (point.y - originY) / scale;
    output[outputIndex * 3 + 2] = 1;
  });
  return output;
}

export function frameFeatures(frame: TrackingFrame): Float32Array {
  const slots = new Map<string, TrackingFrame["hands"][number]>();
  for (const hand of frame.hands) {
    const label = hand.modelLabel.toLowerCase();
    if ((label === "left" || label === "right") && (!slots.has(label) || hand.score > slots.get(label)!.score)) slots.set(label, hand);
  }
  const output = new Float32Array(FRAME_FEATURES);
  output.set(handBlock(slots.get("left")?.landmarks ?? null, frame.pose), 0);
  output.set(handBlock(slots.get("right")?.landmarks ?? null, frame.pose), HAND_FEATURES);
  output.set(bodyBlock(frame.pose), HAND_FEATURES * 2);
  return output;
}

function mirrorHand(block: Float32Array) {
  const result = new Float32Array(block);
  for (let index = 0; index < 21; index += 1) result[index * 3] *= -1;
  result[63] *= -1;
  return result;
}

function canonicalize(frames: FeatureFrame[]): { features: Float32Array[]; dominant: "left" | "right" } {
  const leftCount = frames.filter((frame) => frame.features[66] > 0).length;
  const rightCount = frames.filter((frame) => frame.features[HAND_FEATURES + 66] > 0).length;
  const dominant = leftCount > rightCount ? "left" : "right";
  const features = frames.map(({ features: source }) => {
    const left = source.slice(0, HAND_FEATURES);
    const right = source.slice(HAND_FEATURES, HAND_FEATURES * 2);
    const body = source.slice(HAND_FEATURES * 2);
    let dominantHand = right;
    let otherHand = left;
    if (dominant === "left") {
      dominantHand = mirrorHand(left);
      otherHand = mirrorHand(right);
      for (let index = 0; index < BODY_ANCHORS.length; index += 1) body[index * 3] *= -1;
      for (const [leftIndex, rightIndex] of BODY_PAIRS) {
        for (let channel = 0; channel < 3; channel += 1) {
          const first = leftIndex * 3 + channel;
          const second = rightIndex * 3 + channel;
          [body[first], body[second]] = [body[second], body[first]];
        }
      }
    }
    const output = new Float32Array(FRAME_FEATURES);
    output.set(dominantHand, 0);
    output.set(otherHand, HAND_FEATURES);
    output.set(body, HAND_FEATURES * 2);
    return output;
  });
  return { features, dominant };
}

function selectActiveInterval(features: Float32Array[]): [number, number] {
  const present = features.map((frame) => frame[66] > 0);
  const indexes = present.flatMap((value, index) => value ? [index] : []);
  if (!indexes.length) throw new Error("No dominant hand was tracked during the scan.");
  const bridged = present.slice();
  for (let index = 1; index < indexes.length; index += 1) {
    const left = indexes[index - 1];
    const right = indexes[index];
    if (right - left - 1 <= 3) for (let fill = left; fill <= right; fill += 1) bridged[fill] = true;
  }
  const runs: Array<{ start: number; end: number; score: number[] }> = [];
  for (let index = 0; index < bridged.length;) {
    if (!bridged[index]) { index += 1; continue; }
    const start = index;
    while (index < bridged.length && bridged[index]) index += 1;
    const end = index;
    const detections = present.slice(start, end).filter(Boolean).length;
    const span = end - start;
    const density = detections / span;
    let wristMotion = 0;
    let prior: Float32Array | null = null;
    for (let frame = start; frame < end; frame += 1) {
      if (!present[frame]) continue;
      if (prior) wristMotion += Math.hypot(features[frame][63] - prior[63], features[frame][64] - prior[64]);
      prior = features[frame];
    }
    runs.push({ start, end, score: [detections * density, detections, density, wristMotion, span, -start] });
  }
  runs.sort((a, b) => {
    for (let index = 0; index < a.score.length; index += 1) if (a.score[index] !== b.score[index]) return b.score[index] - a.score[index];
    return 0;
  });
  return [Math.max(0, runs[0].start - 2), Math.min(features.length, runs[0].end + 2)];
}

export function prepareSequenceDetailed(frames: FeatureFrame[]): PreparedBrowserSequence {
  if (frames.length < 2) throw new Error("Not enough tracked frames were captured.");
  const { features, dominant } = canonicalize(frames);
  const [start, end] = selectActiveInterval(features);
  const active = features.slice(start, end).map((frame) => frame.slice());
  for (const offset of [0, HAND_FEATURES]) {
    const depths = active.filter((frame) => frame[offset + 66] > 0).map((frame) => frame[offset + 65]).sort((a, b) => a - b);
    if (depths.length) {
      const middle = Math.floor(depths.length / 2);
      const median = depths.length % 2 ? depths[middle] : (depths[middle - 1] + depths[middle]) / 2;
      for (const frame of active) if (frame[offset + 66] > 0) frame[offset + 65] -= median;
    }
  }
  const positions = frames.slice(start, end).map((frame) => frame.timestampMs);
  const output = new Float32Array(NORMALIZED_FRAMES * FRAME_FEATURES);
  for (let targetIndex = 0; targetIndex < NORMALIZED_FRAMES; targetIndex += 1) {
    const target = positions[0] + (positions.at(-1)! - positions[0]) * targetIndex / (NORMALIZED_FRAMES - 1);
    let nearest = 0;
    for (let index = 1; index < positions.length; index += 1) if (Math.abs(positions[index] - target) < Math.abs(positions[nearest] - target)) nearest = index;
    output.set(active[nearest], targetIndex * FRAME_FEATURES);
  }
  const dominantFrames = active.filter((frame) => frame[66] > 0);
  let wristPath = 0;
  for (let index = 1; index < dominantFrames.length; index += 1) {
    wristPath += Math.hypot(
      dominantFrames[index][63] - dominantFrames[index - 1][63],
      dominantFrames[index][64] - dominantFrames[index - 1][64],
    );
  }
  const rate = (matches: number) => matches / active.length;
  const bodyPresent = active.reduce((total, frame) => {
    let present = 0;
    for (let anchor = 0; anchor < BODY_ANCHORS.length; anchor += 1) present += frame[HAND_FEATURES * 2 + anchor * 3 + 2] > 0 ? 1 : 0;
    return total + present / BODY_ANCHORS.length;
  }, 0) / active.length;
  return {
    tensor: output,
    diagnostics: {
      rawFrameCount: frames.length,
      captureDurationMs: frames.at(-1)!.timestampMs - frames[0].timestampMs,
      activeStartFrame: start,
      activeEndFrame: end,
      activeFrameCount: active.length,
      activeDurationMs: positions.at(-1)! - positions[0],
      detectedDominantHand: dominant,
      dominanceMirrored: dominant === "left",
      dominantHandPresenceRate: rate(dominantFrames.length),
      nonDominantHandPresenceRate: rate(active.filter((frame) => frame[HAND_FEATURES + 66] > 0).length),
      twoHandPresenceRate: rate(active.filter((frame) => frame[66] > 0 && frame[HAND_FEATURES + 66] > 0).length),
      bodyAnchorPresenceRate: bodyPresent,
      dominantWristPath: wristPath,
    },
  };
}

export function prepareSequence(frames: FeatureFrame[]): Float32Array {
  return prepareSequenceDetailed(frames).tensor;
}
