import { FRAME_FEATURES, NORMALIZED_FRAMES } from "./preprocessing";
import { Recognizer } from "./recognizer";

const result = document.getElementById("result")!;
try {
  const recognizer = await Recognizer.create();
  const ranking = await recognizer.rank(new Float32Array(FRAME_FEATURES * NORMALIZED_FRAMES));
  result.textContent = `Recognition model loaded: ${ranking.length} ranked candidates.`;
  document.body.dataset.status = "pass";
} catch (error) {
  result.textContent = `Recognition model failed: ${(error as Error).message}`;
  document.body.dataset.status = "fail";
}
