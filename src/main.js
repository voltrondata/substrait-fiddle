import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "./assets/css/main.css";
import "./assets/css/styles.scss";

import "bootstrap/dist/js/bootstrap.min.js";

const app = createApp(App);

app.use(router);

app.mount("#app");
