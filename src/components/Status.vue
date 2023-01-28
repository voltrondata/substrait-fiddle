<template>
  <div class="col-12" id="status">
    {{ msg }}
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
  name: "Status",
  props: {
    msg: String,
  },
};
</script>
