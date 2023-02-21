<template>
  <div class="col-12" id="status" style="margin-left: 3vh">
    {{ message }}
  </div>
</template>

<style scoped>
#status {
  margin-left: 2vh;
  background-color: black;
  color: #2ecffa;
  font-family: "Inconsolata", monospace;
  height: 150px;
  overflow-y: scroll;
  white-space: pre-line;
}
</style>

<script>
export default {
  name: "StatusBox",
  data: function () {
    return {
      message: "// Status\n",
      counter: 0,
    };
  },

  mounted: function () {
    this.message = "// Status\n";
    this.counter = 0;
  },

  methods: {
    resetStatus() {
      this.message = "// Status\n";
      this.counter = 0;
    },
    updateStatus(str) {
      this.message += "\n[" + ++this.counter + "] " + str;
    },
  },
};
</script>
