<template class="container">
  <div class="row mw-100">
    <div class="col-md-7 col-lg-5 col-xl-5">
      <div class="row d-flex justify-content-center">
        <div class="col-5">
          <div class="progress m-1" role="progressbar" aria-label="Progress" aria-valuenow={{state.progress}}
               aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{width: state.progress + '%'}">
              <div class="mx-1" v-if="state.progress >= 15">{{ state.progress }}%</div>
            </div>
            <div class="mx-1" v-if="state.progress < 15 & state.progress > 0">{{ state.progress }}%</div>
          </div>
        </div>
      </div>
      <div class="row d-flex justify-content-center">
        <div class="col-5">
          <form>
            <div class="input-group row m-1">
              <span class="input-group-text col-2" id="dateFrom">от</span>
              <input class="form-control" type="date" v-model="state.dateInterval.dateFrom"
                     aria-describedby="dateFrom"/>
            </div>
            <div class="input-group row m-1">
              <span class="input-group-text col-2" id="dateTo">до</span>
              <input class="form-control" type="date" v-model="state.dateInterval.dateTo" aria-describedby="dateTo"/>
            </div>
            <div class="input-group m-1">
              <input class="form-control" type="file" @change="addDocument" accept=".xlsx"/>
            </div>
            <div class="input-group m-1">
              <button v-if="state.isRunVsdExam" class="form-control btn btn-primary btn-sm" type="button" disabled>
                Run exam
              </button>
              <button v-else class="form-control btn btn-primary btn-sm" type="button" @click="run_vsd_exam">Run exam
              </button>
            </div>
            <div class="input-group m-1">
              <button
                  v-if="state.isRunVsdExam"
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
<!--            <div class="input-group m-1">-->
<!--              <button-->
<!--                  class="form-control btn btn-primary btn-sm"-->
<!--                  type="button"-->
<!--                  @click="get_report">-->
<!--                Получить отчет-->
<!--              </button>-->
<!--            </div>-->
          </form>
        </div>
      </div>
      <div class="m-1 d-flex justify-content-center">
        <img v-if="state.isRunVsdExam" src="@/assets/anime-dance.gif" width="325" alt="eat">
      </div>
    </div>
    <div class="col-md-8 col-lg-7 col-xl-6">
      <ul class="list-group" v-for="msg in state.log">
        <li class="list-group-item">{{ msg }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {reactive} from "vue";
import API from "@/plugins/axios";

const state = reactive({
  isLoading: false,
  isRunVsdExam: false,
  log: [],
  progress: 0,
  activeUser: '',
  user: {
    login: '',
    password: '',
  },
  dateInterval: {
    dateFrom: '',
    dateTo: ''
  },
  uploadFile: null,
})

getIsRunVsdExam()

const ws = new WebSocket("ws://boyara.space/ws")

ws.onmessage = function (event) {
  let data = JSON.parse(event.data)
  if (data.channel === 'log') {
    if (state.log.length < 13) {
      state.log.unshift(data.message)
    } else {
      state.log.pop()
      state.log.unshift(data.message)
    }
  } else if (data.channel === 'progress') {
    state.progress = Number(data.message).toFixed(2)
  }
}

async function stopVsdExam() {
  const response = await API.get('vetis/cancel_tasks')
  if (response.status === 200) {
    state.isRunVsdExam = false
    state.progress = 0
  }
}

async function getIsRunVsdExam() {
  const response = await API.get('vetis/is_running')
  if (response.status === 200) {
    state.isRunVsdExam = response.data.detail === true;
  }
}

async function run_vsd_exam() {
  state.isRunVsdExam = true
  let detectorFormData = new FormData();
  detectorFormData.append("date_interval", JSON.stringify(state.dateInterval))
  detectorFormData.append('file', state.uploadFile)
  try {
    await API.post('vetis/run_document_examinator_with_xlsx', detectorFormData, {headers: {"Content-Type": "multipart/form-data"}})
  } catch (error) {
    console.log('Проверка уже запущена')
  }
  await getIsRunVsdExam()
}
function addDocument(event) {
  state.uploadFile = event.target.files[0]
}
</script>

<style scoped>
.btn:focus {
  background-color: #0d6efd;
  color: #fff;
  border-color: #0d6efd;
  box-shadow: None;
}

</style>