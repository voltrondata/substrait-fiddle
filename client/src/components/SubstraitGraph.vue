<template>
  <div class="col-12" style="margin-left: 4vh">
    <div style="margin-top: 10px; list-style: none" id="index" class="fa"></div>
    <div id="svgContainer">
      <div style="margin-right: 10vh; text-align: right">
        <button
          id="copy-button"
          type="button"
          class="btn btn-outline-primary btn-sm"
          v-show="downloadJSON"
          style="margin-right: 1vh"
          @click="generateJSON"
        >
          Download JSON
        </button>
        <button
          id="copy-button"
          type="button"
          class="btn btn-outline-primary btn-sm"
          v-show="download"
          style="margin-right: 1vh"
          @click="generateLink"
          ref="copyButton"
        >
          Copy Link
        </button>
        <button
          type="button"
          class="btn btn-outline-primary btn-sm"
          v-show="download"
          style="margin-right: 1vh"
          @click="generateSVG"
        >
          Save as SVG
        </button>
        <button
          type="button"
          class="btn btn-outline-primary btn-sm"
          v-show="download"
          @click="generatePNG"
        >
          Save as PNG
        </button>
      </div>
      <svg ref="d3Plot"></svg>
    </div>
    <div id="nodeData" style="overflow-y: scroll; height: 300px"></div>
  </div>
</template>

<script>
import { store } from "../components/store";
import axios from "axios";
import Clipboard from "clipboard";

export default {
  name: "SubstraitGraph",
  data: function () {
    return {
      download: false,
      downloadJSON: false,
      shareable_link: "",
    };
  },
  mounted() {
    this.currentUrl = window.location.origin;
    this.observer = new MutationObserver(() => {
      const svgElement = this.$refs.d3Plot;
      this.download = svgElement.childNodes.length > 0 ? true : false;
      this.downloadJSON = store.plan.length > 0 && this.download ? true : false;
    });

    this.observer.observe(this.$refs.d3Plot, {
      childList: true,
    });
    this.clipboard = new Clipboard("#copy-button", {
      text: () => this.shareable_link,
    });
  },
  beforeDestroy() {
    this.observer.disconnect();
  },
  methods: {
    generateSVG() {
      const svg = document.querySelector("svg");
      const svgData = new XMLSerializer().serializeToString(svg);
      const svgBlob = new Blob([svgData], { type: "image/svg+xml" });
      const svgUrl = URL.createObjectURL(svgBlob);
      const svgLink = document.createElement("a");
      svgLink.download = "substrait_plan.svg";
      svgLink.href = svgUrl;
      svgLink.click();
    },
    generatePNG() {
      const svg = document.querySelector("svg");
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      const { x, y, width, height } = svg.viewBox.baseVal;
      canvas.width = width * 2;
      canvas.height = height * 2;

      const svgData = new XMLSerializer().serializeToString(svg);
      const svgUrl =
        "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgData);

      const image = new Image();
      image.onload = function () {
        ctx.fillStyle = "white";
        ctx.fillRect(x, y, canvas.width, canvas.height);
        ctx.drawImage(image, x, y);
        const pngUrl = canvas.toDataURL("image/png");
        const pngLink = document.createElement("a");
        pngLink.download = "substrait_plan.png";
        pngLink.href = pngUrl;
        pngLink.click();
      };
      image.src = svgUrl;
    },
    generateJSON() {
      const jsonObject = JSON.parse(store.plan);
      const jsonString = JSON.stringify(
        jsonObject,
        /* no replacer function required */ null,
        /* whitespace for indentation */ 4
      );
      const blob = new Blob([jsonString], { type: "application/json" });
      const plan_link = document.createElement("a");
      plan_link.href = URL.createObjectURL(blob);
      plan_link.download = "plan.json";
      plan_link.click();
      URL.revokeObjectURL(plan_link.href);
    },
    async generateLink() {
      try {
        const resp = await axios.post("/api/save/", {
          json_string: store.plan,
          validator_overrides: store.validation_override_levels,
        });

        this.shareable_link = this.currentUrl + "/plan/" + resp.data;
        this.clipboard.onClick({ currentTarget: this.$refs.copyButton });
        alert("Link copied to clipboard!");
      } catch (error) {
        console.log(error.response.data["detail"]);
      }
    },
  },
};
</script>
