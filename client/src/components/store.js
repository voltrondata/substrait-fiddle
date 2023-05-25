import { reactive } from "vue";

export const store = reactive({
  plan: "",
  reset_plan() {
    this.plan = "";
  },
  set_plan(data) {
    this.plan = data;
  },
});
