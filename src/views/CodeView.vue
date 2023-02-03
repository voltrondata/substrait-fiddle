<template>
  <div class="col-12" style="margin-left: 3vh">
    <div class="container">
      <div class="row" style="margin-top: 30px">
        <div class="col-6" style="padding: 0px">
          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="generate"
          >
            Generate
          </button>
        </div>
        <div class="col-6" id="select-lang" align="right" style="padding: 0px">
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
      ref="myid"
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
import axios from "axios";

import * as substrait from "substrait";
import {validate, plot} from "../resources/js/shared";

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
    };
  },
  methods: {
    updateStatus(str){
      this.$refs.status.updateStatus(str);
    },
    changeLanguage() {
      const models = monaco.editor.getModels();
      monaco.editor.setModelLanguage(models[0], this.language);
      models[0].setValue(this.default_code[this.language]);
      this.status = "// Status";
    },
    async generate() {
      this.$refs.status.resetStatus();
      this.code = monaco.editor.getModels()[0].getValue();
      if (this.language == "json") {
        this.updateStatus("Validating JSON plan with Substrait Validator...");
        validate(JSON.parse(this.code), this.updateStatus);
        this.updateStatus("Generating plot for substrait JSON plan...");
        const plan = substrait.substrait.Plan.fromObject(this.content);
        plot(plan, this.updateStatus);
      } else {
        try{
          this.updateStatus("Converting SQL query to Substrait Plan...");
          const duckDbRsp = await axios
            .post("/api/parse/", {
              query: this.code,
             });
          this.updateStatus("SQL query converted to Substrait Plan successfully!");
          this.updateStatus("Validating converted Substrait plan...");
          validate(JSON.parse(duckDbRsp.data), this.updateStatus);
          this.updateStatus("Generating plot for converted substrait plan...");
          const plan = substrait.substrait.Plan.fromObject(JSON.parse(duckDbRsp.data));
          plot(plan, this.updateStatus);
        } catch (error){
          this.updateStatus(error.response.data["detail"]);

        }
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
    Status,
  },
};
</script>
