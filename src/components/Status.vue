<template>
  <div class="col-5" id="status">
  {{ msg }}
  </div>
</template>

<style scoped>

#status{
  margin-left: 2vh; 
  background-color: black; 
  color: #2ECFFA;
  font-family: 'Inconsolata', monospace;
  height:150px;
  overflow-y: scroll;
}

</style>

<script>
export default {
  name: 'Status',
  props: {
    msg: String
  }
}
</script>
