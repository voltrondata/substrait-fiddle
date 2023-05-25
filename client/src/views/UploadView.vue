<template>
  <div>
    <div
      class="container"
      style="margin-left: 2vh; margin-top: 30px; display: flex"
    >
      <div class="col-8">
        <label class="form-label" for="file">Upload your substrait plan</label>
      </div>
      <div class="col-4" style="margin-left: 1vh;">
        <ValidationLevel ref="override_level" />
      </div>
    </div>
    <div class="col-12" style="margin-left: 3vh; margin-top: 0%">
      <input
        type="file"
        class="form-control"
        id="file-upload"
        style="width: 40%"
        accept=".json,.sql,.bin"
        ref="fileInput"
        @change="generate"
        @click="$event.target.value = ''"
      />
      <span style="color: gray; font-size: small"
        >*only .json, .sql and .bin are accepted</span
      >
    </div>

    <StatusBox ref="status" style="margin-top: 435px" />
  </div>
</template>

<script scoped>
import StatusBox from "@/components/StatusBox.vue";
import ValidationLevel from "@/components/ValidationLevel.vue";
import axios from "axios";
import { readFile, readText, validate, plot } from "../assets/js/shared";

import * as substrait from "substrait";

export default {
  data: function () {
    return {
      file: null,
      content: null,
      logger: 0,
    };
  },
  methods: {
    updateStatus(str) {
      this.$refs.status.updateStatus(str);
    },
    getValidationOverrideLevel() {
      return this.$refs.override_level.getValidationOverrideLevel();
    },
    async generateFromJson() {
      this.updateStatus("JSON file detected, parsing...");
      const jsonFileRes = await readText(this.file);
      this.content = JSON.parse(jsonFileRes);
      this.updateStatus("JSON Parsing successful!");
      this.updateStatus("Validating JSON plan with Substrait Validator...");
      validate(
        this.content,
        this.getValidationOverrideLevel(),
        this.updateStatus
      );
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
      plot(plan, this.updateStatus);
    },
    async generateFromSql() {
      this.updateStatus("SQL file detected, reading...");
      const sqlFileRes = await readText(this.file);
      this.updateStatus("SQL file read successfully!");
      this.content = sqlFileRes;
      this.updateStatus("Converting SQL Query to Substrait Plan via DuckDB...");
      const duckDbRsp = await axios.post("/api/parse/", {
        query: this.content,
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
    async generateFromBinary() {
      this.updateStatus("Binary file detected.");
      const fileReadRsp = await readFile(this.file);
      this.updateStatus("Validating plan with Substrait Validator...");
      try {
        var formData = new FormData();
        formData.append("file", this.file);
        formData.append("override_levels", this.getValidationOverrideLevel());
        await axios.post("/api/validate/file/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.updateStatus("Plan validation successful!");
      } catch (error) {
        this.updateStatus(error.response.data["detail"]);
      }
      this.updateStatus("Generating plot for Substrait plan...");
      const plan = substrait.substrait.Plan.decode(new Uint8Array(fileReadRsp));
      plot(plan, this.updateStatus);
    },
    async generate() {
      this.$refs.status.resetStatus();
      this.file = this.$refs.fileInput.files[0];
      try {
        if (this.file.name.includes(".json")) {
          this.generateFromJson();
        } else if (this.file.name.includes(".sql")) {
          this.generateFromSql();
        } else {
          this.generateFromBinary();
        }
      } catch (error) {
        this.updateStatus("Error parsing substrait plan: ", error);
      }
    },
  },
  mounted: function () {
    this.$refs.status.resetStatus();
  },
  components: {
    StatusBox,
    ValidationLevel,
  },
};
</script>
