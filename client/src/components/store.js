import { reactive } from "vue";

export const store = reactive({
  plan: "",
  validation_override_levels: [],

  reset_plan() {
    this.plan = "";
    this.validation_override_levels.length = 0;
  },
  set_plan(data, levels) {
    this.plan = data;
    this.validation_override_levels = levels;
  },
});
