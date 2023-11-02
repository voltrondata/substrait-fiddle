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
              Show/Add Schema
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="accordion" id="schemaAccordion">
              <div
                v-for="(schema, i) in schemas"
                :key="schema.name"
                class="accordion-item"
              >
                <h2 class="accordion-header" :id="`heading${schema.name}`">
                  <button
                    class="accordion-button"
                    :class="{ collapsed: i !== activeAccordionItem }"
                    type="button"
                    @click="toggleAccordion(i)"
                    :aria-expanded="i === activeAccordionItem"
                    :aria-controls="`collapse${schema.name}`"
                  >
                    {{ schema.name }}
                  </button>
                </h2>
                <div
                  :id="`collapse${schema.name}`"
                  class="accordion-collapse collapse"
                  :class="{ show: i === activeAccordionItem }"
                  :aria-labelledby="`heading${schema.name}`"
                  data-bs-parent="#schemaAccordion"
                >
                  <pre class="accordion-body">{{ schema.schema }}</pre>

                  <div v-if="i > 0 && !schema.validated">
                    <textarea
                      v-model="tempSchemaText"
                      class="form-control"
                      rows="4"
                      placeholder="Enter new schema"
                      id="schemaTextArea"
                    ></textarea>
                    <div class="d-flex justify-content-end">
                      <button
                        class="btn btn-primary mt-2 btn-sm"
                        style="margin-bottom: 1%; margin-right: 1%"
                        @click="validateSchema(i)"
                      >
                        Validate
                      </button>
                    </div>
                  </div>

                  <span
                    v-if="i > 0"
                    class="delete-icon"
                    @click="deleteSchema(i)"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-trash3-fill"
                      viewBox="0 0 16 16"
                    >
                      <path
                        d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5Zm-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5ZM4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06Zm6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528ZM8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5Z"
                      />
                    </svg>
                  </span>
                </div>
              </div>
            </div>
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
              class="btn btn-success"
              @click="addNewSchema"
              id="addSchema"
            >
              Add Schema
            </button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="saveChanges"
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
.pre {
  white-space: pre-wrap;
  font-family:
    Consolas,
    Menlo,
    Monaco,
    Lucida Console,
    Liberation Mono,
    DejaVu Sans Mono,
    Bitstream Vera Sans Mono,
    Courier New,
    monospace,
    serif;
}

.modal-content {
  height: 50vh;
  overflow-y: auto;
}

.accordion-button {
  background-color: #f8f9fa !important;
}

.accordion-body {
  background-color: #ffffff;
}

.delete-icon {
  cursor: pointer;
  color: red;
  position: absolute;
  top: 10px;
  right: 10px;
}

.form-control {
  border: none;
  resize: none;
}
</style>

<script>
import Ajv from "ajv";
import axios from "axios";
import "bootstrap/dist/js/bootstrap.js";

import { store } from "../components/store";
import schema_lineitem from "../assets/js/schema_lineitem.json";

export default {
  name: "SqlSchema",
  props: {
    showSchemaOption: Boolean,
  },
  data: function () {
    return {
      tempSchema: "",
      currSchema: "",
      schemas: [],
      activeAccordionItem: -1,
      canSaveChanges: false,
      newSchemaText: "",
      tempSchemaText: "",
    };
  },
  mounted() {
    this.currSchema = this.defaultSchema;
    this.tempSchema = this.defaultSchema;
    this.schemas.push({
      name: "lineitem",
      schema: schema_lineitem,
    });
  },
  methods: {
    toggleAccordion(index) {
      if (this.activeAccordionItem === index) {
        this.activeAccordionItem = -1;
      } else {
        this.activeAccordionItem = index;
      }
    },
    getSchema() {
      return this.defaultSchema;
    },
    updateSchema() {
      this.tempSchema = this.defaultSchema;
    },
    addNewSchema() {
      this.schemas.push({
        name: "New Schema",
        schema: "",
      });
      this.activeAccordionItem = this.schemas.length - 1;
      this.canSaveChanges = true;
    },
    deleteSchema(index) {
      if (index >= 0 && index < this.schemas.length) {
        this.schemas.splice(index, 1);
        if (this.activeAccordionItem === index) {
          this.activeAccordionItem = -1;
        } else if (this.activeAccordionItem > index) {
          this.activeAccordionItem--;
        }
      }
    },
    async saveChanges() {
      if (this.schemas.length > 1) {
        for (var i = 1; i < this.schemas.length; ++i) {
          try {
            await axios.post(
              "/api/route/add_schema/",
              {
                schema: this.schemas[i],
              },
              {
                headers: {
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${store.sessionToken}`,
                },
              },
            );
            store.add_schema(JSON.parse(this.schemas[i]["schema"]).table);
          } catch (error) {
            this.$emit(
              "updateSchemaStatus",
              "Error while executing schema: " + error,
            );
          }
        }
      }
    },
    validateSchema(index) {
      const ajv = new Ajv();
      const allowedPattern = "^[a-zA-Z0-9_ ]+$";
      const format = {
        type: "object",
        properties: {
          table: {
            type: "string",
            pattern: allowedPattern,
          },
          fields: {
            type: "array",
            items: {
              type: "object",
              properties: {
                name: { type: "string", pattern: allowedPattern },
                type: { type: "string", pattern: allowedPattern },
                properties: {
                  type: "array",
                  items: { type: "string", pattern: allowedPattern },
                },
              },
              required: ["name", "type", "properties"],
              additionalProperties: false,
            },
          },
        },
        required: ["table", "fields"],
        additionalProperties: false,
      };

      const validate = ajv.compile(format);
      try {
        const jsonData = JSON.parse(this.tempSchemaText);
        if (jsonData.table === "lineitem") {
          alert('Invalid schema: Table name cannot be "lineitem"');
        } else if (ajv.validate(format, jsonData)) {
          alert("Schema validated!");
          const schemaToSave = this.schemas[index];
          schemaToSave.name = jsonData.table;
          schemaToSave.schema = this.tempSchemaText;
          schemaToSave.validated = true;
        } else {
          const errors = ajv.errorsText(validate.errors, { separator: "\n" });
          alert(`Invalid schema: \n${errors}`);
        }
      } catch (error) {
        alert("Invalid JSON: " + error);
      }
      this.tempSchemaText = "";
    },
    showEnteredText(index) {
      return index === this.activeAccordionItem;
    },
  },
};
</script>
