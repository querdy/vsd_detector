import axios from 'axios';
const API = axios.create({
    baseURL: process.env.VUE_APP_BASE_URL_API,
    headers: {
        'Content-Type': 'application/json',
        // 'Access-Control-Allow-Origin': '*',
        // 'Access-Control-Allow-Methods': '*',
        'Authorization': `Bearer ${localStorage.getItem("JWT")}`,
        // "Access-Control-Allow-Headers": "Content-Type, Authorization",
        // "Access-Control-Allow-Credentials": "true",
    },
    // xsrfCookieName: 'csrftoken',
    // xsrfHeaderName: 'X-CSRFToken',
    // withCredentials: true
});

export default API