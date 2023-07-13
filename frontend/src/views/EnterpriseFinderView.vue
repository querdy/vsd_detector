<template>
  <div class="row d-flex justify-content-center">
    <div class="col-3 col-xxl-2">
      <div class="mx-2">{{websocketStore.fileProgress}}</div>
    </div>
    <div class="col-7 col-xxl-8">
      <div class="progress m-1" role="progressbar" aria-label="Progress" aria-valuenow={{websocketStore.progress}}
           aria-valuemin="0" aria-valuemax="100">
        <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{width: websocketStore.progress + '%'}">
          <div class="mx-1" v-if="websocketStore.progress >= 50">{{ websocketStore.progress }}%</div>
        </div>
        <div class="mx-1" v-if="websocketStore.progress < 50 & websocketStore.progress > 0">{{ websocketStore.progress }}%</div>
      </div>
    </div>
  </div>
  <div class="row d-flex justify-content-center">
    <div class="col-10">
      <div class="mx-2">prediction: {{websocketStore.prediction}}</div>
    </div>
  </div>
  <div class="row d-flex justify-content-center">
    <div class="col-10">
      <form>
        <div class="form-outline m-1">
          <input class="form-control" type="file" multiple @change="addDocument" accept=".xlsx, .xls"/>
        </div>
        <div class="form-outline m-1">
          <button v-if="websocketStore.isRun" class="form-control btn btn-primary btn-sm" type="button" disabled>Run ent. find</button>
          <button v-else class="form-control btn btn-primary btn-sm" type="button" @click="run_enterprise_finder">Run ent. find</button>
        </div>
        <div class="form-outline m-1">
          <button v-if="websocketStore.isRun" class="form-control btn btn-danger btn-sm" type="button" @click="stopTasks">Stop Tasks</button>
          <button v-else class="form-control btn btn-danger btn-sm" type="button" disabled>Stop Tasks</button>
        </div>
      </form>
    </div>
  </div>
  <div class="m-1 d-flex justify-content-center">
    <img class="w-75" v-if="websocketStore.isRun" src="@/assets/finder.gif" alt="eat">
  </div>
</template>

<script setup>
import {onMounted, reactive} from "vue";
import API from "@/services/axios";
import {useWebsocketStore} from "@/stores/WebsocketStore";

const websocketStore = useWebsocketStore()
const state = reactive({
  uploadFile: [],
})

async function stopTasks() {
  const response = await API.get('vetis/cancel_tasks')
  if (response.status === 200) {
    await websocketStore.setIsRun(false)
    await websocketStore.setProgress(0)
    await websocketStore.setFileProgress('0/0')
    await websocketStore.setPrediction('')
  }
}

async function run_enterprise_finder() {
  await websocketStore.setIsRun(true)
  let detectorFormData = new FormData();
  state.uploadFile.forEach((file) => detectorFormData.append('files', file));
  try {
    await API.post('vetis/run_enterprise_finder', detectorFormData, {headers: {"Content-Type": "multipart/form-data"}})
  } catch (error) {
    console.log('Проверка уже запущена')
  }
}


function addDocument(event) {
  state.uploadFile = []
  let selectedFiles = event.target.files;
  for (let i = 0; i < selectedFiles.length; i++) {
    state.uploadFile.push(selectedFiles[i]);
  }
}
</script>

<style scoped>

</style>