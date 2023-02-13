<template>
  <div class="col-12" style="margin-left: 3vh; margin-top: 30px">
    <label class="form-label" for="file">Upload your substrait plan</label>
    <input type="file" class="form-control" id="file-upload" style="width: 40%" accept=".json,.sql,.bin" ref="fileInput" @change="generate"/>
    <span style="color:gray; font-size:small;">*only .json, .sql and .bin are accepted</span>
  </div>
  <Status ref="status" style="margin-top: 435px"/>
</template>

<script scoped>
import Status from "@/components/Status.vue";
import axios from "axios";
import {readFile, readText, validate, plot} from "../assets/js/shared";

import * as substrait from "substrait";

export default {
  data: function(){
    return {
      file: null,
      content: null,
      logger: 0,
    };
  },
  methods: {
    updateStatus(str){
      this.$refs.status.updateStatus(str);
    },
    async generateFromJson(){
      this.updateStatus("JSON file detected, parsing...");
      const jsonFileRes = await readText(this.file);
      this.content = JSON.parse(jsonFileRes);
      this.updateStatus("JSON Parsing successful!");
      this.updateStatus("Validating JSON plan with Substrait Validator...");
      validate(this.content, this.updateStatus);
      this.updateStatus("Generating plot for substrait JSON plan...");
      const plan = substrait.substrait.Plan.fromObject(this.content);
      plot(plan, this.updateStatus);
    },
    async generateFromSql(){
      this.updateStatus("SQL file detected, reading...");
      const sqlFileRes = await readText(this.file);
      this.updateStatus("SQL file read successfully!");
      this.content = sqlFileRes;
      this.updateStatus("Converting SQL Query to Substrait Plan via DuckDB...");
      const duckDbRsp = await axios
        .post("/api/parse/", {
          query: this.content,
        });
      this.updateStatus("SQL query converted to Substrait Plan successfully!");
      this.updateStatus("Validating converted Substrait plan...");
      validate(JSON.parse(duckDbRsp.data), this.updateStatus);
      this.updateStatus("Generating plot for converted substrait plan...");
      const plan = substrait.substrait.Plan.fromObject(JSON.parse(duckDbRsp.data));
      plot(plan, this.updateStatus);
    },
    async generateFromBinary(){
      this.updateStatus("Binary file detected.");
      const fileReadRsp = await readFile(this.file);
      this.updateStatus("Validating plan with Substrait Validator...");
      try {
        var formData = new FormData();
        formData.append("data", this.file);
        const fileValidRsp = await axios
          .post("/api/validate/file/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            }
          }
        );
        this.updateStatus("Plan validation successful!");
      } catch (error){
        this.updateStatus(error.response.data["detail"]);
      }
        this.updateStatus("Generating plot for Substrait plan...");
        const plan = substrait.substrait.Plan.decode(new Uint8Array(fileReadRsp));
        plot(plan, this.updateStatus);
    },
    async generate(){
      this.$refs.status.resetStatus();
      this.file = this.$refs.fileInput.files[0];
      const reader = new FileReader();
      try {
        if (this.file.name.includes(".json")) {
          this.generateFromJson();
        } else if(this.file.name.includes(".sql")){
          this.generateFromSql();
        } else {
          this.generateFromBinary();
        }
      } catch(error){
          this.updateStatus("Error parsing substrait plan: ", error)
      }
    },
  },  
  mounted: function() {
    this.$refs.status.resetStatus();
  },
  components: {
    Status,
  },
};
</script>
