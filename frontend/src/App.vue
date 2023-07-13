<template>
  <NavbarComponent/>
  <div class="p-5 row mw-100">
    <div class="col-12 col-xxl-3 col-lg-4">
      <router-view/>
    </div>
    <div class="col-xxl-4 d-none d-xxl-flex d-flex align-items-center" style="height: 88vh">
      <img class="mw-100" src="@/assets/inter.png" alt="inter">
    </div>
    <div class="col-12 col-xxl-5 col-lg-8">
      <LoggerComponent/>
    </div>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
<script setup>
import NavbarComponent from "@/components/NavbarComponent.vue";
import LoggerComponent from "@/components/LoggerComponent.vue";
import {useWebsocketStore} from "@/stores/WebsocketStore";
import {onMounted} from "vue";
import API from "@/services/axios";

const websocketStore = useWebsocketStore()

const ws = new WebSocket("ws://127.0.0.1:8001/ws/")
ws.onmessage = async function (event) {
  let data = JSON.parse(event.data)
  if (data.channel === 'progress') {
    await websocketStore.setProgress(Number(data.message).toFixed(2))
  } else if (data.channel === 'vsd_progress') {
    await websocketStore.setVsdProgress(Number(data.message).toFixed(2))
  } else if (data.channel === 'log') {
    await websocketStore.setLog(data.message)
  } else if (data.channel === 'file') {
    await websocketStore.setFileProgress(data.message)
  } else if (data.channel === 'complete') {
    await websocketStore.setIsRun(false)
  } else if (data.channel === 'prediction') {
    await websocketStore.setPrediction(data.message.split('.')[0])
  }
}

onMounted(() => {
  getIsRun()
})

async function getIsRun() {
  const response = await API.get('vetis/is_running')
  if (response.status === 200) {
    await websocketStore.setIsRun(response.data.detail === true)
  }
}
</script>