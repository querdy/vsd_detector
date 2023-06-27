import { createRouter, createWebHistory } from 'vue-router'
import EnterpriseFinderView from "@/views/EnterpriseFinderView.vue";
import VSDExaminatorWithXlsx from "@/views/VSDExaminatorWithXlsx.vue";
import VSDExaminatorWithoutXlsx from "@/views/VSDExaminatorWithoutXlsx.vue";

const routes = [
    {
        path: '/',
        name: 'vsd_examinator_without_xlsx',
        component: VSDExaminatorWithoutXlsx
    },
    {
        path: '/vsd_examinator_with_xlsx',
        name: 'vsd_examinator_with_xlsx',
        component: VSDExaminatorWithXlsx
    },
    {
        path: '/enterprise_finder',
        name: 'enterpriseFinder',
        component: EnterpriseFinderView
    }

]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router