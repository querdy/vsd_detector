import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/vsd_examine',
    name: 'vsd_examine',
    component: () => import('../views/VSDExaminationView.vue')
  },
  {
    path: '/enterprise_finder',
    name: 'enterpriseFinder',
    component: () => import('../views/EnterpriseFinderView.vue')
  },
  {
    path: '/report',
    name: 'report',
    component: () => import('../views/ReportView.vue')
  },
  {
    path: '/account',
    name: 'account',
    component: () => import('../views/AccountView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
