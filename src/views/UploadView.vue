<template>
  <div class="col-12" style="margin-left: 3vh; margin-top: 30px">
    <label class="form-label" for="file">Upload your substrait plan</label>
    <input type="file" class="form-control" id="file" style="width: 40%" accept=".json,.sql,.bin" ref="fileInput" @change="onFileUpload"/>
    <span style="color:gray; font-size:small;">*only .json, .sql and .bin are accepted</span>
  </div>
  <Status ref="status" style="margin-top: 435px"/>
</template>

<script scoped>
import Status from "@/components/Status.vue";
import axios from "axios";
import {validate, plot} from "../resources/js/shared";

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
    onFileUpload(){
      this.$refs.status.resetStatus();
      this.file = this.$refs.fileInput.files[0];
      const reader = new FileReader();
      if (this.file.name.includes(".json")) {
          reader.onload = (res) => {
            this.updateStatus("JSON file detected, parsing...");
            this.content = JSON.parse(res.target.result);
            this.updateStatus("JSON Parsing successful!");
            this.updateStatus("Validating JSON plan with Substrait Validator...");
            validate(this.content, this.updateStatus);
            this.updateStatus("Generating plot for substrait JSON plan...");
            const plan = substrait.substrait.Plan.fromObject(this.content);
            plot(plan, this.updateStatus);
          };
          reader.onerror = (err) => console.log(err);
          reader.readAsText(this.file);
      } else if(this.file.name.includes(".sql")){
        reader.onload = (res) => {
            this.updateStatus("SQL file detected.");
            this.content = res.target.result;
            this.updateStatus("Converting SQL Query to Substrait Plan via DuckDB...");
            axios
            .post("/api/parse/", {
              query: this.content,
            })
            .then((response) => {
              this.updateStatus("SQL query converted to Substrait Plan successfully!");
              this.updateStatus("Validating converted Substrait plan...");
              validate(JSON.parse(response.data), this.updateStatus);
              this.updateStatus("Generating plot for converted substrait plan...");
              const plan = substrait.substrait.Plan.fromObject(JSON.parse(response.data));
              plot(plan, this.updateStatus);
            })
            .catch((error) => {
              console.log(error)
              this.updateStatus(error.response.data["detail"]);
            });
          };
          reader.onerror = (err) => console.log(err);
          reader.readAsText(this.file);
      } else {
            this.updateStatus("Binary file detected.");
            this.updateStatus("Validating plan with Substrait Validator...");
            var formData = new FormData();
            formData.append("data", this.file);
            axios
            .post("/api/validate/file/", formData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                }
              }
            )
            .then(() => this.updateStatus("Plan validation successful!"))
            .catch((error) => {
              this.updateStatus(error.response.data["detail"]);
            });
            this.updateStatus("Generating plot for Substrait plan...");
            reader.onload = () => {
              try {
                const plan = substrait.substrait.Plan.decode(new Uint8Array(reader.result));
                plot(plan, this.updateStatus);
              } catch (e) {
                this.updateStatus("Error parsing the plan: "+ e)
              }
            };
            reader.readAsArrayBuffer(this.file);
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
