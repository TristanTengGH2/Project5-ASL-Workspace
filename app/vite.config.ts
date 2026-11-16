import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        app: "index.html",
        modelSmoke: "model-smoke.html",
        workerSpike: "worker-spike.html",
      },
    },
  },
});
