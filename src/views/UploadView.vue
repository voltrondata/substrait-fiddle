<template>
  <div class="col-12" style="margin-left: 3vh; margin-top: 30px">
    <label class="form-label" for="file">Upload your substrait plan</label>
    <input type="file" class="form-control" id="file" style="width: 40%" accept=".json,.sql,.bin" ref="fileInput" @change="onFileUpload"/>
  </div>
  <Status ref="status" style="margin-top: 435px"/>
</template>

<script scoped>
import Status from "@/components/Status.vue";
import axios from "axios";

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
    generate(){
    },
    validate(plan) {
      axios
        .post("/api/validate/", plan)
        .then((response) => console.log(response))
        .catch((error) => {
          console.log(error)
          this.updateStatus(error.response.data["detail"]);
        });
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
            this.validate(this.content);
          };
          reader.onerror = (err) => console.log(err);
          reader.readAsText(this.file);
      } else if(this.file.name.includes(".sql")){
        reader.onload = (res) => {
            this.updateStatus("SQL file detected, parsing...");
            this.content = res.target.result;
            this.updateStatus("SQL Parsing successful!");
            this.updateStatus("Converting SQL Query to Substrait Plan via DuckDB...");
            axios
            .post("/api/parse/", {
              query: this.content,
            })
            .then((response) => {
              this.updateStatus("SQL query converted to Substrait Plan successfully!");
              this.updateStatus("Validating converted Substrait plan...");
              this.validate(JSON.parse(response.data));
            })
            .catch((error) => {
              this.status += error.response.data["detail"];
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
            .then((response) => console.log(response))
            .catch((error) => {
              console.log(error)
              this.status += error.response.data["detail"];
            });
      }
    },  
  },
  components: {
    Status,
  },
};
</script>
