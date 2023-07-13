<template>
  <div class="font-monospace fixed-top bg-body-tertiary shadow-sm d-flex align-items-center">
    <nav class="navbar navbar-expand-lg">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item mx-1">
              <router-link to="/">Home</router-link>
            </li>
            <li class="nav-item mx-1">
              <router-link to="/vsd_examine">VSD.examine</router-link>
            </li>
            <li class="nav-item mx-1">
              <router-link to="/enterprise_finder">Ent.finder</router-link>
            </li>
            <li class="nav-item mx-1">
              <router-link to="/report">Report</router-link>
            </li>
            <li class="nav-item mx-1">
              <router-link to="/account">Account</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="mx-1 ps-5">
      <div v-if="userStore.activeUser === ''">
        <form id="login">
          <div class="input-group input-group-sm">
            <input class="form-control" type="text" v-model="state.user.login" placeholder="Логин" required/>
            <input class="form-control" type="password" v-model="state.user.password" placeholder="Пароль" required/>
            <button class="form-control" type="button" @click="authenticate">Войти</button>
          </div>
        </form>
      </div>
      <div v-else class="d-flex align-items-center input-group input-group-sm">
        <div class="mx-1">
          Пользователь: {{ userStore.activeUser }}
        </div>
        <div class="mx-1">
          <button class="form-control" type="button" @click="logout">
            Выйти
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {useUserStore} from "@/stores/UserStore";
import {onMounted, reactive} from "vue";
import API from "@/services/axios";

const userStore = useUserStore()
const state = reactive({
  user: {
    login: '',
    password: '',
  },
})

onMounted(() => {
  if (userStore.JWT !== 'null') {
    me()
  }
})

async function me() {
  try {
    const response = await API.get("user/me")
    if (response.status === 200) {
      await userStore.setActiveUser(response.data.user)
    }
  } catch (e) {
    return e
  }
}

async function logout() {
  await userStore.setJWT(null)
  await userStore.setActiveUser("")
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
    await userStore.setJWT(token)
    API.defaults.headers['Authorization'] = `Bearer ${token}`
    await userStore.setActiveUser(response.data.user)
  }
  if (response.status === 200) {
    await API.get('/user/me').then(async (response) => {
          await userStore.setActiveUser(response.data.user)
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

.navbar-toggler-icon {
  display: inline-block;
  width: 1.0em;
  height: 1.0em;
  background-image: var(--bs-navbar-toggler-icon-bg);
}
</style>