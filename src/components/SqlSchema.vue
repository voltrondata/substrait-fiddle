<template>
  <div>
    <button
      v-show="showSchemaOption"
      type="button"
      class="btn btn-outline-info btn-sm"
      data-bs-toggle="modal"
      data-bs-target="#schemaModal"
    >
      Show/Modify Schema
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
            <textarea
              v-model="schema"
              class="form-control"
              id="schemaTextArea"
              rows="20"
              cols="40"
            >
            </textarea>
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
import "bootstrap/dist/js/bootstrap.js";

export default {
  name: "SqlSchema",
  props: {
    showSchemaOption: Boolean,
  },
  data: function () {
    return {
      schema: "",
    };
  },

  mounted: function () {
    this.schema = `CREATE TABLE lineitem(
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
            l_comment VARCHAR NOT NULL);";`;
  },

  methods: {
    getSchema() {
      return this.schema;
    },
    saveSchema(str) {
      this.schema = str;
    },
  },
};
</script>
