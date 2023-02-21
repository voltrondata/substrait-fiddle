<script setup>
import { RouterView } from "vue-router";

import SubstraitGraph from "@/components/SubstraitGraph.vue";
</script>

<template>
  <div>
    <header>
      <nav
        class="navbar navbar-dark navbar-expand-md py-4 shadow-lg p-3 mb-5"
        style="background-color: #e92063"
      >
        <img
          class="inverted"
          src="../public/logo.svg"
          alt="Substrait Fiddle"
          style="width: 4%; margin: 0%; padding: 0%; border: 0ch"
        />
        <span
          class="nav-header"
          style="color: #fff; margin-left: 1vh; font-size-adjust: 0.5"
          >Substrait Fiddle</span
        >
      </nav>
    </header>
    <div class="col-5 tabs" style="margin-left: 3vh">
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: $route.path === '/' }"
            id="code-tab"
            @click="goToCode"
            type="button"
          >
            Code
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: $route.path === '/upload' }"
            id="upload-tab"
            @click="goToUpload"
            type="button"
          >
            Upload
          </button>
        </li>
      </ul>
    </div>
    <div class="row">
      <div class="col-5">
        <RouterView />
      </div>
      <div class="col-7">
        <SubstraitGraph />
      </div>
    </div>
  </div>
</template>

<style scoped>
.inverted {
  filter: invert(100%);
}

.nav-header {
  font-size: 40px;
  font-size-adjust: 0.5px;
}
</style>

<script>
import { clearGraph } from "./assets/js/substrait-d3.js";

export default {
  methods: {
    goToCode() {
      clearGraph();
      this.$router.push("/");
    },
    goToUpload() {
      clearGraph();
      this.$router.push("/upload");
    },
  },
};
</script>
