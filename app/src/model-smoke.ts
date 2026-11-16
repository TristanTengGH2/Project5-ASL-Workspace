import { FRAME_FEATURES, NORMALIZED_FRAMES } from "./preprocessing";
import { CaptureController } from "./capture-controller";
import { Recognizer } from "./recognizer";
import type { TrackingFrame } from "./tracker";

const result = document.getElementById("result")!;
try {
  const recognizer = await Recognizer.create();
  const ranking = await recognizer.rank(new Float32Array(FRAME_FEATURES * NORMALIZED_FRAMES));
  const landmarks = Array.from({ length: 21 }, (_, index) => ({
    x: 0.5 + (index % 4) * 0.01,
    y: 0.5 + Math.floor(index / 4) * 0.01,
    z: index * -0.001,
    // Hand Landmarker may report zero/absent visibility; unlike pose, finite hand
    // coordinates must remain usable under contract v2.
    visibility: 0,
  }));
  const pose = Array.from({ length: 33 }, () => ({ x: 0.5, y: 0.5, z: 0, visibility: 1 }));
  pose[11] = { x: 0.4, y: 0.5, z: 0, visibility: 1 };
  pose[12] = { x: 0.6, y: 0.5, z: 0, visibility: 1 };
  const frame: TrackingFrame = {
    hands: [{ landmarks, modelLabel: "Right", score: 1 }],
    pose,
    width: 1280,
    height: 720,
    ms: 1,
  };
  const pipelineResult = new Promise<number>((resolve, reject) => {
    const controller = new CaptureController(
      () => undefined,
      async (sequence) => {
        try { resolve((await recognizer.rank(sequence)).length); }
        catch (error) { reject(error); }
      },
      () => undefined,
    );
    controller.start();
    for (const timestamp of [100, 700, 1700, 2700, 3700]) controller.consume(frame, timestamp);
    for (let timestamp = 3800; timestamp <= 6800; timestamp += 100) controller.consume(frame, timestamp);
  });
  const pipelineCandidates = await pipelineResult;
  result.textContent = `Recognition pipeline loaded: ${ranking.length} direct and ${pipelineCandidates} captured candidates.`;
  document.body.dataset.status = "pass";
} catch (error) {
  result.textContent = `Recognition model failed: ${(error as Error).message}`;
  document.body.dataset.status = "fail";
}
