<template>
  <div class="d-flex align-items-center sticky-top bg-light font-monospace" style="min-height: 4vh">
    <nav class="p-0 navbar navbar-expand-lg">
      <ul class="navbar-nav">
        <li class="nav-item mx-1">
          <router-link to="/">VSD.examine(no xlsx)</router-link>
        </li>
        <li class="nav-item mx-1">
          <router-link to="/vsd_examinator_with_xlsx">VSD.examine(xlsx)</router-link>
        </li>
        <li class="nav-item mx-1">
          <router-link to="/enterprise_finder">Ent.finder</router-link>
        </li>
        <li class="nav-item mx-1">
          <router-link to="/report">Report</router-link>
        </li>
<!--        <li class="nav-item mx-1">-->
<!--          <router-link to="/account">Account</router-link>-->
<!--        </li>-->
<!--        <li class="nav-item mx-1">-->
<!--          <router-link to="/help">Help</router-link>-->
<!--        </li>-->
      </ul>
    </nav>

    <div class="m-1 ps-5">
      <div v-if="state.activeUser === ''">
      <form id="login">
        <div class="input-group input-group-sm">
            <input class="form-control" type="text" v-model="state.user.login" placeholder="Логин" required/>
            <input class="form-control" type="password" v-model="state.user.password" placeholder="Пароль" required/>
            <button class="form-control" type="button" @click="authenticate">Войти</button>
        </div>
      </form>
      </div>
      <div v-else class="d-flex align-items-center">
        <div class="mx-1">
          Пользователь: {{ state.activeUser }}
        </div>
        <div class="mx-1">
          <button class="form-control btn btn-sm btn-dark" type="button" @click="logout" style="font-family: monospace">Выйти</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {reactive} from "vue";
import API from "@/plugins/axios";

const state = reactive({
  activeUser: '',
  user: {
    login: '',
    password: '',
  },
})

if (localStorage.getItem("JWT")) {
  me()
}


async function me() {
  try {
    const response = await API.get("user/me")
    if (response.status === 200) {
      state.activeUser = response.data.user
    }
  } catch (e) {
    return e
  }

}

async function logout() {
  localStorage.removeItem("JWT")
  state.activeUser = ''
}

async function authenticate() {
  let userFormData = new FormData();
  userFormData.append("user", JSON.stringify(state.user))
  const response = await API.post(
      'user/login',
      userFormData,
      {headers: {"Content-Type": "multipart/form-data"}}
  )
  if (response.status === 200) {
    const token = response.data.accessToken
    localStorage.setItem("JWT", token)
    API.defaults.headers['Authorization'] = `Bearer ${token}`
  }
  if (response.status === 200) {
    await API.get('/user/me').then((response) => {
          state.activeUser = response.data.user
        }
    )
  }
}


</script>

<style scoped>

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a::after {
  content: '';
  display: block;
  left: 0;
  width: 0;
  background-color: #495057;
  height: 1px;
  transition: all .5s;
}

nav a:hover:after {
  width: 100%;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>