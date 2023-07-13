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
    <div class="col-3 col-xxl-2">
      <div class="mx-2">vsd: </div>
    </div>
    <div class="col-7 col-xxl-8">
      <div class="progress m-1" role="progressbar" aria-label="Progress" aria-valuenow={{websocketStore.vsdProgress}}
           aria-valuemin="0" aria-valuemax="100">
        <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{width: websocketStore.vsdProgress + '%'}">
          <div class="mx-1" v-if="websocketStore.vsdProgress >= 50">{{ websocketStore.vsdProgress }}%</div>
        </div>
        <div class="mx-1" v-if="websocketStore.vsdProgress < 50 & websocketStore.vsdProgress > 0">{{ websocketStore.vsdProgress }}%</div>
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
          <div class="input-group">
            <span class="input-group-text" id="dateFrom">от</span>
            <input class="form-control" type="date" v-model="state.dateInterval.dateFrom"
                   aria-describedby="dateFrom"/>
          </div>
        </div>
        <div class="form-outline m-1">
          <div class="input-group">
            <span class="input-group-text" id="dateTo">до</span>
            <input class="form-control" type="date" v-model="state.dateInterval.dateTo" aria-describedby="dateTo"/>
          </div>
        </div>
        <div class="form-outline m-1">
          <input class="form-control" type="file" multiple @change="addDocument" accept=".xlsx, .xls"/>
        </div>
        <div class="form-outline m-1">
          <button v-if="websocketStore.isRun" class="form-control btn btn-primary btn-sm" type="button" disabled>
            Run exam
          </button>
          <button v-else class="form-control btn btn-primary btn-sm" type="button" @click="run_vsd_exam">Run exam
          </button>
        </div>
        <div class="form-outline m-1">
          <button
              v-if="websocketStore.isRun"
              class="form-control btn btn-danger btn-sm"
              type="button"
              @click="stopVsdExam">
            Stop Tasks
          </button>
          <button
              v-else
              class="form-control btn btn-danger btn-sm"
              type="button"
              disabled>
            Stop Tasks
          </button>
        </div>
      </form>
    </div>
  </div>
  <div class="m-1 d-flex justify-content-center">
    <img class="w-75" v-if="websocketStore.isRun" src="@/assets/detector.gif" alt="detector-gif">
  </div>
</template>

<script setup>
import {onMounted, reactive} from "vue";
import API from "@/services/axios";
import {useWebsocketStore} from "@/stores/WebsocketStore";

const websocketStore = useWebsocketStore()
const state = reactive({
  dateInterval: {
    dateFrom: '',
    dateTo: ''
  },
  uploadFile: [],
})

async function stopVsdExam() {
  const response = await API.get('vetis/cancel_tasks')
  if (response.status === 200) {
    await websocketStore.setIsRun(false)
    await websocketStore.setProgress(0)
    await websocketStore.setFileProgress('0/0')
    await websocketStore.setVsdProgress(0)
    await websocketStore.setPrediction('')
  }
}

async function run_vsd_exam() {
  await websocketStore.setIsRun(true)
  let detectorFormData = new FormData();
  detectorFormData.append("date_interval", JSON.stringify(state.dateInterval))
  if (state.uploadFile !== []) {
    state.uploadFile.forEach((file) => detectorFormData.append('files', file));
  }
  try {
    await API.post('vetis/run_document_examinator', detectorFormData, {headers: {"Content-Type": "multipart/form-data"}})
  } catch (error) {
    console.log('Проверка уже запущена')
  }
}

function addDocument(event) {
  let selectedFiles = event.target.files;
  for (let i = 0; i < selectedFiles.length; i++) {
    state.uploadFile.push(selectedFiles[i]);
  }
}
</script>

<style scoped>

</style>