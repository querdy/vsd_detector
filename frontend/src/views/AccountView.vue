<template>
  <div class="row d-flex justify-content-center">
    <div class="col-8" v-if="!userStore.activeUser">
      <div class="m-1">
        Регистрация:
      </div>
      <form>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.user.login" aria-describedby="login" placeholder="Логин"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="password" v-model="state.user.password" aria-describedby="password" placeholder="Пароль"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="password" v-model="state.user.confirmPassword" aria-describedby="confirmPassword" placeholder="Подтверждение пароля"/>
        </div>
        <div class="form-group m-1">
          <button class="form-control btn btn-primary btn-sm" type="button" @click="register">
            Зарегистрироваться
          </button>
        </div>
      </form>
    </div>
    <div v-else class="col-8">
      <div class="m-1">
        Данные для доступа к API:
      </div>
      <form>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.enterpriseLogin" aria-describedby="login" placeholder="Логин"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.enterprisePassword" aria-describedby="password" placeholder="Пароль"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.apiKey" aria-describedby="apiKey" placeholder="apiKey"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.serviceId" aria-describedby="serviceId" placeholder="serviceId"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.issuerId" aria-describedby="issuerId" placeholder="issuerId"/>
        </div>
        <div class="form-group m-1">
          <input class="form-control" type="text" v-model="state.vetis.initiator" aria-describedby="initiator" placeholder="initiator (Логин пользователя)"/>
        </div>
        <div class="form-group m-1">
          <button class="form-control btn btn-primary btn-sm" type="button" @click="vetisSave">
            Сохранить
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import {reactive} from "vue";
import API from "@/services/axios";
import {useUserStore} from "@/stores/UserStore";

const userStore = useUserStore()
const state = reactive({
  user: {
    login: '',
    password: '',
    confirmPassword: '',
  },
  vetis: {
    enterpriseLogin: '',
    enterprisePassword: '',
    apiKey: '',
    serviceId: '',
    issuerId: '',
    initiator: '',
  }
})

async function register() {
  let registerFormData = new FormData();
  registerFormData.append("user", JSON.stringify(state.user))
  const response = await API.post('user/register', registerFormData, {headers: {"Content-Type": "multipart/form-data"}})
  if (response.status === 201) {
    const token = response.data.accessToken
    await userStore.setJWT(token)
    API.defaults.headers['Authorization'] = `Bearer ${token}`
    await userStore.setActiveUser(response.data.user)
  }
  if (response.status === 201) {
    await API.get('/user/me').then(async (response) => {
          await userStore.setActiveUser(response.data.user)
        }
    )
  }
}

async function vetisSave() {
  let vetisFormData = new FormData();
  vetisFormData.append("vetis", JSON.stringify(state.vetis))
  const response = await API.patch('user/vetis_auth_data', vetisFormData, {headers: {"Content-Type": "multipart/form-data"}})
  if (response.status === 200) {
    state.vetis = {
      enterpriseLogin: '',
      enterprisePassword: '',
      apiKey: '',
      serviceId: '',
      issuerId: '',
      initiator: '',
    }
  }
}
</script>

<style scoped>

</style>