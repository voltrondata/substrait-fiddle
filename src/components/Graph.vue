<template>
  <div class="col-12" style="margin-left:4vh;">
    <div style="margin-top: 10px; list-style: none" id="index" class="fa"></div>
    <div id="svgContainer">
      <div style="margin-right: 10vh; text-align: right;">
      <button type="button" class="btn btn-outline-primary btn-sm" v-show="download" style="margin-right:1vh;" @click="generateSVG">Save as SVG</button>
      <button type="button" class="btn btn-outline-primary btn-sm" v-show="download" @click="generatePNG">Save as PNG</button>
      </div>
      <svg ref="d3Plot"></svg>
    </div>
    <div id="nodeData" style="overflow-y: scroll; height: 300px"></div>
  </div>
</template>

<script>

import { saveAs } from 'file-saver';

export default {
  name: "Graph",
  data: function(){
    return {
      download: false,
    };
  },
  mounted() {
    this.observer = new MutationObserver(() => {
      const svgElement = this.$refs.d3Plot;
      this.download = svgElement.childNodes.length > 0 ? true:false;
    });

    this.observer.observe(this.$refs.d3Plot, {
      childList: true,
    });
  },
  beforeDestroy() {
    this.observer.disconnect();
  },
  methods: {
    generateSVG(){
      const svg = document.querySelector('svg');
      const svgData = new XMLSerializer().serializeToString(svg);
      const svgBlob = new Blob([svgData], {type: "image/svg+xml"});
      const svgUrl = URL.createObjectURL(svgBlob);
      const svgLink = document.createElement("a");
      svgLink.download = "substrait_plan.svg";
      svgLink.href = svgUrl;
      svgLink.click();
    },
    generatePNG(){
      const svg = document.querySelector('svg');
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      const {x, y, width, height} = svg.viewBox.baseVal;
      canvas.width = width * 2;
      canvas.height = height * 2;

      const svgData = new XMLSerializer().serializeToString(svg);
      const svgUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgData);

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
  },
};
</script>
