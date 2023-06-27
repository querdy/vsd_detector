<template>
  <navbar class="shadow-sm p-1 mb-3 bg-body-tertiary rounded" />
  <router-view />
<!--  <notifications position="bottom left" />-->
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.content {
  margin: 10px;
}
</style>

<script setup>
import Navbar from "@/components/NavbarView.vue";

</script>