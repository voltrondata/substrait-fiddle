import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "./assets/css/main.css";
import "./assets/css/styles.scss";

import { icon } from './assets/js/directive';

const app = createApp(App);

app.directive('icon', icon);

app.use(router);

app.mount("#app");
