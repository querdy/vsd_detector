import {defineStore} from "pinia";
import {ref, watch} from 'vue';

export const useWebsocketStore = defineStore('websocketStore', () => {
    const isRun = ref(false)
    const progress = ref(0)
    const vsdProgress = ref(0)
    const fileProgress = ref('0/0')
    const prediction = ref('')
    const log = ref([])


    const setIsRun = async (newIsRun) => {
        isRun.value = newIsRun
    }
    const setProgress = async (newProgress) => {
        progress.value = newProgress
    }
    const setVsdProgress = async (newVsdProgress) => {
        vsdProgress.value = newVsdProgress
    }
    const setFileProgress = async (newFileProgress) => {
        fileProgress.value = newFileProgress
    }
    const setPrediction = async (newPrediction) => {
        prediction.value = newPrediction
    }
    const setLog = async (newLog) => {
        if (log.value.length > 12) {
            log.value.pop()
        }
        log.value.unshift(newLog)
    }


    return {
        isRun, progress, vsdProgress, fileProgress, prediction, log, setIsRun, setProgress, setVsdProgress,
        setFileProgress, setPrediction, setLog
    }
})