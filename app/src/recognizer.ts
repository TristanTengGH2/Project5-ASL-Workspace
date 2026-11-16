import * as ort from "onnxruntime-web/wasm";
import { FRAME_FEATURES, NORMALIZED_FRAMES } from "./preprocessing";

interface ModelMetadata {
  model: string;
  inputName: string;
  outputName: string;
  labels: string[];
  mean: number[];
  scale: number[];
}

interface SignCatalog {
  signs: Array<{ id: string; displayGloss: string; status: string }>;
}

export interface RankedCandidate { id: string; label: string; score: number }

export class Recognizer {
  private constructor(
    private session: ort.InferenceSession,
    private metadata: ModelMetadata,
    private signs: Map<string, { id: string; displayGloss: string }>,
  ) {}

  static async create(): Promise<Recognizer> {
    ort.env.wasm.numThreads = 1;
    const base = import.meta.env.BASE_URL;
    const [modelResponse, catalogResponse] = await Promise.all([
      fetch(`${base}models/sign-recognizer.json`),
      fetch(`${base}data/sign-catalog.json`),
    ]);
    if (!modelResponse.ok) throw new Error(`model metadata HTTP ${modelResponse.status}`);
    if (!catalogResponse.ok) throw new Error(`sign catalog HTTP ${catalogResponse.status}`);
    const metadata = await modelResponse.json() as ModelMetadata;
    const catalog = await catalogResponse.json() as SignCatalog;
    if (metadata.mean.length !== FRAME_FEATURES || metadata.scale.length !== FRAME_FEATURES) throw new Error("model metadata does not match the 167-feature aspect-correct contract");
    const signs = new Map(catalog.signs.filter((sign) => sign.status === "supported").map((sign) => [sign.displayGloss, sign]));
    const missing = metadata.labels.filter((label) => !signs.has(label));
    if (missing.length || signs.size !== metadata.labels.length) throw new Error(`model/catalog vocabulary mismatch${missing.length ? `: ${missing.join(", ")}` : ""}`);
    const session = await ort.InferenceSession.create(`${base}models/${metadata.model}`, { executionProviders: ["wasm"] });
    return new Recognizer(session, metadata, signs);
  }

  async rank(sequence: Float32Array): Promise<RankedCandidate[]> {
    const standardized = sequence.slice();
    for (let frame = 0; frame < NORMALIZED_FRAMES; frame += 1) for (let feature = 0; feature < FRAME_FEATURES; feature += 1) {
      const index = frame * FRAME_FEATURES + feature;
      standardized[index] = (standardized[index] - this.metadata.mean[feature]) / this.metadata.scale[feature];
    }
    const input = new ort.Tensor("float32", standardized, [1, NORMALIZED_FRAMES, FRAME_FEATURES]);
    const output = await this.session.run({ [this.metadata.inputName]: input });
    const logits = Array.from(output[this.metadata.outputName].data as Float32Array);
    const maximum = Math.max(...logits);
    const exponentials = logits.map((value) => Math.exp(value - maximum));
    const total = exponentials.reduce((sum, value) => sum + value, 0);
    return this.metadata.labels
      .map((label, index) => ({ id: this.signs.get(label)!.id, label: this.signs.get(label)!.displayGloss, score: exponentials[index] / total }))
      .sort((a, b) => b.score - a.score);
  }
}
