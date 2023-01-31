<script setup>
import { RouterLink, RouterView } from "vue-router";
import * as bootstrap from "bootstrap";

import Graph from "@/components/Graph.vue";
</script>

<template>
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
  <div class="col-5" style="margin-left: 3vh">
    <ul class="nav nav-tabs" id="myTab" role="tablist">
      <li class="nav-item" role="presentation">
          <button
            class="nav-link"
            :class = "{ active: $route.path === '/' }"
            id="code-tab"
            @click="goToCode"
            data-bs-toggle="tab"
            data-bs-target="#code"
            type="button"
            role="tab"
            aria-controls="code"
            aria-selected="true"
          >
            Code
          </button>
      </li>
      <li class="nav-item" role="presentation">
          <button
            class="nav-link"
            :class = "{ active: $route.path === '/upload' }"
            id="upload-tab"
            @click="goToUpload"
            data-bs-toggle="tab"
            data-bs-target="#upload"
            type="button"
            role="tab"
            aria-controls="upload"
            aria-selected="false"
          >
            Upload
          </button>
      </li>
    </ul>
    <div class="tab-content" id="myTabContent">
      <div
        class="tab-pane fade show active"
        id="code"
        role="tabpanel"
        aria-labelledby="code-tab"
      ></div>
      <div
        class="tab-pane fade"
        id="upload"
        role="tabpanel"
        aria-labelledby="upload-tab"
      ></div>
    </div>
  </div>
  <div class="row">
    <div class="col-5">
      <RouterView />
    </div>
    <div class="col-7">
      <Graph />
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
$('a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
  e.target;
  e.relatedTarget;
});

export default {
  methods: {
    goToCode() {
      this.$router.push("/");
    },
    goToUpload() {
      this.$router.push("/upload");
    }
  }
};

</script>
