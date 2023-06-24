<template>
  <div>
    <div class="col-12" style="margin-left: 3vh">
      <div class="container">
        <div class="row" style="margin-top: 30px">
          <div class="col-5" style="padding: 0px">
            <div class="row" style="margin-left: 1%; font-size: small">
              Substrait Validator Errors to Ignore
            </div>
            <div class="row">
              <ValidationLevel ref="override_level" />
            </div>
          </div>
          <div class="col-2" id="select-lang" style="padding: 0px">
            <div class="row" style="font-size: small">Plan type</div>
            <div class="row">
              <select
                class="form-select form-select-sm w-auto"
                id="language"
                v-model="language"
                @change="changeLanguage"
              >
                <option value="json">JSON</option>
                <option value="sql">SQL</option>
              </select>
            </div>
          </div>
          <div
            class="col-5"
            style="
              padding: 0px;
              display: flex;
              margin-top: 3%;
              justify-content: flex-end;
            "
          >
            <SqlSchema
              :showSchemaOption="language == 'sql'"
              ref="schema"
              style="margin-left: 1.5vh; margin-right: 1vh"
              @updateSchemaStatus="updateStatus"
            />
            <button
              type="button"
              class="btn btn-primary btn-sm"
              @click="generate"
            >
              Generate
            </button>
          </div>
        </div>
      </div>
      <div
        id="editor"
        style="margin-top: 10px; height: 500px"
        class="border"
      ></div>
    </div>
    <br />
    <StatusBox ref="status" />
  </div>
</template>

<style></style>
<script>
import * as monaco from "monaco-editor";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";

import StatusBox from "@/components/StatusBox.vue";
import ValidationLevel from "@/components/ValidationLevel.vue";
import SqlSchema from "@/components/SqlSchema.vue";

import axios from "axios";

import * as substrait from "substrait";
<<<<<<< HEAD
import { validate, plot } from "../assets/js/shared";
import { clearGraph } from "../assets/js/substrait-d3";
import { store } from "../components/store";
=======
import { validate, plot, getPlan } from "../assets/js/shared";
import { store } from "../components/store";

<<<<<<< HEAD
>>>>>>> 9fc6ee1 (feat: client side features for shareable link)

=======
>>>>>>> 84e6f1b (feat: shareable link for UploadView)
self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === "json") {
      return new jsonWorker();
    }
  },
};

export default {
  data: function () {
    return {
      default_code: {
        sql: "-- Enter SQL query to generate Substrait Plan",
        json: '{"_comment1": "Enter JSON to generate Substrait Plan"}',
      },
      code: "",
      language: "sql",
      editor: null,
      schema: "",
      planId: null,
    };
  },
  created: function () {
    this.planId = this.$route.params.id;
    if (this.planId) {
      this.loadPlan(this.planId);
    }
  },
  methods: {
    updateStatus(str) {
      this.$refs.status.updateStatus(str);
    },
    getValidationOverrideLevel() {
      return this.$refs.override_level.getValidationOverrideLevel();
    },
    clearValidationOverrideLevel() {
      return this.$refs.override_level.clearLevels();
    },
    addValidationOverrideLevel(level) {
      this.$refs.override_level.addLevel(level);
    },
    changeLanguage() {
      const models = monaco.editor.getModels();
      monaco.editor.setModelLanguage(models[0], this.language);
      models[0].setValue(this.default_code[this.language]);
      this.status = "// Status";

      // Disable minimap and overview ruler if language is SQL
      const editors = monaco.editor.getEditors();
      if (this.language === "sql") {
        editors[0].updateOptions({ minimap: { enabled: false } });
        editors[0].updateOptions({ overviewRulerLanes: 0 });
      } else {
        editors[0].updateOptions({ minimap: { enabled: true } });
        editors[0].updateOptions({ overviewRulerLanes: 2 });
      }
      clearGraph();
    },
    async generateFromJson() {
      this.updateStatus("Validating JSON plan with Substrait Validator...");
      validate(
        JSON.parse(this.code),
        this.getValidationOverrideLevel(),
        this.updateStatus
      );
      store.set_plan(this.code, this.getValidationOverrideLevel());
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
      plot(plan, this.updateStatus);
    },
    async generateFromSql() {
      this.updateStatus("Converting SQL query to Substrait Plan...");
      const duckDbRsp = await axios.post("/api/parse/", {
        query: this.code,
      });
      store.set_plan(duckDbRsp.data);
      this.updateStatus("SQL query converted to Substrait Plan successfully!");
      this.updateStatus("Validating converted Substrait plan...");
      validate(
        JSON.parse(duckDbRsp.data),
        this.getValidationOverrideLevel(),
        this.updateStatus
      );
      store.set_plan(duckDbRsp.data, this.getValidationOverrideLevel());
      this.updateStatus("Generating plot for converted substrait plan...");
      const plan = substrait.substrait.Plan.fromObject(
        JSON.parse(duckDbRsp.data)
      );
      plot(plan, this.updateStatus);
    },
    async generate() {
      this.$refs.status.resetStatus();
      this.code = monaco.editor.getModels()[0].getValue();
      try {
        if (this.language == "json") {
          this.generateFromJson();
        } else {
          this.generateFromSql();
        }
      } catch (error) {
        this.updateStatus("Error parsing substrait plan: ", error);
      }
    },
    async loadPlan(id) {
      const resp = await getPlan(id);
      const jsonObject = JSON.parse(resp.data[0]);

      this.code = JSON.stringify(jsonObject, null, 2);
      this.language = "json";

      const models = monaco.editor.getModels();
      monaco.editor.setModelLanguage(models[0], "json");
      models[0].setValue(this.code);

      this.clearValidationOverrideLevel();
      resp.data[1].forEach((value) => {
        this.addValidationOverrideLevel(value);
      });
    },
  },
  mounted: function () {
    monaco.editor.create(document.getElementById("editor"), {
      value: this.default_code[this.language],
      language: this.language,
      features: ["coreCommands", "find"],
      automaticLayout: true,
    });
  },

  unmounted: function () {
    monaco.editor.getModels()[0].dispose();
  },

  components: {
    StatusBox,
    ValidationLevel,
    SqlSchema,
  },
};
</script>
