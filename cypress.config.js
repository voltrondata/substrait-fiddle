const { defineConfig } = require("cypress");
const fs = require("fs");

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://localhost:5173",
    supportFile: false,
    setupNodeEvents(on) {
      on("task", {
        deleteFile(filePath) {
          fs.unlinkSync(filePath);
          return null;
        },
      });
    },
  },
});
