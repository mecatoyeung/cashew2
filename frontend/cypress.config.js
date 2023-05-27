const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
    },
    baseUrl: "http://localhost:3000"
  },
  env: {
    apiUrl: "http://localhost:8000/"
  }
});
