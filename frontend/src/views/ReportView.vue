<template>
  <div class="row d-flex justify-content-center">
    <div class="col-10 m-1">
      <form>
        <div class="input-group">
          <button
              class="form-control btn btn-primary btn-sm"
              type="button"
              @click="create_report">
            Получить новый отчет
          </button>
        </div>
      </form>
    </div>
    <div class="col-10 m-1">
      <ul class="list-group my-1" v-for="report in state.reports">
        <li class="list-group-item border-0">
          <a class="pe-1" v-bind:href="state.url + report.url">{{ report.filename }}</a>
          <button type="button" class="btn btn-sm cross-button" @click="delete_report(report)"></button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {onMounted, reactive} from "vue";
import API from "@/services/axios";

const state = reactive({
  log: [],
  reports: [],
  url: process.env.VUE_APP_BASE_URL
})

onMounted(() => {
  get_reports()
})

async function create_report() {
  const response = await API.post('vetis/report')
}

async function get_reports() {
  const response = await API.get('vetis/report')
  if (response.status === 200) {
    state.reports = response.data.detail;
  }
}

async function delete_report(report) {
  const response = await API.delete("vetis/report/" + report.uuid)
  if (response.status === 202) {
    await get_reports()
  }
}
</script>

<style scoped>
.cross-button {
  width: 20px;
  height: 20px;
  border: none;
  background-image: url('@/assets/cross.png');
  background-size: cover;
}
</style>