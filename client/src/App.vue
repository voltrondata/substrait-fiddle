<script setup>
import { RouterView } from "vue-router";

import SubstraitGraph from "@/components/SubstraitGraph.vue";
</script>

<template>
  <div>
    <header>
      <nav
        class="navbar navbar-dark navbar-expand-md shadow-lg mb-5"
        style="background-color: #e92063"
      >
        <div
          class="container"
          style="margin-left: 0%; min-width: 100%; padding-top: 1.5%"
        >
          <div class="col-8" style="padding-bottom: 1%">
            <div class="d-flex align-items-center">
              <img
                class="inverted"
                src="../public/logo.svg"
                alt="Substrait Fiddle"
                style="width: 5%"
              />
              <span
                class="nav-header"
                style="color: #fff; font-size-adjust: 0.5; margin-left: 1rem"
                >Substrait Fiddle</span
              >
            </div>
          </div>
          <div class="col-4">
            <div
              class="d-flex justify-content-end"
              style="text-align: right; padding-bottom: 0%; margin-right: 1.5%"
            >
              <img
                height="20"
                width="20"
                src="https://cdn.simpleicons.org/github/white"
                style="margin-top: 2px; margin-right: 4px"
              />
              <a
                href="https://github.com/voltrondata/substrait-fiddle/"
                target="_blank"
              >
                <span
                  class="nav-header navbar-right"
                  style="
                    color: #fff;
                    font-size: 1.1rem;
                    display: inline-block;
                    font-family: sans-serif;
                  "
                  >voltrondata/substrait-fiddle</span
                >
              </a>
            </div>
          </div>
        </div>
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
