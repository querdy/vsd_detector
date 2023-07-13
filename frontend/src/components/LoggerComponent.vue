<template>
  <div>
    <ul class="list-group" v-for="msg in websocketStore.log">
      <li class="list-group-item border-0 border-bottom">{{ msg }}</li>
    </ul>
  </div>
</template>

<script setup>

import {useWebsocketStore} from "@/stores/WebsocketStore";
const websocketStore = useWebsocketStore()

</script>

<style scoped>

</style>