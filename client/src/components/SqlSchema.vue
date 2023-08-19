<template>
  <div>
    <button
      v-show="showSchemaOption"
      type="button"
      class="btn btn-outline-info btn-sm"
      data-bs-toggle="modal"
      data-bs-target="#schemaModal"
      @click="updateSchema"
    >
      Show/Add Schema
    </button>
    <div
      class="modal fade"
      id="schemaModal"
      tabindex="-1"
      aria-labelledby="schemaModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-danger" id="schemaModalLabel">
              Show/Modify Schema
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Close
            </button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="saveSchema"
              disabled
            >
              Save changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
#schemaTextArea {
  font-family: Consolas, Menlo, Monaco, Lucida Console, Liberation Mono,
    DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace, serif;
}

</style>

<script>
import axios from "axios";
import "bootstrap/dist/js/bootstrap.js";

export default {
  name: "SqlSchema",
  props: {
    showSchemaOption: Boolean,
  },
  data: function () {
    return {
      tempSchema: "",
      currSchema: "",
      defaultSchema: `CREATE TABLE lineitem(
            l_orderkey INTEGER NOT NULL, 
            l_partkey INTEGER NOT NULL, 
            l_suppkey INTEGER NOT NULL, 
            l_linenumber INTEGER NOT NULL, 
            l_quantity INTEGER NOT NULL, 
            l_extendedprice DECIMAL(15,2) NOT NULL, 
            l_discount DECIMAL(15,2) NOT NULL, 
            l_tax DECIMAL(15,2) NOT NULL, 
            l_returnflag VARCHAR NOT NULL, 
            l_linestatus VARCHAR NOT NULL, 
            l_shipdate DATE NOT NULL, 
            l_commitdate DATE NOT NULL, 
            l_receiptdate DATE NOT NULL, 
            l_shipinstruct VARCHAR NOT NULL, 
            l_shipmode VARCHAR NOT NULL, 
            l_comment VARCHAR NOT NULL);`,
      otherSchema: [],
    };
  },
  mounted() {
    this.currSchema = this.defaultSchema;
    this.tempSchema = this.defaultSchema;
  },
  created() {
    this.getData();
  },
  methods: {
    getSchema() {
      return this.defaultSchema;
    },
    updateSchema() {
      this.tempSchema = this.defaultSchema;
    },
    async saveSchema() {
      if (this.tempSchema != this.defaultSchema) {
        try {
          this.defaultSchema = this.tempSchema;
          await axios.post("/api/execute/duckdb/", [this.schema]);
          this.$emit(
            "updateSchemaStatus",
            "Modified schema executed successfully!"
          );
        } catch (error) {
          console.log(error);
          this.$emit(
            "updateSchemaStatus",
            "Error while executing schema: " + error.response.data["detail"]
          );
        }
      }
    },
  },
};
</script>
