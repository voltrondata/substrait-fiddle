<template>
  <div class="col-12" style="margin-left: 3vh; margin-top: 30px">
    <label class="form-label" for="file">Upload your substrait plan</label>
    <input type="file" class="form-control" id="file" style="width: 40%" accept=".json,.sql,.bin" ref="fileInput" @change="onFileUpload"/>
    <button type="button" class="btn btn-primary btn-sm" style="margin-top: 3%" @click="generate">
      Generate
    </button>
  </div>
  <Status :msg="status" style="margin-top: 435px"/>
</template>

<script scoped>
import Status from "@/components/Status.vue";
import axios from "axios";

export default {
  data: function(){
    return {
      file: null,
      content: null,
      status: "// Status",
      logger: 0,
    };
  },
  methods: {
    generate(){
    },
    validate(plan) {
      axios
        .post("/api/validate/", plan)
        .then((response) => console.log(response))
        .catch((error) => {
          console.log(error)
          this.status += error.response.data["detail"];
        });
    },
    onFileUpload(){
      this.status = "// Status";
      this.file = this.$refs.fileInput.files[0];
      const reader = new FileReader();
      if (this.file.name.includes(".json")) {
          reader.onload = (res) => {
            this.status += "\n\n["+(++this.logger)+"] JSON file detected, parsing...";
            this.content = JSON.parse(res.target.result);
            this.status += "\n["+(++this.logger)+"] JSON Parsing successful!";
            this.status += "\n["+(++this.logger)+"] Validating JSON plan with Substrait Validator...\n";
            this.validate(this.content);
          };
          reader.onerror = (err) => console.log(err);
          reader.readAsText(this.file);
      } else if(this.file.name.includes(".sql")){
        reader.onload = (res) => {
            this.status += "\n\n["+(++this.logger)+"] SQL file detected, parsing...";
            this.content = res.target.result;
            this.status += "\n["+(++this.logger)+"] SQL Parsing successful!";
            this.status += "\n["+(++this.logger)+"] Converting SQL Query to Substrait Plan via DuckDB...";
            axios
            .post("/api/parse/", {
              query: this.content,
            })
            .then((response) => {
              this.status +=
              "\n["+(++this.logger)+"] SQL query converted to Substrait Plan successfully!";
              this.status += "\n["+(++this.logger)+"] Validating converted Substrait plan...\n";
              this.validate(JSON.parse(response.data));
            })
            .catch((error) => {
              this.status += error.response.data["detail"];
            });
          };
          reader.onerror = (err) => console.log(err);
          reader.readAsText(this.file);
      } else {
            this.status += "\n\n["+(++this.logger)+"] Binary file detected.";
            this.status += "\n["+(++this.logger)+"] Validating plan with Substrait Validator...\n";
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
  mounted: function(){
    this.logger = 0;
  },
  components: {
    Status,
  },
};
</script>
