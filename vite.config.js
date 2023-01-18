import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import inject from "@rollup/plugin-inject";

const path = require('path')
const prefix = `monaco-editor/esm/vs`;


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(),
           inject({   // => that should be first under plugins array
               $: 'jquery',
               jQuery: 'jquery',
             }),],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
      '~monaco': path.resolve(__dirname, 'node_modules/monaco-editor'),

    },
  },
});
