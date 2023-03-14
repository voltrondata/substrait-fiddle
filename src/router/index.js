import { createRouter, createWebHistory } from "vue-router";
import CodeView from "../views/CodeView.vue";
import UploadView from "../views/UploadView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "code",
      component: CodeView,
    },
    {
      path: "/upload",
      name: "upload",
      component: UploadView,
    },
  ],
});

export default router;
