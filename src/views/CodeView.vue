<template>
  <div class="col-12" style="margin-left: 3vh">
    <div class="container">
      <div class="row" style="margin-top: 30px">
        <div class="col-5" style="padding: 0px">
          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="generate"
          >
            Generate
          </button>
          <Schema :showSchemaOption="language == 'sql'" ref="schema"/>
        </div>
        <div class="col-5" align="right" style="padding: 0px">
          <ValidationLevel ref="override_level" />
        </div>
        <div class="col-2" id="select-lang" align="right" style="padding: 0px">
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
  <Status ref="status"/>
</template>

<style></style>
<script>
import * as monaco from "monaco-editor";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";

import Status from "@/components/Status.vue";
import ValidationLevel from "@/components/ValidationLevel.vue"
import Schema from "@/components/Schema.vue"

import axios from "axios";

import * as substrait from "substrait";
import {validate, plot} from "../assets/js/shared";


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
      language: "json",
      editor: null,
      schema: "",
      showModal: false,
    };
  },
  methods: {
    updateStatus(str){
      this.$refs.status.updateStatus(str);
    },
    getValidationOverrideLevel(){
      return this.$refs.override_level.getValidationOverrideLevel();
    },
    changeLanguage() {
      const models = monaco.editor.getModels();
      monaco.editor.setModelLanguage(models[0], this.language);
      models[0].setValue(this.default_code[this.language]);
      this.status = "// Status";
    },
    async generateFromJson(){
      this.updateStatus("Validating JSON plan with Substrait Validator...");
      validate(JSON.parse(this.code), this.getValidationOverrideLevel(), this.updateStatus);
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
      plot(plan, this.updateStatus);
    },
    async generateFromSql(){
      this.updateStatus("Converting SQL query to Substrait Plan...");
      const duckDbRsp = await axios
        .post("/api/parse/", {
          query: this.code,
          });
      this.updateStatus("SQL query converted to Substrait Plan successfully!");
      this.updateStatus("Validating converted Substrait plan...");
      validate(JSON.parse(duckDbRsp.data), this.getValidationOverrideLevel(), this.updateStatus);
      this.updateStatus("Generating plot for converted substrait plan...");
      const plan = substrait.substrait.Plan.fromObject(JSON.parse(duckDbRsp.data));
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
      } catch(error){
          this.updateStatus("Error parsing substrait plan: ", error)
      }
    },
    confirmModal() {
      console.log('Modal confirmed')
      this.showModal = false
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
    Status, ValidationLevel, Schema,
  },
};
</script>
