<template>
 <div class="col-5" style="margin-left: 2vh; margin-top:30px">
  <label class="form-label" for="file">Upload your substrait plan</label>
  <input type="file" class="form-control" id="file" style="width:40%;"/>
  <button type="button" class="btn btn-primary btn-sm" style="margin-top: 3%;">Generate</button>
 </div>

 <Status msg="// Status" style="margin-top: 435px"/> 
</template>

<script scoped>

import Status from '@/components/Status.vue'

export default {
components: {
    Status
  },
}
</script>
