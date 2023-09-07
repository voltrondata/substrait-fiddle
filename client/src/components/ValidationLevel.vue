<template>
  <div id="override_level">
    <multiselect
      v-model="selected"
      placeholder="Add a validation override level"
      label="level"
      track-by="level"
      :options="filterOptions"
      :multiple="true"
      :taggable="true"
      :searchable="true"
      @search-change="handleSearchChange"
    >
      <template #option="{ option }">
        <div v-if="filterOptions.length > 0">
          <span class="option__small"
            >{{ option.level }} - {{ option.desc }}</span
          >
        </div>
        <div class="option__unavailable" v-else>
          <span>Level</span><br />
          <span>not supported</span>
        </div>
      </template>
    </multiselect>
  </div>
</template>

<script>
import Multiselect from "vue-multiselect";
import validationOverrideLevels from "../assets/js/validation-override-levels.json";

export default {
  name: "ValidationLevel",
  components: {
    Multiselect,
  },
  data() {
    return {
      selected: [],
      options: [],
      searchLevel: "",
    };
  },
  computed: {
    filterOptions() {
      if (!this.searchLevel) {
        return this.options;
      }
      const searchLevelLower = this.searchLevel.toLowerCase();
      return this.options.filter(
        (option) =>
          option.level.toString().startsWith(searchLevelLower) ||
          option.desc.toLowerCase().includes(searchLevelLower)
      );
    },
    showNoOptions() {
      return this.searchLevel !== "" && this.filterOptions.length === 0;
    },
  },
  mounted() {
    this.options = validationOverrideLevels;
    this.selected.push(this.options.find((option) => option.level === 1002));
  },
  methods: {
    handleSearchChange(searchLevel) {
      this.searchLevel = searchLevel;
    },
    clearLevels() {
      this.value.length = 0;
    },
    getValidationOverrideLevel() {
      return this.selected.map((item) => item.level);
    },
  },
};
</script>

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
  z-index: 1;
}
.multiselect__content-wrapper {
  width: unset !important;
  min-width: 100% !important;
  max-height: 200px !important;
}
.option__unavailable {
  line-height: 1.4;
}
</style>
