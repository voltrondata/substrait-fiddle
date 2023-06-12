<template>
  <div>
    <div class="col-12" style="margin-left: 3vh">
      <div class="container">
        <div class="row" style="margin-top: 30px">
          <div class="col-5" style="padding: 0px; display: flex">
            <button
              type="button"
              class="btn btn-primary btn-sm"
              @click="generate"
            >
              Generate
            </button>
            <SqlSchema
              :showSchemaOption="language == 'sql'"
              ref="schema"
              style="margin-left: 1.5vh"
              @updateSchemaStatus="updateStatus"
            />
          </div>
          <div class="col-5" align="right" style="padding: 0px">
            <ValidationLevel ref="override_level" />
          </div>
          <div
            class="col-2"
            id="select-lang"
            align="right"
            style="padding: 0px"
          >
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
import { validate, plot } from "../assets/js/shared";

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
    };
  },
  methods: {
    updateStatus(str) {
      this.$refs.status.updateStatus(str);
    },
    getValidationOverrideLevel() {
      return this.$refs.override_level.getValidationOverrideLevel();
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
    },
    async generateFromJson() {
      this.updateStatus("Validating JSON plan with Substrait Validator...");
      validate(
        JSON.parse(this.code),
        this.getValidationOverrideLevel(),
        this.updateStatus
      );
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
      plot(plan, this.updateStatus);
    },
    async generateFromSql() {
      this.updateStatus("Converting SQL query to Substrait Plan...");
      const duckDbRsp = await axios.post("/api/parse/", {
        query: this.code,
      });
      this.updateStatus("SQL query converted to Substrait Plan successfully!");
      this.updateStatus("Validating converted Substrait plan...");
      validate(
        JSON.parse(duckDbRsp.data),
        this.getValidationOverrideLevel(),
        this.updateStatus
      );
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
