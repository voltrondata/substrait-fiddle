<template>
  <div>
    <div
      class="container"
      style="margin-left: 2vh; margin-top: 30px; display: flex"
    >
      <div class="col-8">
        <label class="form-label" for="file">Upload your substrait plan</label>
      </div>
      <div class="col-4" style="margin-left: 1vh">
        <div class="row" style="font-size: small; margin-left: 1%">
          Substrait Validator Errors to Ignore
        </div>
        <div class="row">
          <ValidationLevel ref="override_level" />
        </div>
      </div>
    </div>
    <div class="col-12" style="margin-left: 3vh; margin-top: -2.5%">
      <input
        type="file"
        class="form-control"
        id="file-upload"
        style="width: 40%"
        accept=".json, .bin"
        ref="fileInput"
        @change="generate"
        @click="$event.target.value = ''"
      />
      <span style="color: gray; font-size: small"
        >*only .json and .bin are accepted</span
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

import { store } from "../components/store";

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
        this.updateStatus,
      );
      store.set_plan(jsonFileRes, this.getValidationOverrideLevel());
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
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
        await axios.post("/api/route/validate/file/", formData, {
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
      const planJson = JSON.stringify(plan, null, 2);
      store.set_plan(planJson, this.getValidationOverrideLevel());
      plot(plan, this.updateStatus);
    },
    async generate() {
      this.$refs.status.resetStatus();
      this.file = this.$refs.fileInput.files[0];
      try {
        if (this.file.name.includes(".json")) {
          this.generateFromJson();
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
