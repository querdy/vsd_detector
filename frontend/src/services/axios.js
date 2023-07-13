import axios from 'axios';
const API = axios.create({
    baseURL: process.env.VUE_APP_BASE_URL_API,
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem("JWT")}`,
    },
});

export default API