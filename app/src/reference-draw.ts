// Shared drawing for "How to sign" references: the tutorial panel and the reference recorder
// preview both use these functions so a take looks the same when it is saved and replayed.
// Points are 21 x,y pairs per hand in shoulder widths (x right, y down, unmirrored image).

export interface ReferenceMotion {
  /** Signing (dominant) hand, one flat array of 42 numbers per frame. */
  frames: number[][];
  /** The other hand, when the sign uses it and a real recording of it exists. */
  otherFrames?: number[][];
}

// Each finger has its own landmark chain and color so a handshape can be read at a glance.
export const FINGERS = [
  { name: "Thumb", color: "#ff8a7a", chain: [1, 2, 3, 4] },
  { name: "Index", color: "#ffd166", chain: [5, 6, 7, 8] },
  { name: "Middle", color: "#7bd88f", chain: [9, 10, 11, 12] },
  { name: "Ring", color: "#6ec1ff", chain: [13, 14, 15, 16] },
  { name: "Pinky", color: "#c39bff", chain: [17, 18, 19, 20] },
] as const;
const PALM = [0, 1, 5, 9, 13, 17];
const BODY_VIEW = { left: -0.95, top: -1.0, size: 2.2 };
const OTHER_HAND_ALPHA = 0.7;

function handsAt(motion: ReferenceMotion, frame: number): number[][] {
  return motion.otherFrames ? [motion.frames[frame], motion.otherFrames[frame]] : [motion.frames[frame]];
}

function bounds(hands: number[][]): { centerX: number; centerY: number; extent: number } {
  const all = hands.flat();
  const xs = all.filter((_, index) => index % 2 === 0);
  const ys = all.filter((_, index) => index % 2 === 1);
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  return { centerX: (minX + maxX) / 2, centerY: (minY + maxY) / 2, extent: Math.max(maxX - minX, maxY - minY) };
}

/** One scale for the whole sign keeps the close-up from changing size as the hands move. */
export function sceneExtent(motion: ReferenceMotion): number {
  return Math.max(...motion.frames.map((_, frame) => bounds(handsAt(motion, frame)).extent)) * 1.15;
}

export function drawBodyScene(canvas: HTMLCanvasElement, motion: ReferenceMotion, frame: number, mirrored: boolean): void {
  const context = canvas.getContext("2d")!;
  const scale = canvas.width / BODY_VIEW.size;
  const project = (x: number, y: number): [number, number] => [((mirrored ? -x : x) - BODY_VIEW.left) * scale, (y - BODY_VIEW.top) * scale];
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = "#8fa3b5";
  context.lineWidth = 6;
  context.beginPath();
  context.moveTo(...project(-0.5, 0));
  context.lineTo(...project(0.5, 0));
  context.stroke();
  context.lineWidth = 3;
  context.beginPath();
  const [headX, headY] = project(0, -0.58);
  context.ellipse(headX, headY, 0.24 * scale, 0.32 * scale, 0, 0, Math.PI * 2);
  context.stroke();
  context.fillStyle = "#8fa3b5";
  context.font = "600 15px system-ui, sans-serif";
  context.fillText("head", headX - 17, headY + 5);
  context.fillText("shoulders", ...project(-0.28, 0.14));
  // Wrist trails: the full path faintly, the part already travelled brightly, with start and end.
  const trails = [motion.frames, ...(motion.otherFrames ? [motion.otherFrames] : [])];
  trails.forEach((frames, index) => {
    const path = frames.map((points) => project(points[0], points[1]));
    context.globalAlpha = index === 0 ? 1 : OTHER_HAND_ALPHA;
    trace(context, path, "rgba(247, 201, 72, 0.3)", 3);
    trace(context, path.slice(0, frame + 1), "#f7c948", 4);
    marker(context, path[0], index === 0 ? "start" : "", false);
    marker(context, path[path.length - 1], index === 0 ? "end" : "", true);
  });
  context.globalAlpha = 1;
  // Hands at their real positions, drawn small: the close-up carries the handshape.
  handsAt(motion, frame).forEach((points, index) => {
    context.globalAlpha = index === 0 ? 1 : OTHER_HAND_ALPHA;
    drawHand(context, points.map((value, at) => (at % 2 === 0 ? project(value, points[at + 1])[0] : project(points[at - 1], value)[1])), 2.2);
  });
  context.globalAlpha = 1;
}

export function drawHandScene(canvas: HTMLCanvasElement, motion: ReferenceMotion, frame: number, mirrored: boolean, extent: number): void {
  const context = canvas.getContext("2d")!;
  const hands = handsAt(motion, frame);
  const { centerX, centerY } = bounds(hands);
  const scale = (canvas.width * 0.9) / extent;
  const flip = mirrored ? -1 : 1;
  context.clearRect(0, 0, canvas.width, canvas.height);
  hands.forEach((points, index) => {
    context.globalAlpha = index === 0 ? 1 : OTHER_HAND_ALPHA;
    drawHand(context, points.map((value, at) => (at % 2 === 0
      ? canvas.width / 2 + flip * (value - centerX) * scale
      : canvas.height / 2 + (value - centerY) * scale)), canvas.width / 90);
  });
  context.globalAlpha = 1;
}

function trace(context: CanvasRenderingContext2D, path: Array<[number, number]>, color: string, width: number): void {
  context.strokeStyle = color;
  context.lineWidth = width;
  context.beginPath();
  path.forEach(([x, y], index) => (index === 0 ? context.moveTo(x, y) : context.lineTo(x, y)));
  context.stroke();
}

function marker(context: CanvasRenderingContext2D, [x, y]: [number, number], label: string, filled: boolean): void {
  context.strokeStyle = "#f7c948";
  context.fillStyle = "#f7c948";
  context.lineWidth = 3;
  context.beginPath();
  context.arc(x, y, 6, 0, Math.PI * 2);
  if (filled) context.fill(); else context.stroke();
  if (label) {
    context.font = "600 13px system-ui, sans-serif";
    context.fillText(label, x + 9, y - 8);
  }
}

/** `pixels` holds 21 x,y pairs already in canvas coordinates; `weight` scales line widths. */
function drawHand(context: CanvasRenderingContext2D, pixels: number[], weight: number): void {
  const at = (index: number): [number, number] => [pixels[index * 2], pixels[index * 2 + 1]];
  context.lineCap = "round";
  context.lineJoin = "round";
  context.beginPath();
  PALM.forEach((index, position) => (position === 0 ? context.moveTo(...at(index)) : context.lineTo(...at(index))));
  context.closePath();
  context.fillStyle = "rgba(255, 255, 255, 0.16)";
  context.fill();
  context.strokeStyle = "rgba(255, 255, 255, 0.55)";
  context.lineWidth = weight;
  context.stroke();
  for (const finger of FINGERS) {
    context.strokeStyle = finger.color;
    context.lineWidth = weight * 2.4;
    context.beginPath();
    context.moveTo(...at(finger.name === "Thumb" ? 1 : 0));
    // Fingers start at the palm knuckle; the thumb starts at its base joint.
    if (finger.name !== "Thumb") context.lineTo(...at(finger.chain[0]));
    finger.chain.forEach((index) => context.lineTo(...at(index)));
    context.stroke();
    context.fillStyle = finger.color;
    context.beginPath();
    context.arc(...at(finger.chain[3]), weight * 2.1, 0, Math.PI * 2);
    context.fill();
  }
  context.fillStyle = "#ffffff";
  context.beginPath();
  context.arc(...at(0), weight * 1.8, 0, Math.PI * 2);
  context.fill();
}
