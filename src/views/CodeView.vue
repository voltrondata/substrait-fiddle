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
  <Status :msg="status" />
</template>

<style></style>

<script>
import * as monaco from "monaco-editor";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";

import Status from "@/components/Status.vue";
import axios from "axios";

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
      status: "// Status",
    };
  },
  methods: {
    changeLanguage() {
      const models = monaco.editor.getModels();
      monaco.editor.setModelLanguage(models[0], this.language);
      models[0].setValue(this.default_code[this.language]);
      this.status = "// Status";
    },
    validate(plan) {
      axios
        .post("/api/validate/", JSON.parse(plan))
        .then((response) => console.log(response))
        .catch((error) => {
          this.status += error.response.data["detail"];
        });
    },
    generate() {
      this.status = "// Status";
      this.code = monaco.editor.getModels()[0].getValue();
      if (this.language == "json") {
        this.status += "\n\nValidating JSON plan with Substrait Validator...\n";
        this.validate(this.code);
      } else {
        this.status += "\n\nConverting SQL query to Substrait Plan...\n";
        console.log(this.code);
        axios
          .post("/api/parse/", {
            query: this.code,
          })
          .then((response) => {
            this.status +=
              "\nSQL query converted to Substrait Plan successfully!";
            this.status += "\nValidating converted Substrait plan...\n";
            this.validate(response.data);
          })
          .catch((error) => {
            this.status += error.response.data["detail"];
          });
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
