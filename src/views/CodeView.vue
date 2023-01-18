<template>
<div class="col-5" style="margin-left: 2vh;">
  <div class="container">
    <div class="row" style="margin-top:30px;">
    <div class="col-6" style="padding:0px;">
      <button type="button" class="btn btn-primary btn-sm">Generate</button>
    </div>
  <div class="col-6" id="select-lang" align="right" style="padding: 0px;">
    <select class="form-select form-select-sm w-auto" id="language" v-model="language" @change="changeLanguage">
      <option value="json">JSON</option>
      <option value="sql">SQL</option>
    </select>
  </div>
  </div>
  </div>
  <div id="editor"  ref="myid" style="margin-top:10px; 100%; height: 500px" class="border"></div>
</div>
<br/>
<Status msg="// Status"/>

</template>

<style>

</style>

<script>
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'

import Status from '@/components/Status.vue'


self.MonacoEnvironment = {
  getWorker(_, label){
    if (label === 'json') {
      return new jsonWorker();
    }
  }
}
export default {
  data: function(){
    return {
      default_code: {
        "sql": "-- Enter SQL query to generate Substrait Plan", 
        "json": '{"_comment1": "Enter JSON to generate Substrait Plan"}'},
      code: "",
      language: "json",
      editor: null,
    }
  },
  methods: {
    changeLanguage(){
      const models = monaco.editor.getModels();  
      monaco.editor.setModelLanguage(models[0], this.language);
      models[0].setValue(this.default_code[this.language]);

  }
},
  mounted: function(){
  monaco.editor.create(document.getElementById('editor'), {
  value: this.default_code[this.language],
  language: this.language,
  features: ["coreCommands", "find"],
  automaticLayout: true
})
},

components: {
    Status
  }

}


</script>
