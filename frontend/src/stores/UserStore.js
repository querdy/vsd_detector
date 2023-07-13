import {defineStore} from "pinia";
import {ref, watch} from 'vue';

export const useUserStore = defineStore('userStore', () => {
    const activeUser = ref("")
    const JWT = ref("")
    const LocalStorageJWT = localStorage.getItem("JWT")
    if (LocalStorageJWT) {
        JWT.value = LocalStorageJWT
    }

    watch(
        () => JWT.value, (state) => {
            localStorage.setItem('JWT', state)
        }
    )

    const setJWT = async(newJWT) => {
        JWT.value = newJWT
    }

    const setActiveUser = async(newUser) => {
        activeUser.value = newUser
    }

    return {
        activeUser, JWT, setJWT, setActiveUser
    }
})