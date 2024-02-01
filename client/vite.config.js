import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import inject from "@rollup/plugin-inject";

const path = require("path");

export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    inject({
      $: "jquery",
      jQuery: "jquery",
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "~bootstrap": path.resolve(__dirname, "node_modules/bootstrap"),
      "~jsonwebtoken": path.resolve(__dirname, "node_modules/jsonwebtoken"),
      "~monaco": path.resolve(__dirname, "node_modules/monaco-editor"),
      "~vue-multiselect": path.resolve(
        __dirname,
        "node_modules/vue-multiselect",
      ),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://api:9090",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  test: {
    globals: true,
  },
});
