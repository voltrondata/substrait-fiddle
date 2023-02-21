<template>
  <div id="override_level">
    <Multiselect
      v-model="value"
      placeholder="Add a validation override level"
      label="code"
      track-by="code"
      :options="options"
      :multiple="true"
      :taggable="true"
      :option-height="50"
      @tag="addLevel"
    ></Multiselect>
  </div>
</template>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style>
.multiselect {
  min-height: 9px;
  height: 32px;
  min-width: 10px;
  width: 27vh;
}
.multiselect__tags {
  min-height: 9px;
  height: 32px;
  min-width: 10px;
  width: 27vh;
  font-size: 14px;
  padding-top: 5px;
  border-color: rgb(206, 212, 218);
}
.multiselect__tag {
  height: 20px;
}
.multiselect__select {
  padding-top: 0%;
  z-index: 9999;
}
</style>

<script>
import Multiselect from "vue-multiselect";

export default {
  name: "ValidationLevel",
  components: {
    Multiselect,
  },
  data: function () {
    return {
      value: [{ code: 1002 }],
      options: [{ code: 1002 }, { code: 2001 }, { code: 1 }],
    };
  },
  methods: {
    addLevel(level) {
      this.options.push({ code: parseInt(level) });
      this.value.push({ code: parseInt(level) });
    },
    getValidationOverrideLevel() {
      return this.value.map((item) => item.code);
    },
  },
};
</script>
