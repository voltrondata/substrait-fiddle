import { v4 as uuidv4 } from "uuid";
import { reactive } from "vue";

import { generateToken } from "../assets/js/shared";

export const store = reactive({
  plan: "",
<<<<<<< HEAD
  validation_override_levels: [],

=======
  user_id: "",
  schemas: [],
  sessionToken: "",
>>>>>>> 436f9b4 (feat: add JWT, Custom TTLCache and table manipulation for custom schema)
  reset_plan() {
    this.plan = "";
    this.validation_override_levels.length = 0;
  },
  set_plan(data, levels) {
    this.plan = data;
    this.validation_override_levels = levels;
  },
  set_user(user_id) {
    this.user_id = user_id;
  },
  add_schema(schema_name) {
    this.schemas.push(schema_name);
  },
  async set_token() {
    const sessionToken = uuidv4();
    this.user = sessionToken.replace(/-/g, "_");
    this.token = await generateToken(store.user_id);
  },
});
